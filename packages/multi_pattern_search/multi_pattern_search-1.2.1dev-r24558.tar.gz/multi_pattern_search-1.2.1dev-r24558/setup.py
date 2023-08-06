#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from setuptools import find_packages
from distutils.core import Extension,setup
setup(
    name = 'multi_pattern_search',
    version='1.2.1',
    author='zsp',
    author_email="zsp007@gmail.com",
    description="Multi-Pattern Matching Algorithms 多模式匹配算法",
    zip_safe = False,
    ext_package = "multi_pattern_search",
    ext_modules = [
        Extension(
            'multi_pattern_search',
            [
                "multi_pattern_search/cpp/search_py.cpp",
            ],
            extra_compile_args=['-O3'],
            libraries=['boost_python'],
        ),
    ],
    packages=find_packages(),
    long_description="""
Engling Example:

from multi_pattern_search import MultiPatternSearch

search = MultiPatternSearch()
search.add_keyword("zsp")
search.add_keyword("my")

print search.exist("sdfgasg sadgfa zsp my ")

for k, v in search.count("my zsp ewtawt  my zsp wat233").iteritems():
    print k.decode('utf-8'), v

中文演示:

#coding=utf-8

from multi_pattern_search import MultiPatternSearch

search = MultiPatternSearch()
search.add_keyword("张沈鹏")
search.add_keyword("我是")

print search.exist("asdga sddqbq 珍珠饰张沈鹏品 ")

for k, v in search.count("我是张沈鹏.我是张沈鹏.我是张沈鹏.我是张沈鹏.").iteritems():
    print k.decode('utf-8'), v
            """,
)

