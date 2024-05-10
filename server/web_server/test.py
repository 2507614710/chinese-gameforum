import requests
import json

# 后端服务的登录URL
url = "http://127.0.0.1:5000/user_login"

# 登录数据
login_data = {
    'userid': 'user2',  # 替换成有效的用户名
    'password': 'pass456'  # 替换成有效的密码
}

headers = {'Content-Type': 'application/json'}  # 设置请求头

# 发送POST请求，将数据以JSON格式发送
response = requests.post(url, json=login_data, headers=headers)

# 检查HTTP状态码
if response.status_code == 200:
    try:
        # 尝试解析JSON响应
        data = response.json()
        print("登录成功:", data)
    except json.JSONDecodeError:
        # 如果响应不是JSON格式
        print("登录失败: 响应不是有效的JSON格式")
else:
    print(f"登录失败: 服务器返回了一个{response.status_code}状态码")