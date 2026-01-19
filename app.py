import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

# SecretsからAPIキーを自動取得
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("StreamlitのSecretsに 'GEMINI_API_KEY' が設定されていません。")
    api_key = None

# --- アプリのUI ---
st.title("💎 ルパン三世のAI投資判断")
st.caption("チャート・企業情報・財務の3つの視点から、お宝銘柄を徹底的に鑑定します。")

col1, col2, col3 = st.columns(3)
with col1:
    chart_file = st.file_uploader("📈 チャート画像（必須）", type=["png", "jpg", "jpeg"])
with col2:
    company_info_file = st.file_uploader("🏢 企業情報画像（任意）", type=["png", "jpg", "jpeg"])
with col3:
    finance_file = st.file_uploader("💰 財務画像（任意）", type=["png", "jpg", "jpeg"])

# システムプロンプト（指示内容は以前と同じ）
system_instruction = """
あなたは「ルパン三世のAI投資判断」チームです。
アナリストA〜HとファンドマネージャーXの役割で、アップロードされた画像のみを根拠に分析してください。
（中略：以前の指示をここに含めています）
"""

if st.button("鑑定開始（潜入開始）"):
    if not api_key:
        st.error("鍵がねぇと潜入できねぇ。Secretsを設定してくれ。")
    elif not chart_file:
        st.error("チャート画像をアップロードしてくれ。")
    else:
        try:
            # 安定版のモデルを使用
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            images = [Image.open(chart_file)]
            if company_info_file: images.append(Image.open(company_info_file))
            if finance_file: images.append(Image.open(finance_file))
            
            with st.spinner("次元、五ェ門、準備はいいか？真実を盗み出すぜ..."):
                response = model.generate_content([system_instruction] + images)
                st.markdown("---")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"トラブルだ：{e}")
