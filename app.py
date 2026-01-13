import streamlit as st
import requests
import base64
from PIL import Image
import io
import yfinance as ticker_info

# 1. アプリ設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（404エラー最終解決版）")

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
analyze_button = st.button("小次郎講師に【客観的分析】を依頼する", type="primary")

# 5. 分析ロジック（URL修正版）
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

            # 【解決の核心】URLを v1 にし、モデル名から "models/" を除去
            # これで Google サーバーの拒絶反応を回避します
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            prompt = f"""
            あなたは小次郎講師です。チャート画像から「短期・中期・長期」の3本の移動平均線の位置関係を読み取ってください。
            【事実重視ルール】
            1. ハルシネーション（推測や嘘）を禁止します。画像に見える事実のみ述べてください。
            2. 線の並び順（上から順に何があるか）を記述し、第1〜第6ステージを判定してください。
            3. 数値計算は以下の事実のみを使用：価格 {current_price}円、総資金 {total_capital}円、リスク {risk_per_trade}%。
            """
            
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
                st.error("分析に失敗しました。接続設定を再確認します。")
                st.json(result) # エラーの正体を特定するために表示
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
