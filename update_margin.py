import json
import urllib.request
from bs4 import BeautifulSoup

# 監視したい銘柄のリスト（銘柄コードと名前）
TARGET_STOCKS = [
    {"code": "7203", "name": "トヨタ自動車"},
    {"code": "6758", "name": "ソニーグループ"},
    {"code": "9984", "name": "ソフトバンクグループ"},
]

def fetch_stock_data(code):
    """
    Yahoo!ファイナンス等から信用残高・信用倍率を取得するサンプル関数
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
            
            # サンプルとしてダミースコアを返す構造にしています
            return {
                "buyMargin": 1000000,
                "sellMargin": 500000,
                "marginRatio": 2.0
            }
    except Exception as e:
        print(f"Error fetching {code}: {e}")
        return None

def main():
    updated_data = []
    
    for stock in TARGET_STOCKS:
        data = fetch_stock_data(stock["code"])
        if data:
            item = {
                "code": stock["code"],
                "name": stock["name"],
                "buyMargin": data["buyMargin"],
                "sellMargin": data["sellMargin"],
                "marginRatio": data["marginRatio"],
                "score": 80 if data["marginRatio"] < 3.0 else 30,
                "signal": "ロング推奨" if data["marginRatio"] < 3.0 else "下落警戒"
            }
            updated_data.append(item)

    output_data = {
        "updatedAt": "2026-10-31",
        "stocks": updated_data
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("data.json has been successfully updated.")

if __name__ == "__main__":
    main()
