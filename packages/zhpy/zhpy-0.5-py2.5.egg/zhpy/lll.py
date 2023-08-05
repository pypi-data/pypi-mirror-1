#coding=utf-8
from pyparsing import *

"""
1. detect header docstring
2. 

"""
chineseChars = srange(r"[\0x0080-\0xfe00]")
InlineWord = '"'+Word(chineseChars)+'"'+":"+'"'+Word(alphas)+'"'+","

if __name__ == "__main__":
    utest = """
    keywords = {
    "我":"print",
    "你":"for"
    }
    """
    result = InlineWord.transformString(utest)
    print result