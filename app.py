# GitHubの app.py の修正例
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("SecretsにAPIキーを設定してくれ。")
