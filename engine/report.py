from __future__ import annotations

import html
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from engine.model import Finding, SEVERITY_ORDER, severity_rank
from engine.criteria_map import criteria_for


def build_payload(findings: list[Finding], files_scanned: int, targets: list[str]) -> dict:
    counts = {lvl: sum(1 for f in findings if f.severity == lvl) for lvl in SEVERITY_ORDER}
    domain_summary: dict[str, int] = {}
    enriched = []
    for f in findings:
        c = criteria_for(f.rule)
        domain_summary[c["domain"]] = domain_summary.get(c["domain"], 0) + 1
        item = asdict(f)
        item["criteria"] = c
        enriched.append(item)
    enriched.sort(key=lambda x: (-severity_rank(x["severity"]), x["target"], x["path"], x["line"]))
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "targets": targets,
        "filesScanned": files_scanned,
        "summary": counts,
        "domainSummary": domain_summary,
        "findings": enriched,
    }


def write_reports(findings: list[Finding], files_scanned: int, targets: list[str], output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(findings, files_scanned, targets)
    (output_dir / "security-report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "security-report.html").write_text(_render_html(payload), encoding="utf-8")
    return payload


def _render_html(payload: dict) -> str:
    counts = payload["summary"]
    total = sum(counts.values())
    domain_summary = payload.get("domainSummary", {})

    if counts.get("CRITICAL", 0) or counts.get("HIGH", 0):
        status_class, status_text = "danger", "위험 신호 발견"
    elif total:
        status_class, status_text = "warn", "주의 항목 확인 필요"
    else:
        status_class, status_text = "ok", "위험 신호 없음"

    # Group findings by rule
    from collections import OrderedDict
    rule_groups: dict[str, dict] = OrderedDict()
    for item in payload["findings"]:
        rule = item["rule"]
        if rule not in rule_groups:
            rule_groups[rule] = {
                "severity": item["severity"],
                "criteria": item["criteria"],
                "message": item["message"],
                "occurrences": [],
            }
        rule_groups[rule]["occurrences"].append(item)

    # Sort groups: by severity desc, then count desc
    sorted_groups = sorted(
        rule_groups.items(),
        key=lambda kv: (-severity_rank(kv[1]["severity"]), -len(kv[1]["occurrences"]))
    )

    # Build rule-group blocks
    group_blocks = []
    for rule_id, grp in sorted_groups:
        sev = grp["severity"].lower()
        c = grp["criteria"]
        occ_count = len(grp["occurrences"])
        group_search = html.escape(
            f'{grp["severity"]} {rule_id} {c["domain"]} {grp["message"]}'.lower(),
            quote=True,
        )

        # Build occurrence rows for this group's inner table
        occ_rows = []
        for item in grp["occurrences"]:
            occ_search = html.escape(
                f'{item["severity"]} {rule_id} {item["target"]} {c["domain"]} {item["path"]} {item["message"]}'.lower(),
                quote=True,
            )
            evidence_block = (
                f'<div class="field"><span>발견 내용</span><code>{html.escape(item["evidence"])}</code></div>'
                if item["evidence"] else ""
            )
            occ_rows.append(
                f'<tr class="occ-row" data-target="{html.escape(item["target"])}" data-search="{occ_search}">'
                f'<td data-label="대상">{html.escape(item["target"])}</td>'
                f'<td data-label="위치"><code>{html.escape(item["path"])}:{item["line"]}</code></td>'
                f'<td data-label="결과"><strong>{html.escape(item["message"])}</strong>'
                f'<details class="inner-detail"><summary>상세 보기</summary><div class="detail">{evidence_block}'
                f'<div class="field"><span>권장 조치</span><p>{html.escape(item["recommendation"])}</p></div>'
                f'</div></details></td></tr>'
            )

        occ_table = (
            f'<div class="occ-table-wrap"><table class="occ-table"><thead><tr>'
            f'<th>대상</th><th>위치</th><th>결과</th>'
            f'</tr></thead><tbody>{"".join(occ_rows)}</tbody></table></div>'
        )

        group_blocks.append(
            f'<details class="rule-group" data-severity="{sev}" '
            f'data-domain="{html.escape(c["domain"])}" data-search="{group_search}" '
            f'data-count="{occ_count}">'
            f'<summary class="group-summary">'
            f'<span class="badge {sev}">{html.escape(grp["severity"])}</span>'
            f'<code class="rule">{html.escape(rule_id)}</code>'
            f'<span class="group-title">{html.escape(grp["message"])}</span>'
            f'<span class="group-domain">{html.escape(c["domain"])}</span>'
            f'<span class="group-count occ-visible-count">{occ_count}건</span>'
            f'</summary>'
            f'{occ_table}'
            f'</details>'
        )

    # Build domain summary cards
    domain_cards = "".join(
        f'<div class="card domain"><div class="label">{html.escape(d)}</div>'
        f'<div class="value">{n}</div></div>'
        for d, n in sorted(domain_summary.items(), key=lambda kv: -kv[1])
    ) or ""

    # Build unique target and domain option lists for filter selects
    unique_targets = sorted({item["target"] for item in payload["findings"]})
    unique_domains = sorted({item["criteria"]["domain"] for item in payload["findings"]})
    target_options = "".join(
        f'<option value="{html.escape(t)}">{html.escape(t)}</option>'
        for t in unique_targets
    )
    domain_options = "".join(
        f'<option value="{html.escape(d)}">{html.escape(d)}</option>'
        for d in unique_domains
    )

    targets_meta = html.escape(", ".join(payload["targets"]))

    return (
        '<!doctype html><html lang="ko"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>보안 점검 리포트</title>'
        '<style>'
        ':root{--bg:#eef1f7;--panel:#fff;--ink:#1a2233;--muted:#6b7488;--line:#e6eaf2;--accent:#4f6bff;--accent2:#8a5cff;--critical:#dc2626;--high:#ea580c;--medium:#ca8a04;--low:#0284c7;--info:#4f46e5;--ok:#059669;--warn:#b45309;--danger:#dc2626}'
        '*{box-sizing:border-box}'
        'body{margin:0;background:radial-gradient(1200px 600px at 100% -10%,#dfe6ff 0,transparent 55%),var(--bg);color:var(--ink);font:14px/1.6 system-ui,-apple-system,"Segoe UI","Malgun Gothic",sans-serif}'
        '.shell{max-width:1280px;margin:auto;padding:40px 24px 72px}'
        '.hero{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:28px 30px;overflow:hidden;box-shadow:0 10px 40px #1a22330d}'
        '.hero::before{content:"";position:absolute;inset:0 0 auto 0;height:4px;background:linear-gradient(90deg,var(--accent),var(--accent2))}'
        '.eyebrow{color:var(--accent);font-weight:800;letter-spacing:.14em;text-transform:uppercase;font-size:11px}'
        'h1{font-size:30px;letter-spacing:-.03em;margin:8px 0 6px}'
        '.sub{color:var(--muted);margin:0 0 18px;max-width:62ch}'
        '.meta{display:flex;gap:10px;flex-wrap:wrap}'
        '.meta span{background:#f4f6fc;border:1px solid var(--line);color:var(--muted);border-radius:999px;padding:5px 12px;font-size:12px}'
        '.status{position:absolute;top:26px;right:28px;display:inline-flex;align-items:center;gap:7px;border-radius:999px;padding:8px 15px;font-weight:800;font-size:13px}'
        '.status::before{content:"";width:8px;height:8px;border-radius:50%;background:currentColor}'
        '.status.ok{background:#ecfdf3;color:var(--ok);border:1px solid #b7ebcd}'
        '.status.warn{background:#fff7ed;color:var(--warn);border:1px solid #fed7aa}'
        '.status.danger{background:#fef2f2;color:var(--danger);border:1px solid #fecaca}'
        '.cards{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:20px 0 14px}'
        '.card{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px 18px 16px 22px;box-shadow:0 4px 18px #1a223308;transition:transform .15s,box-shadow .15s}'
        '.card:hover{transform:translateY(-2px);box-shadow:0 10px 28px #1a223314}'
        '.card::before{content:"";position:absolute;left:0;top:14px;bottom:14px;width:3px;border-radius:3px;background:var(--muted)}'
        '.card.critical::before{background:var(--critical)}.card.high::before{background:var(--high)}.card.medium::before{background:var(--medium)}.card.low::before{background:var(--low)}.card.total::before{background:var(--accent)}.card.domain::before{background:var(--accent2)}'
        '.card .label{color:var(--muted);font-size:12px;font-weight:700}'
        '.card .value{font-size:30px;font-weight:850;margin-top:2px}'
        '.card.critical .value{color:var(--critical)}.card.high .value{color:var(--high)}.card.medium .value{color:var(--medium)}.card.low .value{color:var(--low)}'
        '.domain-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:0 0 14px}'
        '.domain-cards .card.domain .value{font-size:22px}'
        '.panel{background:var(--panel);border:1px solid var(--line);border-radius:18px;box-shadow:0 4px 18px #1a223308;overflow:hidden}'
        '.toolbar{display:flex;gap:10px;align-items:center;padding:16px;border-bottom:1px solid var(--line);flex-wrap:wrap}'
        'input,select{border:1px solid #d6dce8;border-radius:10px;background:#fff;padding:10px 13px;color:var(--ink);font:inherit}'
        'input{min-width:220px;flex:1}'
        'input:focus,select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px #4f6bff22}'
        '.result-count{margin-left:auto;color:var(--muted);font-size:12px;font-weight:600}'
        '.groups-wrap{padding:12px 16px}'
        '.rule-group{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-bottom:10px;overflow:hidden;transition:box-shadow .15s}'
        '.rule-group:hover{box-shadow:0 4px 18px #1a223310}'
        '.rule-group[data-severity="critical"]{border-left:4px solid var(--critical)}'
        '.rule-group[data-severity="high"]{border-left:4px solid var(--high)}'
        '.rule-group[data-severity="medium"]{border-left:4px solid var(--medium)}'
        '.rule-group[data-severity="low"]{border-left:4px solid var(--low)}'
        '.rule-group[data-severity="info"]{border-left:4px solid var(--info)}'
        '.group-summary{display:flex;align-items:center;gap:10px;padding:14px 16px;cursor:pointer;list-style:none;flex-wrap:wrap}'
        '.group-summary::-webkit-details-marker{display:none}'
        '.group-summary::before{content:"\\25b8";color:var(--muted);font-size:11px;min-width:14px}'
        '.rule-group[open] > .group-summary::before{content:"\\25be"}'
        '.group-title{color:var(--ink);font-weight:600;font-size:13px;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
        '.group-domain{color:var(--muted);font-size:12px;background:#f4f6fc;border:1px solid var(--line);border-radius:999px;padding:3px 10px}'
        '.group-count{background:var(--accent);color:#fff;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:800}'
        '.occ-table-wrap{overflow:auto;border-top:1px solid var(--line)}'
        '.occ-table{border-collapse:collapse;width:100%;min-width:600px}'
        '.occ-table th{background:#fafbfe;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;padding:10px 14px;text-align:left;border-bottom:1px solid var(--line)}'
        '.occ-table td{border-bottom:1px solid var(--line);padding:10px 14px;vertical-align:top}'
        '.occ-table tbody tr:last-child td{border-bottom:none}'
        '.occ-table tbody tr:hover{background:#f7f9ff}'
        '.rule{font:12px ui-monospace,Consolas,monospace;background:#f1f3fb;border-radius:6px;padding:2px 6px}'
        '.rule-title{display:block;color:var(--muted);font-size:11px;margin-top:3px}'
        'code{font:12px/1.6 ui-monospace,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere}'
        '.badge{display:inline-flex;border-radius:999px;padding:4px 10px;font-size:11px;font-weight:850;letter-spacing:.02em}'
        '.badge.critical{background:#fee2e2;color:var(--critical)}.badge.high{background:#ffedd5;color:var(--high)}.badge.medium{background:#fef3c7;color:var(--medium)}.badge.low{background:#e0f2fe;color:var(--low)}.badge.info{background:#eef2ff;color:var(--info)}'
        'details.inner-detail{margin-top:8px}'
        'details.inner-detail summary{cursor:pointer;color:var(--accent);font-weight:700;font-size:12px;list-style:none}'
        'details.inner-detail summary::-webkit-details-marker{display:none}'
        'details.inner-detail summary::before{content:"\\25b8 ";font-size:10px}'
        'details.inner-detail[open] summary::before{content:"\\25be "}'
        '.detail{margin-top:10px;border-left:3px solid #dce4ff;padding-left:14px;display:grid;gap:10px}'
        '.field span{display:block;font-size:11px;font-weight:800;color:var(--muted);margin-bottom:4px}'
        '.field p{margin:0}'
        '.empty{padding:56px;text-align:center;color:var(--muted);display:none}'
        'footer{color:var(--muted);font-size:12px;margin-top:18px;text-align:center}'
        '@media(max-width:820px){'
        '.cards{grid-template-columns:repeat(2,1fr)}'
        '.status{position:static;margin-top:14px}'
        '.occ-table,.occ-table thead,.occ-table tbody,.occ-table th,.occ-table td,.occ-table tr{display:block}'
        '.occ-table thead{display:none}'
        '.occ-table{min-width:0}'
        '.occ-table tbody tr{border:1px solid var(--line);border-radius:12px;margin:8px;padding:4px}'
        '.occ-table td{border-bottom:1px solid var(--line)}'
        '.occ-table td:last-child{border-bottom:none}'
        "td::before{content:attr(data-label);display:block;font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700;margin-bottom:4px}}"
        '</style></head><body><main class="shell">'
        '<section class="hero">'
        '<div class="eyebrow">FSI Vuln Scanner</div>'
        '<h1>보안 점검 리포트</h1>'
        '<p class="sub">금융보안원 2026 취약점 분석·평가기준 연계 정적 점검 결과입니다.</p>'
        f'<div class="meta">'
        f'<span>생성 {html.escape(payload["generatedAt"])}</span>'
        f'<span>대상 {len(payload["targets"])}개</span>'
        f'<span>검사 파일 {payload["filesScanned"]}개</span>'
        f'<span>대상: {targets_meta}</span>'
        f'</div>'
        f'<div class="status {status_class}">{status_text}</div>'
        '</section>'
        '<section class="cards">'
        f'<div class="card critical"><div class="label">치명</div><div class="value">{counts.get("CRITICAL",0)}</div></div>'
        f'<div class="card high"><div class="label">높음</div><div class="value">{counts.get("HIGH",0)}</div></div>'
        f'<div class="card medium"><div class="label">중간</div><div class="value">{counts.get("MEDIUM",0)}</div></div>'
        f'<div class="card low"><div class="label">낮음</div><div class="value">{counts.get("LOW",0)}</div></div>'
        f'<div class="card total"><div class="label">전체 발견 항목</div><div class="value">{total}</div></div>'
        '</section>'
        + (f'<section><p style="margin:0 0 8px;font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em">금보원 분야별 현황</p>'
           f'<div class="domain-cards">{domain_cards}</div></section>'
           if domain_cards else '')
        +
        '<section class="panel">'
        '<div class="toolbar">'
        '<input id="search" type="search" placeholder="파일, 규칙, 메시지, 대상, 분야 검색...">'
        '<select id="severity"><option value="all">모든 심각도</option>'
        '<option value="critical">Critical</option>'
        '<option value="high">High</option>'
        '<option value="medium">Medium</option>'
        '<option value="low">Low</option>'
        '<option value="info">Info</option></select>'
        f'<select id="target"><option value="all">모든 대상</option>{target_options}</select>'
        f'<select id="domain"><option value="all">모든 분야</option>{domain_options}</select>'
        '<span class="result-count" id="result-count"></span>'
        '</div>'
        '<div class="groups-wrap" id="findings">'
        + "".join(group_blocks) +
        '<div class="empty" id="empty">필터 조건에 맞는 결과가 없습니다.</div>'
        '</div>'
        '</section>'
        '<footer>자동화된 정적 점검 결과이며, 침투 테스트나 보안 인증을 대체하지 않습니다. '
        '금보원 항목은 공개 분야 분류 기준 근사 매핑입니다.</footer>'
        '</main>'
        '<script>'
        'const groups=[...document.querySelectorAll(\'.rule-group\')],'
        'search=document.getElementById(\'search\'),'
        'severity=document.getElementById(\'severity\'),'
        'targetSel=document.getElementById(\'target\'),'
        'domainSel=document.getElementById(\'domain\'),'
        'count=document.getElementById(\'result-count\'),'
        'empty=document.getElementById(\'empty\');'
        'function filter(){'
        'const q=search.value.toLowerCase().trim(),'
        's=severity.value,'
        't=targetSel.value,'
        'd=domainSel.value;'
        'let total=0;'
        'groups.forEach(g=>{'
        'const gs=g.dataset.severity,gd=g.dataset.domain;'
        'const sevOk=(s===\'all\'||gs===s);'
        'const domOk=(d===\'all\'||gd===d);'
        'if(!sevOk||!domOk){g.style.display=\'none\';return;}'
        'const occRows=[...g.querySelectorAll(\'.occ-row\')];'
        'let vis=0;'
        'occRows.forEach(r=>{'
        'const tOk=(t===\'all\'||r.dataset.target===t);'
        'const qOk=(!q||r.dataset.search.includes(q)||g.dataset.search.includes(q));'
        'const ok=tOk&&qOk;'
        'r.style.display=ok?\'\':\'none\';'
        'if(ok)vis++;'
        '});'
        'if(vis===0&&(t!==\'all\'||q)){g.style.display=\'none\';return;}'
        'g.style.display=\'\';'
        'const vc=g.querySelector(\'.occ-visible-count\');'
        'if(vc)vc.textContent=vis+\'건\';'
        'total+=vis;'
        '});'
        'count.textContent=`${total}개 표시`;'
        'const anyVisible=groups.some(g=>g.style.display!==\'none\');'
        'empty.style.display=anyVisible?\'none\':\'block\';'
        '}'
        'search.addEventListener(\'input\',filter);'
        'severity.addEventListener(\'change\',filter);'
        'targetSel.addEventListener(\'change\',filter);'
        'domainSel.addEventListener(\'change\',filter);'
        'filter();'
        '</script></body></html>'
    )
