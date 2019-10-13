from fractions import Fraction

class Accidental(object):
    '''
    Musical Pitch Accidental.
    '''

    _pool = None

    @property
    def name(self):
        return ['natural',
                'sharp',
                'double sharp',
                'double flat',
                'flat'][self.alternation]

    @property
    def alternation(self):
        return self._alter


    @property
    def symbol(self):
        return ['n','#','x','bb','b'][self.alternation]



    def __new__(cls,alter):

        if cls._pool is None:

            cls._pool = []

            for i in range(5):
                cls._pool.append(object.__new__(Accidental))
                cls._pool[i]._alter = [0,1,2,-2,-1][i]


        return cls._pool[alter]



    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self,other):
        if other is None:
            return self.alternation == 0
        elif hasattr(other,'alternation'):
            return self.alternation == other.alternation
        else:
            return NotImplemented

    def __sub__(self,other):
        return self.__truediv__(other)

    def __truediv__(self,other):
        from cmat.syntax import Construct
        return Construct(self,other).conclude()



class PitchClass(object):
    '''
    Musical Pitch Class.
    '''
    _pool = None

    @property
    def degree(self):
        return self._degree + 1

    @property
    def accidental(self):
        return self._acc

    @property
    def alternation(self):
        return 0 if self.accidental is None else self.accidental.alternation

    @property
    def letter(self):
        return 'CDEFGAB'[self._degree]

    @property
    def chromatic(self):
        p = [0,2,4,5,7,9,11][self._degree]
        return p if self.accidental is None else p + self.accidental.alternation

    @property
    def PIN(self):
        return self.chromatic % 12

    @property
    def enharmonics(self):

        en = []

        for p in PitchClass.all:
            if p.PIN == self.PIN and p is not self:
                en.append(p)

        return en
                

    def __new__(cls,degree,acc=None):

        from cmat.quality import double

        degs = [0,1,2,3,4,5,6]
        accs = [double_flat,flat,natural,sharp,double_sharp,None]

        if cls._pool is None:

            cls._pool = []
            cls.all   = set()
            for d in range(len(degs)):
                cls._pool.append([])
                for a in range(len(accs)):
                    cls._pool[d].append(object.__new__(PitchClass))
                    cls._pool[d][a]._degree = d
                    cls._pool[d][a]._acc = accs[a]

                    if accs[a] is not natural:
                        cls.all.add(cls._pool[d][a])

        acc_idx = 5 if acc is None else acc.alternation + 2
        return cls._pool[degree-1][acc_idx]

    def __str__(self):
        if self.accidental is None:
            return self.letter
        else:
            return self.letter + self.accidental.symbol

    def __repr__(self):
        return str(self)

    def __eq__(self,other):
        if hasattr(other,'PIN'):
            return self.PIN == other.PIN
        else:
            return NotImplemented

    def __hash__(self):
        return hash(str(self))

    def __add__(self,other):
        if hasattr(other,'steps') and hasattr(other,'semitones'):
            degree = self._degree
            steps  = other.steps-1 if other.upward else other.steps+1
            degree = (degree + steps) % 7
            chroma = (self.chromatic + other.semitones) % 12

            degree += 1
            for p in PitchClass.all:
                if p.degree == degree and p.PIN == chroma:
                    return p
            else:
                raise ValueError('No proper representation found.') 

        else:
            return NotImplemented

    def __sub__(self,other):
        if hasattr(other,'degree') and hasattr(other,'accidental'):
            st = other.degree - self.degree
            sm = other.chromatic - self.chromatic
            if sm < 0:
                sm += 12
                st += 7
            return Interval(st+1,sm)
        elif hasattr(other,'steps') and hasattr(other,'semitones'):
            return self.__add__(-other)
        else:
            return self.__truediv__(other)

    def __truediv__(self,other):
        from cmat.syntax import Construct
        return Construct(self,other).conclude()



class Pitch(PitchClass):
    '''
    Musical Pitch
    '''

    _pool = None

    @property
    def octave(self):
        return self._oct

    @property
    def frequency(self):
        return 2**((self.MIDI-69)/12)*440

    @property
    def MIDI(self):
        return self.chromatic + (self.octave+1) * 12

    @property
    def enharmonics(self):
        enharms = super().enharmonics
        assumed = [Pitch(p.degree,self.octave,p.accidental) for p in enharms]
        oct_dif = [int((a.MIDI-self.MIDI)/12) for a in assumed]
        octs    = [a.octave-d for a,d in zip(assumed,oct_dif)]
        enharms = [Pitch(p.degree,o,p.accidental) for p,o in zip(enharms,octs)]
        return [p for p in enharms if p is not self]

    @property
    def overtones(self):
        overtones     = (Interval(1, 0 ),
                         Interval(8, 12),
                         Interval(12,19),
                         Interval(15,24),
                         Interval(17,28),
                         Interval(19,31),
                         Interval(21,34),
                         Interval(22,36),
                         Interval(23,38),
                         Interval(24,40),
                         Interval(25,42),
                         Interval(26,43),
                         Interval(27,45),
                         Interval(28,46),
                         Interval(28,47),
                         Interval(29,48))

        return [self + tone for tone in overtones]


    def __new__(cls,degree,oct,acc=None):

        from cmat.quality import double

        degs = [0,1,2,3,4,5,6]
        octs = [0,1,2,3,4,5,6,7,8,9]
        accs = [double_flat,flat,natural,sharp,double_sharp,None]

        if Pitch._pool is None:
            Pitch._pool = []
            Pitch.all   = set()
            for o in range(len(octs)):
                Pitch._pool.append([])
                for d in range(len(degs)):
                    Pitch._pool[o].append([])
                    for a in range(len(accs)):
                        Pitch._pool[o][d].append(object.__new__(Pitch))
                        Pitch._pool[o][d][a]._degree = d
                        Pitch._pool[o][d][a]._oct = o
                        Pitch._pool[o][d][a]._acc = accs[a]

                        if accs[a] is not natural:
                            Pitch.all.add(Pitch._pool[o][d][a])


        acc_idx = 5 if acc is None else acc.alternation + 2
        return Pitch._pool[oct][degree-1][acc_idx]

    def __str__(self):
        return super().__str__() + str(self.octave)


    def __repr__(self):
        return str(self)

    def __eq__(self,other):
        if hasattr(other,'MIDI'):
            return self.MIDI == other.MIDI
        else:
            return NotImplemented

    def __hash__(self):
        return hash(str(self))

    def __gt__(self,other):
        if hasattr(other,'MIDI'):
            return self.MIDI > other.MIDI
        else:
            return NotImplemented

    def __ge__(self,other):
        if hasattr(other,'MIDI'):
            return self.MIDI >= other.MIDI
        else:
            return NotImplemented

    def __lt__(self,other):
        if hasattr(other,'MIDI'):
            return self.MIDI < other.MIDI
        else:
            return NotImplemented

    def __le__(self,other):
        if hasattr(other,'MIDI'):
            return self.MIDI <= other.MIDI
        else:
            return NotImplemented

    def __add__(self,other):
        if hasattr(other,'steps') and hasattr(other,'semitones'):
            pc  = super().__add__(other)
            oct = int((self.MIDI+other.semitones-pc.alternation)/12-1)
            return Pitch(pc.degree,oct,pc.accidental)
        else:
            return NotImplemented

    def __sub__(self,other):
        if hasattr(other,'degree') and hasattr(other,'MIDI'):
            s  = (self.octave-other.octave) * 7 + (self.degree - other.degree)
            s += -1 if s < 0 else 1
            sm =  self.MIDI-other.MIDI
            return Interval(s,sm)
        elif hasattr(other,'steps') and hasattr(other,'semitones'):
            return self.__add__(-other)
        else:
            return self.__truediv__(other)

    def __truediv__(self,other):
        from cmat.syntax import Construct
        return Construct(self,other).conclude()



class Interval(object):
    '''
    Musical Interval
    '''

    _pool = None

    @property
    def steps(self):
        return self._steps

    @property
    def semitones(self):
        return self._semitones

    @property
    def name(self):

        steps = abs(self._steps) - 1

        if steps > 13:
            if steps % 7 == 0:
                steps  = 7
            else:
                steps %= 7
            prefix  = 'compound'
        else:
            prefix  = None

        name = ['unison',
                'second',
                'third',
                'fourth',
                'fifth',
                'sixth',
                'seventh',
                'octave',
                'nineth',
                'tenth',
                'eleventh',
                'twelfth',
                'thirteenth',
                'fourteenth'][steps]

        if prefix is not None:
            name = ' '.join([prefix,name])

        return name

    @property
    def quality(self):

        from cmat.quality import double, triple, quadruple
        from cmat.quality import perfect, major, minor, augmented, diminished

        if self._semitones is None:
            return None

        steps,semitones = self.steps,self.semitones

        if self.upward:
            steps -= 1
        else:
            steps =  -steps - 1
            semitones = -semitones

        if steps > 6 and steps %7 == 0:
            while steps > 7:
                steps -= 7
                semitones -= 12

        elif steps > 6:
            while steps > 6:
                steps -= 7
                semitones -= 12

        dev = semitones - [0,2,4,5,7,9,11,12][steps]

        if steps in [0,3,4,7]:
            if -5 < dev < 5:
                quality = [perfect,
                           augmented,
                           double/augmented,
                           triple/augmented,
                           quadruple/augmented,
                           quadruple/diminished,
                           triple/diminished,
                           double/diminished,
                           diminished][dev]
            else:
                raise ValueError
        else:
            if -6 < dev < 5:
                quality = [major,
                           augmented,
                           double/augmented,
                           triple/augmented,
                           quadruple/augmented,
                           quadruple/diminished,
                           triple/diminished,
                           double/diminished,
                           diminished,
                           minor][dev]
            else:
                raise ValueError

        return quality

    @property
    def upward(self):
        return True if self.steps > 0 else False

    @property
    def compound(self):
        return True if abs(self.steps) > 8 else False

    @property
    def inversion(self):
        f = 1 if self.upward else -1

        steps = self.steps * f
        semit = self.semitones * f

        while steps > 8 or semit > 12:
            steps -= 7
            semit -= 12

        steps = (9 - steps) * f
        semit = (12 - semit) * f

        return Interval(steps,semit)

    def __new__(cls,steps,semitones=None):

        template = {1:[None,-2,-1,0,1,2],
                    2:[None,-1,0,1,2,3,4],
                    3:[None,1,2,3,4,5,6],
                    4:[None,3,4,5,6,7],
                    5:[None,5,6,7,8,9],
                    6:[None,6,7,8,9,10,11],
                    7:[None,8,9,10,11,12,13],
                    8:[None,10,11,12,13,14],
                    9:[None,11,12,13,14,15,16],
                   10:[None,13,14,15,16,17,18],
                   11:[None,15,16,17,18,19],
                   12:[None,17,18,19,20,21],
                   13:[None,18,19,20,21,22,23],
                   14:[None,20,21,22,23,24,25],
                   -1:[None,2,1,0,-1,-2],
                   -2:[None,0,-1,-2,-3,-4],
                   -3:[None,-1,-2,-3,-4,-5,-6],
                   -4:[None,-3,-4,-5,-6,-7],
                   -5:[None,-5,-6,-7,-8,-9],
                   -6:[None,-6,-7,-8,-9,-10,-11],
                   -7:[None,-8,-9,-10,-11,-12,-13],
                   -8:[None,-10,-11,-12,-13,-14],
                   -9:[None,-11,-12,-13,-14,-15,-16],
                  -10:[None,-13,-14,-15,-16,-17,-18],
                  -11:[None,-15,-16,-17,-18,-19],
                  -12:[None,-17,-18,-19,-20,-21],
                  -13:[None,-18,-19,-20,-21,-22,-23],
                  -14:[None,-20,-21,-22,-23,-24,-25]}

        if Interval._pool is None:

            Interval._pool = {}

            for s in template.keys():
                Interval._pool[s] = {}
                for t in template[s]:
                    Interval._pool[s][t] = object.__new__(Interval)
                    Interval._pool[s][t]._steps = s
                    Interval._pool[s][t]._semitones = t

        try:
            i = Interval._pool[steps][semitones]
        except KeyError:
            i = object.__new__(Interval)
            i._steps = steps
            i._semitones = semitones

        return i

    def __str__(self):

        if self.semitones is None:
            return self.name

        name,quality = self.name,str(self.quality)

        if name.startswith('compound'):
            return name.replace(' ',quality.center(len(quality)+2))
        else:
            return ' '.join([quality,name])

    def __repr__(self):
        return str(self)

    def __eq__(self,other):
        if hasattr(other,'steps') and hasattr(other,'semitones'):
            if self.semitones is None or other.semitones is None:
                return False 
            else:
                return abs(self.semitones) == abs(other.semitones)
        else:
            return NotImplemented

    def __hash__(self):
        return hash(str(self))

    def __gt__(self,other):
        if hasattr(other,'steps') and hasattr(other,'semitones'):
            if self.semitones is None or other.semitones is None:
                return False 
            else:
                return abs(self.semitones) > abs(other.semitones)
        else:
            return NotImplemented

    def __ge__(self,other):
        return self>other or self==other

    def __lt__(self,other):
        if hasattr(other,'steps') and hasattr(other,'semitones'):
            if self.semitones is None or other.semitones is None:
                return False
            else:
                return abs(self.semitones) < abs(other.semitones)
        else:
            return NotImplemented

    def __le__(self,other):
        return self<other or self==other

    def __add__(self,other):
        if hasattr(other,'steps') and hasattr(other,'semitones'):
            if self.semitones is None or other.semitones is None:
                raise ValueError('indefinite interval.')
            else:
                s1 = self.steps-1 if self.upward else self.steps+1
                s2 = other.steps-1 if other.upward else other.steps+1
                st = s1 + s2
                sm = self.semitones + other.semitones

                if st > 0:
                    st+=1
                elif st < 0:
                    st-=1
                elif sm > 0:
                    st+=1
                elif sm < 0:
                    st-=1
                else:
                    st+=1
                return Interval(st,sm)
                    
        else:
            return NotImplemented

    def __sub__(self,other):
        if hasattr(other,'steps') and hasattr(other,'semitones'):
            return self.__add__(-other)
        else:
            return self.__truediv__(other)

    def __truediv__(self,other):
        from cmat.syntax import Construct
        return Construct(self,other).conclude()

    def __neg__(self):
        if self.semitones is None:
            return Interval(-self.steps)
        else:
            return Interval(-self.steps,-self.semitones)

class Triad(object):
    pass

class Quarters(Fraction):
    def __new__(cls,value,denominator=None):

        self = super(Quarters,cls).__new__(cls)
        frac = Fraction(value).limit_denominator()
        self._numerator,self._denominator = frac.numerator,frac.denominator
        return self

    def __str__(self):
        return str(self.numerator/self.denominator)

    def __repr__(self):
        return str(self)

    def __add__(a,b):
        f = Fraction.__add__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __radd__(a,b):
        f = Fraction.__radd__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __sub__(a,b):
        f = Fraction.__sub__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __rsub__(a,b):
        f = Fraction.__rsub__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __mul__(a,b):
        f = Fraction.__mul__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __rmul__(a,b):
        f = Fraction.__rmul__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __truediv__(a,b):
        f = Fraction.__truediv__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __rtruediv__(a,b):
        f = Fraction.__rtruediv__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __abs__(a):
        f = Fraction.__abs__(a)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __pos__(a):
        f = Fraction.__pos__(a)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __neg__(a):
        f = Fraction.__neg__(a)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __pow__(a,b):
        f = Fraction.__pow__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __rpow__(a,b):
        f = Fraction.__rpow__(a,b)
        return NotImplemented if f is NotImplemented else Quarters(f)

    def __round__(self,ndigits=None):
        f = Fraction.__round__(self,ndigits)
        return NotImplemented if f is NotImplemented else Quarters(f)


class NoteType(object):
    '''
    Note type in Quarter Length
    '''

    _pool = None

    @property
    def name(self):

        from math import log

        i = int(log(4/self.quarters,2))
        return ['whole','half','quarter','eighth',
                'sixteenth','thirty second','sixty fourth'][i]

    @property
    def quarters(self):
        return self._quarters

    def __new__(cls,v):

        from numbers import Real

        if not isinstance(v,Real):
            raise TypeError('initialize with non-numeric.')
        elif v < 1/16 or v > 4:
            raise ValueError('value is out of range.')

        if NoteType._pool is None:
            NoteType._pool = {}
            for d in [1/16,1/8,1/4,1/2,1,2,4]:
                q = Quarters(d)
                NoteType._pool[q] = object.__new__(NoteType)
                NoteType._pool[q]._quarters = q

        try:
            return NoteType._pool[Quarters(v)]
        except KeyError:
           raise ValueError('invalid note duration.')

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self,other):
        if hasattr(other,'quarters'):
            return self.quarters == other.quarters
        else:
            return self.quarters == other

    def __hash__(self):
        return hash(self.quarters)

    def __gt__(self,other):
        if hasattr(other,'quarters'):
            return self.quarters > other.quarters
        else:
            return self.quarters > other

    def __lt__(self,other):
        if hasattr(other,'quarters'):
            return self.quarters < other.quarters
        else:
            return self.quarters < other

    def __ge__(self,other):
        return self > other or self == other

    def __le__(self,other):
        return self < other or self <= other


    def __add__(self,other):
        if hasattr(other,'quarters'):
            return self.quarters + other.quarters
        else:
            return self.quarters + other

    def __radd__(self,other):
        return self + other

    def __sub__(self,other):

        from numbers import Real

        if hasattr(other,'quarters'):
            return self.quarters - other.quarters
        elif isinstance(other,Real):
            return self.quarters - other
        else:
            return self.__truediv__(other)

    def __rsub__(self,other):
        return -self + other

    def __mul__(self,other):
        if hasattr(other,'quarters'):
            return self.NotImplemented
        else:
            return self.quarters * other

    def __rmul__(self,other):
        return NotImplemented
        #return self * other

    def __truediv__(self,other):

        from numbers import Real

        from cmat.syntax import Construct
        if hasattr(other,'quarters'):
            return float(self.quarters / other.quarters)
        elif isinstance(other,Real):
            return self.quarters / other
        else:
            return Construct(self,other).conclude()

    def __rtruediv__(self,other):
        if hasattr(other,'quarters'):
            return float(other.quarters / self.quarters)
        else:
            return float(other / self.quarters)

    def __floordiv__(self,other):
        if hasattr(other,'quarters'):
            return float(self.quarters // other.quarters)
        else:
            return float(self.quarters // other)

    def __rfloordiv__(self,other):
        if hasattr(other,'quarters'):
            return float(other.quarters // self.quarters)
        else:
            return float(other // self.quarters)



class Tuplet(object):

    _pool = None

    @property
    def name(self):
        try:
            return {(2 ,3):'duplet',
                    (3 ,2):'triplet',
                    (4 ,3):'quadruplet',
                    (5 ,4):'quintuplet',
                    (6 ,4):'sextuplet',
                    (7 ,4):'septuplet',
                    (8 ,6):'octuplet',
                    (9 ,8):'nonuplet',
                    (10,8):'decuplet',
                    (11,8):'undecuplet',
                    (12,8):'dodecuplet',
                    (13,8):'tredecuplet'}[(self.actual,self.normal)]
        except KeyError:
            return 'T[{}:{}]'.format(self.actual,self.normal)

    @property
    def normal(self):
        return self._norm

    @property
    def actual(self):
        return self._act

    @property
    def ratio(self):
        return self.normal / self.actual

    def __new__(cls,actual,normal=None):

        template = {2:3,
                    3:2,
                    4:3,
                    5:4,
                    6:4,
                    7:4,
                    8:6,
                    9:8,
                    10:8,
                    11:8,
                    12:8,
                    13:8}

        if normal is None:
            try:
                normal = {2:3,3:2,4:3,5:4,6:4,7:4,8:6,
                          9:8,10:8,11:8,12:8,13:8}[actual]
            except KeyError:
                raise ValueError('please specifies both parameter.')

        if Tuplet._pool is None:
            Tuplet._pool = {}
            for a,n in template.items():
                Tuplet._pool[(a,n)] = object.__new__(Tuplet)
                Tuplet._pool[(a,n)]._act  = a
                Tuplet._pool[(a,n)]._norm = n
        else:
            try:
                return Tuplet._pool[actual,normal]
            except KeyError:
                self = object.__new__(Tuplet)
                self._act,self._norm = actual,normal
                return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __sub__(self,other):
        return self.__truediv__(other)

    def __truediv__(self,other):
        from cmat.syntax import Construct
        return Construct(self,other).conclude()



class Duration(object):
    @property
    def quarters(self):
        ratio = 1 + (2**self.dots-1)/2**self.dots
        if self.tuplet is not None:
            ratio *= self.tuplet.ratio

        return self.base * ratio

    @property
    def copy(self):
        return Duration(self.base,self.dots,self.tuplet)

    def __init__(self,base,dots=0,tuplet=None):
        self.base = base
        self.dots = dots
        self.tuplet = tuplet

    def __str__(self):
        t = self.base.name
        d = [None,'dotted','double dotted','triple dotted'][self.dots]
        u = None if self.tuplet is None else self.tuplet.name

        return ' '.join([p for p in [d,t,u] if p is not None])

    def __repr__(self):
        return str(self)

    def __eq__(self,other):
        if hasattr(other,'quarters'):
            return self.quarters == other.quarters
        else:
            return self.quarters == other

    def __gt__(self,other):
        if hasattr(other,'quarters'):
            return self.quarters > other.quarters
        else:
            return self.quarters > other

    def __lt__(self,other):
        if hasattr(other,'quarters'):
            return self.quarters < other.quarters
        else:
            return self.quarters < other

    def __ge__(self,other):
        return self > other or self == other

    def __le__(self,other):
        return self < other or self <= other


    def __add__(self,other):
        if hasattr(other,'quarters'):
            return self.quarters + other.quarters
        else:
            return self.quarters + other

    def __radd__(self,other):
        return self + other

    def __sub__(self,other):

        from numbers import Real

        if hasattr(other,'quarters'):
            return self.quarters - other.quarters
        elif isinstance(other,Real):
            return self.quarters - other
        else:
            return self.__truediv__(other)

    def __rsub__(self,other):
        return -self + other

    def __mul__(self,other):
        if hasattr(other,'quarters'):
            return self.NotImplemented
        else:
            return self.quarters * other

    def __rmul__(self,other):
        return NotImplemented

    def __truediv__(self,other):

        from numbers import Real
        from cmat.syntax import Construct

        if hasattr(other,'quarters'):
            return float(self.quarters / other.quarters)
        elif isinstance(other,Real):
            return self.quarters / other
        else:
            return Construct(self,other).conclude()

    def __rtruediv__(self,other):
        if hasattr(other,'quarters'):
            return float(other.quarters / self.quarters)
        else:
            return float(other / self.quarters)

    def __floordiv__(self,other):
        if hasattr(other,'quarters'):
            return float(self.quarters // other.quarters)
        else:
            return float(self.quarters // other)

    def __rfloordiv__(self,other):
        if hasattr(other,'quarters'):
            return float(other.quarters // self.quarters)
        else:
            return float(other // self.quarters)


class Key(object):
    pass



natural = Accidental(0)
sharp   = Accidental(1)
flat    = Accidental(-1)
double_sharp = Accidental(2)
double_flat  = Accidental(-2)

C    = PitchClass(1,None)
Cn   = PitchClass(1,natural)
Cs   = PitchClass(1,sharp)
Cx   = PitchClass(1,double_sharp)
Cb   = PitchClass(1,flat)
Cbb  = PitchClass(1,double_flat)

D    = PitchClass(2,None)
Dn   = PitchClass(2,natural)
Ds   = PitchClass(2,sharp)
Dx   = PitchClass(2,double_sharp)
Db   = PitchClass(2,flat)
Dbb  = PitchClass(2,double_flat)

E    = PitchClass(3,None)
En   = PitchClass(3,natural)
Es   = PitchClass(3,sharp)
Ex   = PitchClass(3,double_sharp)
Eb   = PitchClass(3,flat)
Ebb  = PitchClass(3,double_flat)

F    = PitchClass(4,None)
Fn   = PitchClass(4,natural)
Fs   = PitchClass(4,sharp)
Fx   = PitchClass(4,double_sharp)
Fb   = PitchClass(4,flat)
Fbb  = PitchClass(4,double_flat)

G    = PitchClass(5,None)
Gn   = PitchClass(5,natural)
Gs   = PitchClass(5,sharp)
Gx   = PitchClass(5,double_sharp)
Gb   = PitchClass(5,flat)
Gbb  = PitchClass(5,double_flat)

A    = PitchClass(6,None)
An   = PitchClass(6,natural)
As   = PitchClass(6,sharp)
Ax   = PitchClass(6,double_sharp)
Ab   = PitchClass(6,flat)
Abb  = PitchClass(6,double_flat)

B    = PitchClass(7,None)
Bn   = PitchClass(7,natural)
Bs   = PitchClass(7,sharp)
Bx   = PitchClass(7,double_sharp)
Bb   = PitchClass(7,flat)
Bbb  = PitchClass(7,double_flat)


