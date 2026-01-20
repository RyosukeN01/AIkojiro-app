import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import io

# --- ページ設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide", page_icon="💎")

st.title("💎 ルパン三世のAI投資判断")
st.markdown("> **「制限？ Quota？ そんなもん、俺たちのチームワークでぶち破るぜ。」**")

# --- 画像最適化（リサイズ）関数 ---
def optimize_image(uploaded_file, max_size=(800, 800)):
    """画像をリサイズしてAPIの負荷とデータ転送量を減らすぜ"""
    img = Image.open(uploaded_file)
    # アスペクト比を維持してリサイズ
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    # RGBに変換（念のため）
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    return img

# --- サイドバー：API設定 ---
with st.sidebar:
    st.header("🔑 秘密の鍵")
    api_key = st.text_input("Google API Keyを入力", type="password")
    st.info("2026年最新モデル（Gemini 2.5/3.0系）をフル活用するぜ。")

# --- 画像アップロード ---
st.subheader("📸 お宝（画像）を3枚用意しな")
col1, col2, col3 = st.columns(3)
with col1:
    chart_file = st.file_uploader("📈 チャート", type=['png', 'jpg', 'jpeg'])
with col2:
    info_file = st.file_uploader("🏢 企業情報", type=['png', 'jpg', 'jpeg'])
with col3:
    financial_file = st.file_uploader("📄 財務状況", type=['png', 'jpg', 'jpeg'])

stock_name = st.text_input("🔢 銘柄名/コード", placeholder="例：ルパン三世工業 (1630)")

# --- メインロジック ---
if st.button("💰 お宝鑑定スタート！"):
    if not api_key:
        st.error("APIキーがねぇと、金庫は開かねぇぜ。")
    elif not (chart_file and info_file and financial_file):
        st.warning("画像が3枚揃ってねぇな。準備しな。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 2026年の優先モデルリスト（バックアップ戦略）
            model_candidates = [
                'models/gemini-3-flash-preview', # 最新
                'models/gemini-2.5-flash',       # 安定
                'models/gemini-2.0-flash',       # 旧型だが強力
                'models/gemini-1.5-flash'        # 最終バックアップ
            ]
            
            # 利用可能なモデルを確認
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            active_models = [m for m in model_candidates if m in available]
            
            if not active_models:
                active_models = [available[0]] # 最悪、リストの先頭を使う

            # 画像の最適化（転送量を減らして429回避）
            with st.spinner("画像をスキャン中...（最適化実施）"):
                imgs = [optimize_image(f) for f in [chart_file, info_file, financial_file]]

            # カスタム指示（プロンプト）
            prompt = f"""
あなたは小次郎講師の理論をマスターしたルパン三世の投資鑑定チームです。3枚の画像から事実のみを抜き出し、投資判断を行ってください。
銘柄名：{stock_name}

【分析指示：A〜Hの順で各員が意見を述べよ】
アナリストA：小次郎講師流バリュー投資。財務画像からCF/BSの数字のみを信じろ。
アナリストB：市場心理。過熱感と関心を分析せよ。
アナリストC：移動平均線大循環分析。現在のステージと明日の動向を判断せよ。
アナリストD：ローソク足・酒田五法。売り買いの優劣を判断せよ。
アナリストE：チャネル分析。今後の株価推移確率の高いレンジを特定せよ。
アナリストF：MACD分析。勢いと過熱感を判断せよ。
アナリストG：だまし分析。過去の事例と現在の成功率を判断せよ。
アナリストH：悲観的ディスクマネージャー。最悪のシナリオ（ブラックスワン）を突きつけ反論せよ。

最後に、ファンドマネージャーXが最終判断（判断材料、売買量、エントリー、ロスカット、目標値、ATR、支持・抵抗線）を具体的数値で出力してください。
"""

            # --- バックアップ & リトライ実行 ---
            success = False
            for model_name in active_models:
                if success: break
                
                model = genai.GenerativeModel(model_name)
                st.info(f"🔍 {model_name} で鑑定を試みるぜ...")
                
                # 指数バックオフによるリトライ（最大3回）
                for attempt in range(3):
                    try:
                        response = model.generate_content([prompt] + imgs)
                        st.markdown("---")
                        st.subheader("🕵️‍♂️ 鑑定結果レポート")
                        st.write(response.text)
                        success = True
                        break
                    except Exception as e:
                        err_msg = str(e)
                        if "429" in err_msg or "Quota" in err_msg:
                            wait_time = (attempt + 1) * 20 # 20秒, 40秒...と待機
                            st.warning(f"制限に引っかかったぜ。{wait_time}秒待機して再トライする。少し待ちな。")
                            time.sleep(wait_time)
                        else:
                            st.error(f"モデル {model_name} で予期せぬエラーだ：{e}")
                            break # 次のモデルへ

            if not success:
                st.error("全モデルが制限中か、エラーで全滅だ...。1分ほど空けてからまた呼んでくれ。")

        except Exception as e:
            st.error(f"致命的なトラブルだ：{e}")

st.markdown("---")
st.caption("© 2026 Lupin III AI Investment. 投資は自己責任。捕まっても知らねえぜ。")
