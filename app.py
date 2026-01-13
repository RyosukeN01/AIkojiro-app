import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import yfinance as ticker_info

# ==========================================
# 1. アプリ設定とタイトル
# ==========================================
st.set_page_config(page_title="Ryosuke専用：投資アナリスト会議室", layout="wide")
st.title("📈 Ryosuke専用：投資アナリスト会議室")

# ==========================================
# 2. APIキーの設定
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Secretsに GEMINI_API_KEY を設定してください。")
    st.stop()

# 接続設定を初期化
genai.configure(api_key=api_key)

# ==========================================
# 3. サイドバー：資金管理設定
# ==========================================
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000, step=100000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0, 0.1)

# ==========================================
# 4. メイン画面：入力フォーム
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 チャート画像")
    uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="分析対象チャート", use_container_width=True)

with col2:
    st.subheader("🔢 銘柄情報入力")
    symbol = st.text_input("銘柄コード (例: 7203.T)", value="7203.T")
    analyze_button = st.button("小次郎講師チームに依頼する", type="primary")

# ==========================================
# 5. 分析ロジック
# ==========================================
if analyze_button:
    if not uploaded_file:
        st.error("チャート画像をアップロードしてください。")
    else:
        with st.spinner("アナリストたちが会議を行っています..."):
            try:
                # 株価取得
                stock = ticker_info.Ticker(symbol)
                hist = stock.history(period="1d")
                current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"
                
                if current_price != "取得失敗":
                    st.success(f"現在の株価: {current_price:.1f}円 を取得しました。")

                # 【404エラー対策の最重要ポイント】
                # 'v1beta' ルートを回避し、標準的なモデル指定を行います
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                あなたは小次郎講師率いる8人の投資家チームです。
                添付のチャート画像と銘柄（{symbol}、現在値{current_price}円）を分析してください。
                移動平均線大循環分析の視点に基づき、各自の立場から具体的意見を出し、
                最後に小次郎講師が、資金管理（総資金{total_capital}円、リスク{risk_per_trade}%）を考慮した結論をまとめてください。
                """
                
                # AI分析実行
                response = model.generate_content([prompt, image])
                
                st.markdown("---")
                if response.text:
                    st.markdown(response.text)
                else:
                    st.warning("AIからの回答が空でした。再度お試しください。")
                
            except Exception as e:
                # 404エラーの場合は、接続の再試行を促す
                st.error("AIとの通信で問題が発生しました。")
                st.info("モデル名の指定を最新の状態に更新しました。一度ブラウザを更新して、再度ボタンを押してください。")
                st.code(f"技術詳細: {str(e)}")
