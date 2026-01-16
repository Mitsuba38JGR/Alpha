import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- 設定 ---
# 接続するスプレッドシートの名前（正確に入力してください）
SHEET_NAME = "ai_memo_data"

# --- 関数定義 ---

def connect_to_sheet():
    """Googleスプレッドシートに接続する"""
    try:
        # StreamlitのSecretsから認証情報を取得
        # (辞書形式で定義されていることを想定)
        creds_dict = st.secrets["gcp_service_account"]
        
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # スプレッドシートを開く
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        st.error(f"スプレッドシート接続エラー: {e}")
        return None

def get_ai_response(user_input):
    """OpenAI APIで応答を取得"""
    try:
        client = openai.OpenAI(api_key=st.secrets["openai"]["api_key"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは優秀な記録係です。簡潔に応答してください。"},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AIエラー: {e}"

# --- アプリケーション UI ---

st.title("📱 AIメモ (クラウド保存版)")
st.write("入力内容はGoogleスプレッドシートに自動保存されます。")

# シート接続
sheet = connect_to_sheet()

if sheet:
    # 入力フォーム
    with st.form("memo_form", clear_on_submit=True):
        user_input = st.text_area("メモを入力", height=100)
        submitted = st.form_submit_button("記録")

        if submitted and user_input:
            with st.spinner("AI思考中 & スプレッドシート書き込み中..."):
                # 1. AI応答
                ai_reply = get_ai_response(user_input)
                
                # 2. 現在時刻
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 3. シートに追加 (行: 日時, ユーザー, AI)
                sheet.append_row([now, user_input, ai_reply])
                
                st.success("スプレッドシートに保存しました！")

    # 履歴の表示（最新5件だけ取得して表示など）
    st.divider()
    st.subheader("📋 最新の記録")
    
    # 全データを取得（データ量が多い場合は注意）
    try:
        all_records = sheet.get_all_records()
        # リストを逆順にして最新を上に
        for record in reversed(all_records[-10:]): # 最新10件まで
            # カラム名はスプレッドシートの1行目に依存します
            # 1行目に「Timestamp」「User」「AI」と書いてある想定
            timestamp = record.get("Timestamp", "")
            user_text = record.get("User", "")
            ai_text = record.get("AI", "")
            
            with st.expander(f"{timestamp} - {str(user_text)[:15]}..."):
                st.markdown(f"**あなた:**\n{user_text}")
                st.info(f"**AI:**\n{ai_text}")
    except Exception as e:
        st.caption("データの読み込みに失敗しました（またはデータが空です）。")

else:
    st.warning("スプレッドシートに接続できませんでした。Secretsの設定を確認してください。")
