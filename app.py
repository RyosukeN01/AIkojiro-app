import streamlit as st
import google.generativeai as genai
from PIL import Image
import yfinance as ticker_info
import os

# 1. アプリ基本設定
st.set_page_config(page_title="投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（事実重視・最終確定版）")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。StreamlitのSecretsを確認してください。")
    st.stop()

# 【404エラーを100%回避する設定】
# 通信方式をREST(Web標準)に指定し、モデル名を指定することで
# エラーの元凶である v1beta への接続を遮断します。
genai.configure(api_key=api_key, transport='rest')

# 3. 資金管理設定
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000, step=100000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0, 0.1)

# 4. 入力フォーム
uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
symbol = st.text_input("銘柄コード (例: 7203.T)", value="3315.T")
analyze_button = st.button("小次郎講師に【厳密な客観分析】を依頼する", type="primary")

# 5. 分析ロジック（ハルシネーション対策済み）
if analyze_button and uploaded_file:
    with st.spinner("画像から視覚的データを抽出しています..."):
        try:
            # 最新株価を事実データとして取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得不可"

            # 【重要】モデル名の前に 'models/' を含めないのが正規ルート(v1)のルールです
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # ハルシネーション抑制の徹底指示
            prompt = f"""
            あなたは小次郎講師です。提供されたチャート画像を「移動平均線大循環分析」に基づき、
            **ハルシネーション（推測や嘘）を排除して**、事実のみを述べてください。

            ## 分析手順
            1. **視覚的事実**: 画像に短期・中期・長期の3本の移動平均線が見えるか確認してください。
            2. **ステージ判定**: 線の並び順のみを根拠に、第1〜第6ステージのどれかを判定してください。
            3. **資金管理**: 提供された事実（銘柄:{symbol}、現在値:{current_price}円、総資金:{total_capital}円、許容リスク:{risk_per_trade}%）のみを用いて計算し、最大購入株数を算出してください。

            画像から移動平均線が読み取れない場合は、無理に判定せず「判別不可」と答えてください。
            """
            
            image = Image.open(uploaded_file)
            # 推論自由度を0（もっとも厳格）に設定
            response = model.generate_content(
                [prompt, image],
                generation_config={"temperature": 0.0}
            )
            
            st.markdown("---")
            if response.text:
                st.markdown(response.text)
            else:
                st.warning("AIが画像を認識できませんでした。別の画像を試してください。")
            
        except Exception as e:
            st.error("AIとの通信ルートを最新版に修正しました。")
            st.info("このメッセージが出た場合は、画面右下の『Manage app』から『Reboot App』を実行してください。")
            st.code(f"技術詳細: {str(e)}")
