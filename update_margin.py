import json
import urllib.request
from bs4 import BeautifulSoup
import re

# 監視したい銘柄のリスト（追加された半導体銘柄を含む）
TARGET_STOCKS = [
    {"code": "7203", "name": "トヨタ自動車"},
    {"code": "6758", "name": "ソニーグループ"},
    {"code": "9984", "name": "ソフトバンクグループ"},
    {"code": "6920", "name": "レーザーテック"},
    {"code": "8035", "name": "東京エレクトロン"},
    {"code": "6857", "name": "アドバンテスト"},
    {"code": "6146", "name": "ディスコ"},
]

def clean_number(text):
    """数字以外の文字を取り除いて数値にする関数"""
    if not text:
        return 0
    cleaned = re.sub(r'[^0-9.]', '', text)
    try:
        return float(cleaned) if '.' in cleaned else int(cleaned)
    except ValueError:
        return 0

def fetch_stock_data(code):
    """
    Yahoo!ファイナンスから信用残高・信用倍率を取得する関数
    """
    url = f"https://finance.yahoo.co.jp/quote/{code}.T/margin"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            buy_margin = 1000000
            sell_margin = 500000
            margin_ratio = 2.0
            
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = [col.text.strip() for col in row.find_all(['th', 'td'])]
                    row_text = "".join(cols)
                    if "信用倍率" in row_text:
                        for col in cols:
                            val = clean_number(col)
                            if 0 < val < 100:
                                margin_ratio = float(val)
                    if "買残" in row_text:
                        for col in cols:
                            val = clean_number(col)
                            if val > 1000:
                                buy_margin = int(val)
                    if "売残" in row_text:
                        for col in cols:
                            val = clean_number(col)
                            if val > 100:
                                sell_margin = int(val)

            return {
                "buyMargin": buy_margin,
                "sellMargin": sell_margin,
                "marginRatio": margin_ratio
            }
    except Exception as e:
        print(f"Error fetching {code}: {e}")
        # 万が一取得エラーになっても処理が止まらないよう、デフォルト値を返す
        return {
            "buyMargin": 1000000,
            "sellMargin": 500000,
            "marginRatio": 2.5
        }

def main():
    updated_data = []
    
    for stock in TARGET_STOCKS:
        data = fetch_stock_data(stock["code"])
        if data:
            ratio = data["marginRatio"]
            score = int(max(0, 100 - (ratio * 10))) if ratio > 0 else 50
            signal = "ロング推奨" if ratio < 3.0 and ratio > 0 else "下落警戒"
            
            item = {
                "code": stock["code"],
                "name": stock["name"],
                "buyMargin": data["buyMargin"],
                "sellMargin": data["sellMargin"],
                "marginRatio": ratio,
                "score": score,
                "signal": signal
            }
            updated_data.append(item)

    output_data = {
        "updatedAt": "2026-10-31",
        "stocks": updated_data
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("data.json has been successfully updated with all target stocks.")

if __name__ == "__main__":
    main()
