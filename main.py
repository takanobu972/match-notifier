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
    
    print(f"アクセスするURL: {url}")
    
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        
        # ページ全体のテキストを取得
        page_text = soup.get_text()
        
        # 取得できたテキストの長さを確認
        print(f"取得したテキストの文字数: {len(page_text)}")
        
        # テキストの中に「11」や「1日」が含まれているか、あるいはどんな文字列があるか確認するため一部を表示
        # （見やすくするために改行を整理）
        lines = [line.strip() for line in page_text.splitlines() if line.strip()]
        
        print("--- ページ内のテキスト抜粋（最初の30行） ---")
        for line in lines[:30]:
            print(line)
        print("---------------------------------------------")
        
        # 今回はテストとして、必ずメールが飛ぶようにここで一旦 True（試合あり）を返すか、
        # あるいは「1日」などの文字が入っているかチェックします
        target_str = f"{tomorrow.day}日" # 例: "1日"
        if target_str in page_text:
            print(f"'{target_str}' がページ内に見つかりました！")
            return True
        else:
            print(f"'{target_str}' がページ内に見つかりませんでした。")
            
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
