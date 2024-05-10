from flask import Flask, jsonify, abort, redirect, url_for, request, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import json
import os

# 实例化 Flask 和 Flask-Login
app = Flask(__name__)
CORS(app)  # 允许跨域请求
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 用户类示例
class User(UserMixin):
    def __init__(self, userid, password):
        self.id = userid
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# 用于读取用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    user_dict = load_user_json()
    user_data = next((item for item in user_dict.get('users', []) if item["userid"] == user_id), None)
    if user_data:
        user = User(user_id, user_data.get('password'))
        return user
    return None

# 读取用户 JSON 数据的方法
def load_user_json():
    with open(os.path.join('json', 'user.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

# 首页数据读取方法
def load_data(filename):
    """读取 JSON 数据文件。"""
    with open(filename, encoding='utf-8') as file:
        return json.load(file)

# 根据游戏 ID 获取游戏详细信息的方法
@app.route('/game_details/<int:game_id>')
def game_details(game_id):
    """根据游戏 ID 获取游戏详细信息。"""
    current_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(current_dir, 'json', 'game_details.json')
    with open(file_path, encoding='utf-8') as f:
        all_game_details = json.load(f)
        game_detail = all_game_details.get(str(game_id))
        if not game_detail:
            abort(404)  # 如果找不到指定 ID 的游戏，返回 404 错误
        return jsonify(game_detail)

# 论坛分类接口
@app.route('/forum_categories')
def forum_categories():
    """获取论坛分类。"""
    # ... 省略代码

# 登录路由
# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('userid')
        password = request.form.get('password')
        user_dict = load_user_json()
        user_data = next((item for item in user_dict.get('users', []) if item["userid"] == user_id), None)
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_id, password)
            login_user(user)
            return redirect(url_for('protected'))
        return jsonify({'error': 'Invalid UserID or Password'}), 401
    return render_template('user_login.html')

# 受保护的路由，需要登录
@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + 'user_id'

# 注销路由
@app.route('/logout')
def logout():
    logout_user()
    return 'You have been logged out'

# 更多路由配置...

if __name__ == '__main__':
    app.run(debug=True)