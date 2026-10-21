"""콘텐츠 작성 보조: 단계 생성, 교재 링크, 코드 블록 이스케이프."""
import html

SLUG = {0: "00-intro", 1: "01-factory-method", 2: "02-abstract-factory", 3: "03-builder", 4: "04-singleton",
        5: "05-adapter", 6: "06-decorator", 7: "07-composite", 8: "08-facade", 9: "09-proxy", 10: "10-strategy",
        11: "11-observer", 12: "12-command", 13: "13-state", 14: "14-template-method", 15: "15-iterator", 99: "99-summary"}

STAGES = {
    "engage": ("몰입", "Tuning in"), "find": ("조사", "Finding out"), "sort": ("조직", "Sorting out"),
    "general": ("일반화", "Making conclusions"), "transfer": ("전이", "Going further"), "reflect": ("성찰", "Reflecting"),
}


def P(ch, name, anchor=""):
    """교재 장 링크 (inquiry/ 와 textbook/ 은 형제 폴더)."""
    return {"ch": ch, "name": f"{ch}장 {name}" if ch not in (0, 99) else name,
            "href": f"../textbook/{SLUG[ch]}.html{anchor}"}


def code(s):
    return "<pre><code>" + html.escape(s.strip("\n")) + "</code></pre>"


def stage(key, minutes, intro, items, tnote=None):
    ko, en = STAGES[key]
    d = {"key": key, "title": ko, "en": en, "minutes": minutes, "intro": intro, "items": items}
    if tnote:
        d["tnote"] = tnote
    return d


def info(id_, body):
    return {"id": id_, "type": "info", "html": body}
