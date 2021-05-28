""" Test gridict.line module """

from itertools import chain

import pytest

from gridict.line import Grid, XLine, YLine, find_boxes


def test_gridict_line():
    """ Test girdict.line """

    grid = Grid([
        XLine(bx=2, ex=6, y=1),
        XLine(bx=1, ex=7, y=3.2),
        XLine(bx=1, ex=7, y=5),
    ],[
        YLine(x=3, by=-1, ey=6),
        YLine(x=4.1, by=0, ey=9),
        YLine(x=5.3, by=0, ey=8),
    ])

    boxes = find_boxes(chain(grid.xls, grid.yls))
    assert set((box.bx, box.by, box.ex, box.ey) for box in boxes) == {
        (3.0, 1.0, 4.1, 3.2),
        (4.1, 1.0, 5.3, 3.2),
        (3.0, 3.2, 4.1, 5.0),
        (4.1, 3.2, 5.3, 5.0),
    }
