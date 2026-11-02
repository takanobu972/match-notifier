import datetime
import os
import urllib.request
import json
from bs4 import BeautifulSoup
import re

def check_today_match():
    today = datetime.date.today()
    target_keywords = ["明治安田J1", "U-21 Jリーグ交流戦", "ルヴァンカップ", "天皇杯"]
    
    year_month_str = today.strftime("%Y%m")
    url = f"https://www.frontale.co.jp/schedule/monthly.php?m={year_month_str}"
    print(f"アクセスするURL: {url}")
    print(f"確認する今日の日付: {today.strftime('%Y年%m月%d日')}")
    
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        
        # 今日を示す文字列（例: "2日" や "2(" など）を定義
        target_day_str1 = f"{today.day}日"
        target_day_str2 = f"{today.day}("
        
        # ページ内の要素を走査して今日の試合を探す
        for el in soup.find_all(['div', 'td', 'li', 'section']):
            text = el.get_text()
            
            if "OFF" in text or "非公開" in text:
                continue
            # 時間（例: 14:00など）が含まれていないものはスキップ
            if not re.search(r'\d{1,2}:\d{2}', text):
                continue
            
            # 指定された4大大会のいずれかを含むかチェック
            if not any(kw in text for kw in target_keywords):
                continue
            
            # 【重要】その要素の中に「今日の日付」の文字列が確実に含まれているかチェック
            if target_day_str1 in text or target_day_str2 in text:
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                match_lines = [l for l in lines if not re.match(r'^\d+日?$', l) and l != "日"]
                match_details_text = "\n".join(match_lines)
                
                formatted_date = f"{today.month}月{today.day}日"
                match_info = f"【川崎フロンターレ 試合当日通知】\n\n【日付】\n{formatted_date}\n\n【試合詳細】\n{match_details_text}\n\n公式スケジュール:\n{url}"
                print(f"本日の試合が見つかりました: {formatted_date}")
                return match_info
                        
    except Exception as e:
        print(f"データ取得エラー: {e}")

    print("本日の対象試合はありません。")
    return None

def send_line(match_body):
    access_token = os.environ["LINE_ACCESS_TOKEN"]
    
    # 環境変数から複数人の user_id を取得し、カンマで分割してリスト化する
    user_ids_env = os.environ["LINE_USER_ID"]
    user_ids = [uid.strip() for uid in user_ids_env.split(",") if uid.strip()]
    
    line_url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # 登録されている全員に対してループでメッセージを送信
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
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as res:
                print(f"LINEに通知を送信しました（宛先: {user_id}）。")
        except Exception as e:
            print(f"LINE送信失敗（宛先: {user_id}）: {e}")

if __name__ == "__main__":
    print("本日の試合日程の確認を開始します...")
    match_details = check_today_match()
    if match_details:
        send_line(match_details)
    else:
        print("本日は通知対象の試合がないため、LINE送信はスキップします。")
