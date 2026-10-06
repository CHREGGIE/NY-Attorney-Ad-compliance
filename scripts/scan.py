#!/usr/bin/env python3
"""First-pass scanner for NY attorney-advertising red flags.

High recall, low precision by design: every hit must be judged in context.
It cannot detect false facts, misleading omissions, or solicitation context.

Usage:
    python scan.py <file-or-folder> [<file-or-folder> ...] [--json]
    cat copy.txt | python scan.py - [--json]

Accepts .txt, .md, .html/.htm files. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path

# (category, rule, default severity, regex)
PATTERNS: list[tuple[str, str, str, str]] = [
    ("Outcome guarantee", "7.1(a)", "Block",
     r"\bguarantee[ds]?\b|\bwe (?:always )?win\b|\bnever (?:lose|lost)\b|\bresults? guaranteed\b|"
     r"\b100\s?% (?:success|win)|\bwe(?:'ll| will) get you\b|\bmaximum (?:compensation|recovery)\b|"
     r"\b(?:compensation|justice|results?) you deserve\b"),
    ("Superlative / quality claim", "7.1(a)", "Revise",
     r"\b(?:best|top(?:-rated)?|leading|premier|preeminent|finest|foremost|elite|unmatched|unrivall?ed|"
     r"unparall?eled|second to none|world[- ]class)\b|#\s?1\b|\bnumber one\b|\bno\.\s?1\b|"
     r"\bmost (?:experienced|trusted|respected|successful|aggressive|powerful|feared)\b"),
    ("Comparison with other lawyers", "7.1(a)", "Revise",
     r"\b(?:more|better|bigger|larger|faster|stronger) than (?:any|other|all|most)\b|\bthan any other\b|"
     r"\bunlike (?:other|most|big|large) (?:firms?|lawyers?|attorneys?)\b|\bthe only (?:firm|lawyer|attorney)\b"),
    ("Certified-specialist claim (name certifier)", "7.1(c)", "Block",
     r"\b(?:board[- ])?certifi(?:ed|cation)\b"),
    ("Specialist / expert claim (verify accuracy)", "7.1(a), Cmt [7]", "Verify",
     r"\bspeciali[sz](?:t|ts|e|es|ed|ing|ation)\b|\bspecialty\b|\bexperts?\b|\bexpertise\b"),
    ("Case result / dollar figure (context + disclaimer)", "7.1(a)", "Revise",
     r"\$\s?\d[\d,.]*\s?(?:million|billion|[mbk])?\b|\b\d{1,3}\s?% (?:success|win|of cases)\b|"
     r"\bwin rate\b|\bsuccess rate\b|\bverdicts?\b|\bsettlements?\b|\brecovered\b"),
    ("Experience / size claim (verify, anchor to year)", "7.1(a)", "Verify",
     r"\b(?:over|more than|nearly|almost)?\s?\d+\+?\s+years\b|\bdecades of\b|\bcombined experience\b|"
     r"\b(?:hundreds|thousands) of (?:cases|clients|matters)\b"),
    ("Implied structure / size", "7.1(a), 7.5", "Revise",
     r"&\s?associates\b|\band associates\b|\bteam of (?:attorneys|lawyers|litigators)\b|\barmy of\b|"
     r"\bnationwide\b|\boffices (?:across|throughout|in)\b|\bnetwork of (?:firms|attorneys|lawyers)\b"),
    ("Influence / insider implication", "7.1(a), 8.4", "Block",
     r"\b(?:relationships?|connections?|ties) (?:with|to) (?:the )?(?:judges?|courts?|prosecutors?|DAs?|"
     r"district attorneys?|agency|officials?)\b|\bknows? (?:the|how) (?:judges?|prosecutors?|DAs?)\b|"
     r"\binside (?:track|connections?)\b"),
    ("Award / rating (issuer + year)", "7.1(a)", "Verify",
     r"\bsuper ?lawyers?\b|\brising stars?\b|\bbest lawyers\b|\bmartindale\b|\bAV[- ]?(?:preeminent|rated)\b|"
     r"\bavvo\b|\bchambers\b|\blegal 500\b|\btop (?:10|25|40|50|100)\b|\blawyer of the year\b|\baward"),
    ("Testimonial / review content", "7.1(a), FTC, Google", "Verify",
     r"\btestimonials?\b|\b(?:5|five)[- ]stars?\b|\breviews?\b|\brated \d"),
    ("Referral incentive", "7.2(a), Jud. Law 482", "Block",
     r"\breferral (?:bonus|reward|fee|gift|credit|program)\b|\brefer a friend\b|\bgift cards?\b|"
     r"\bfinder'?s fee\b|\bpay[- ]per[- ](?:lead|case|client|signed)\b"),
    ("Fee claim (completeness)", "7.1(a)", "Verify",
     r"\bno (?:attorney'?s? )?fees? unless\b|\bno recovery,? no fee\b|\bfree consultation\b|\bflat fee\b|"
     r"\baffordable\b|\blow[- ]cost\b"),
    ("Client identity (consent?)", "1.6", "Verify",
     r"\bclients include\b|\bour clients\b|\bwe represented\b|\brepresented (?:[A-Z][\w&.]+\s?){1,4}(?:in|against)\b"),
    ("Legal-document / government look-alike", "7.1(a), 8.4(c)", "Block",
     r"\b(?:legal|official|court) notice\b|\bsummons\b|\bnotice of (?:claim|action|rights)\b|\bfinal notice\b"),
    ("Restricted name term", "7.5(b)(2)", "Block",
     r"\blegal aid\b|\blegal services? office\b|\blegal assistance office\b|\bdefender office\b|"
     r"\bnon-?profit\b|\bnot-for-profit\b"),
    ("Urgency / fear", "7.1(a)", "Revise",
     r"\bact now\b|\bbefore it'?s too late\b|\blose your rights\b|\burgent\b|\bdon'?t wait\b"),
    ("AI / draft artifact", "7.1(a), 8.4(c)", "Block",
     r"lorem ipsum|\[(?:insert|firm name|name|city|year|tbd)[^\]]*\]|\bTBD\b|\bXX+\b|as an ai\b"),
]

PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+(?:[A-Z0-9][\w.'-]*\s+){1,5}(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Pl|Place|"
    r"Plaza|Broadway|Ln|Lane|Dr|Drive|Way|Pkwy|Parkway|Ct|Court|Sq|Square|Ter|Terrace)\b\.?", re.I)
ENTITY_RE = re.compile(r"\b(?:PLLC|LLP|LLC|P\.?C\.?)\b")


@dataclass
class Hit:
    file: str
    line: int
    category: str
    rule: str
    severity: str
    match: str
    context: str


class _Text(HTMLParser):
    """Extract visible text, meta descriptions/titles, alt text, and JSON-LD blocks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.jsonld: list[str] = []
        self._skip = 0
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._in_jsonld = True
        elif tag in ("script", "style", "noscript"):
            self._skip += 1
        if tag == "meta" and (a.get("name") or a.get("property") or "").lower() in (
                "description", "og:description", "og:title", "twitter:title", "twitter:description"):
            self.parts.append(f"\n[meta] {a.get('content', '')}\n")
        if tag == "img" and a.get("alt"):
            self.parts.append(f"\n[alt] {a['alt']}\n")
        if tag in ("p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "footer", "title"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
        elif tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_jsonld:
            self.jsonld.append(data)
        elif not self._skip:
            self.parts.append(data)


def load(path: Path | None, raw: str | None = None) -> tuple[str, list[str]]:
    text = raw if raw is not None else path.read_text(encoding="utf-8", errors="replace")
    name = (path.suffix.lower() if path else "")
    if name in (".html", ".htm") or (raw is not None and "<html" in text.lower()):
        p = _Text()
        p.feed(text)
        visible = re.sub(r"[ \t]+", " ", "".join(p.parts))
        visible = re.sub(r"\n\s*\n+", "\n", visible)
        return visible, p.jsonld
    return text, []


def scan_text(label: str, text: str, jsonld: list[str]) -> tuple[list[Hit], list[str]]:
    hits: list[Hit] = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        for cat, rule, sev, rx in PATTERNS:
            for m in re.finditer(rx, line, re.I):
                ctx = line.strip()
                if len(ctx) > 160:
                    s = max(0, m.start() - 70)
                    ctx = ("…" if s else "") + line[s:s + 160].strip() + "…"
                hits.append(Hit(label, i, cat, rule, sev, m.group(0), ctx))

    notes: list[str] = []
    if not PHONE_RE.search(text) and not ADDRESS_RE.search(text):
        notes.append("7.1(d): no phone number or street address found. Confirm a sitewide footer or "
                     "profile supplies responsible-lawyer/firm contact info.")
    if not ENTITY_RE.search(text):
        notes.append("Entity designator (PLLC/LLP/LLC/PC) not found. Confirm the firm's legal name appears somewhere.")
    for block in jsonld:
        low = block.lower()
        if "aggregaterating" in low or '"review"' in low:
            notes.append("Schema: aggregateRating/review markup on the firm's own entity. Self-serving, not "
                         "eligible for Google review rich results; verify ratings are genuine (7.1(a)).")
        for kw in ("best", "top", "leading", "#1", "certified", "guarantee"):
            if re.search(rf"\b{re.escape(kw)}\b", low):
                notes.append(f"Schema contains '{kw}'. Hidden/structured content is still a communication (7.1(a)).")
    return hits, notes


def iter_inputs(args: list[str]):
    for a in args:
        if a == "-":
            yield "stdin", None, sys.stdin.read()
            continue
        p = Path(a)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.suffix.lower() in (".txt", ".md", ".html", ".htm"):
                    yield str(f), f, None
        elif p.exists():
            yield str(p), p, None
        else:
            print(f"warning: {a} not found", file=sys.stderr)


SEV_ORDER = {"Block": 0, "Revise": 1, "Verify": 2, "Note": 3}


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    targets = [a for a in argv if a != "--json"]
    if not targets:
        print(__doc__)
        return 2
    report = []
    for label, path, raw in iter_inputs(targets):
        text, jsonld = load(path, raw)
        hits, notes = scan_text(label, text, jsonld)
        hits.sort(key=lambda h: (SEV_ORDER.get(h.severity, 9), h.line))
        report.append({"file": label, "hits": [asdict(h) for h in hits], "notes": notes})

    if as_json:
        print(json.dumps(report, indent=2))
        return 0

    for r in report:
        print(f"\n## {r['file']}")
        counts = {}
        for h in r["hits"]:
            counts[h["severity"]] = counts.get(h["severity"], 0) + 1
        print("First-pass hits: " + (", ".join(f"{k} {v}" for k, v in sorted(
            counts.items(), key=lambda kv: SEV_ORDER.get(kv[0], 9))) or "none"))
        if r["hits"]:
            print("\n| Line | Default severity | Category | Rule | Match | Context |")
            print("|---|---|---|---|---|---|")
            for h in r["hits"]:
                ctx = h["context"].replace("|", "\\|")
                print(f"| {h['line']} | {h['severity']} | {h['category']} | {h['rule']} | "
                      f"`{h['match']}` | {ctx} |")
        for n in r["notes"]:
            print(f"- NOTE: {n}")
    print("\nFirst pass only. Judge every hit in context; this scan cannot detect false facts, "
          "misleading omissions, confidentiality issues in context, or solicitation circumstances.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
