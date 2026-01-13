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
# Secretsに保存されている場合は自動取得、なければサイドバーに入力欄を表示
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("APIキーを入力、またはStreamlitのSecretsに設定してください。")
    st.stop()

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
    symbol = st.text_input("銘柄コード (例: 7203.T)", placeholder="日本株は末尾に .T を付与")
    analyze_button = st.button("Team ルパン に依頼する", type="primary")

# ==========================================
# 5. 分析ロジック（エラー回避処理付き）
# ==========================================
if analyze_button:
    if not uploaded_file or not symbol:
        st.error("画像と銘柄コードの両方を入力してください。")
    else:
        with st.spinner("アナリストたちが会議を行っています..."):
            try:
                # 株価取得の試行
                stock = ticker_info.Ticker(symbol)
                hist = stock.history(period="1d")
                
                # データが取得できた場合
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    st.success(f"現在の株価: {current_price:.1f}円 を取得しました。")
                # データが空だった場合（エラーにせず警告を出す）
                else:
                    st.warning(f"銘柄コード '{symbol}' の株価データが見つかりませんでした。分析のみ続行します。")
                    current_price = "不明（チャートから判断）"

                # AI（Gemini）へのプロンプト作成
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                あなたはルパン率いる8人の投資家チーム（門下生たち）です。
                添付のチャート画像と銘柄情報（銘柄コード: {symbol}、現在値: {current_price}）を元に分析してください。
                
                1. 移動平均線大循環分析の視点（第1ステージ〜第6ステージのどこか）
                2. 各アナリスト（短期・中期・長期・ファンダなど）からの個別意見
                3. 最後にルパンが、資金管理（総資金{total_capital}円、許容リスク{risk_per_trade}%）を考慮した具体的な結論をまとめてください。
                """
                
                # 分析実行
                response = model.generate_content([prompt, image])
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                # 想定外のエラーが発生した場合の表示
                st.error("分析中に技術的なエラーが発生しました。時間をおいて再度お試しください。")
                st.info(f"詳細エラー: {e}")
