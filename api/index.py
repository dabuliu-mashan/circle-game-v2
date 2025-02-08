from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import random
import string
import os
from datetime import timedelta

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key-here")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)

# 使用内存变量存储数据
users_data = {}
scores_data = []

class User(UserMixin):
    def __init__(self, user_id, username, best_score=0):
        self.id = user_id
        self.username = username
        self.best_score = best_score

    def get_id(self):
        return str(self.id)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"

@login_manager.user_loader
def load_user(user_id):
    return users_data.get(user_id)

def generate_username():
    adjectives = ["快乐", "开心", "可爱", "聪明", "勇敢"]
    nouns = ["画家", "艺术家", "玩家", "达人", "高手"]
    number = "".join(random.choices(string.digits, k=4))
    return random.choice(adjectives) + random.choice(nouns) + number

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("game"))
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", generate_username())
    
    # 检查用户名是否存在
    for user in users_data.values():
        if user.username == username:
            return jsonify({"success": False, "message": "用户名已存在"})
    
    # 创建新用户
    user_id = str(len(users_data) + 1)
    user = User(user_id, username)
    users_data[user_id] = user
    login_user(user)
    return jsonify({"success": True})

@app.route("/game")
@login_required
def game():
    return render_template("game.html")

@app.route("/submit_score", methods=["POST"])
@login_required
def submit_score():
    data = request.get_json()
    score = float(data.get("score", 0))
    
    # 记录分数
    scores_data.append({
        "user_id": current_user.get_id(),
        "score": score
    })
    
    # 更新最高分
    if score > current_user.best_score:
        current_user.best_score = score
    
    return jsonify({"success": True})

@app.route("/leaderboard")
@login_required
def leaderboard():
    # 获取所有用户并按最高分排序
    users_list = sorted(
        users_data.values(),
        key=lambda x: x.best_score,
        reverse=True
    )
    return render_template("leaderboard.html", users=users_list)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)