import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- ページ設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

# --- 演出・タイトル ---
st.title("💎 ルパン三世のAI投資判断")
st.markdown("""
### 「なーに、お宝（銘柄）を盗むには、まずは下見が肝心ってことよ。」
チャート・企業情報・財務情報の3枚の画像から、俺の仲間たちがハルシネーション（嘘）なしで厳しく鑑定してやるぜ。
---
""")

# --- サイドバー：APIキー設定 ---
with st.sidebar:
    st.header("🔑 秘密の鍵（API設定）")
    api_key = st.text_input("Google API Keyを入力してくれ", type="password")
    st.info("※Google AI Studioで取得したAPIキーが必要だぜ。")
    st.markdown("---")
    st.caption("モデル: gemini-1.5-flash を使用中")

# --- メイン画面：画像アップロードエリア ---
st.subheader("📸 鑑定用画像を3枚揃えな（チャート・企業情報・財務）")
col1, col2, col3 = st.columns(3)

with col1:
    chart_img = st.file_uploader("1. 📈 銘柄チャート画像", type=['png', 'jpg', 'jpeg'])
    if chart_img:
        st.image(chart_img, caption="チャート", use_container_width=True)

with col2:
    info_img = st.file_uploader("2. 🏢 企業情報画像 (四季報・ニュース等)", type=['png', 'jpg', 'jpeg'])
    if info_img:
        st.image(info_img, caption="企業情報", use_container_width=True)

with col3:
    financial_img = st.file_uploader("3. 📄 財務画像 (B/S, C/F, 決算短信等)", type=['png', 'jpg', 'jpeg'])
    if financial_img:
        st.image(financial_img, caption="財務状況", use_container_width=True)

stock_name = st.text_input("🔢 分析する銘柄名（任意）", placeholder="例：ルパン商事")

# --- 分析実行セクション ---
if st.button("💰 お宝鑑定スタート！"):
    if not api_key:
        st.error("APIキーを入力しなきゃ、始まらねぇぜ。")
    elif not (chart_img and info_img and financial_img):
        st.warning("画像が足りねぇな。3枚揃えてから出直しな。")
    else:
        try:
            # API設定
            genai.configure(api_key=api_key)
            # Flashモデルを指定
            model = genai.GenerativeModel('gemini-1.5-flash')

            # 画像の読み込み
            img_list = [
                Image.open(chart_img),
                Image.open(info_img),
                Image.open(financial_img)
            ]

            # 専門家集団（プロンプト）の構築
            prompt = f"""
あなたは世界最高の投資アナリストチームです。提供された3枚の画像（チャート、企業情報、財務状況）をスキャンし、ハルシネーション（嘘）を排し、以下の銘柄の投資判断を行ってください。
銘柄名：{stock_name if stock_name else "画像から読み取った銘柄"}

【分析ルール】
各アナリストA〜Hが独自の視点で分析し、最後にマネージャーXが結論を出します。

■アナリストA（厳格なバリュー投資家）
小次郎講師流。定性的な夢物語は無視。財務画像から読み取れるキャッシュフローとバランスシートの数字のみを根拠に割安性を判断。

■アナリストB（市場心理トレーダー）
企業情報とチャートから、市場の過熱感や関心を分析。人気がなければ「価値なし」と断じる。

■アナリストC（移動平均線大循環分析）
チャートから移動平均線の並びと傾きを分析。現在のステージ、トレンド継続性、明日の利確売りの可能性を判断。

■アナリストD（ローソク足分析・酒田五法）
直近数本のローソク足から売り買いの優劣を分析。酒田五法に基づき今後のトレンドを予測。

■アナリストE（チャネル分析）
チャート上の支持線・抵抗線を結んだチャネルを分析し、株価が動く確率が高いレンジを特定。

■アナリストF（MACD・オシレーター）
MACD等の指標に基づき、勢いと過熱感を判断。明日の優勢度はどちらか。

■アナリストG（チャートパターン・だまし）
過去のブレイクアウトが「だまし」であった形跡があるか、現在の状況でだまされる確率は高いかを判断。

■アナリストH（悲観的リスクマネージャー）
他者の強気意見に対し、ブラックスワン（最悪のシナリオ）を突きつけ、論理的に反論せよ。

---
### 最終判断：ファンドマネージャーX
上記A〜Hを統合し、以下を具体的数値で出力：
1. 【最終判断】（買うべきか・見送るか、全力か打診か）
2. 【トレード戦略】（エントリー価格、ロスカット設定値、デイトレ目標値、スイング目標値）
3. 【テクニカル指標】（現在のATR、支持線、抵抗線）
"""

            with st.spinner("次元が狙撃準備中... 五ェ門が雑音を斬り捨て中..."):
                # 画像とプロンプトをまとめて送信
                response = model.generate_content([prompt] + img_list)
                
                # 結果表示
                st.markdown("---")
                st.subheader("🕵️‍♂️ 鑑定結果レポート")
                st.write(response.text)

        except Exception as e:
            st.error(f"おいおい、トラブルだぜ：{e}")

# --- フッター ---
st.markdown("---")
st.caption("© 2026 Lupin III AI Investment. ※投資は自己責任。捕まっても知らねえぜ。")
