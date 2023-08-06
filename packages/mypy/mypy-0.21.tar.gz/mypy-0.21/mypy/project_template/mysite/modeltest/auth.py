#coding:utf-8
import init_path

import unittest
from mysite.model import auth

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.email = "zsp.007@gmail.com"
        self.password = "test123456"
        self.name = "张沈鹏"

    def tearDown(self):
        auth.remove_user_by_email(self.email)

    def test_reg(self):
        if auth.UserEmail.get(email = self.email):
            auth.remove_user_by_email(self.email)

        auth.apply(self.email, self.password, self.name)

        e = auth.UserEmail.get(email = self.email)
        assert e is not None

        id = e.id

        assert auth.UserApply.get(id) is not None

        user_password = auth.UserPassword.get(id)
        assert user_password is not None
        assert user_password.verify(self.password)

        user = auth.create_user(id)
        assert user is not None
        assert auth.UserApply.get(id) is None

        user = auth.User.get(id)
        assert user is not None
        assert self.name == user.name

        assert auth.is_existed(self.email)

if __name__ == '__main__':
    unittest.main()

