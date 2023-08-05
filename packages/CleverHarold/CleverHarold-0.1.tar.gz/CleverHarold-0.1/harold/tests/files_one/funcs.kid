<?python

def P():
    return 'P'

def Q(a):
    return 'Q %s' % (a, )

def R(a, b):
    return 'R %s %s' % (a, b)

def S(a, b=0):
    return 'S %s %s' % (a, b, )

def T(a, **c):
    return 'T %s %s' % (a, c)

def U(*b):
    return 'U %s' % (b, )

def V(a, *b):
    return 'V %s %s' % (a, b)

def W(a, *b, **c):
    return 'W %s %s %s' % (a, b, c)

for func in (P, Q, R, S, T, U, V, W):
    func.expose = True

?>
<html xmlns:py="http://purl.org/kid/ns#">

<div py:def="A()">ntf A</div>

<div py:def="E()">ntf E</div>

<div py:def="F(a, b)">ntf F ${a} ${b}</div>

<div py:def="G(a=0, b=0)">ntf G ${a} ${b}</div>

<div py:def="H(a, b=0)">ntf H ${a} ${b}</div>

<div py:def="I(a, b)">ntf I ${a} ${b}</div>

<div py:def="J(a, b)">ntf J ${a} ${b}</div>

<div py:def="K(a, b=0)">ntf K ${a} ${b}</div>


<div py:def="show_mapping(d)" py:strip="">
    <div py:for="k, v in d.items()" py:strip="">
    ${str(k)}:${str(v)}
    </div>
</div>


<div py:def="L(**kwds)">ntf L
    ${show_mapping(kwds)}
</div>


<div py:def="M(a, **kwds)">ntf M ${a} ${str(kwds)}
    ${a}
    ${show_mapping(kwds)}
</div>


<div py:def="N(a, b='', c='juice', **kwds)">ntf M ${a} ${str(kwds)}
    ${a}
    ${b}
    ${c}
    ${show_mapping(kwds)}
</div>


</html>
