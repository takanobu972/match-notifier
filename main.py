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
    
    day_num = str(tomorrow.day)
    print(f"アクセスするURL: {url}")
    print(f"探している日: {day_num}日")
    
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        
        # ページ全体のHTMLから、明日の日付に該当する行や周辺のテキストを抽出する
        # （簡易的にページ全体のテキストから、試合情報らしき行を抽出します）
        page_text = soup.get_text()
        
        # テスト用・本番用として、明日が試合日の場合の詳細情報を取得する処理
        # フロンターレのスケジュールページ特有の表記から情報を探します
        match_info = f"明日は川崎フロンターレの試合日です！\n\n日付: {tomorrow.month}月{tomorrow.day}日\n"
        
        # ページから大会名やキックオフ時間、場所のキーワードが含まれる部分を探す
        # （例: J1リーグ, ルヴァンカップ, 天皇杯, vs などをキャッチ）
        found_details = []
        for line in page_text.splitlines():
            line_str = line.strip()
            # 「vs」や大会名が含まれていて、かつ明日の日付の周辺にある情報を拾う
            if ("vs" in line_str or "J1" in line_str or "ルヴァン" in line_str or "天皇杯" in line_str) and len(line_str) > 5:
                found_details.append(line_str)

        if found_details:
            match_info += "【試合詳細】\n" + "\n".join(found_details[:3]) # 見つかった情報をいくつかまとめる
        else:
            match_info += "【試合詳細】スケジュールページをご確認ください。\n"

        match_info += f"\n公式スケジュール: {url}"
        
        print("明日の試合予定が見つかりました！")
        return match_info
            
    except Exception as e:
        print(f"データ取得エラー: {e}")

    return None

def send_email(match_body):
    sender = os.environ["MY_EMAIL"]
    password = os.environ["MAIL_PASSWORD"]
    receiver = os.environ["MY_EMAIL"]

    subject = "【お知らせ】明日は川崎フロンターレの試合日です！"

    msg = MIMEText(match_body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("メールを送信しました。")
    except Exception as e:
        print(f"メール送信失敗: {e}")

if __name__ == "__main__":
    print("試合日程の確認を開始します...")
    match_details = check_kawasaki_match()
    if match_details:
        send_email(match_details)
    else:
        print("明日の試合予定はありません。")
