import streamlit as st
import openai
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# データを保存するファイル名
DATA_FILE = "memo_history.json"

# --- 関数定義 ---

def load_history():
    """保存された履歴を読み込む"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_history(history):
    """履歴をファイルに保存する"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def get_ai_response(user_input):
    """OpenAI APIを使って応答を取得する"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # または gpt-4
            messages=[
                {"role": "system", "content": "あなたは優秀なメモアシスタントです。ユーザーの入力を整理して記録してください。"},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"エラーが発生しました: {e}"

# --- アプリケーションのUI (Streamlit) ---

st.title("📝 AI メモ & レコーダー")
st.write("自由にテキストを入力してください。AIが応答し、履歴を記録します。")

# 履歴の初期化
if "history" not in st.session_state:
    st.session_state.history = load_history()

# 入力フォーム
with st.form("memo_form", clear_on_submit=True):
    user_input = st.text_area("内容を入力", height=100)
    submitted = st.form_submit_button("記録する")

    if submitted and user_input:
        # AIの応答を取得
        with st.spinner("AIが思考中..."):
            ai_reply = get_ai_response(user_input)
        
        # データの構築
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_input,
            "ai": ai_reply
        }
        
        # 履歴に追加して保存
        st.session_state.history.insert(0, record) # 新しいものを上に
        save_history(st.session_state.history)
        st.success("記録しました！")

# 履歴の表示
st.divider()
st.subheader("📜 過去の記録")

if st.session_state.history:
    for item in st.session_state.history:
        with st.expander(f"{item['timestamp']} - {item['user'][:20]}..."):
            st.markdown(f"**あなた:**\n{item['user']}")
            st.info(f"**AI:**\n{item['ai']}")
else:
    st.write("まだ記録はありません。")
