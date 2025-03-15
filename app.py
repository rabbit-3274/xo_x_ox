from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import os
import random
import string
from dotenv import load_dotenv

# .env のフルパスを指定して明示的に読み込む
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

app = Flask(__name__)
auth = HTTPBasicAuth()

# 環境変数から認証情報を取得
AUTH_USER = os.getenv("AUTH_USER", "").strip()
AUTH_PASS = os.getenv("AUTH_PASS", "").strip()

# 環境変数が適切に設定されているか確認
if not AUTH_USER or not AUTH_PASS:
    raise ValueError("環境変数 AUTH_USER または AUTH_PASS が設定されていません。")

@auth.verify_password
def verify_password(username, password):
    print(f"入力されたユーザー名: {username}")
    print(f"入力されたパスワード: {password}")
    print(f"環境変数のユーザー名: {AUTH_USER}")
    print(f"環境変数のパスワード: {AUTH_PASS}")

    if username.strip() == AUTH_USER and password.strip() == AUTH_PASS:
        return username
    return None

# SQLiteデータベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# URLデータベースモデル
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(10), unique=True, nullable=False)
    visits = db.Column(db.Integer, default=0)

# データベースの初期化
with app.app_context():
    db.create_all()

# 短縮IDを生成
def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# トップページ（認証必須）
@app.route("/", methods=["GET", "POST"])
@auth.login_required  # ログイン必須に設定
def index():
    if request.method == "POST":
        original_url = request.form["original_url"]
        custom_id = request.form["custom_id"] or generate_short_id()
        existing_url = URL.query.filter_by(short_id=custom_id).first()

        if existing_url:
            return "このカスタムIDはすでに使用されています。", 400

        new_url = URL(original_url=original_url, short_id=custom_id)
        db.session.add(new_url)
        db.session.commit()
        return redirect(url_for("index"))

    urls = URL.query.all()
    return render_template("index.html", urls=urls)

# 短縮URLのリダイレクト機能
@app.route("/<short_id>")
def redirect_url(short_id):
    url_entry = URL.query.filter_by(short_id=short_id).first_or_404()
    url_entry.visits += 1
    db.session.commit()
    return redirect(url_entry.original_url)

# 短縮URLの削除
@app.route("/delete/<int:url_id>")
@auth.login_required  # 削除も認証必須に設定
def delete_url(url_id):
    url_entry = URL.query.get_or_404(url_id)
    db.session.delete(url_entry)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
