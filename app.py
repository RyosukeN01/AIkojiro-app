import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions
from PIL import Image
import yfinance as ticker_info

# 1. アプリ設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（厳密分析・正常接続版）")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。")
    st.stop()

# 【404エラーを物理的に回避する設定】
# APIバージョンを 'v1' に強制固定し、自動的な v1beta への遷移を阻止します
genai.configure(api_key=api_key, transport='rest')
client_options = RequestOptions(api_version='v1')

# 3. 資金管理設定
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

# 4. 入力フォーム
uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード (例: 7203.T)", value="3315.T")
analyze_button = st.button("小次郎講師に【客観的分析】を依頼する", type="primary")

# 5. 分析ロジック（ハルシネーション対策）
if analyze_button and uploaded_file:
    with st.spinner("画像から視覚的データを抽出しています..."):
        try:
            # 最新株価を事実として取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得不可"

            # モデル起動（オプションでv1を強制）
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            あなたは小次郎講師です。提供されたチャート画像を「移動平均線大循環分析」に基づき、
            客観的な事実のみを述べてください。ハルシネーション（嘘や推測）は厳禁です。

            1. ステージ判定: 短期・中期・長期の移動平均線の並び順（上から順）を画像から読み取り、
               第1〜第6ステージのどれに該当するか事実のみを判定してください。
            2. 資金管理: 総資金 {total_capital}円、許容リスク {risk_per_trade}%、現在価格 {current_price}円
               という数値データのみを用いて、最大購入株数を計算してください。

            画像に移動平均線が見えない場合は、無理に予測せず「判別不可」と答えてください。
            """
            
            image = Image.open(uploaded_file)
            # 接続オプション(v1)を適用して実行
            response = model.generate_content(
                [prompt, image],
                generation_config={"temperature": 0.0},
                request_options=client_options
            )
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error("AIとの通信を最新版(v1)に固定しました。")
            st.info("一度ブラウザを更新して再度お試しください。")
            st.code(f"技術詳細: {str(e)}")
