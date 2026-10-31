import datetime
import os
import urllib.request
import json
from bs4 import BeautifulSoup
import re

def get_nearest_match():
    today = datetime.date.today()
    target_keywords = ["明治安田J1", "U-21 Jリーグ交流戦", "ルヴァンカップ", "天皇杯"]
    
    # 今月と来月のデータを順に確認して、今日以降の最も近い試合を探す
    target_months = [
        (today.year, today.month),
        (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    ]
    
    for year, month in target_months:
        year_month_str = f"{year}{month:02d}"
        url = f"https://www.frontale.co.jp/schedule/monthly.php?m={year_month_str}"
        print(f"アクセスするURL: {url}")
        
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, "html.parser")
            
            # ページ内の要素を走査して今日以降の試合を探す
            for tr in soup.find_all(['tr', 'div']):
                text = tr.get_text()
                if "OFF" in text or "非公開" in text:
                    continue
                if re.search(r'\d{1,2}:\d{2}', text):
                    # 指定された4大大会のいずれかを含むかチェック
                    if not any(kw in text for kw in target_keywords):
                        continue
                    
                    # 日付の数字を抽出
                    day_match = re.search(r'(\d{1,2})\s*日', text)
                    if not day_match:
                        day_match = re.search(r'(\d{1,2})\s*\(', text)
                    
                    if day_match:
                        day_num = int(day_match.group(1))
                        try:
                            match_date = datetime.date(year, month, day_num)
                        except ValueError:
                            continue
                        
                        # 今日以降の試合であれば採用
                        if match_date >= today:
                            lines = [line.strip() for line in text.splitlines() if line.strip()]
                            match_lines = [l for l in lines if not re.match(r'^\d+日?$', l) and l != "日"]
                            match_details_text = "\n".join(match_lines)
                            
                            formatted_date = f"{month}月{day_num}日"
                            match_info = f"【テスト通知：直近の試合予定】\n\n【日付】\n{formatted_date}\n\n【試合詳細】\n{match_details_text}\n\n公式スケジュール:\n{url}"
                            print(f"直近の試合が見つかりました: {formatted_date}")
                            return match_info
                            
        except Exception as e:
            print(f"データ取得エラー ({year}年{month}月): {e}")

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
    print("直近の試合日程の確認を開始します...")
    match_details = get_nearest_match()
    if match_details:
        send_line(match_details)
    else:
        print("未来の対象試合が見つかりませんでした。")
