import unittest
from flask import Flask, session, jsonify
from app import app  # 请将这里的 `your_flask_application` 替换为实际的 Flask 应用模块名
from flask.sessions import SecureCookieSessionInterface
import json

# 使得 Flask session 可以在测试中被修改和访问
class MockSessionInterface(SecureCookieSessionInterface):
    def open_session(self, *args, **kwargs):
        return self.session_class()

    def save_session(self, *args, **kwargs):
        return

app.session_interface = MockSessionInterface()

class FlaskLoginTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_user_login_successful(self):
        # 填写有效的测试凭据
        test_userid = 'user2'
        valid_credentials = json.dumps({
            'userid': 'user2',
            'password': 'pass456'
        })
        response = self.client.post('/user_login', data=valid_credentials, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        with self.client as c:
            response = c.post('/user_login', data=valid_credentials, content_type='application/json')
            self.assertIn('userid', session)
            self.assertEqual(session['userid'], test_userid)

if __name__ == '__main__':
    unittest.main()