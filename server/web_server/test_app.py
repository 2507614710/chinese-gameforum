import unittest
import json
from flask import session
from app import app

class FlaskTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_user_login_success(self):
        data = {
            "userid": "user2",
            "password": "pass456"
        }
        with self.app as c:
            response = c.post('/user_login', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            expected_userid = 'user2'
            returned_userid = session['userid']
            self.assertEqual(expected_userid, returned_userid)
            # 检查返回的消息是否为"登录成功200"
            self.assertEqual(response.get_json()["message"], "登录成功200")

    def test_user_login_fail(self):
        data = {
            "userid": "wrong_username",
            "password": "wrong_password"
        }
        with self.app as c:
            response = c.post('/user_login', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 401)  # 如果用户名或密码错误, 状态码应为401


if __name__ == "__main__":
    unittest.main()