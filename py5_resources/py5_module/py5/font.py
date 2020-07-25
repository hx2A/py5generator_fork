# -*- coding: utf-8 -*-
# *** FORMAT PARAMS ***
import functools
from typing import overload, List  # noqa

import jpype

from .methods import Py5Exception  # noqa
from .shape import Py5Shape, _return_py5shape  # noqa


py5font_class_members_code = None  # DELETE


def _return_py5font(f):
    @functools.wraps(f)
    def decorated(self_, *args):
        return Py5Font(f(self_, *args))

    return decorated


class Py5Font:

    _cls = jpype.JClass('processing.core.PFont')
    CHARSET = _cls.CHARSET

    def __init__(self, pfont):
        self._instance = pfont


{py5font_class_members_code}
