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
    
    # 検索する日付（例: 明日が1日なら "1" や "1日"）
    day_num = str(tomorrow.day)
    
    print(f"アクセスするURL: {url}")
    print(f"探している日: {day_num}日 (またはカレンダーの日付)")
    
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        
        page_text = soup.get_text()
        
        # サイト内に対象の日付の数字が含まれているかチェック
        # さらに確実にテストできるよう、もし見つからない場合でも今日の段階でメールが飛ぶように強制確認することも可能です
        if f"{day_num}日" in page_text or f" {day_num} " in page_text or f"\n{day_num}\n" in page_text:
            print(f"明日の日付 ({day_num}日) のスケジュールが見つかりました！")
            return True
        else:
            print(f"'{day_num}日' の直接一致は見つかりませんでした。が、テスト用にメールを送信します！")
            # ※今回は確実にメールが届くかのテストを兼ねているため、ここで一旦 True を返してメール送信させます
            return True
            
    except Exception as e:
        print(f"データ取得エラー: {e}")
        # エラー時もテスト用に強制送信
        return True

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
