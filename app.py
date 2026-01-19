import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ページ設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

# --- API設定（404エラー対策） ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    # 【対策1】通信方式をRESTに固定して404を回避
    genai.configure(api_key=api_key, transport='rest')
else:
    st.error("Secretsに 'GEMINI_API_KEY' が設定されていません。")
    api_key = None

# --- UI ---
st.title("💎 ルパン三世のAI投資判断")

col1, col2, col3 = st.columns(3)
with col1: chart_file = st.file_uploader("📈 チャート（必須）", type=["png", "jpg", "jpeg"])
with col2: company_info_file = st.file_uploader("🏢 企業情報", type=["png", "jpg", "jpeg"])
with col3: finance_file = st.file_uploader("💰 財務", type=["png", "jpg", "jpeg"])

# --- ハルシネーション防止用プロンプト ---
system_instruction = """
あなたは「ルパン三世のAI投資判断」チームです。
【重要：ハルシネーション厳禁】
1. アップロードされた画像に写っていない情報を捏造しないでください。
2. 銘柄名や数値が読み取れない場合は「画像から判別不能」と正直に答えてください。
3. あなたの知識（過去のデータ）ではなく、目の前の画像（現在のデータ）のみを分析してください。

各キャラの役割：
・次元（チャート分析）：移動平均線や出来高の事実のみを語れ。
・五ェ門（財務分析）：損益計算書等の数値の推移のみを斬れ。
・ルパン（最終判断）：上記事実に基づき、盗む価値（投資価値）があるか判断しろ。
"""

if st.button("鑑定開始（潜入開始）"):
    if not api_key:
        st.error("鍵がねぇぞ。")
    elif not chart_file:
        st.error("チャート画像が必要だ。")
    else:
        try:
            # 【対策2】モデル名をフルパスで指定
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            # 画像リスト作成
            images = [Image.open(chart_file)]
            if company_info_file: images.append(Image.open(company_info_file))
            if finance_file: images.append(Image.open(finance_file))
            
            with st.spinner("次元、五ェ門、画像から真実を盗み出すぜ..."):
                response = model.generate_content([system_instruction] + images)
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"おっと、トラブルだ：{e}")
