from flask import Flask
from flask_httpauth import HTTPBasicAuth
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

# 環境変数から認証用のユーザー名とパスワードを取得
USERS = {
    os.getenv("uechin22"): os.getenv("reito0922")
}

@auth.verify_password
def verify_password(username, password):
    if username in USERS and USERS[username] == password:
        return username

@app.route('/')
@auth.login_required  # 認証が必要
def home():
    return "短縮URLサービスが動作しています！（認証成功）"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Renderの環境変数PORTを使い、なければ10000をデフォルトに
    app.run(host="0.0.0.0", port=port)
