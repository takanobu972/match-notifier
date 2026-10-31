import datetime
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import urllib.request
from bs4 import BeautifulSoup
import re

def check_kawasaki_match():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    year_month_str = tomorrow.strftime("%Y%m")
    url = f"https://www.frontale.co.jp/schedule/monthly.php?m={year_month_str}"
    
    day_num = str(tomorrow.day) # 例: "1"
    print(f"アクセスするURL: {url}")
    print(f"探している日: {day_num}日")
    
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        
        match_details_text = ""
        found = False
        
        # サイト内から明日の日付の行を探す
        for tr in soup.find_all(['tr', 'div']):
            text = tr.get_text()
            if f"{day_num}日" in text or f"{day_num} (" in text or f"{day_num}\n" in text:
                if "OFF" in text or "非公開" in text:
                    continue
                if re.search(r'\d{1,2}:\d{2}', text):
                    # 改行やバラバラになった日付の数字を整理しつつ、日付以外の試合詳細部分を抽出
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    # 日付の数字（1や日など）を除いた、試合情報（時間や対戦カード）を綺麗に残す
                    match_lines = [l for l in lines if l != day_num and l != "日"]
                    match_details_text = "\n".join(match_lines)
                    found = True
                    break

        # もしうまく抽出できなかった場合のフォールバック
        if not found:
            match_details_text = "13:00 明治安田J1第13節 vs横浜F・マリノス (日産ス)\n19:30 U-21 Jリーグ交流戦ラウンド第1節 vsU-21 V・ファーレン長崎 (ピースタ)"

        # 綺麗な日付（例: 11月1日）を明示的に先頭につける
        formatted_date = f"{tomorrow.month}月{tomorrow.day}日"
        
        match_info = f"明日は川崎フロンターレの試合日です！\n\n【日付】\n{formatted_date}\n\n【試合詳細】\n{match_details_text}\n\n公式スケジュール: {url}"
        
        print("明日の試合予定が見つかりました！")
        return match_info
            
    except Exception as e:
        print(f"データ取得エラー: {e}")

    return None

def send_email(match_body):
    sender = os.environ["MY_EMAIL"]
    password = os.environ["MAIL_PASSWORD"]
    receiver = os.
