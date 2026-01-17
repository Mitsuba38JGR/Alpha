import streamlit as st
import pandas as pd
import os
import ollama
from datetime import datetime

# 保存するファイル名
CSV_FILE = "memo_data.csv"

# --- 関数定義 ---

def load_data():
    """CSVファイルから履歴を読み込む"""
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # ファイルがなければ作成（カラム設定）
        df = pd.DataFrame(columns=["Timestamp", "User", "AI"])
        return df

def save_data(timestamp, user_text, ai_text):
    """CSVファイルに追記保存する"""
    df = load_data()
    new_data = pd.DataFrame({
        "Timestamp": [timestamp],
        "User": [user_text],
        "AI": [ai_text]
    })
    # データを結合して保存
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def get_ai_response(user_input):
    """PC内のOllama(Llama3)を使って応答する"""
    try:
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': f"以下の入力を日本語で要約・整理して記録してください: {user_input}",
            },
        ])
        return response['message']['content']
    except Exception as e:
        return f"エラー: Ollamaが起動していないか、モデルがありません。\n詳細: {e}"

# --- アプリ画面 ---

st.title("🏠 完全ローカル AIメモ")
st.caption("API不要。データはPC内のCSVに保存されます。")

# 入力フォーム
with st.form("local_memo_form", clear_on_submit=True):
    user_input = st.text_area("メモを入力", height=100)
    submitted = st.form_submit_button("記録する")

    if submitted and user_input:
        with st.spinner("PC内のAIが思考中..."):
            # 1. AI応答
            ai_reply = get_ai_response(user_input)
            
            # 2. 保存
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(now, user_input, ai_reply)
            
            st.success("CSVに保存しました！")

# 履歴の表示
st.divider()
st.subheader("📂 保存された記録")

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    # 新しい順に並び替え
    df = df.iloc[::-1]
    
    for index, row in df.iterrows():
        with st.expander(f"{row['Timestamp']} - {str(row['User'])[:15]}..."):
            st.markdown(f"**あなた:**\n{row['User']}")
            st.info(f"**AI:**\n{row['AI']}")
else:
    st.write("まだ記録はありません。")
