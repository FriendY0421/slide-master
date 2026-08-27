import { App } from "@modelcontextprotocol/ext-apps";

const app = new App(
  { name: "Slide Master Template Picker", version: "1.0.0" },
  {},
  { autoResize: true, strict: false },
);

const root = document.getElementById("root");
let payload = null;
let selectedTemplate = null;
let selectedPreset = null;
let detailTemplate = null;
let mode = "recommended";
let kind = "all";
let query = "";
let page = 1;
const PAGE_SIZE = 6;

const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[c]));

function persistState() {
  window.openai?.setWidgetState?.({
    selectedTemplate: selectedTemplate?.id ?? null,
    selectedPreset: selectedPreset?.id ?? null,
    mode, kind, query, page,
  });
}

function bind(selector, fn) {
  root.querySelectorAll(selector).forEach((el) => el.addEventListener("click", () => fn(el)));
}

function currentTemplates() {
  const base = mode === "all" ? payload.all_templates : payload.shortlist;
  const q = query.trim().toLowerCase();
  return base.filter((t) => {
    if (kind !== "all" && t.template_kind !== kind) return false;
    if (!q) return true;
    return [t.name, t.id, t.summary, t.reason, t.cat].join(" ").toLowerCase().includes(q);
  });
}

function templateCard(t) {
  const preview = t.previews?.[0]?.src || "";
  return `<button type="button" class="template-card${selectedTemplate?.id === t.id ? " selected" : ""}" data-open="${esc(t.id)}">
    <div class="preview">${preview ? `<img src="${preview}" alt="${esc(t.name)} 대표 미리보기">` : "<span>Preview unavailable</span>"}</div>
    <div class="card-body">
      <div class="card-title">${t.rec ? '<span class="badge">추천</span>' : ""}${esc(t.name)}</div>
      <div class="card-id">${esc(t.id)}</div>
      <p>${esc(t.summary)}</p><small>${esc(t.reason || "")}</small>
    </div>
  </button>`;
}

function presetCard(p) {
  const rank = p.recommended_rank ? `<span class="rank">추천 ${p.recommended_rank}</span>` : "";
  return `<button type="button" class="preset-card${selectedPreset?.id === p.id ? " selected" : ""}" data-preset="${esc(p.id)}">
    <strong>${rank}${esc(p.display_name)}</strong><span>${esc(p.summary)}</span>
    <small>${esc(p.slide_range)}장 · 텍스트 ${esc(p.visual_ratio?.text)}% / 시각 ${esc(p.visual_ratio?.visual)}%</small>
  </button>`;
}

function renderGallery() {
  const filtered = currentTemplates();
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  page = Math.min(Math.max(page, 1), pages);
  const start = (page - 1) * PAGE_SIZE;
  const list = filtered.slice(start, start + PAGE_SIZE);
  root.innerHTML = `<section class="picker-shell">
    <header><div><strong>Slide Master 템플릿 선택</strong><p>${esc(payload.purpose)}</p></div>
      <div class="tabs"><button data-mode="recommended" class="${mode === "recommended" ? "active" : ""}">추천</button><button data-mode="all" class="${mode === "all" ? "active" : ""}">전체</button></div></header>
    <div class="toolbar"><input data-search type="search" value="${esc(query)}" placeholder="템플릿 이름·ID·특징 검색" aria-label="템플릿 검색">
      <div class="filters"><button data-kind="all" class="${kind === "all" ? "active" : ""}">전체</button><button data-kind="deck" class="${kind === "deck" ? "active" : ""}">Deck</button><button data-kind="layout" class="${kind === "layout" ? "active" : ""}">Layout</button></div></div>
    <div class="summary">${filtered.length}개 표시 · 페이지 ${page}/${pages}</div>
    ${list.length ? `<div class="grid">${list.map(templateCard).join("")}</div>` : '<div class="empty">조건에 맞는 템플릿이 없습니다.</div>'}
    <div class="pager"><button type="button" data-prev ${page <= 1 ? "disabled" : ""}>← 이전</button><span>${page} / ${pages}</span><button type="button" data-next ${page >= pages ? "disabled" : ""}>다음 →</button></div>
    <div class="free"><button type="button" data-free>Free Design 선택</button></div>
  </section>`;
  bind("[data-mode]", (el) => { mode = el.dataset.mode; page = 1; persistState(); renderGallery(); });
  bind("[data-kind]", (el) => { kind = el.dataset.kind; page = 1; persistState(); renderGallery(); });
  bind("[data-prev]", () => { page -= 1; persistState(); renderGallery(); });
  bind("[data-next]", () => { page += 1; persistState(); renderGallery(); });
  bind("[data-open]", (el) => { detailTemplate = payload.all_templates.find((x) => x.id === el.dataset.open); renderDetail(); });
  bind("[data-free]", () => { selectedTemplate = { id: "free", name: "Free Design", previews: [] }; persistState(); renderPresets(); });
  const search = root.querySelector("[data-search]");
  search?.addEventListener("input", (event) => { query = event.target.value; page = 1; persistState(); renderGallery(); });
}

function renderDetail() {
  const t = detailTemplate;
  const shots = (t.previews || []).map((p) => `<figure><img src="${p.src}" alt="${esc(p.label)}"><figcaption>${esc(p.label)}</figcaption></figure>`).join("");
  root.innerHTML = `<section class="picker-shell">
    <header><button type="button" data-back>← 다른 템플릿 보기</button><div><strong>${esc(t.name)}</strong><p>${esc(t.id)} · ${esc(t.summary)}</p></div></header>
    <div class="detail-grid">${shots}</div>
    <div class="actions"><button type="button" class="primary" data-use>이 템플릿 선택</button></div>
  </section>`;
  bind("[data-back]", () => renderGallery());
  bind("[data-use]", () => { selectedTemplate = t; persistState(); renderPresets(); });
}

function renderPresets() {
  root.innerHTML = `<section class="picker-shell">
    <header><button type="button" data-back>← 템플릿으로</button><div><strong>제작 방식 선택</strong><p>${esc(selectedTemplate?.name || selectedTemplate?.id)}</p></div></header>
    <div class="preset-grid">${(payload.presets || []).map(presetCard).join("")}</div>
    <div class="actions"><button type="button" class="primary" data-next ${selectedPreset ? "" : "disabled"}>선택 내용 확인</button></div>
  </section>`;
  bind("[data-back]", () => renderGallery());
  bind("[data-preset]", (el) => { selectedPreset = payload.presets.find((x) => x.id === el.dataset.preset); persistState(); renderPresets(); });
  bind("[data-next]", () => renderFinal());
}

const localToken = () => `${selectedTemplate.id} | preset:${selectedPreset.id}`;

async function confirmSelection() {
  let token = localToken();
  try {
    const validated = await app.callServerTool({
      name: "validate_slide_master_selection",
      arguments: { purpose: payload.purpose, template_id: selectedTemplate.id, preset_id: selectedPreset.id },
    });
    token = validated?.structuredContent?.selection_token || token;
  } catch (error) {
    root.innerHTML = `<section class="picker-shell final warning"><h2>선택 검증에 실패했습니다</h2><p>템플릿 목록을 새로 열어 다시 선택해주세요.</p><small>${esc(error?.message || "selection validation failed")}</small></section>`;
    return;
  }

  const message = `PPT 템플릿 최종 선택: ${token}. 이 선택을 확정하고 Slide Master 게이트에 템플릿과 제작 프리셋을 기록한 뒤 PPT 제작을 계속 진행해줘.`;
  try {
    await app.updateModelContext({ content: [{ type: "text", text: `선택된 PPT 구성: ${token}` }] });
    const result = await app.sendMessage({ role: "user", content: [{ type: "text", text: message }] });
    if (result?.isError) throw new Error("host rejected selection message");
    root.innerHTML = `<section class="picker-shell final success"><h2>선택이 채팅에 전달되었습니다</h2><code>${esc(token)}</code><p>이 선택값을 기준으로 다음 PPT 제작 단계가 진행됩니다.</p></section>`;
  } catch (error) {
    root.innerHTML = `<section class="picker-shell final warning"><h2>자동 전달을 사용할 수 없습니다</h2><p>아래 선택값을 채팅에 보내주세요.</p><code>${esc(token)}</code><small>${esc(error?.message || "host message bridge unavailable")}</small></section>`;
  }
}

function renderFinal() {
  const token = localToken();
  root.innerHTML = `<section class="picker-shell final">
    <button type="button" data-back>← 제작 방식 다시 선택</button><h2>선택 내용 확인</h2>
    <dl><dt>템플릿</dt><dd>${esc(selectedTemplate.name || selectedTemplate.id)}</dd><dt>제작 방식</dt><dd>${esc(selectedPreset.display_name)}</dd><dt>선택 ID</dt><dd><code>${esc(token)}</code></dd></dl>
    <button type="button" class="primary confirm" data-confirm>이 구성으로 PPT 제작</button>
  </section>`;
  bind("[data-back]", () => renderPresets());
  bind("[data-confirm]", () => confirmSelection());
}

const style = document.createElement("style");
style.textContent = `:root{font-family:Inter,Pretendard,"Malgun Gothic",system-ui,sans-serif;color:#172033}*{box-sizing:border-box}body{margin:0;background:transparent}.picker-shell{padding:12px;min-width:0}header{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:14px}header strong{font-size:20px}header p{margin:4px 0;color:#657086;font-size:13px}.tabs,.filters,.pager{display:flex;gap:6px;align-items:center}.tabs button,header button,.free button,.actions button,.final button,.filters button,.pager button{border:1px solid #d5dbe7;background:#fff;border-radius:10px;padding:9px 12px;cursor:pointer}.tabs .active,.filters .active,.primary{background:#3157d5!important;color:#fff!important;border-color:#3157d5!important}.toolbar{display:grid;grid-template-columns:minmax(180px,1fr) auto;gap:8px;margin-bottom:8px}.toolbar input{min-height:42px;border:1px solid #d5dbe7;border-radius:10px;padding:8px 11px;font-size:16px}.summary{color:#667085;font-size:12px;margin:6px 0 10px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.template-card,.preset-card{border:1px solid #dce2ec;background:#fff;border-radius:14px;padding:0;text-align:left;overflow:hidden;cursor:pointer}.template-card.selected,.preset-card.selected{outline:3px solid #3157d533;border-color:#3157d5}.preview{aspect-ratio:16/9;background:#f1f4f8;display:flex;align-items:center;justify-content:center}.preview img{width:100%;height:100%;object-fit:contain;background:#fff}.card-body{padding:12px}.card-title{font-weight:800}.badge,.rank{font-size:10px;background:#e8edff;color:#3157d5;border-radius:999px;padding:3px 6px;margin-right:6px}.card-id{font:11px ui-monospace,monospace;color:#758197;margin-top:4px}.card-body p{font-size:13px;line-height:1.45;margin:8px 0}.card-body small{display:block;color:#667085;line-height:1.4}.detail-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}.detail-grid figure{margin:0;border:1px solid #dce2ec;border-radius:12px;overflow:hidden;background:#fff}.detail-grid img{width:100%;aspect-ratio:16/9;object-fit:contain}.detail-grid figcaption{padding:8px;font-size:12px}.preset-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}.preset-card{padding:13px;display:flex;flex-direction:column;gap:5px}.preset-card span,.preset-card small{color:#667085}.actions,.free{display:flex;justify-content:flex-end;margin-top:14px}.pager{justify-content:center;margin-top:14px}.pager button:disabled,.actions button:disabled{opacity:.45;cursor:not-allowed}.empty{text-align:center;padding:24px;border:1px dashed #d5dbe7;border-radius:12px;color:#667085}.final{display:grid;gap:12px}.final dl{display:grid;grid-template-columns:90px 1fr;gap:8px;margin:0}.final dt{color:#667085}.final dd{margin:0;font-weight:700}.final code{display:block;padding:10px;background:#f3f5f9;border-radius:9px;overflow-wrap:anywhere}.confirm{min-height:44px}.success{border-left:4px solid #1a8f5a}.warning{border-left:4px solid #c47700}@media(max-width:620px){header{flex-direction:column}.toolbar{grid-template-columns:1fr}.filters{flex-wrap:wrap}.grid,.detail-grid,.preset-grid{grid-template-columns:1fr}.final dl{grid-template-columns:1fr}}`;
document.head.appendChild(style);

app.ontoolresult = (result) => {
  payload = result?._meta?.pickerPayload || result?.structuredContent?.pickerPayload || null;
  if (!payload) { root.innerHTML = '<section class="picker-shell warning">템플릿 데이터를 불러오지 못했습니다.</section>'; return; }
  const prior = window.openai?.widgetState;
  if (prior) {
    mode = prior.mode || mode; kind = prior.kind || kind; query = prior.query || query; page = prior.page || page;
  }
  renderGallery();
};

root.innerHTML = '<section class="picker-shell">최신 Slide Master 템플릿을 불러오는 중입니다…</section>';
await app.connect();
