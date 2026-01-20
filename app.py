import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- ページ設定 ---
st.set_page_config(page_title="AI小次郎講師の投資判断", layout="wide")

st.title("📊 AI小次郎講師の投資判断")
st.markdown("""
銘柄チャート・企業情報・財務状況の3枚の画像から、8人の専門家エージェントがハルシネーション（嘘）を排して徹底分析します。
""")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("🔑 API設定")
    api_key = st.text_input("Google API Keyを入力してください", type="password")
    st.info("※Google AI Studioで取得したAPIキーを使用します。")
    st.markdown("---")
    st.caption("2026 Stable Edition")

# --- 画像アップロード ---
st.subheader("📸 分析用画像をアップロード（3枚必須）")
col1, col2, col3 = st.columns(3)

with col1:
    chart_img = st.file_uploader("📈 1. 銘柄チャート画像", type=['png', 'jpg', 'jpeg'])
with col2:
    info_img = st.file_uploader("🏢 2. 企業情報画像 (四季報・ニュース等)", type=['png', 'jpg', 'jpeg'])
with col3:
    financial_img = st.file_uploader("📄 3. 財務画像 (B/S, C/F等)", type=['png', 'jpg', 'jpeg'])

stock_name = st.text_input("🔢 分析する銘柄名/コード", placeholder="例：7203 トヨタ")

# --- 分析実行 ---
if st.button("🚀 投資判断を開始する"):
    if not api_key:
        st.error("APIキーを入力してください。")
    elif not (chart_img and info_img and financial_img):
        st.warning("画像が3枚揃っていません。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 利用可能なモデルをリストアップ
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 2026年の優先モデル順位
            priority_targets = [
                'models/gemini-2.0-flash', 
                'models/gemini-2.5-flash', 
                'models/gemini-3-flash-preview', 
                'models/gemini-1.5-flash'
            ]
            
            target_model = next((t for t in priority_targets if t in available_models), available_models[0])
            st.write(f"🔍 使用モデル: {target_model}")
            
            model = genai.GenerativeModel(target_model)

            # 画像の準備
            images = [Image.open(chart_img), Image.open(info_img), Image.open(financial_img)]

            # プロンプト（指示書）
            prompt = f"""
あなたは小次郎講師の理論を極めた投資アナリストチームです。提供された3枚の画像から事実のみを抽出し、ハルシネーションを排して投資判断を行ってください。
銘柄：{stock_name}

以下の手順で分析してください。

■アナリストA（厳格なバリュー投資家）：財務画像からC/FとB/Sの数字のみを信じて割安性を判断せよ。
■アナリストB（市場心理トレーダー）：市場の過熱感と関心を分析。人気がなければ価値なしとせよ。
■アナリストC（移動平均線大循環分析）：チャートからステージ、トレンド、明日の利確売りの可能性を判断せよ。
■アナリストD（ローソク足・酒田五法）：売り買いの優勢、酒田五法によるトレンド方向性を教えよ。
■アナリストE（チャネル分析）：支持・抵抗線から今後の推移確率が高いレンジを特定せよ。
■アナリストF（MACD・オシレーター）：勢いと過熱感、明日の優勢度を判断せよ。
■アナリストG（チャートパターン・だまし）：過去のだましの有無と、現在のブレイクアウト成功率を判断せよ。
■アナリストH（悲観的リスクマネージャー）：他者の強気意見に対し、最悪のシナリオ（ブラックスワン）で論理的に反論せよ。

最後に、今買うべきか、全力買いか打診買いかも含め、各々意見を述べよ。

---
### 最終判断：ファンドマネージャーX
上記A〜Hの分析を統合し、結論を以下の項目で出力せよ：
1. 【最終判断】（買うべきか・見送るか、全力か打診か）
2. 【トレード戦略】（エントリー価格、ロスカット設定値、デイトレ目標値、スイング目標値）
3. 【テクニカル数値】（チャートから読み取れる現在のATR、支持線、抵抗線）
"""

            with st.spinner("AIアナリスト軍団が協議中...（混雑時はリトライします）"):
                # 429エラー回避のための簡易リトライ
                success = False
                for i in range(3):
                    try:
                        response = model.generate_content([prompt] + images)
                        st.markdown("---")
                        st.subheader("🕵️‍♂️ 投資判断レポート")
                        st.write(response.text)
                        success = True
                        break
                    except Exception as e:
                        if "429" in str(e):
                            time.sleep(10 * (i + 1)) # 待機時間を増やして再試行
                        else:
                            raise e
                
                if not success:
                    st.error("APIの利用制限中です。少し時間を置いてから再度お試しください。")

        except Exception as e:
            st.error(f"エラーが発生しました：{e}")

# --- フッター ---
st.markdown("---")
st.caption("© 2026 AI小次郎講師の投資判断. 本アプリの判断は投資の成果を保証するものではありません。")
