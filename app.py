import streamlit as st
import google.generativeai as genai
from PIL import Image
import yfinance as ticker_info

# 1. アプリ基本設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（事実重視・接続修正版）")

# 2. APIキー設定
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが未設定です。StreamlitのSecretsを確認してください。")
    st.stop()

# 【重要】エラー解消の核心：REST通信を指定し、v1betaへの自動遷移を阻止
genai.configure(api_key=api_key, transport='rest')

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
    with st.spinner("画像から視覚的データを抽出中..."):
        try:
            # 最新株価を事実データとして取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"

            # 【重要】404回避のため、シンプルなモデル名で呼び出し
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            あなたは小次郎講師です。以下のルールを厳守してください。
            【分析ルール】
            1. ハルシネーション（推測、未来予知、嘘）を厳禁します。
            2. 画像に見える3本の移動平均線の「並び順」のみを事実として抽出してください。
            3. 並び順から第1〜第6ステージを判定し、現在のエッジを述べてください。
            4. 銘柄:{symbol}、価格:{current_price}円、総資金:{total_capital}円、リスク:{risk_per_trade}% という事実のみで計算してください。
            5. 判別不能な箇所は「不明」と回答してください。
            """
            
            image = Image.open(uploaded_file)
            # 温度0で嘘をつく余地を排除
            response = model.generate_content(
                [prompt, image], 
                generation_config={"temperature": 0.0}
            )
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error("分析プロセスでエラーが発生しました。")
            st.info("右下の『Manage app』から『Reboot App』を必ず実行してください。")
            st.code(str(e))
