import datetime
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import urllib.request
from bs4 import BeautifulSoup

def check_kawasaki_match():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    year_month_str = tomorrow.strftime("%Y%m")
    url = f"https://www.frontale.co.jp/schedule/monthly.php?m={year_month_str}"
    
    # 検索する日付のパーツ（例: 11月1日 なら "11月" と "1日" や "1" の組み合わせ）
    month_str = f"{tomorrow.month}月"
    day_str1 = f"{tomorrow.day}日"
    day_str2 = f"/{tomorrow.day}"
    day_str3 = f"{tomorrow.day}" # 単体の数字
    
    print(f"アクセスするURL: {url}")
    print(f"探しているパーツ: 月={month_str}, 日付={day_str1} または {day_str2}")
    
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        
        page_text = soup.get_text()
        
        # 「11月」が含まれていて、かつ「1日」または「1/1」またはカレンダーの「1日」のセル周辺にあるか判定
        if month_str in page_text and (day_str1 in page_text or day_str2 in page_text):
            print("明日の試合予定（日付の合致）が見つかりました！")
            return True
        else:
            print("明日の試合予定は見つかりませんでした。")
            
    except Exception as e:
        print(f"データ取得エラー: {e}")

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
