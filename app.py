import streamlit as st
import google.generativeai as genai
from PIL import Image
import yfinance as ticker_info
import os

# 1. アプリ基本設定
st.set_page_config(page_title="Ryosuke専用：投資アナリスト会議室", layout="wide")
st.title("📈 投資アナリスト会議室（ハルシネーション抑制版）")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("SecretsにAPIキーが設定されていません。")
    st.stop()

# 【重要】接続先を正規版(v1)に強制固定し、試験運用版(v1beta)を回避する
genai.configure(api_key=api_key, transport='rest')

# 3. サイドバー：資金管理
with st.sidebar:
    st.header("💰 資金管理設定")
    total_capital = st.number_input("投資総資金 (円)", value=1000000)
    risk_per_trade = st.slider("1トレードの許容リスク (%)", 0.1, 5.0, 1.0)

# 4. 入力フォーム
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("チャート画像をアップロード", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

with col2:
    symbol = st.text_input("銘柄コード (例: 7203.T)", value="7203.T")
    analyze_button = st.button("小次郎講師に厳密な分析を依頼する", type="primary")

# 5. 分析ロジック（ハルシネーション抑制）
if analyze_button and uploaded_file:
    with st.spinner("画像から客観的な事実を抽出中..."):
        try:
            # 最新株価取得
            stock = ticker_info.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else "取得失敗"

            # モデルの初期化（v1ルート用の標準指定）
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # ハルシネーションを徹底排除する指示
            prompt = f"""
            # 命令
            提供されたチャート画像を「移動平均線大循環分析」に基づき、客観的な事実のみを述べてください。
            
            # 厳守事項
            1. ハルシネーション（推測や嘘）を厳禁します。
            2. 画像に見えていないインジケーターや数値については「判別不能」と述べてください。
            3. 銘柄コード:{symbol}、現在値:{current_price}円という事実を前提にしてください。
            
            # 分析項目
            - 現在のステージ（短期・中期・長期の移動平均線の並び順から判定）
            - 買い、売り、休みのいずれのエッジ（優位性）が発生しているか
            - 資金管理: 総資金{total_capital}円、許容リスク{risk_per_trade}%に基づき、この現在値から何株までエントリー可能か（ユニット計算）
            
            # 出力
            小次郎講師の口調で、論理的かつ誠実に回答してください。
            """
            
            # 生成実行
            response = model.generate_content([prompt, image])
            
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"接続エラーが発生しました。")
            st.info("解決策: 一度ブラウザを更新し、Reboot Appを行ってください。")
            st.code(str(e))
