import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import yfinance as ticker_info

# 1. アプリ設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（404エラー完全回避版）")

# 2. APIキー設定
api_key = st.secrets.get("GEMINI_API_KEY")

# 3. 資金管理
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

# 4. 入力
uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード", value="3315.T")
analyze_button = st.button("小次郎講師に【厳密な客観分析】を依頼する", type="primary")

# 5. 分析ロジック（直通ルート）
if analyze_button and uploaded_file and api_key:
    with st.spinner("画像から視覚的な事実を抽出中..."):
        try:
            # 最新株価取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"

            # 画像のエンコード
            img_byte_arr = io.BytesIO()
            Image.open(uploaded_file).save(img_byte_arr, format='JPEG')
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            # 【重要】ライブラリを介さず、正規版URL(v1)へ直接POST
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            prompt = f"あなたは小次郎講師です。提供されたチャート画像の移動平均線（短期・中期・長期）の並び順だけを見て、第1〜第6ステージのどれかを客観的に判定してください。ハルシネーション（嘘）は厳禁です。銘柄:{symbol}、価格:{current_price}円、総資金:{total_capital}円、リスク:{risk_per_trade}%として計算してください。"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                    ]
                }],
                "generationConfig": {"temperature": 0.0}
            }

            response = requests.post(url, json=payload)
            result = response.json()

            st.markdown("---")
            if "candidates" in result:
                st.markdown(result["candidates"][0]["content"]["parts"][0]["text"])
            else:
                st.error("分析に失敗しました。")
                st.json(result) # エラー詳細を表示
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
