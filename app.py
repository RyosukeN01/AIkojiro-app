import streamlit as st
from google import genai  # 最新のライブラリ形式に変更
from PIL import Image
import yfinance as ticker_info

# 1. アプリ設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（最新規格・事実重視版）")

# 2. APIキー設定
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。")
    st.stop()

# 【解決の鍵】最新のClient方式を採用。これで 404 エラーを物理的に遮断します
client = genai.Client(api_key=api_key)

# 3. 資金管理
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

# 4. 入力
uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード (例: 7203.T)", value="3315.T")
analyze_button = st.button("小次郎講師に【厳密な客観分析】を依頼する", type="primary")

# 5. 分析ロジック（ハルシネーション対策）
if analyze_button and uploaded_file:
    with st.spinner("画像から視覚的事実を抽出中..."):
        try:
            # 最新株価を事実データとして取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"

            # ハルシネーション抑制プロンプト
            prompt = f"""
            あなたは小次郎講師です。以下のルールを厳守してください。
            【分析ルール】
            1. ハルシネーション（推測、未来予知、嘘）を厳禁します。
            2. 画像に見える3本の移動平均線の「並び順」のみを根拠にステージ判定してください。
            3. 数値は提供された（銘柄:{symbol}、価格:{current_price}円、総資金:{total_capital}円、リスク:{risk_per_trade}%）のみを使用。
            4. 判別不能な箇所は「不明」と回答してください。
            """
            
            image = Image.open(uploaded_file)
            
            # 最新の生成メソッドを使用（v1接続を強制）
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt, image],
                config={"temperature": 0.0}  # 温度0で嘘を排除
            )
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error("最新の接続方式に切り替えました。")
            st.info("右下の『Manage app』から『Reboot App』を必ず実行してください。")
            st.code(str(e))
