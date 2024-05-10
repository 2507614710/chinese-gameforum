import unittest
import requests

class UserSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000"  # 修改为你应用的URL
        self.login_url = f"{self.base_url}/user_login"
        self.check_login_url = f"{self.base_url}/check-login"
        self.session = requests.Session()  # 用于维护会话状态

    def test_login(self):
        """测试用户登录"""
        credentials = {'userid': 'user2', 'password': 'pass456'}
        response = self.session.post(self.login_url, json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertIn('userid', self.session.cookies.get_dict())

    def test_check_login(self):
        """登录后，测试检查会话状态"""
        self.test_login()  # 确保先登录
        response = self.session.get(self.check_login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('loggedIn'))

    def tearDown(self):
        self.session.close()

if __name__ == "__main__":
    unittest.main()