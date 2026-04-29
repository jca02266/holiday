#!/usr/bin/env python3
"""Google Calendar と calendar.csv を同期するスクリプト。

- 祝日名が "休日" のエントリは個人の独自休日として同期対象外とする
- それ以外のエントリは Google Calendar の内容と同期する
- CSV の最小日付より前のデータは追加しない
"""

import csv
import urllib.request
from datetime import date
from pathlib import Path

GOOGLE_CALENDAR_ICS = (
    "https://calendar.google.com/calendar/ical/"
    "ja.japanese%23holiday%40group.v.calendar.google.com/public/basic.ics"
)
CSV_PATH = Path("calendar.csv")

PERSONAL_NAME = "休日"  # この名前のエントリは個人の独自休日として同期対象外

# Google Calendar には法定祝日以外の行事も含まれるため除外する
EXCLUDE_KEYWORDS = {
    "七夕", "雛祭り", "七五三", "節分", "クリスマス",
    "母の日", "父の日", "銀行休業日", "ハロウィン", "バレンタインデー",
}


def fetch_ics(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def parse_ics(ics_text: str) -> dict[date, str]:
    lines = []
    for line in ics_text.splitlines():
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)

    events: dict[date, str] = {}
    in_event = False
    dtstart = None
    summary = None

    for line in lines:
        if line == "BEGIN:VEVENT":
            in_event = True
            dtstart = None
            summary = None
        elif line == "END:VEVENT":
            if dtstart and summary:
                events[dtstart] = summary
            in_event = False
        elif in_event:
            if line.startswith("DTSTART;VALUE=DATE:"):
                val = line.split(":", 1)[1].strip()
                dtstart = date(int(val[:4]), int(val[4:6]), int(val[6:8]))
            elif line.startswith("SUMMARY:"):
                summary = line[8:].strip().replace("\\,", ",").replace("\\n", " ")

    return {d: name for d, name in events.items()
            if not any(kw in name for kw in EXCLUDE_KEYWORDS)}


def load_csv(path: Path) -> dict[date, str]:
    with path.open(encoding="utf-8", newline="") as f:
        return {date.fromisoformat(row["日付"]): row["祝日名"] for row in csv.DictReader(f)}


def save_csv(path: Path, data: dict[date, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["日付", "祝日名"])
        for d in sorted(data):
            writer.writerow([d.isoformat(), data[d]])


def main() -> None:
    existing = load_csv(CSV_PATH)
    personal = {d: name for d, name in existing.items() if name == PERSONAL_NAME}
    external = {d: name for d, name in existing.items() if name != PERSONAL_NAME}

    min_date = min(existing)
    print(f"現在のデータ: {min_date} 〜 {max(existing)}")
    print(f"個人休日エントリ: {len(personal)} 件（同期対象外）")

    print("\nGoogle Calendar から祝日を取得中...")
    gcal = {d: name for d, name in parse_ics(fetch_ics(GOOGLE_CALENDAR_ICS)).items()
            if d >= min_date}

    gcal_years = {d.year for d in gcal}

    added   = [(d, name) for d, name in sorted(gcal.items()) if d not in existing]
    updated = [(d, external[d], name) for d, name in sorted(gcal.items())
               if d in external and external[d] != name]
    missing = [(d, name) for d, name in sorted(external.items())
               if d.year in gcal_years and d not in gcal]

    if added:
        print(f"\n[追加] {len(added)} 件")
        for d, name in added:
            print(f"  + {d}  {name}")

    if updated:
        print(f"\n[名称更新] {len(updated)} 件")
        for d, old, new in updated:
            print(f"  ~ {d}  {old} → {new}")

    if missing:
        print(f"\n[Google Calendar に存在しない外部エントリ] {len(missing)} 件")
        for d, name in missing:
            print(f"  ? {d}  {name}")

    if not added and not updated and not missing:
        print("差分はありません。")
        return

    merged = dict(personal)
    merged.update(external)
    for d, name in added:
        merged[d] = name
    for d, _, new in updated:
        merged[d] = new

    save_csv(CSV_PATH, merged)
    print(f"\ncalendar.csv を更新しました。")


if __name__ == "__main__":
    main()
