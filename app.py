import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pandas as pd
from PIL import Image

# --- 1. 基本設定とUI ---
st.set_page_config(page_title="AI小次郎講師・投資判断", layout="wide")
st.title("📈 AI小次郎講師の投資判断（完全版）")

# サイドバー設定
with st.sidebar:
    st.header("🔑 設定")
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000, step=100000)
    risk_percent = st.slider("1トレードの許容リスク (%)", 0.1, 2.0, 1.0)
    
    st.info("※APIキーは Google AI Studio で無料で取得できます。")

# --- 2. データ取得・計算ロジック ---
def get_stock_data(ticker):
    try:
        data = yf.download(ticker, period="3mo", interval="1d")
        if data.empty: return None
        
        # ATRの計算 (14日間)
        high_low = data['High'] - data['Low']
        high_close = (data['High'] - data['Close'].shift()).abs()
        low_close = (data['Low'] - data['Close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(14).mean().iloc[-1]
        
        current_price = data['Close'].iloc[-1]
        return {"price": current_price, "atr": atr, "data": data.tail(5)}
    except:
        return None

# --- 3. メイン画面 ---
col1, col2 = st.columns([1, 1])
with col1:
    uploaded_file = st.file_uploader("チャート画像をアップロード", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.image(Image.open(uploaded_file), caption='分析対象チャート', use_container_width=True)

with col2:
    ticker_input = st.text_input("銘柄コードを入力 (例: 7203.T)", placeholder="日本株は末尾に .T を付与")
    analyze_btn = st.button("小次郎講師チームに依頼する", type="primary")

if analyze_btn and uploaded_file and api_key and ticker_input:
    # リアルタイムデータの取得
    market_info = get_stock_data(ticker_input)
    
    if market_info:
        # ユニット計算
        risk_amount = total_capital * (risk_percent / 100)
        unit_size = int(risk_amount / (market_info['atr'] * 2))
        
        # AI分析（Gemini）
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        あなたは小次郎講師率いる投資エージェントチームです。銘柄 {ticker_input} を分析せよ。
        
        【外部提供データ】
        - 現在値: {market_info['price']:.1f}円
        - ATR(14): {market_info['atr']:.1f}
        - 1ユニットの推奨株数: {unit_size}株 (総資金{total_capital}円、リスク{risk_percent}%時)

        【分析指示】
        アナリストA〜Hはそれぞれの専門分野（バリュー、センチメント、大循環、酒田五法、チャネル、MACD/DMI、だまし判定、リスク管理）に基づき、添付画像と上記データを照合して、ハルシネーションを避けて論理的に分析してください。
        
        最後にファンドマネージャーXが、エントリー価格、ロスカット値(2ATR下)、デイトレ/スイングの利確目標を具体的に提示してください。
        """
        
        with st.spinner('8人のアナリストが徹底討議中...'):
            response = model.generate_content([prompt, Image.open(uploaded_file)])
            st.markdown("---")
            st.markdown(response.text)
    else:
        st.error("銘柄データの取得に失敗しました。コードが正しいか確認してください。")
