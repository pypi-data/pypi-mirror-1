#!/usr/bin/env python
# -*- coding: utf-8 -*-
from grun import grun
class G(object):
    def t1(self): return 1
    def t2(self,a):
        """ press OK"""
        return a

    @staticmethod
    def t3(a):
        "press ok"
        return a

    @grun
    def t4(self,a):
        """ press OK"""
        return a


if __name__ == "__main__":
    grun.autotest=True
    g=G()
    assert grun(g.t1)() == 1
    assert grun(g.t2)("ok") == "ok"
    assert grun(G.t3)("ok")=="ok"
    assert g.t4("ok")=="ok"
    #~ assert grun(g.t4)("ok")=="ok"        # DON'T WORK (decorator eat the instance ?!) but will be corrected in the future
