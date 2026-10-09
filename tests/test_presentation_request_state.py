#!/usr/bin/env python3
"""Protect three request-selection regressions with synthetic private state files.

Usage: python3 -m unittest discover -s tests -v
Dependencies: standard library only; no renderer, external API or company data
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / '.claude/skills/ppt-master/scripts'))

from presentation_request import prepare_request  # noqa: E402
from presentation_request_state import apply_session, locked_state  # noqa: E402


class PresentationRequestStateRegression(unittest.TestCase):
    """Use the real request preparation and disk transaction, without generation."""

    def setUp(self) -> None:
        private_root = REPO_ROOT / 'projects'
        private_root.mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(prefix='_selection_regression_', dir=private_root)
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.path = self.base / 'session.json'
        self.brief = {'workflow_version': 2, 'slide_count': 1, 'reference_files': []}

    def invoke(self, brief: dict | None = None, choice: str | None = None,
               token: str | None = None, text: str = '복제해줘') -> tuple[dict, dict]:
        """Apply one synthetic event through the same disk transaction as the CLI."""
        current = self.brief if brief is None else brief
        request_ref = 'SYNTHETIC original request'
        prepared, origin = prepare_request(
            current, text, request_ref, choice, 'SYNTHETIC edit event' if choice is not None else None,
        )
        with locked_state(self.path, REPO_ROOT / 'projects') as state:
            apply_session(state, prepared, origin, current, self.base, request_ref, choice, token, False)
        return prepared, origin

    def assert_edit_stored(self) -> None:
        state = json.loads(self.path.read_text(encoding='utf-8'))
        self.assertEqual(state['selection']['purpose_choice'], 'edit_existing')
        self.assertEqual(state['selection']['purpose_confirmation_ref'], 'SYNTHETIC edit event')
        self.assertFalse(self.path.with_name(self.path.name + '.lock').exists())

    def test_original_copy_resume_preserves_latest_edit(self) -> None:
        _, original = self.invoke()
        _, selected = self.invoke(choice='edit_existing', token=original['selection_context_sha256'])
        before = self.path.read_bytes()

        resumed, origin = self.invoke()

        self.assertEqual(resumed['purpose_choice'], 'edit_existing')
        self.assertEqual(resumed['purpose_confirmation_ref'], 'SYNTHETIC edit event')
        self.assertEqual(origin['purpose_origin'], 'bound_session')
        self.assertEqual(origin['selection_context_sha256'], selected['selection_context_sha256'])
        self.assertEqual(self.path.read_bytes(), before)
        self.assert_edit_stored()

    def test_consumed_copy_callback_cannot_overwrite_newer_edit(self) -> None:
        _, original = self.invoke()
        _, selected = self.invoke(choice='edit_existing', token=original['selection_context_sha256'])
        before = self.path.read_bytes()

        with self.assertRaises(ValueError):
            self.invoke(choice='copy_original', token=original['selection_context_sha256'])

        self.assertNotEqual(original['selection_context_sha256'], selected['selection_context_sha256'])
        self.assertEqual(selected['state_revision'], original['state_revision'] + 1)
        self.assertEqual(self.path.read_bytes(), before)
        self.assert_edit_stored()

    def test_stale_snapshot_rejection_preserves_latest_disk_selection(self) -> None:
        _, original = self.invoke()
        changed = copy.deepcopy(self.brief)
        changed['slide_count'] = 2
        _, refreshed = self.invoke(brief=changed, text='PPT 만들어줘')
        self.invoke(brief=changed, choice='edit_existing', token=refreshed['selection_context_sha256'])
        before = self.path.read_bytes()

        with self.assertRaises(ValueError):
            self.invoke(brief=self.brief, choice='copy_original', token=original['selection_context_sha256'])

        self.assertEqual(self.path.read_bytes(), before)
        self.assert_edit_stored()
