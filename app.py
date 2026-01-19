import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 設定 ---
st.set_page_config(page_title="ルパン三世のAI投資判断", layout="wide")

# APIキーの設定（サイドバーで入力）
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter Google Gemini API Key:AIzaSyDciZ27wTS6IGbgKCn5S9GJUd6Xni0DTRE", type="password")
    if api_key:
        genai.configure(api_key=api_key)

# --- アプリのUI ---
st.title("💎 ルパン三世のAI投資判断")
st.caption("チャート・企業情報・財務の3つの視点から、お宝銘柄を徹底的に鑑定します。")

# 3カラムに変更
col1, col2, col3 = st.columns(3)
with col1:
    chart_file = st.file_uploader("📈 チャート画像をアップロード（必須）", type=["png", "jpg", "jpeg"])
with col2:
    company_info_file = st.file_uploader("🏢 企業情報画像をアップロード（任意）", type=["png", "jpg", "jpeg"])
with col3:
    finance_file = st.file_uploader("💰 財務画像をアップロード（任意）", type=["png", "jpg", "jpeg"])

# --- システムプロンプトの構築 ---
system_instruction = """
あなたは「ルパン三世のAI投資判断」チームです。以下の9名のエージェントになりきって、アップロードされた画像（チャート、企業情報、財務）のみを根拠に分析を行ってください。

【基本原則】
1. 画像から読み取れる数値・形状のみを根拠とせよ。
2. 画像にない情報は「不明」と断定し、憶測（ハルシネーション）を徹底排除せよ。
3. 最新の株価・指標は、画像内のOCR結果を最優先せよ。
4. 小次郎講師の理論をベースに、各キャラクターの口調（ルパン三世風の粋な雰囲気）を交えつつ回答せよ。

【分析フロー】
以下の順に発言してください：
アナリストA（バリュー）：CF・BS・財務の健全性。数字が全て。
アナリストB（トレーダー）：市場の関心・出来高。不人気株は却下。
アナリストC（移動平均線）：移動平均線大循環分析（ステージ1〜6）。
アナリストD（ローソク足）：酒田五法・窓・ヒゲの分析。
アナリストE（チャネル）：平行チャネル・フラッグ・ペナント。
アナリストF（MACD）：過熱感・ダイバージェンス。
アナリストG（騙しハンター）：過去のブレイクアウト失敗の形跡。
アナリストH（リスクマネージャー）：最悪のシナリオ（ブラックスワン）の提示。

最後に「ファンドマネージャーX」が、以下のフォーマットで最終判断を下してください。

【最終投資判断】
判定: （全力買い / 打診買い / 観望 / 売り）
根拠: 総合的な判断理由
戦術パラメータ:
| 項目 | 設定値 |
| :--- | :--- |
| エントリー価格 | 画像から読み取った価格 |
| ロスカット設定値 | 損切りライン |
| 目標値（デイトレ） | 期待値 |
| 目標値（スイング） | ターゲット |
| 現在のATR / 支持・抵抗 | ボラティリティと壁 |
"""

if st.button("鑑定開始（潜入開始）"):
    if not api_key:
        st.error("APIキーを入力してくれ。仕事にならねぇ。")
    elif not chart_file:
        st.error("チャート画像がないと始まらねぇな。アップロードしてくれ。")
    else:
        try:
            # モデルの初期化
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 画像の準備（存在するファイルのみリストに追加）
            images = []
            if chart_file:
                images.append(Image.open(chart_file))
            if company_info_file:
                images.append(Image.open(company_info_file))
            if finance_file:
                images.append(Image.open(finance_file))
            
            with st.spinner("次元、五ェ門、準備はいいか？3つの情報源から真実を盗み出すぜ..."):
                # 解析実行
                response = model.generate_content([system_instruction] + images)
                
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"おっと、予期せぬトラブルだ: {e}")

# --- フッター ---
st.sidebar.info("※投資は自己責任です。このAIは画像データに基づいたテクニカル・ファンダメンタル分析をシミュレーションするものです。")
