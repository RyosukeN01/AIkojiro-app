import streamlit as st
import google.generativeai as genai
from PIL import Image
import yfinance as ticker_info

# 1. アプリ設定
st.set_page_config(page_title="Ryosuke専用：投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（厳密分析版）")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("SecretsにAPIキーが設定されていません。")
    st.stop()

# 【解決の鍵】接続ルートを強制的に「正規版(v1)」へ。これで404エラーを回避します。
genai.configure(api_key=api_key, transport='rest')

# 3. 入力フォーム
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード (例: 7203.T)", value="7203.T")
analyze_button = st.button("小次郎講師に【客観的分析】を依頼する", type="primary")

# 4. ハルシネーション抑制ロジック
if analyze_button and uploaded_file:
    with st.spinner("画像から視覚的な事実を抽出しています..."):
        try:
            # 株価取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"

            # モデル起動（正規版ルート）
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # ハルシネーションを極限まで減らすための「思考プロセス」を指示
            prompt = f"""
            あなたは小次郎講師です。以下の手順で厳密に分析し、推測や嘘（ハルシネーション）を徹底的に排除してください。

            1. 画像の確認: 3本の移動平均線（短期・中期・長期）が見えるか確認してください。
            2. ステージ判定: 線の並び順のみから、第1〜第6のどのステージか判定してください。
            3. 事実確認: 銘柄 {symbol}、現在価格 {current_price}円 という事実に基づき記述してください。
            4. 資金管理: 総資金 {total_capital}円 に対し、1回のトレードで失っていい金額（リスク額）を算出し、現在価格から逆算した最大購入株数を計算してください。

            画像に移動平均線が見えない場合は、無理に判定せず「判別不可」と答えてください。
            """
            
            image = Image.open(uploaded_file)
            response = model.generate_content([prompt, image])
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error("接続ルートの再構築が必要です。画面右上の『⋮』から Reboot App を押してください。")
            st.code(str(e))
