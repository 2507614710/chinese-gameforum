from flask import Flask, jsonify, abort,current_app,request,render_template
from flask_cors import CORS
import json
import os
import redis
from flask_session import Session
from flask import session
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置SECRET_KEY以启用会话
CORS(app, supports_credentials=True)  # 允许跨域请求，保证前端可以将cookie发送到服务器

app.config['SECRET_KEY'] = os.urandom(24)  # 使用操作系统的随机数作为SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'  # 使用文件系统来保存session
app.config['SESSION_FILE_DIR']='flask_session'
# 设置session的有效期为7天
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_USE_SIGNER'] = True  # 增加session的安全性
Session(app)  # 初始化session


@app.route('/forum')
def forum():
    """返回论坛页面"""
    return render_template('forum.html')

@app.route('/forum_details')
def forum_details():
    """返回论坛详情页面。利用查询字符串获取分类ID"""
    # 注意：这里不直接使用查询字符串，而是传递给模板，前端JavaScript处理
    return render_template('forum_details.html')

def load_data(filename):
    """读取JSON数据文件"""
    with open(filename, encoding='utf-8') as file:  # 使用utf-8编码打开
        return json.load(file)

def save_data(filename, data):
    """数据写入JSON文件"""
    with open(filename, mode='w', encoding='utf-8') as file:  # 使用utf-8编码保存
        json.dump(data, file, ensure_ascii=False, indent=2)

@app.route('/games')
def get_games():
    """获取全部游戏列表"""
    games = load_data('./json/games.json')
    return jsonify(games)

@app.route('/posts')
def get_posts():
    """获取全部帖子列表"""
    posts = load_data('./json/posts.json')
    return jsonify(posts)

@app.route('/game_details/<int:game_id>')
def game_details(game_id):
    """根据游戏ID获取游戏详细信息"""
    current_dir = os.path.abspath(os.path.dirname(__file__))  # 当前文件绝对路径
    file_path = os.path.join(current_dir, 'json', 'game_details.json')
    with open(file_path, encoding='utf-8') as f:
        all_game_details = json.load(f)
        game_detail = all_game_details.get(str(game_id))
        if not game_detail:
            abort(404)
        return jsonify(game_detail)

@app.route('/posts_details/<int:post_id>')
def post_details(post_id):
    """根据帖子ID获取帖子详细信息"""
    file_path = 'json/posts_details.json'
    with open(file_path, encoding='utf-8') as f:
        all_post_details = json.load(f)
        post_detail = all_post_details.get(str(post_id))
        if not post_detail:
            abort(404)
        return jsonify(post_detail)

@app.route('/forum_categories')
def forum_categories():
    """返回论坛分类数据"""
    try:
        with open('json/Forum_category.json', 'r', encoding='utf-8') as forum_file:
            data = json.load(forum_file)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "分类数据文件找不到"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "JSON数据格式错误"}), 400
    except UnicodeDecodeError:
        return jsonify({"error": "文件编码错误"}), 500

@app.route('/forum_details/<int:category_id>')
def get_forum_details(category_id):
    """返回指定论坛分类详情"""
    file_path = os.path.join('json', f'{category_id}.json')
    if not os.path.isfile(file_path):
        abort(404)
    with open(file_path, encoding='utf-8') as f:
        category_details = json.load(f)
    return jsonify(category_details)


@app.route('/update_post/<int:forum_id>', methods=['POST'])
def update_post(forum_id):
    """处理帖子的更新请求，向指定的json文件尾部添加带有特定用户ID的新帖子信息"""
    # 首先获取请求中的新帖子信息
    new_post_data = request.get_json(force=True)
    if not new_post_data:
        return jsonify({"error": "请求中需要包含新的帖子信息"}), 400

    # 在新帖子信息的前面添加固定的用户ID
    new_post_data_with_userid = {"userid": "user2", **new_post_data}

    file_path = os.path.join('json', f'{forum_id}.json')
    if not os.path.isfile(file_path):
        abort(404)

    # 打开文件，读取现有帖子，然后添加新帖子
    with open(file_path, encoding='utf-8') as f:
        posts = json.load(f)
    posts.append(new_post_data_with_userid)

    # 将更新后的帖子列表写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

    return jsonify({"message": f"帖子已添加到论坛{forum_id}", "post_data": new_post_data_with_userid}), 201

@app.route('/game_boards')
def get_game_boards():
    """获取游戏板块数据"""
    try:
        with open('json/Game_board.json', 'r', encoding='utf-8') as games_file:
            data = json.load(games_file)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "游戏数据文件找不到"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "JSON数据格式错误"}), 400
    except UnicodeDecodeError:
        return jsonify({"error": "文件编码错误"}), 500



def load_users():
    """读取用户数据"""
    with open('json/user.json', encoding='utf-8') as file:
        return json.load(file)

@app.route('/user_login', methods=['POST'])
def user_login():
    # 用户登录，将用户ID存入session
    session.permanent = True  # 设置session持久化
    users = load_users()["users"]  # 加载用户数据
    data = request.get_json()  # 获取请求的JSON数据
    userid = data.get('userid')
    password = data.get('password')

    # 在用户数据中查找是否存在相应的用户
    user = next((u for u in users if u["userid"] == userid and u["password"] == password), None)
    if user:
        session['userid'] = userid  # 存储用户ID到session
        session['loggedIn'] = True  # 设置session中的loggedIn为True，表示用户已登录
        return jsonify({"message": "登录成功", "userid": userid}), 200
    else:
        return jsonify({"message": "账号或密码错误"}), 401

@app.route('/get_session', methods=['GET'])
def get_session():
    # 获取session中的userid
    userid = session.get('userid')
    if userid:
        return jsonify({"userid": userid}), 200
    else:
        return "Session为空！", 401

@app.route('/check-login', methods=['GET'])
def check_login():
    """检查用户是否已登录"""
    userid_response = get_session()  # 尝试通过get_session获取userid
    if userid_response[1] == 200:  # 如果状态码是200，意味着成功获取到userid
        userid = userid_response[0].json['userid']
        return jsonify({
            'userid': userid,
            'loggedIn': True
        }), 200
    else:
        return jsonify({
            'message': '用户未登录',
            'loggedIn': False
        }), 401

@app.route('/user_register', methods=['POST'])
def user_register():
    """用户注册处理"""
    users_data_path = 'json/user.json'
    new_user = request.get_json()
    userid = new_user.get('userid')
    password = new_user.get('password')
    if not userid or not password:
        abort(400, description="用户名或密码不能为空")
    with open(users_data_path, encoding='utf-8') as file:
        users_data = json.load(file)
    user_exists = any(user['userid'] == userid for user in users_data['users'])
    if user_exists:
        abort(400, description="用户名已存在")
    new_user_record = {"userid": userid, "password": password}
    users_data['users'].append(new_user_record)
    with open(users_data_path, 'w', encoding='utf-8') as file:
        json.dump(users_data, file, ensure_ascii=False, indent=4)
    return jsonify({"message": "注册成功", "userid": userid})

@app.route('/submit_post/<int:forum_id>', methods=['POST'])
def submit_post(forum_id):
    """提交论坛帖子数据"""
    if 'userid' not in session:
        return jsonify({"error": "请先登录"}), 401
    userid = session['userid']
    post_data = request.get_json()
    if not all(k in post_data for k in ("content", "date")) or post_data['userid'] != userid:
        abort(400, description="数据不完整或用户ID不匹配")
    post_data['userid'] = userid
    file_path = os.path.join('json', f'{forum_id}.json')
    if os.path.exists(file_path):
        posts = load_data(file_path)
    else:
        posts = []
    posts.append(post_data)
    save_data(file_path, posts)
    return jsonify({"message": f"帖子已提交到论坛分类{forum_id}", "post_data": post_data}), 200

@app.route('/contact_info')
def contact_info():
    """返回联系我们信息"""
    try:
        contact_info = load_data('./json/contact.json')
        return jsonify(contact_info)
    except Exception as e:
        print(f"Error: {e}")  # 打印错误信息
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)