import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

# タイトル・演出
st.title("💎 ルパン三世のAI投資判断")
st.markdown("""
> **「なーに、お宝（銘柄）を盗むには、まずは下見が肝心ってことよ。」** > 銘柄チャート、企業情報、財務状況の画像をアップロードしな。俺の仲間（専門家集団）が徹底的に分析してやるぜ。
""")

# サイドバーでAPIキー入力
with st.sidebar:
    st.header("🔑 鍵（API設定）")
    api_key = st.text_input("Gemini API Keyを入力してくれ", type="password")
    st.info("※APIキーはGoogle AI Studioで無料で取得できるぜ。")

# --- 入力エリア ---
col1, col2 = st.columns(2)
with col1:
    chart_img = st.file_uploader("📈 銘柄チャート画像 (日足/週足)", type=['png', 'jpg', 'jpeg'])
    financial_img = st.file_uploader("📄 財務画像 (B/S, C/F等)", type=['png', 'jpg', 'jpeg'])

with col2:
    company_info = st.text_area("🏢 企業情報・最新ニュース (コピペでOKだ)", height=150)
    stock_code = st.text_input("🔢 銘柄名/コード", placeholder="例：7203 トヨタ自動車")

# --- 分析実行 ---
if st.button("お宝鑑定スタート！"):
    if not api_key:
        st.error("APIキーを入力しなきゃ、始まらねぇぜ。")
    elif not (chart_img and financial_img):
        st.warning("画像が足りねぇな。チャートと財務情報の両方が必要だ。")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash') # または gemini-1.5-pro

            # 画像の読み込み
            img1 = Image.open(chart_img)
            img2 = Image.open(financial_img)

            # プロンプト構築
            prompt = f"""
あなたは世界最高の投資チームです。以下の銘柄情報を多角的に分析し、ハルシネーション（嘘）を排し、事実に基づいた冷徹な判断を下してください。
銘柄：{stock_code}
企業情報：{company_info}

【手順】
1. アナリストA〜Hの順で各々の視点から分析を述べる。
2. 最後にファンドマネージャーXが最終判断を下す。

---
### カスタム指示（役割）

■アナリストA（厳格なバリュー投資家）
小次郎講師流。定性的な夢物語は無視。C/FとB/Sの数字のみを信じ、割安性を判断。

■アナリストB（市場心理トレーダー）
市場の過熱感と関心を分析。人気がなければ「価値なし」と断じる。

■アナリストC（移動平均線大循環分析）
トレンド分析。現在のステージ、明日以降の動向、利確売りの可能性を判断。

■アナリストD（ローソク足分析・酒田五法）
売り買いの優勢、数本の組み合わせによる方向性、酒田五法によるトレンド判断。

■アナリストE（チャネル分析）
株価の変動レンジと、今後の推移確率を判断。

■アナリストF（MACD・オシレーター）
過熱感、買い・売りの勢い、明日の優勢度を判断。

■アナリストG（チャートパターン・だまし）
過去の「だましのブレイクアウト」の有無と、現在の状況でのだまし確率を判断。

■アナリストH（悲観的リスクマネージャー）
他者の強気意見に対し、ブラックスワン（最悪のシナリオ）を突きつけ論理的に反論せよ。

---
### 最終判断：ファンドマネージャーX
上記A〜Hの分析を統合し、以下を出力せよ：
1. 【最終結論】（買うべきか・見送るか、全力か打診か）
2. 【トレード戦略】（エントリー価格、ロスカット値、デイトレ目標値、スイング目標値）
3. 【テクニカル指標】（現在のATR、支持線、抵抗線）
"""

            with st.spinner("次元と五ェ門が警備を確認中... 不二子が情報を収集中..."):
                response = model.generate_content([prompt, img1, img2])
                
                # 結果表示
                st.markdown("---")
                st.subheader("🕵️‍♂️ 鑑定結果レポート")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"おいおい、トラブルだぜ：{e}")

# --- フッター ---
st.markdown("---")
st.caption("© 2026 Lupin III AI Investment. ※投資は自己責任。捕まっても知らねえぜ。")
