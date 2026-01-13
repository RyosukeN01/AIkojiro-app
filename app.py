import streamlit as st
import google.generativeai as genai
from PIL import Image
import yfinance as ticker_info

# 1. アプリ基本設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（事実重視・最終版）")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが未設定です。")
    st.stop()

# 【重要】エラー回避の核心：最も安定したREST通信を強制
genai.configure(api_key=api_key, transport='rest')

# 3. 資金管理設定
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

# 4. 入力フォーム
uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード", value="3315.T")
analyze_button = st.button("小次郎講師に【厳密な客観分析】を依頼する", type="primary")

# 5. 分析ロジック（ハルシネーション対策）
if analyze_button and uploaded_file:
    with st.spinner("画像から視覚的データを抽出しています..."):
        try:
            # 最新株価を事実として取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"

            # モデルの初期化（もっとも標準的な呼び出し）
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # ハルシネーションを極限まで抑える「事実限定」指示
            prompt = f"""
            あなたは小次郎講師です。以下の【ルール】を死守してチャートを分析してください。
            
            【ルール】
            1. ハルシネーション（推測、未来予測、嘘）を一切禁止します。
            2. 画像に見える「短期・中期・長期」の3本の移動平均線の並び順のみを報告してください。
            3. 並び順から第1〜第6ステージを機械的に判定してください。
            4. 銘柄:{symbol}、価格:{current_price}円、総資金:{total_capital}円、リスク:{risk_per_trade}% という数値事実のみでユニット計算してください。
            5. 画像に線が見えない場合は「判定不能」と正直に答えてください。
            """
            
            image = Image.open(uploaded_file)
            # 推論の自由度を0にし、嘘をつく余地を無くします
            response = model.generate_content(
                [prompt, image],
                generation_config={"temperature": 0.0}
            )
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error("AIとの通信に失敗しました。")
            st.info("右下の『Manage app』から『Reboot App』を実行してください。")
            st.code(str(e))
