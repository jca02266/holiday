#!/usr/bin/env python3
"""Google Calendar から日本の祝日を取得して calendar.csv を更新するスクリプト。

calendar.csv の最終日付より後のデータを Google Calendar から取得して追記する。
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

# Google Calendar には法定祝日以外の行事も含まれるため除外する
EXCLUDE_KEYWORDS = {
    "七夕", "雛祭り", "七五三", "節分", "クリスマス",
    "母の日", "父の日", "銀行休業日", "ハロウィン", "バレンタインデー",
}


def fetch_ics(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def parse_ics(ics_text: str) -> list[tuple[date, str]]:
    # RFC 5545 の行継続 (folding) を展開
    lines = []
    for line in ics_text.splitlines():
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)

    events = []
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
                events.append((dtstart, summary))
            in_event = False
        elif in_event:
            if line.startswith("DTSTART;VALUE=DATE:"):
                val = line.split(":", 1)[1].strip()
                dtstart = date(int(val[:4]), int(val[4:6]), int(val[6:8]))
            elif line.startswith("SUMMARY:"):
                # ICS のエスケープ (\, \n 等) を簡易展開
                summary = line[8:].strip().replace("\\,", ",").replace("\\n", " ")

    return sorted(events)


def load_csv(path: Path) -> list[tuple[date, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return [(date.fromisoformat(row["日付"]), row["祝日名"]) for row in csv.DictReader(f)]


def save_csv(path: Path, rows: list[tuple[date, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["日付", "祝日名"])
        for d, name in rows:
            writer.writerow([d.isoformat(), name])


def main() -> None:
    existing = load_csv(CSV_PATH)
    last_date = max(d for d, _ in existing)
    print(f"現在のデータ: {min(d for d, _ in existing)} 〜 {last_date}")

    print("Google Calendar から祝日を取得中...")
    holidays = parse_ics(fetch_ics(GOOGLE_CALENDAR_ICS))

    new_entries = [
        (d, name) for d, name in holidays
        if d > last_date and not any(kw in name for kw in EXCLUDE_KEYWORDS)
    ]

    if not new_entries:
        print("追加するデータはありません。")
        return

    print(f"\n追加候補: {len(new_entries)} 件")
    for d, name in new_entries:
        print(f"  {d}  {name}")

    save_csv(CSV_PATH, sorted(existing + new_entries))
    print(f"\ncalendar.csv を更新しました。")


if __name__ == "__main__":
    main()
