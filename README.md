# AI Memo Recorder

ユーザーが入力したテキストをAIが処理し、その対話履歴をローカルのJSONファイルに自動的に記録・保存するアプリケーションです。

## 特徴
- **AI対話**: OpenAI APIを利用して、入力に対する応答や要約を行います。
- **自動記録**: 全てのやり取りは `memo_history.json` にタイムスタンプ付きで保存されます。
- **シンプルUI**: Streamlitを使用した直感的なインターフェース。

## 前提条件
- Python 3.8 以上
- OpenAI API Key

## インストール方法

1. リポジトリをクローンします。
   ```bash
   git clone https://github.com/あなたのユーザー名/リポジトリ名.git
   cd リポジトリ名
