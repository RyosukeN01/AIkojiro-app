import streamlit as st
from google import genai
from PIL import Image
import yfinance as ticker_info

# 1. アプリ設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（正規ルート接続版）")

# 2. APIキー設定
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが未設定です。")
    st.stop()

# 【解決の鍵】最新のClient方式
client = genai.Client(api_key=api_key)

# 3. 資金管理
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

# 4. 入力
uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード", value="3315.T")
analyze_button = st.button("小次郎講師に【厳密な客観分析】を依頼する", type="primary")

# 5. 分析ロジック
if analyze_button and uploaded_file:
    with st.spinner("画像から視覚的な事実を抽出中..."):
        try:
            # 株価取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"

            # ハルシネーションを封じる「事実限定プロンプト」
            prompt = f"""
            あなたは小次郎講師です。提供されたチャート画像を「移動平均線大循環分析」に基づき、客観的な事実のみを述べてください。
            【ルール】
            1. 推測や将来予測（ハルシネーション）を一切禁じます。
            2. 画像に見える「短期・中期・長期」の3本の線の並び順のみを報告してください。
            3. 線の上下関係から第1〜第6ステージを機械的に判定してください。
            4. 銘柄:{symbol}、価格:{current_price}円、総資金:{total_capital}円、リスク:{risk_per_trade}% という数値事実のみでユニット計算してください。
            """
            
            image = Image.open(uploaded_file)
            
            # 【重要】モデル名に 'models/' を含めないことで、API v1 を強制使用させます
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt, image],
                config={
                    "temperature": 0.0,  # ハルシネーション抑制
                }
            )
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error("接続ルートの再構築が必要です。")
            st.info("右下の『Manage app』から『Reboot App』を実行してください。")
            st.code(str(e))
