import unittest
from url_mount.lexical_analysis import get_token_sequence


class MyTestCase(unittest.TestCase):
    def test_something(self):
        code = """
# 路由语法
route "a/b" to "path/to/you.html" (render)
route "a/b2" to "path/to/you.html" (raw)

# 引用子路由
route "url/" to sub route "m1.route"
route "url/" to sub route route1

# 静态文件挂载语法
mount "url/" to "path/to/static/dir" (auto_html)

# 路由到python函数
from module1.module2 import functionA
route "url/" to functionA 


# 子路由内联定义
@route1
route "c/d" to "path/to/you.html" (render)
route "c/d2" to "path/to/you.html" (raw)
        
        """
        result = str(get_token_sequence(code))

        with open(r"test\test_lexical_expect.txt", "rt")as f:
            self.assertEqual(result, f.read())


if __name__ == '__main__':
    unittest.main()
