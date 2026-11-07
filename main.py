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
        
        # 今日を示すパターン（例: 先頭や行頭の「7日」や「7(」など）
        # テーブルの行(tr) または リスト項目/ブロックごとに探索
        elements = soup.find_all(['tr', 'li', 'div'])
        
        for el in elements:
            # 直下の小要素を含みすぎない末端に近いブロックを対象にするため、子要素が多すぎる親タグはスキップ
            if len(el.find_all(['tr', 'li'])) > 0:
                continue
                
            text = el.get_text(separator=" ", strip=True)
            
            if "OFF" in text or "非公開" in text:
                continue
                
            # 時間（16:00など）が含まれるか
            if not re.search(r'\d{1,2}:\d{2}', text):
                continue
                
            # 対象大会キーワードが含まれるか
            if not any(kw in text for kw in target_keywords):
                continue
            
            # 日付判定: 「7日」「7(」「 7 」などの単語境界または表記を正確にチェック
            # 行の先頭付近に今日の日付数字があるかを判定
            day_pattern = rf'(?:^|\s|>{today.day}(?:日|\(|\s|$)'
            if re.search(day_pattern, text) or f"{today.day}日" in text or f"{today.day}(" in text:
                formatted_date = f"{today.month}月{today.day}日"
                
                # 不要な改行・空白を整えて綺麗なメッセージを作成
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
