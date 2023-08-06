import re
import lpo

base = """
is(c=X3, s=X2);
isa(c=X2, e=X1)
-->
isa(c=X3, e=X1).

is(c=X2, s=X1);
is(c=X3, s=X2)
-->
is(c=X3, s=X1)
"""

# isa(e=prop(s=X1, v=X2, t=X3), c=fact)
# -->
# isa(e=X1,c=name);
# isa(e=X2,c=verb);
# isa(e=X3,c=number)


base = re.sub(r'\s+', r'', base)
bss = base.split('.')
for base in bss:
    lpo.tell(base)

class _KnowledgeBase(object):

    @classmethod
    def tell(cls, ob):
        s = isinstance(ob, basestring) and ob or repr(ob)
        if getattr(ob, 'addable', False) or isinstance(ob, basestring):
            lpo.tell(s)
        print s

    @classmethod
    def delete(cls, ob):
        s = isinstance(ob, str) and ob or repr(ob)
        if getattr(ob, 'addable', False) or isinstance(ob, str):
            lpo.delete(s)
        return s

    @classmethod
    def ask(cls, ob):
        return lpo.ask(repr(ob))

    @classmethod
    def extend(cls):
        return lpo.extend()

KB = _KnowledgeBase()

class Number(object):
    mods = {}
    def __init__(self, name, a1=None, a2=None):
        self.name = name
        try:
            int(name)
        except ValueError:
            self.a1 = a1
            self.a2 = a2
    def __str__(self):
        try:
            return int(self.name)
        except ValueError:
            args = (self.a1 is not None and self.a2 is not None) and \
                         '(a1=%s,a2=%s)' % (self.a1,self.a2) or ''
            return '%s%s' % (self.name, args)

class MetaName(type):
    def __init__(cls, classname, bases, newdict):
        for base in bases:
            if base is not object:
                KB.tell('is(s=%s,c=%s)' % (classname.lower(),
                                           base.__name__.lower()))

class Name(object):
    __metaclass__ = MetaName
    addable = True
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'isa(e=%s,c=%s)' % (self.name,
                                  self.__class__.__name__.lower())
    def __str__(self):
        return self.name

class MetaVerb(type):
    def __init__(cls, classname, bases, newdict):
        if classname != 'Verb':
            mods = []
            cons = []
            var = 3
            for mod, c in cls.advs.items():
                mods.append('%s=X%d' % (mod, var))
                cons.append('isa(e=X%d,c=%s)' % (var, c.__name__.lower()))
                var += 1
            mods = ','.join(mods)
            cons = ';\n'.join(cons)
            if mods:
                mods = '(%s)' % mods
                cons = ';\n%s' % cons
            KB.tell('''isa(e=prop(s=X1,v=%s%s,t=X2),c=fact)
-->
isa(e=X1,c=%s)%s''' % \
            (cls.__name__.lower(),
            mods,
            cls.subject.__name__.lower(),
            cons))


class Verb(object):
    __metaclass__ = MetaVerb
    addable = True
    subject = Name
    advs = {}
    def __init__(self, **kwargs):
        for k, v in self.advs.items():
            if isinstance(kwargs[k], v):
                setattr(self, k, kwargs[k])
            else:
                raise "very bad indeed"
    def __str__(self):
        mods = []
        for k, v in self.advs.items():
            mods.append('%s=%s' % (k, str(getattr(self, k))))
        mods = ','.join(mods)
        if mods:
            mods = '(%s)' % mods
        return '%s%s' % (self.__class__.__name__.lower(), mods)

class Prop(object):
    addable = True
    def __init__(self, s, v, t):
        self.s, self.v, self.t = s, v, t
    def __repr__(self):
        return 'isa(e=prop(s=%s,v=%s,t=%s),c=fact)' % \
                            (str(self.s), str(self.v), str(self.t))
    __str__ = __repr__

class Rule(object):
    addable = True
    def __init__(self, prems, cons):
        self.prems = prems
        self.cons = cons
    def __repr__(self):
        prems = ';\n'.join([repr(prem) for prem in self.prems])
        cons = ';\n'.join([repr(con) for con in self.cons])
        return '%s\n-->\n%s' % (prems, cons)
    __str__ = __repr__
