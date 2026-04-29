#!/usr/bin/env python3
"""calendar.csv を calendar.ics に変換するスクリプト"""

import csv
import uuid
from datetime import date, timedelta
from pathlib import Path

PRODID = "-//jca02266//holiday//JA"
CALNAME = "祝日・休日"


def csv_to_ics(src: Path, dst: Path) -> None:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        f"X-WR-CALNAME:{CALNAME}",
        "X-WR-TIMEZONE:Asia/Tokyo",
    ]

    with src.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            d = date.fromisoformat(row["日付"])
            end = d + timedelta(days=1)
            lines += [
                "BEGIN:VEVENT",
                f"UID:{uuid.uuid4()}@holiday",
                f"DTSTART;VALUE=DATE:{d:%Y%m%d}",
                f"DTEND;VALUE=DATE:{end:%Y%m%d}",
                f"SUMMARY:{row['祝日名']}",
                "END:VEVENT",
            ]

    lines.append("END:VCALENDAR")
    dst.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    print(f"Generated: {dst} ({sum(1 for l in lines if l == 'BEGIN:VEVENT')} events)")


if __name__ == "__main__":
    csv_to_ics(Path("calendar.csv"), Path("calendar.ics"))
