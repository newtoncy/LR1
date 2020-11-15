# -*- coding: utf-8 -*-

# @File    : lexical_analysis.py
# @Date    : 2020-11-07
# @Author  : 王超逸
# @Brief   : 词法分析

import re
from collections import namedtuple

token_re = [
    ("@", r"@"),
    ("mount", "mount"),
    ("route", "route"),
    ("to", "to"),
    ("sub_route", "sub route"),
    ("from", "from"),
    ("import", "import"),
    ("str", r"[\",'].*?[\",']"),
    ("(", r"\("),
    (")", r"\)"),
    (".", "."),
    ("id", r"([a-zA-Z_]|[^\x00-\xff])([\w]|[^\x00-\xff])*")

]


class LexicalErrors(Exception):

    def __init__(self, word, line):
        super().__init__("词法错误，第%d行，%s..." % (line, word))


Token = namedtuple("Token", ("name", "org", "pos_line"))


def get_token_sequence(code_org):
    """

    :type code_org: str
    """
    lines = code_org.split('\n')
    token_sequence = []
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("#"):
            continue
        remain = line
        while remain:
            # 长度优先，同等长度，从上到下有先
            matched = None
            token_name = None
            max_matched = 0
            for name, regular in token_re:
                t = re.match(regular, remain)
                if not t:
                    continue
                t = t.group(0)
                if len(t) > max_matched:
                    matched = t
                    token_name = name
                    max_matched = len(t)

            if not matched:
                raise LexicalErrors(remain, i)
            token_sequence.append(Token(token_name, matched, i))
            remain = remain[len(matched):]
            remain = remain.strip()
    return token_sequence
