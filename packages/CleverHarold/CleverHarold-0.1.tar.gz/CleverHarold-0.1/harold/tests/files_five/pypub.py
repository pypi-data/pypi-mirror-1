#!/usr/bin/env python

"""

a - no args - def X()
b - kwd args - def X(x=1) 
c - extra args - def X(*v)
d - extra args kwd args - def X(x=1, *v)
e - pos args - def X(x)
f - pos args kwd args - def X(x, y=2)
g - pos args extra args - def X(x, *v)
h - pos args extra args kwd args - def X(x, *v, y=2)

"""

class a_base:
    expose = ['meth']
    def __init__(self):
        pass
    
class a_a(a_base):
    def meth(self):
        pass

class a_b(a_base):
    def meth(self, x=1):
        return x

class a_c(a_base):
    def meth(self, *v):
        return v

class a_d(a_base):
    def meth(self, x=1, *v):
        return x, v

class a_e(a_base):
    def meth(self, x, y):
        return x, y

class a_f(a_base):
    def meth(self, x, y=0):
        return x, y

class a_g(a_base):
    def meth(self, x, *v):
        return x, v

class a_h(a_base):
    def meth(self, x, y=0, *v):
        return x, y, v


class b_base:
    expose = ['meth']
    def __init__(self, p):
        self.p = p
    
class b_a(b_base):
    def meth(self):
        return self.p

class b_b(b_base):
    def meth(self, x=0):
        return self.p, x

class b_c(b_base):
    def meth(self, *v):
        return self.p, v

class b_d(b_base):
    def meth(self, x=1, *v):
        return x, v

class b_e(b_base):
    def meth(self, x, y):
        return x, y

class b_f(b_base):
    def meth(self, x, y=0):
        return x, y

class b_g(b_base):
    def meth(self, x, *v):
        return x, v

class b_h(b_base):
    def meth(self, x, y=0, *v):
        return x, y, v

