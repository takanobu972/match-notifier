
import datetime
import os
import urllib.request
import urllib.error
import json
import re
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

JST = ZoneInfo("Asia/Tokyo")

# 試合として通知する大会名
TARGET_KEYWORDS = [
    "明治安田J1",
    "U-21 Jリーグ",
    "ルヴァンカップ",
    "天皇杯"
]


def check_today_match():

    # 日本時間で今日の日付を取得
    today = datetime.datetime.now(JST).date()

    year_month_str = today.strftime("%Y%m")
    url = f"https://www.frontale.co.jp/schedule/monthly.php?m={year_month_str}"

    print(f"アクセスするURL: {url}")
    print(f"確認する今日の日付: {today.strftime('%Y年%m月%d日')}")

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html"
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")

        soup = BeautifulSoup(html, "html.parser")

        # 公式サイトのスケジュール表を調べる
        rows = soup.find_all("tr")

        for row in rows:

            cells = row.find_all(["td", "th"], recursive=False)

            # 日付・曜日・予定の3列がない行はスキップ
            if len(cells) < 3:
                continue

            # 1列目から日付を取得
            day_text = cells[0].get_text(strip=True)

            # 日付が数字だけの行を対象にする
            if not re.fullmatch(r"\d{1,2}", day_text):
                continue

            if int(day_text) != today.day:
                continue

            # 3列目以降から予定を取得
            schedule_text = " ".join(
                cell.get_text(" ", strip=True)
                for cell in cells[2:]
            )

            schedule_text = " ".join(schedule_text.split())

            print(f"今日の予定を確認: {schedule_text}")

            # 大会名が含まれているか確認
            matched_keywords = [
                keyword for keyword in TARGET_KEYWORDS
                if keyword in schedule_text
            ]

            if not matched_keywords:
                continue

            formatted_date = f"{today.month}月{today.day}日"

            match_info = (
                "【川崎フロンターレ 試合当日通知】\n\n"
                f"【日付】\n{formatted_date}\n\n"
                f"【試合詳細】\n{schedule_text}\n\n"
                f"公式スケジュール:\n{url}"
            )

            print("本日の試合が見つかりました！")
            print(match_info)

            return match_info

        print("本日の対象試合はありません。")
        return None

    except Exception as e:
        print(f"スケジュール取得エラー: {type(e).__name__}: {e}")
        raise


def send_line(match_body):

    access_token = os.environ.get("LINE_ACCESS_TOKEN")
    user_ids_env = os.environ.get("LINE_USER_ID")

    if not access_token:
        raise ValueError("LINE_ACCESS_TOKEN が設定されていません")

    if not user_ids_env:
        raise ValueError("LINE_USER_ID が設定されていません")

    user_ids = [
        uid.strip()
        for uid in user_ids_env.split(",")
        if uid.strip()
    ]

    line_url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    for user_id in user_ids:

        data = {
            "to": user_id,
            "messages": [
                {
                    "type": "text",
                    "text": match_body
                }
            ]
        }

        req = urllib.request.Request(
            line_url,
            data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = response.read().decode("utf-8", errors="ignore")
                print(
                    f"LINE送信成功: 宛先={user_id}, "
                    f"HTTPステータス={response.status}"
                )
                print(f"LINE API応答: {result}")

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            print(f"LINE送信失敗: HTTP {e.code}")
            print(f"エラー詳細: {error_body}")
            raise

        except Exception as e:
            print(f"LINE送信エラー: {type(e).__name__}: {e}")
            raise


if __name__ == "__main__":

    print("================================")
    print("川崎フロンターレ試合日程チェック")
    print(f"実行日時（日本時間）: {datetime.datetime.now(JST)}")
    print("================================")

    match_details = check_today_match()

    if match_details:
        send_line(match_details)
    else:
        print("通知対象の試合がないためLINE送信をスキップします。")

    print("処理終了")
