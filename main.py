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
        
        elements = soup.find_all(['tr', 'li', 'div'])
        
        for el in elements:
            # 大きな親要素をスキップ
            if len(el.find_all(['tr', 'li'])) > 0:
                continue
                
            text = el.get_text(separator=" ", strip=True)
            
            if "OFF" in text or "非公開" in text:
                continue
                
            # 時間（16:00など）が含まれているか
            if not re.search(r'\d{1,2}:\d{2}', text):
                continue
                
            # 大会名キーワードが含まれているか
            if not any(kw in text for kw in target_keywords):
                continue
            
            # 【確定修正】今日の日付（例: "7日" または "7(" または "7 "）が含まれているか安全にチェック
            day_str1 = f"{today.day}日"
            day_str2 = f"{today.day}("
            day_str3 = f" {today.day} "
            
            if day_str1 in text or day_str2 in text or day_str3 in text:
                formatted_date = f"{today.month}月{today.day}日"
                clean_text = " ".join(text.split())
                
                match_info = (
                    f"【川崎フロンターレ 試合当日通知】\n\n"
                    f"【日付】\n{formatted_date}\n\n"
                    f"【試合詳細】\n{clean_text}\n\n"
                    f"公式スケジュール:\n{url}"
                )
                print(f"本日の試合が見つかりました: {formatted_date}")
                return match_info
                        
    except Exception as e:
        print(f"データ取得エラー: {e}")

    print("本日の対象試合はありません。")
    return None
