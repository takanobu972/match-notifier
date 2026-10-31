import datetime
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import urllib.request
from bs4 import BeautifulSoup

def check_kawasaki_match():
    # 明日の日付を取得
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    # 明日の「月」と「日」の表記パターン（例: "11月1日" と "11/1"）
    target_str1 = f"{tomorrow.month}月{tomorrow.day}日"
    target_str2 = f"{tomorrow.month}/{tomorrow.day}"
    
    print(f"確認対象の日付: {target_str1} または {target_str2}")

    # チェックするURLのリスト（翌月の個別ページ ＋ メインのスケジュールページ）
    year_month = tomorrow.strftime("%Y_%m")
    urls_to_check = [
        f"https://www.frontale.co.jp/schedule/{year_month}.html",
        "https://www.frontale.co.jp/schedule/"
    ]

    for url in urls_to_check:
        try:
            print(f"アクセス中: {url}")
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, "html.parser")
            
            page_text = soup.get_text()
            
            if target_str1 in page_text or target_str2 in page_text:
                print(f"明日の試合予定が見つかりました！（確認先: {url}）")
                return True
                
        except Exception as e:
            # ページが存在しない場合などのエラーは無視して次のURLへ
            print(f"スキップまたはアクセスエラー: {url} ({e})")

    print("明日の試合予定は見つかりませんでした。")
    return False

def send_email():
    sender = os.environ["MY_EMAIL"]
    password = os.environ["MAIL_PASSWORD"]
    receiver = os.environ["MY_EMAIL"]

    subject = "【お知らせ】明日は川崎フロンターレの試合日です！"
    body = "明日は川崎フロンターレの試合日です。スケジュールを確認してください。"

    msg = MIMEText(body, "plain", "utf-8")
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
    if check_kawasaki_match():
        send_email()
    else:
        print("明日の試合予定はありません。")
