""" Gridict module """

from abc import ABC
from dataclasses import dataclass
from functools import total_ordering
from itertools import chain
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

class Line(ABC):
    """ Line class """


@total_ordering
@dataclass
class XLine(Line):
    """ X Line class """
    bx  :float
    ex  :float
    y   :float
    pl  :Optional['XLine'] = None # previous (left) line
    nl  :Optional['XLine'] = None # next (right) line
    pll :Optional['YLine'] = None # previous (left) left (top) line
    prl :Optional['YLine'] = None # previous (left) right (bottom) line
    nll :Optional['YLine'] = None # next (right) left (top) line
    nrl :Optional['YLine'] = None # next (right) right (bottom) line

    def __post_init__(self):
        assert self.bx <= self.ex
        self.rev = ReversedXLine(self)

    def __repr__(self) -> str:
        return 'XL#{:04}(bx:{:.1f}, ex:{:.1f}, y:{:.1f})'.format(id(self) % 10000, self.bx, self.ex, self.y)

    def __hash__(self) -> int:
        # return hash((self.bx, self.ex, self.y))
        return id(self)

    def has_x(self, x:float) -> bool:
        # return x <= self.ex if self.bx <= x else x >= self.ex
        return self.bx <= x and x <= self.ex

    def has(self, x:float, y:float) -> bool:
        return self.y == y and self.has_x(x)

    def cross(self, yl:'YLine') -> Optional[Tuple[float, float]]:
        if self.has_x(yl.x) and yl.has_y(self.y):
            return yl.x, self.y
        return None

    def __eq__(self, o) -> bool:
        if not isinstance(o, XLine):
            return NotImplemented
        return self.y == o.y and self.bx == o.bx and self.ex == o.ex

    def __lt__(self, o) -> bool:
        if not isinstance(o, XLine):
            return NotImplemented
        return self.y < o.y

    def split_by_x(self, x:float) -> Tuple['XLine', 'XLine']:
        """ Split this line by x coord """
        l1 = XLine(bx=self.bx, ex=x, y=self.y, pl=self.pl, pll=self.pll, prl=self.prl)
        l2 = XLine(bx=x, ex=self.ex, y=self.y, nl=self.nl, nll=self.nll, nrl=self.nrl)
        l1.nl = l2
        l2.pl = l1
        if self.pl:
            self.pl.nl = l1
        if self.pll:
            self.pll.prl = l1
        if self.prl:
            self.prl.nrl = l1
        if self.nl:
            self.nl.pl = l2
        if self.nll:
            self.nll.pll = l2
        if self.nrl:
            self.nrl.nll = l2
        return l1, l2

    def split_by_line(self, yl:'YLine') -> Tuple[Tuple['XLine', 'XLine'], Tuple['YLine', 'YLine']]:
        xl1, xl2 = self.split_by_x(yl.x)
        yl1, yl2 = yl.split_by_y(self.y)
        xl1.nrl = xl2.prl = yl1
        xl1.nll = xl2.pll = yl2
        yl1.nll = yl2.pll = xl1
        yl1.nrl = yl2.prl = xl2
        return (xl1, xl2), (yl1, yl2)

    @property
    def tonl(self):
        return self.nl

    @property
    def toll(self):
        return self.nll

    @property
    def torl(self):
        return self.nrl.rev if self.nrl else None


@total_ordering
@dataclass
class YLine(Line):
    """ Y Line class """
    x   :float
    by  :float
    ey  :float
    pl  :Optional['YLine'] = None # previous (top) line
    nl  :Optional['YLine'] = None # next (bottom) line
    pll :Optional['XLine'] = None # previous (top) left line
    prl :Optional['XLine'] = None # previous (top) right line
    nll :Optional['XLine'] = None # next (bottom) left line
    nrl :Optional['XLine'] = None # next (bottom) right line

    def __post_init__(self):
        assert self.by <= self.ey
        self.rev = ReversedYLine(self)

    def __repr__(self) -> str:
        return 'YL#{:04}(x:{:.1f}, by:{:.1f}, ey:{:.1f})'.format(id(self) % 10000, self.x, self.by, self.ey)

    def __hash__(self) -> int:
        # return hash((self.x, self.by, self.ey))
        return id(self)

    def has_y(self, y:float) -> bool:
        # return y <= self.ey if self.by <= y else y >= self.ey
        return self.by <= y and y <= self.ey

    def has(self, x:float, y:float) -> bool:
        return self.x == x and self.has_y(y)

    def cross(self, xl:'XLine') -> Optional[Tuple[float, float]]:
        if self.has_y(xl.y) and xl.has_x(self.x):
            return self.x, xl.y
        return None

    def __eq__(self, o) -> bool:
        if not isinstance(o, YLine):
            return NotImplemented
        return self.x == o.x and self.by == o.by and self.ey == o.ey

    def __lt__(self, o) -> bool:
        if not isinstance(o, YLine):
            return NotImplemented
        return self.x < o.x

    def split_by_y(self, y:float) -> Tuple['XLine', 'XLine']:
        """ Split this line by x coord """
        l1 = YLine(by=self.by, ey=y, x=self.x, pl=self.pl, pll=self.pll, prl=self.prl)
        l2 = YLine(by=y, ey=self.ey, x=self.x, nl=self.nl, nll=self.nll, nrl=self.nrl)
        l1.nl = l2
        l2.pl = l1
        if self.pl:
            self.pl.nl = l1
        if self.pll:
            self.pll.nll = l1
        if self.prl:
            self.prl.pll = l1
        if self.nl:
            self.nl.pl = l2
        if self.nll:
            self.nll.nrl = l2
        if self.nrl:
            self.nrl.prl = l2
        return l1, l2

    def split_by_line(self, xl:'XLine') -> Tuple[Tuple['XLine', 'XLine'], Tuple['YLine', 'YLine']]:
        return xl.split_by_line(self)

    @property
    def tonl(self):
        return self.nl

    @property
    def toll(self):
        return self.nll.rev if self.nll else None

    @property
    def torl(self):
        return self.nrl

@dataclass
class ReversedXLine(Line):
    """ Reversed X line class """
    xl: XLine # X Line

    @property
    def y(self):
        return self.xl.y

    @property
    def bx(self):
        return self.xl.bx

    @property
    def ex(self):
        return self.xl.ex1

    @property
    def rev(self):
        return self.xl

    @property
    def pl(self):
        return self.xl.nl

    @property
    def nl(self):
        return self.xl.pl

    @property
    def prl(self):
        return self.xl.nll

    @property
    def pll(self):
        return self.xl.nrl

    @property
    def nrl(self):
        return self.xl.pll

    @property
    def nll(self):
        return self.xl.prl

    @property
    def tonl(self):
        return self.xl.pl.rev if self.xl.pl else None

    @property
    def toll(self):
        return self.xl.prl.rev if self.xl.prl else None

    @property
    def torl(self):
        return self.xl.pll

    def __repr__(self) -> str:
        return 'Rev' + repr(self.xl)

    def __hash__(self) -> int:
        # return hash(('R', self.l))
        return id(self)

    def __eq__(self, o):
        if not isinstance(o, ReversedXLine):
            return NotImplemented
        return self.xl == o.xl

@dataclass
class ReversedYLine(Line):
    """ Reversed Y line class """
    yl: YLine # Y Line

    @property
    def x(self):
        return self.yl.x

    @property
    def by(self):
        return self.yl.by

    @property
    def ey(self):
        return self.yl.ey

    @property
    def rev(self):
        return self.yl

    @property
    def pl(self):
        return self.yl.nl

    @property
    def nl(self):
        return self.yl.pl

    @property
    def prl(self):
        return self.yl.nll

    @property
    def pll(self):
        return self.yl.nrl

    @property
    def nrl(self):
        return self.yl.pll

    @property
    def nll(self):
        return self.yl.prl

    @property
    def tonl(self):
        return self.yl.pl.rev if self.yl.pl else None

    @property
    def toll(self):
        return self.yl.prl

    @property
    def torl(self):
        return self.yl.pll.rev if self.yl.pll else None

    def __repr__(self) -> str:
        return 'Rev' + repr(self.yl)

    def __hash__(self) -> int:
        # return hash(('R', self.l))
        return id(self)

    def __eq__(self, o):
        if not isinstance(o, ReversedYLine):
            return NotImplemented
        return self.yl == o.yl

@dataclass
class Box:
    tl :XLine # top line
    bl :XLine # bottom line
    ll :YLine # left line
    rl :YLine # right line

    def __post_init__(self):
        assert self.bl <= self.tl and self.ll <= self.rl
        # assert self.tl.rb is None and self.bl.lb is None and self.ll.rb is None and self.rl.lb is None
        self.tl.rb = self.bl.lb = self.ll.rb = self.rl.lb = self

    # def unref(self):
    #     assert self.tl.rb == self and self.bl.lb == self and self.ll.rb == self and self.rl.lb == self
    #     self.tl.rb = self.bl.lb = self.ll.rb = self.rl.lb = None

    @property
    def bx(self) -> float:
        return self.ll.x

    @property
    def by(self) -> float:
        return self.bl.y

    @property
    def ex(self) -> float:
        return self.rl.x

    @property
    def ey(self) -> float:
        return self.tl.y

    def __repr__(self) -> str:
        return 'Box#{:04}(bx:{:.1f}, by:{:.1f}, ex:{:.1f}, ey:{:.1f})'.format(id(self) % 10000, self.bx, self.by, self.ex, self.ey)

    def __hash__(self) -> int:
        return hash((self.bx, self.by, self.ex, self.ey))

    def __eq__(self, o) -> bool:
        if not isinstance(o, Box):
            return NotImplemented
        return self.bx == o.bx and self.by == o.by and self.ex == o.ex and self.ey == o.ey


class Grid:

    def __init__(self, o_xls:Iterable[XLine], o_yls:Iterable[YLine]):
        sorted_xls = sorted(o_xls)
        sorted_yls = sorted(o_yls)
        self.xls:Set[XLine] = set()
        self.yls:Set[YLine] = set()
        # self.boxes :List[Box] = []

        for yi in range(len(sorted_yls)):
            yl = sorted_yls[yi]
            self.yls.add(yl)
            for xi in range(len(sorted_xls)):
                xl = sorted_xls[xi]
                self.xls.add(xl)
                print(xl, 'and', yl)
                if cpt := xl.cross(yl):
                    print('Cross at', cpt)
                    (pxl, new_xl), (pyl, new_yl) = xl.split_by_line(yl)
                    self.xls.remove(xl)
                    self.yls.remove(yl)
                    self.xls.add(pxl)
                    self.xls.add(new_xl)
                    self.yls.add(pyl)
                    self.yls.add(new_yl)
                    # if pxl.prl and pxl.nrl and pxl.prl.prl and pxl.prl.prl is pxl.nrl.pll:
                    #     print('Create box.')
                    #     self.boxes.append(Box(pxl, pxl.prl.prl, pxl.prl, pxl.nrl))

                    sorted_xls[xi] = new_xl
                    yl = new_yl


    # def make_boxes(self, xl:XLine) -> Optional['Box']:
    #     """ Refresh the side boxes (if exists) """
    #     # top box (xl.lb)
    #     if xl.pll and xl.nll and xl.pll.prl == xl.nll.pll:
    #         Box.from_lines(xl.pll.prl, xl, xl.pll, xl.nll)
    #     # bottom box (l.rb)
    #     if xl.prl and xl.nrl and xl.prl.nrl == xl.nrl.nll:
    #         Box.from_lines(xl, xl.prl.nrl, xl.prl, xl.nrl)

def find_boxes(lines:Iterable[Line]):
    line_set:Set[Line] = set()
    for l in lines:
        line_set.add(l)
        line_set.add(l.rev)

    searching_lines:List[Line] = []
    boxes_lines:List[List[Line]] = []

    print(line_set)

    def search(l):
        nonlocal searching_lines
        
        print('search', l)

        if l in searching_lines:
            print('search end (success)')
            boxes_lines.append(searching_lines)
            searching_lines = []
            return True

        if not l in line_set:
            print('already searched.')
            return False

        searching_lines.append(l)
        line_set.discard(l)

        if l.toll and (r := search(l.toll)):
            return r
            
        if l.tonl and (r := search(l.tonl)):
            return r

        if l.torl and (r := search(l.torl)):
            return r
        # if not r and l.nrl:
        #     r = search(to_reversed[l.nrl])

        searching_lines.pop()
        return False


    while line_set:
        print('new search ...')
        search(next(iter(line_set)))
        searching_lines = []

    boxes:List[Box] = []
    for lines in boxes_lines:
        tl = bl = ll = rl = None
        for line in lines:
            if isinstance(line, XLine):
                bl = line
            elif isinstance(line, YLine):
                rl = line
            elif isinstance(line, ReversedXLine):
                tl = line.xl
            elif isinstance(line, ReversedYLine):
                ll = line.yl
        if tl and bl and ll and rl:
            # if tl < bl:
            #     tl, bl = bl, tl
            # if rl < ll:
            #     rl, ll = ll, rl
            if tl >= bl and rl >= ll:
                boxes.append(Box(tl, bl, ll, rl))

    return boxes
