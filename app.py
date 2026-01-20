import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ページ設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

st.title("💎 ルパン三世のAI投資判断")
st.markdown("> **「不二子、この金庫（API）は手強いぜ。だが、開かない金庫はねぇ。」**")

# --- サイドバー ---
with st.sidebar:
    st.header("🔑 API設定")
    api_key = st.text_input("Google API Keyを入力", type="password")
    st.info("※動かない場合は、最新のAPIキーか確認してくれ。")

# --- 画像アップロード ---
st.subheader("📸 鑑定用画像を3枚揃えな")
col1, col2, col3 = st.columns(3)
with col1:
    chart_img = st.file_uploader("📈 チャート", type=['png', 'jpg', 'jpeg'])
with col2:
    info_img = st.file_uploader("🏢 企業情報", type=['png', 'jpg', 'jpeg'])
with col3:
    financial_img = st.file_uploader("📄 財務状況", type=['png', 'jpg', 'jpeg'])

stock_name = st.text_input("🔢 銘柄名", placeholder="例：ルパン商事")

if st.button("💰 お宝鑑定スタート！"):
    if not api_key:
        st.error("APIキーを入力しな。話はそれからだ。")
    elif not (chart_img and info_img and financial_img):
        st.warning("画像が3枚揃ってねぇぜ。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # --- 診断機能：使えるモデルを探す ---
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 優先順位をつけてモデルを選択
            selected_model = None
            for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
                if target in available_models:
                    selected_model = target
                    break
            
            if not selected_model:
                st.error(f"使えるモデルが見つからねぇ！現在のお前の環境で使えるのはこれだ：{available_models}")
            else:
                st.info(f"使用モデル: {selected_model}")
                model = genai.GenerativeModel(selected_model)

                # 画像読み込み
                imgs = [Image.open(chart_img), Image.open(info_img), Image.open(financial_img)]

                prompt = f"""
あなたは世界最高の投資アナリストチームです。3枚の画像をスキャンし、ハルシネーション（嘘）を排して投資判断を行ってください。
銘柄名：{stock_name}

■アナリストA〜G（バリュー、心理、移動平均線、ローソク足、チャネル、MACD、だまし分析）
■アナリストH（悲観的リスクマネージャー）
■最終判断：ファンドマネージャーX（具体的数値で結論を出すこと）
"""
                with st.spinner("次元と五ェ門が解析中だ..."):
                    response = model.generate_content([prompt] + imgs)
                    st.markdown("---")
                    st.subheader("🕵️‍♂️ 鑑定結果")
                    st.write(response.text)

        except Exception as e:
            st.error(f"おいおい、またトラブルだ：{e}")
            st.info("解決策：ターミナルで 'pip install -U google-generativeai' を実行してライブラリを最新にしてみてくれ。")

st.markdown("---")
st.caption("© 2026 Lupin III AI Investment.")
