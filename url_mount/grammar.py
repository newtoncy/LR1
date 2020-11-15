# -*- coding: utf-8 -*-

# @File    : grammar.py
# @Date    : 2020-11-07
# @Author  : 王超逸
# @Brief   :

from collections import namedtuple, defaultdict, deque
import copy
from itertools import product
from typing import Set, FrozenSet, Iterable


def calc_once(function):
    def warp(*args, **kwargs):
        if not hasattr(function, "_result"):
            function._result = function(*args, **kwargs)
        return function._result
    return warp


__Production = namedtuple("Production", ["left", "right", "pos", "follow"])
LR1TableRow = namedtuple("LR1TableRow", ["shift_map", "goto_map", "reduce_map"])
# 空串
EPSILON = 0xff0001
END = "__$__"


class Production(__Production):
    def __str__(self):
        right = list(self.right)
        if self.pos != -1:
            right.insert(self.pos, "#")
        if self.follow:
            return "%s -> %s , %s" % (self.left, " ".join(right), self.follow)
        return "%s -> %s" % (self.left, " ".join(right))

    def __repr__(self):
        return str(self)

    def start(self, follow="$"):
        return Production(self.left, self.right, 0, follow)

    @property
    def next_v(self):
        """

        :type self: Production
        :return 如果没有到末尾，则返回语法符号。如果到了末尾，返回None。如果位置无效，抛出assertError
        """
        assert 0 <= self.pos <= len(self.right)
        if self.pos == len(self.right):
            return None
        return self.right[self.pos]

    @property
    def shift(self):
        """
        :type self: Production
        :param self:
        :return:
        """
        assert self.pos < len(self.right)
        return Production(self.left, self.right, self.pos + 1, self.follow)


Statue = FrozenSet[Production]


class GrammarError(Exception):

    def __init__(self, name, description) -> None:
        super().__init__("语法定义错误：%s,%s" % (name, description), name, description)


class Grammar(object):
    def __init__(self, filename="url_mount/grammar_def", start_v="文件"):
        self.start_v = start_v
        self._start_status = None
        self.productions = self.load_grammar_def(filename)
        self.production_dict = defaultdict(list)
        for production in self.productions:
            self.production_dict[production.left].append(production)
        self.production_dict = dict(self.production_dict)
        self._closure_map = {}

    @property
    def start_status(self) -> Statue:
        if self._start_status is None:
            assert len(self.production_dict[self.start_v]) == 1, "开始符号的候选式只能且必须有一个"
            start_p = self.production_dict[self.start_v][0]
            self._start_status = self.closure({start_p.start()})
        return self._start_status

    @property
    @calc_once
    def lr1Table(self):
        queue = deque()
        queue.append(self.start_status)
        lr1_table = {}
        while queue:
            status: Statue = queue.popleft()
            pnextv_p = defaultdict(set)  # {self.next_v(p) for p in status}
            for p in status:
                pnextv_p[p.next_v].add(p)
            reduce = {}
            if None in pnextv_p:
                for p in pnextv_p[None]:
                    if p.follow in reduce:
                        raise GrammarError("规约规约冲突", [str(p) for p in status])
                    reduce[p.follow] = p
                pnextv_p.pop(None)
            goto = {}
            shift = {}
            for v in pnextv_p.keys():
                next_status = self.closure({p.shift for p in pnextv_p[v]})
                # 非终结符
                if v in self.production_dict:
                    goto[v] = next_status
                # 终结符
                else:
                    shift[v] = next_status
                if set(reduce.keys()) & set(shift.keys()):
                    raise GrammarError("移入规约冲突", [str(p) for p in status])
                queue.append(next_status)
            lr1_table[status] = LR1TableRow(shift, goto, reduce)
        return lr1_table

    def get_first_set(self, v_list):
        """
        由一个文法符号数组得到其first_set
        :type v_list: Iterable
        """
        first_set = set()
        for x in v_list:
            # 终结符
            if x not in self.production_dict:
                first_set.add(x)
                return first_set
            if EPSILON not in self.first_set[x]:
                first_set |= self.first_set[x]
                return first_set
            first_set |= self.first_set[x] - {EPSILON}
        first_set.add(EPSILON)
        return first_set

    @property
    @calc_once
    def first_set(self):
        first_set = defaultdict(set)
        vn_set = set(self.production_dict.keys())
        while True:
            first_set_copy = copy.deepcopy(first_set)
            # 对每个vn
            for vn in vn_set:
                # 对vn的每个产生式
                for vn_p in self.production_dict[vn]:
                    all_have_epsilon = True
                    # 对每个产生式的每个语法符号
                    for vn_p_x in vn_p.right:
                        # 如果是终结符
                        if vn_p_x not in vn_set:
                            first_set[vn].add(vn_p_x)
                            all_have_epsilon = False
                            break
                        # 如果没有空串
                        if EPSILON not in first_set[vn_p_x]:
                            first_set[vn] |= first_set[vn_p_x]
                            all_have_epsilon = False
                            break
                        first_set[vn] |= first_set[vn_p_x] - {EPSILON}
                    # 如果每一项都含有空串
                    if all_have_epsilon:
                        first_set[vn].add(EPSILON)
            if first_set_copy == first_set:
                break
        return first_set

    def closure(self, I):
        """

        :type I: set
        """
        J = copy.copy(I)
        J_copy = None
        while J != J_copy:
            J_copy = copy.copy(J)
            for p in J_copy:
                next_v = p.next_v
                if next_v in self.production_dict:
                    follows = self.get_first_set(list(p.right[p.pos + 1:]) + list(p.follow))
                    for pp, follow in product(self.production_dict[next_v], follows):
                        J.add(pp.start(follow))

        J = frozenset(J)
        # 这是为了让相同的闭包始终只有一个在内存里
        # 如果直接返回J的话，内存中可能会有很多个J的拷贝
        if J not in self._closure_map:
            self._closure_map[J] = J
        return self._closure_map[J]

    @staticmethod
    def load_grammar_def(filename):
        productions = []
        with open(filename, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                t = line.split("->")
                left = t[0].strip()
                t = t[1].split("|")
                for right in t:
                    productions.append(Production(left, tuple([i.strip() for i in right.split(" ") if i]), -1, ""))
        return productions


lr1_table = Grammar().lr1Table
lr1_table = Grammar().lr1Table
print()

