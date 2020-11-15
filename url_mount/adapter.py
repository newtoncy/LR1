# -*- coding: utf-8 -*-

# @File    : adapter.py
# @Date    : 2020-11-07
# @Author  : 王超逸
# @Brief   : 不同后台框架的适配器


class Adapter(object):

    def __init__(self, app_context):
        """

        :param app_context: app的上下文，根据需要传入
        """
        self.app_context = app_context

    def route(self, url, file_path, flags=None, data=None, sub_route=None):
        """
        生成并注册好一个视图.
        :param sub_route: 视图所属的子路由
        :param url: url
        :param data: 传给模板文件的数据
        :param file_path:模板文件位置
        :param flags: render是否进行模板渲染
        :return: None
        """
        raise NotImplementedError()

    def mount(self, base_file_path, base_url, flags=None, sub_route=None):
        """
        生成并注册好一个视图，将静态文件夹挂载到url。
        :param sub_route: 视图所属的子路由
        :param base_file_path:
        :param base_url:
        :param flags:
        :return: None
        """
        raise NotImplementedError()

    def get_sub_route(self, base_url):
        """

        :return:返回一个sub route对象
        """
        raise NotImplementedError()

    def register_all(self):
        """
        在结束时会调用这个方法
        如果注册的对象是nginx之类的。可能需要在这里更新配置文件
        :return:
        """
        raise NotImplementedError()
