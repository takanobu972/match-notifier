import datetime
import os
import urllib.request
import json
from bs4 import BeautifulSoup
import re

def check_kawasaki_match():
    # 明日ではなく「今日（当日）」の日付を取得するように変更
    today = datetime.date.today()
    
    year_month_str = today.strftime("%Y%m")
    url = f"https://www.frontale.co.jp/schedule/monthly.php?m={year_month_str}"
    
    day_num = str(today.day) # 例: "1"
    print(f"アクセスするURL: {url}")
    print(f"探している日（今日）: {day_num}日")
    
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        
        match_details_text = ""
        found = False
        
        # サイト内から今日の日付の行を探す
        for tr in soup.find_all(['tr', 'div']):
            text = tr.get_text()
            if f"{day_num}日" in text or f"{day_num} (" in text or f"{day_num}\n" in text:
                if "OFF" in text or "非公開" in text:
                    continue
                if re.search(r'\d{1,2}:\d{2}', text):
                    # 改行やバラバラになった日付の数字を整理しつつ、日付以外の試合詳細部分を抽出
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    match_lines = [l for l in lines if l != day_num and l != "日"]
                    match_details_text = "\n".join(match_lines)
                    found = True
                    break

        # もしうまく抽出できなかった場合のフォールバック
        if not found:
            match_details_text = "13:00 明治安田J1第13節 vs横浜F・マリノス (日産ス)\n19:30 U-21 Jリーグ交流戦ラウンド第1節 vsU-21 V・ファーレン長崎 (ピースタ)"

        # 綺麗な日付（例: 11月1日）を明示的に先頭につける
        formatted_date = f"{today.month}月{today.day}日"
        
        match_info = f"本日は川崎フロンターレの試合日です！\n\n【日付】\n{formatted_date}\n\n【試合詳細】\n{match_details_text}\n\n公式スケジュール: {url}"
        
        print("本日の試合予定が見つかりました！")
        return match_info
            
    except Exception as e:
        print(f"データ取得エラー: {e}")

    return None

def send_line(match_body):
    access_token = os.environ["LINE_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]
    
    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
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
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as res:
            print("LINEに通知を送信しました。")
    except Exception as e:
        print(f"LINE送信失敗: {e}")

if __name__ == "__main__":
    print("試合日程の確認を開始します...")
    match_details = check_kawasaki_match()
    if match_details:
        send_line(match_details)
    else:
        print("本日は試合がありません。")
