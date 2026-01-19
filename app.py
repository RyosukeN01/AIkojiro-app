import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

# 【修正ポイント】SecretsからAPIキーを自動取得
# Streamlit CloudのSettings > Secrets に "GEMINI_API_KEY" という名前で保存します
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("APIキーが設定されていません。StreamlitのSecretsを確認してくれ。")
    api_key = None

# --- アプリのUI ---
st.title("💎 ルパン三世のAI投資判断")
st.caption("チャート・企業情報・財務の3つの視点から、お宝銘柄を徹底的に鑑定します。")

# 3カラム構成
col1, col2, col3 = st.columns(3)
with col1:
    chart_file = st.file_uploader("📈 チャート画像をアップロード（必須）", type=["png", "jpg", "jpeg"])
with col2:
    company_info_file = st.file_uploader("🏢 企業情報画像をアップロード（任意）", type=["png", "jpg", "jpeg"])
with col3:
    finance_file = st.file_uploader("💰 財務画像をアップロード（任意）", type=["png", "jpg", "jpeg"])

# システムプロンプト（内容は以前と同じ）
system_instruction = """ (省略：前回と同じ長い指示) """

if st.button("鑑定開始（潜入開始）"):
    if not api_key:
        st.error("APIキーがねぇ。これじゃあ潜入できねぇぜ。")
    elif not chart_file:
        st.error("チャート画像をアップロードしてくれ。")
    else:
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            images = [Image.open(chart_file)]
            if company_info_file: images.append(Image.open(company_info_file))
            if finance_file: images.append(Image.open(finance_file))
            
            with st.spinner("次元、五ェ門、準備はいいか？真実を盗み出すぜ..."):
                response = model.generate_content([system_instruction] + images)
                st.markdown("---")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"おっと、トラブルだ：{e}")
