# holiday

祝日・休日データを GitHub で管理し、Excel の Power Query 等から自動取り込みすることで、各種ツール間の祝日設定を同期するためのリポジトリです。

## ファイル構成

| ファイル | 内容 |
|---|---|
| `calendar.csv` | メインファイル。Power Query 等の取り込み先はこのファイルを参照する |
| `calendar.ics` | Google Calendar 購読用（`csv2ics.py` で生成） |
| `csv2ics.py` | `calendar.csv` → `calendar.ics` 変換スクリプト |
| `2025.csv` | 移行用。現在は `calendar.csv` と同一内容 |

> **Note**: `2025.csv` は当初、年度ごとにファイルを切り替える運用を想定して作成しましたが、その場合 Power Query のソース URL を毎年変更する必要が生じるためこの方式はやめました。以降は `calendar.csv` を正とし、過去年度分は年度ファイル（例: `2025.csv`）へ切り出して保管することを想定しています。

### CSV フォーマット

```
日付,祝日名
2025-01-01,元日
2025-01-13,成人の日
...
```

| 列 | 形式 | 説明 |
|---|---|---|
| 日付 | YYYY-MM-DD | 休日の日付 |
| 祝日名 | 文字列 | 祝日・休日の名称（日本語） |

#### 祝日名の種別

- 祝日名（例: 元日、成人の日）— 法定祝日
- `振替休日` — 祝日が日曜日に重なった場合の振替
- `休日` — 祝日に挟まれた国民の休日や年末年始等
- `大晦日` — 12月31日

## Power Query での取り込み方法

Excel の Power Query で以下の URL を指定することで、CSV を直接インポートできます。

```
https://raw.githubusercontent.com/jca02266/holiday/main/calendar.csv
```

## Google Calendar への取り込み方法

`calendar.ics` を Google Calendar に URL 購読させることで、常に最新の祝日データを参照できます。

### 1. ICS ファイルの生成とプッシュ

標準ライブラリのみで動作するため、追加のインストールは不要です。

```bash
python3 csv2ics.py
git add calendar.ics
git commit -m "Update calendar.ics"
git push
```

### 2. Google Calendar に登録

1. Google Calendar を開き、左側の「他のカレンダー」の `+` をクリック
2. 「URL で追加」を選択
3. 以下の URL を入力して「カレンダーを追加」

```
https://raw.githubusercontent.com/jca02266/holiday/main/calendar.ics
```

> **Note**: Google Calendar の購読カレンダーは自動更新されますが、反映まで最大 24 時間かかる場合があります。

## 更新方針

年次で手動更新します。**`calendar.csv` のみを更新**し、その後 `csv2ics.py` を実行して `calendar.ics` を再生成してからコミット・プッシュしてください。

過去年度のデータを整理する場合は、該当年度分を `calendar.csv` から切り出して年度ファイル（例: `2025.csv`）へ移動します。
