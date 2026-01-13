import streamlit as st
import google.generativeai as genai
from PIL import Image
import yfinance as ticker_info

# 1. アプリ基本設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（事実重視・厳密分析）")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。")
    st.stop()

# 【404エラー解消】接続ルートを正規版(v1)に強制し、モデル名を指定
genai.configure(api_key=api_key, transport='rest')
# ハルシネーション抑制のため、推論の自由度を最小（temperature=0）に設定
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={"temperature": 0.0}
)

# 3. 資金管理
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

# 4. 入力フォーム
uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード (例: 7203.T)", value="3315.T")
analyze_button = st.button("小次郎講師に【客観的分析】を依頼する", type="primary")

# 5. 分析ロジック
if analyze_button and uploaded_file:
    with st.spinner("画像から視覚的データを抽出しています..."):
        try:
            # 最新株価を事実として取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得不可"

            # ハルシネーションを極限まで排除する「厳密プロンプト」
            prompt = f"""
            あなたは小次郎講師です。提供されたチャート画像を「移動平均線大循環分析」に基づき、以下の手順で**事実のみ**を述べてください。推測や嘘（ハルシネーション）は一切禁止します。

            1. 画像確認: 画面内に3本の移動平均線（短期・中期・長期）が確認できるか明記してください。
            2. ステージ判定: 線の並び順（上からどの順か）を記述し、第1〜第6のどのステージに該当するか判定してください。
            3. 数値事実: 銘柄 {symbol}、取得された現在価格 {current_price}円 という事実のみを使用してください。
            4. 資金管理: 総資金 {total_capital}円、1トレードの許容リスク額 {total_capital * (risk_per_trade/100)}円に基づき、算数的に正しい最大株数を計算してください。

            画像から判別できない場合は、無理に答えず「画像からは判別不能」と正直に回答してください。
            """
            
            image = Image.open(uploaded_file)
            response = model.generate_content([prompt, image])
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error("分析中にエラーが発生しました。")
            st.code(str(e))
