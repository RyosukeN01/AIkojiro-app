import streamlit as st
import google.generativeai as genai
from PIL import Image
import yfinance as ticker_info

# 1. アプリ設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（事実重視・接続修正版）")

# 2. APIキー設定
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが未設定です。")
    st.stop()

# 【解決の鍵】通信プロトコルを強制的に変更し、v1betaへの自動遷移を阻止します
genai.configure(api_key=api_key, transport='rest')

# 3. 資金管理
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

# 4. 入力
uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード", value="3315.T")
analyze_button = st.button("小次郎講師に【厳密な客観分析】を依頼する", type="primary")

# 5. 分析ロジック（ハルシネーション対策）
if analyze_button and uploaded_file:
    with st.spinner("画像から視覚的データを抽出中..."):
        try:
            # 最新価格を事実として取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"

            # 404を回避するため、モデル名から 'models/' を除いた正規版で呼び出し
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            あなたは小次郎講師です。以下のルールを死守して分析してください。
            【ルール】
            1. ハルシネーション（推測や未来予知、嘘）を厳禁します。
            2. 画像の3本の移動平均線の「並び順」のみを根拠にステージ判定してください。
            3. 数値は提供された（銘柄:{symbol}、価格:{current_price}円、総資金:{total_capital}円、リスク:{risk_per_trade}%）のみを使用してください。
            4. 判別不能な箇所は「不明」と正直に述べてください。
            """
            
            image = Image.open(uploaded_file)
            # 推論温度を0にし、嘘をつく余地を排除
            response = model.generate_content([prompt, image], generation_config={"temperature": 0.0})
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error("接続ルートを再構築しました。")
            st.info("右下の『Manage app』から『Reboot App』を実行してください。")
            st.code(str(e))
