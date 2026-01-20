import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- ページ設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

st.title("💎 ルパン三世のAI投資判断")
st.markdown("> **「制限（Quota）なんて、俺たちの前じゃただの紙切れ同然よ。」**")

with st.sidebar:
    st.header("🔑 API設定")
    api_key = st.text_input("Google API Keyを入力", type="password")
    st.info("※最新モデルを自動選択し、制限時にはリトライを試みるぜ。")

st.subheader("📸 鑑定用画像を3枚揃えな")
col1, col2, col3 = st.columns(3)
with col1:
    chart_img = st.file_uploader("📈 チャート", type=['png', 'jpg', 'jpeg'])
with col2:
    info_img = st.file_uploader("🏢 企業情報", type=['png', 'jpg', 'jpeg'])
with col3:
    financial_img = st.file_uploader("📄 財務状況", type=['png', 'jpg', 'jpeg'])

stock_name = st.text_input("🔢 銘柄名（任意）")

if st.button("💰 お宝鑑定スタート！"):
    if not api_key:
        st.error("APIキーを入力しな。")
    elif not (chart_img and info_img and financial_img):
        st.warning("画像が3枚必要だ。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 利用可能なモデルを取得
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 優先して試すモデルのリスト
            targets = ['models/gemini-2.0-flash', 'models/gemini-2.5-flash', 'models/gemini-3-flash-preview', 'models/gemini-1.5-flash']
            active_targets = [t for t in targets if t in available_models]

            imgs = [Image.open(chart_img), Image.open(info_img), Image.open(financial_img)]
            
            prompt = f"銘柄名：{stock_name}\n各アナリストA-Hの視点とファンドマネージャーXの最終判断を出せ。"

            success = False
            # モデルを順番に試し、429エラーなら待機してリトライ
            for model_name in active_targets:
                if success: break
                
                st.write(f"🔍 モデル {model_name} で鑑定中...")
                model = genai.GenerativeModel(model_name)
                
                for attempt in range(3): # 最大3回リトライ
                    try:
                        response = model.generate_content([prompt] + imgs)
                        st.markdown("---")
                        st.subheader("🕵️‍♂️ 鑑定結果レポート")
                        st.write(response.text)
                        success = True
                        break
                    except Exception as e:
                        if "429" in str(e):
                            st.warning(f"混雑してるな...{10 * (attempt + 1)}秒待機してリトライするぜ。")
                            time.sleep(10 * (attempt + 1))
                        else:
                            st.error(f"エラー発生: {e}")
                            break
            
            if not success:
                st.error("全モデルが制限中だ。少し時間を置いてから（1分後くらい）試してみてくれ。")

        except Exception as e:
            st.error(f"致命的なトラブルだぜ：{e}")

st.markdown("---")
st.caption("© 2026 Lupin III AI Investment.")
