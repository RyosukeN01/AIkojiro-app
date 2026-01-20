import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

# タイトル・演出
st.title("💎 ルパン三世のAI投資判断")
st.markdown("""
> **「不二子、準備はいいか？ 3枚のお宝（画像）から真実を抜き出すぜ。」**
> チャート・企業情報・財務状況の画像をアップロードしな。偽物（ハルシネーション）は一切なしだ。
""")

# サイドバーでAPIキー入力
with st.sidebar:
    st.header("🔑 鍵（API設定）")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.info("Google AI Studioで取得したAPIキーを入力してくれ。")

# --- 画像アップロードエリア ---
st.subheader("📸 鑑定用画像を3枚用意しな")
col1, col2, col3 = st.columns(3)

with col1:
    chart_img = st.file_uploader("1. 📈 銘柄チャート画像", type=['png', 'jpg', 'jpeg'])
with col2:
    info_img = st.file_uploader("2. 🏢 企業情報画像 (四季報・ニュース等)", type=['png', 'jpg', 'jpeg'])
with col3:
    financial_img = st.file_uploader("3. 📄 財務画像 (B/S, C/F, 決算短信等)", type=['png', 'jpg', 'jpeg'])

stock_name = st.text_input("🔢 分析する銘柄名（任意）", placeholder="例：ルパン商事")

# --- 分析実行 ---
if st.button("お宝鑑定スタート！"):
    if not api_key:
        st.error("APIキーを入力しなきゃ、始まらねぇぜ。")
    elif not (chart_img and info_img and financial_img):
        st.warning("画像が足りねぇな。3枚揃えてから出直しな。")
    else:
        try:
            genai.configure(api_key=api_key)
            # 高性能なProモデルを推奨（画像を細かく分析するため）
            model = genai.GenerativeModel('gemini-1.5-flash')

            # 画像の読み込み
            img_chart = Image.open(chart_img)
            img_info = Image.open(info_img)
            img_financial = Image.open(financial_img)

            # プロンプト
            prompt = f"""
あなたは世界最高の投資アナリストチームです。提供された3枚の画像（チャート、企業情報、財務状況）を詳細にスキャンし、ハルシネーション（嘘）を徹底的に排除した上で、以下の銘柄の投資判断を行ってください。
銘柄名：{stock_name if stock_name else "画像から判断"}

【分析手順】
以下の各アナリスト(A〜H)の視点で分析を述べ、最後にファンドマネージャーXが最終結論を出してください。

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
MACD等の指標（画像から読み取れる場合）に基づき、勢いと過熱感を判断。明日の優勢度はどちらか。

■アナリストG（チャートパターン・だまし）
過去のブレイクアウトが「だまし」であった形跡があるか、現在の状況でだまされる確率は高いかを判断。

■アナリストH（悲観的リスクマネージャー）
他の強気な意見に対し、ブラックスワン（最悪のシナリオ）を突きつけ、論理的に反論せよ。

---
### 最終判断：ファンドマネージャーX
上記A〜Hを統合し、以下を出力：
1. 【最終判断】（買うべきか・見送るか、全力か打診か）
2. 【トレード戦略】（エントリー価格、ロスカット設定値、デイトレ目標値、スイング目標値）
3. 【テクニカル指標】（現在のATR、支持線、抵抗線）
"""

            with st.spinner("次元が狙撃準備中... 五ェ門が雑音を斬り捨て中..."):
                # 3枚の画像とプロンプトを送信
                response = model.generate_content([prompt, img_chart, img_info, img_financial])
                
                # 結果表示
                st.markdown("---")
                st.subheader("🕵️‍♂️ 鑑定結果レポート")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"おいおい、トラブルだぜ：{e}")

# --- フッター ---
st.markdown("---")
st.caption("© 2026 Lupin III AI Investment. ※投資は自己責任。捕まっても知らねえぜ。")
