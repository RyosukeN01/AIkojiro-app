import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ページ設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

st.title("💎 ルパン三世のAI投資判断")
st.markdown("""
> **「次元、五ェ門、用意はいいか。最新のAI技術で、お宝銘柄を根こそぎいただくぜ！」**
> 3枚の画像から、2026年最新のAIアナリスト軍団がハルシネーション（嘘）なしで鑑定するぜ。
---
""")

# --- サイドバー：API設定 ---
with st.sidebar:
    st.header("🔑 秘密の鍵（API設定）")
    api_key = st.text_input("Google API Keyを入力してくれ", type="password")
    st.info("※お前の環境で利用可能な最新モデル（Gemini 2.0/3.0系）を自動選択するぜ。")

# --- メイン画面：画像アップロードエリア ---
st.subheader("📸 鑑定用画像を3枚揃えな")
col1, col2, col3 = st.columns(3)

with col1:
    chart_img = st.file_uploader("1. 📈 銘柄チャート画像", type=['png', 'jpg', 'jpeg'])
    if chart_img: st.image(chart_img, caption="チャート", use_container_width=True)

with col2:
    info_img = st.file_uploader("2. 🏢 企業情報画像", type=['png', 'jpg', 'jpeg'])
    if info_img: st.image(info_img, caption="企業情報", use_container_width=True)

with col3:
    financial_img = st.file_uploader("3. 📄 財務画像", type=['png', 'jpg', 'jpeg'])
    if financial_img: st.image(financial_img, caption="財務状況", use_container_width=True)

stock_name = st.text_input("🔢 分析する銘柄名（任意）", placeholder="例：ルパン商事")

# --- 分析実行セクション ---
if st.button("💰 お宝鑑定スタート！"):
    if not api_key:
        st.error("APIキーを入力しなきゃ、始まらねぇぜ。")
    elif not (chart_img and info_img and financial_img):
        st.warning("画像が足りねぇな。3枚揃えてから出直しな。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # --- モデルの自動選択ロジック ---
            # リストにあった利用可能な最新モデルを優先的に探す
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 優先順位: 2.0 Flash (安定) > 3.0 Flash (最新) > その他
            if 'models/gemini-2.0-flash' in available_models:
                target_model = 'gemini-2.0-flash'
            elif 'models/gemini-3-flash-preview' in available_models:
                target_model = 'gemini-3-flash-preview'
            elif 'models/gemini-2.5-flash' in available_models:
                target_model = 'gemini-2.5-flash'
            else:
                # リストにある最初の生成可能モデルを拾う
                target_model = available_models[0].replace('models/', '')

            st.write(f"🔍 使用モデル: {target_model}")
            model = genai.GenerativeModel(target_model)

            # 画像の準備
            img_list = [Image.open(chart_img), Image.open(info_img), Image.open(financial_img)]

            # 専門家集団（プロンプト）
            prompt = f"""
あなたは世界最高の投資アナリストチームです。提供された3枚の画像を精密にスキャンし、ハルシネーションを排して以下の銘柄を分析してください。
銘柄名：{stock_name if stock_name else "画像から判断"}

【分析ルール】
■アナリストA（バリュー投資家）：財務画像からC/FとB/Sの数字のみで割安性を判断。
■アナリストB（市場心理）：市場の過熱感と関心を分析。
■アナリストC（移動平均線大循環分析）：チャートからステージ、トレンド、利確売りを判断。
■アナリストD（ローソク足・酒田五法）：数本の組み合わせと酒田五法で方向性を予測。
■アナリストE（チャネル分析）：支持・抵抗線からレンジを特定。
■アナリストF（MACD・オシレーター）：勢いと過熱感を判断。
■アナリストG（チャートパターン・だまし）：だましの確率を判断。
■アナリストH（悲観的リスクマネージャー）：ブラックスワンを突きつけ論理的に反論。

---
### 最終判断：ファンドマネージャーX
上記を統合し、以下を具体的数値で出力せよ：
1. 【最終判断】（買うべきか・見送るか、全力か打診か）
2. 【トレード戦略】（エントリー価格、ロスカット値、デイトレ目標値、スイング目標値）
3. 【テクニカル指標】（現在のATR、支持線、抵抗線）
"""

            with st.spinner("次元がスコープを調整中... 五ェ門がデータを斬り分け中..."):
                response = model.generate_content([prompt] + img_list)
                st.markdown("---")
                st.subheader("🕵️‍♂️ 鑑定結果レポート")
                st.write(response.text)

        except Exception as e:
            st.error(f"おいおい、トラブルだぜ：{e}")

# --- フッター ---
st.markdown("---")
st.caption("© 2026 Lupin III AI Investment. ※投資は自己責任。捕まっても知らねえぜ。")
