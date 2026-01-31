import time
import random

def call_gemini_with_retry(model_name, data, attempt=0):
    try:
        # API呼び出し
        return client.generate_content(model=model_name, content=data)
    except ResourceExhausted: # 429制限など
        if attempt < 3:
            wait_time = (2 ** attempt) + random.random()
            time.sleep(wait_time)
            return call_gemini_with_retry(model_name, data, attempt + 1)
        raise # 上限に達したらエラーを投げて次のモデルへ
