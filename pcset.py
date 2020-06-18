
from collections import MutableSet
from collections import Iterable

from re import match



class P(MutableSet):

    @staticmethod
    def bybracket(self,arguments):
        '''
        This method will be assigned to bass class __getitem__ attribute.
        By doing so, now we can use bracket operator to initialize the set object.
        like:
             s = P[0,1,2,3]
        '''
        arg = list(arguments) if isinstance(arguments,tuple) else arguments

        if isinstance(arg,str):    # Forte number. P['5-Z18A']

            m = match('(\d{1,2})-Z?(\d{1,2})(A|B)?',arg)
            if m == None:
                return P()  # Incorrect number format, returning empty set.

            groups = m.groups()
            cardinality = groups[0]
            index = groups[1]
            variant = groups[2]
            variant = '' if variant == None else variant

            for entry in PRIME_FORM_TABLE:

                m = match('%s-Z?%s%s'%(cardinality,index,variant),entry[1])
                if m != None:
                    return P(entry[4])

            return P()      # Number not found, returning empty set.

        elif isinstance(arg,P):    # Construct from another pc set. P[another]
            return P(arg)

        elif isinstance(arg,list): # Construct from pc integer or note object list.
            return P(arg)

        else:       # Invalid argument type, returning empty set.
            return P()


    def __init__(self,pinlist=[]):

        self._pins = []

        for p in pinlist:
            self.add(p)

    def __iter__(self):
        return iter(self._pins)

    def __getitem__(self,index):
        return self._pins[index]

    def __len__(self):
        return len(self._pins)

    def __contains__(self,pitch):

        if isinstance(pitch,int):
            p = pitch
        elif isinstance(pitch,Note):
            p = pitch.pin
        else:
            return False

        p %= 12
        p = p+12 if p<0 else p  # pin can only be positive.

        return p in self._pins

    def __repr__(self):

        numbers = [str(n) for n in self._pins]
        string = 'P[%s]' % (','.join(numbers))
        return string

    def add(self,pitch):
        '''
        Add a pitch to pc set, the pitch can be a integer number or a Note object.

        add(C)      # C is a predefined Note object name
        add(0)      # Number will be modulo with 12 and invert if negative.
        '''
        if isinstance(pitch,int):
            p = pitch
        elif isinstance(pitch,Note):
            print('add note pin')
            p = pitch.pin
        else:
            return

        p %= 12
        p = 12+p if p<0 else p  # pin can only be positive.

        if p not in self._pins:
            self._pins.append(p)

    def discard(self,pitch):
        '''
        Remove a pitch from pc set, the pitch can be a integer number or a Note object.

        discard(C)      # C is a predefined Note object name
        discard(0)      # Number will be modulo with 12 and invert if negative.
        '''

        if isinstance(pitch,int):
            p = pitch
        elif isinstance(pitch,Note):
            p = pitch.pin
        else:
            return

        p %= 12
        p = p+12 if p<0 else p  # pin can only be positive.

        if p in self._pins:
            self._pins.remove(p)

    # properties
    cardinality = property(__len__)

    def _searching_name(self):
        '''
        Return the Forte name of the set
        '''

        for entry in PRIME_FORM_TABLE:
            if self._pins == entry[4]:
                return entry[1]
        return None
    name = property(_searching_name)

    def _searching_Z(self):
        '''
        Return the name of Z pair if exist.
        '''

        for entry in PRIME_FORM_TABLE:
            if self._pins == entry[4]:
                return entry[3]
        return None
    Zpair = property(_searching_Z)

    def _vector(self):
        '''
        Return interval class vector of the set.
        '''
        iccontent = []
        pins = sorted(self._pins)

        for i in range(len(pins)-1):
            for j in range(i+1,len(pins)):
                iccontent.append(pins[j] - pins[i])

        iccontent = [i if i<7 else 12-i for i in iccontent]

        vector = []
        for i in range(1,7):
            vector.append(iccontent.count(i))

        return tuple(vector)
    icvector = property(_vector)

    def _normal_form(self,method = 'Forte'):
        '''
        Return the normal form of the set.
        '''
        permutations = self.permutations
        candidates = []
        minimal = 12

        for p in permutations:              # Find out most compacted permutation.
            compactness = p[-1] - p[0]
            compactness += 12 if compactness<0 else 0

            if compactness < minimal:
                minimal = compactness
                candidates = [p]
            elif compactness == minimal:
                candidates.append(p)

        if len(candidates) == 1:
            return candidates[0]

        # Forte's method
        for i in range(1,len(candidates[0])):   # pack from left
            factors = []
            for p in candidates:                # caculate each distance
                distance = p[i] - p[0]
                distance += 12 if distance < 0 else 0
                factors.append(distance)

            minimal = min(factors)              # minimal distance
            candidates = [candidates[i] for i in range(len(candidates)) if factors[i] == minimal]
            if len(candidates) == 1:
                break

        # Rahn's method
#        for i in range(-2,-(len(candidates[0])-1),-1):  # pack from right
#            factors = []
#            for p in candidates:                # caculate each distance
#                distance = p[i] - p[0]
#                distance += 12 if distance < 0 else 0
#                factors.append(distance)

#            minimal = min(factors)              # minimal distance
#            candidates = [candidates[i] for i in range(len(candidates)) if factors[i] == minimal]
#            if len(candidates) == 1:
#                break

        return candidates[0]

    normal = property(_normal_form)


    def _prime_form(self,method = 'Forte'):
        '''
        Return the prime form of the set.
        '''
        normal_form = self._normal_form(method)
        prime_form = Tn(normal_form,-normal_form[0])
        return prime_form
    prime = property(_prime_form)

    def _inverse_prime(self,method = 'Forte'):
        '''
        Return the inversed prime form of the set.
        '''
        normal_form = T0I(self.prime).retrograde
        inverse_prime = Tn(normal_form,-normal_form[0])
        return inverse_prime
    inverseprime = property(_inverse_prime)

    def _inverse(self):
        '''
        Inverse around 0
        '''
        return T0I(self)
    inverse = property(_inverse)

    def _sorted(self):
        '''
        Return sorted set
        '''
        return P(sorted(self._pins))
    sorted = property(_sorted)

    def _retrograde(self):
        '''
        Return retrograded set
        '''
        pins = list(self._pins)
        pins.reverse()
        return P(pins)
    retrograde = property(_retrograde)

    def _complement(self):
        '''
        Return complement set
        '''
        c = P(range(12))
        for p in self:
            c.discard(p)
        return c
    complement = property(_complement)

    def _div(self):
        '''
        Directed interval vector of the set.
        '''
        div = []
        for i in range(len(self._pins)-1):
            di = self._pins[i+1] - self._pins[i]
            di += 12 if di<0 else 0
            div.append(di)

        di = self._pins[0] - self._pins[-1]
        di += 12 if di<0 else 0
        div.append(di)

        return div
    div = property(_div)

    def _permutations(self):
        '''
        Return a list contains all the possible permutations.
        '''
        permutations = []
        permutation = self.sorted
        for c in range(self.cardinality):

            permutations.append(P(permutation))
            permutation = permutation.rotate()

        return permutations

    permutations = property(_permutations)

    # methods
    def rotate(self,times=1):
        '''
        Return a pcset in which elements are shifted up 'times' space.
        '''
        pins = list(self._pins)

        times %=12
        times = times+12 if times<0 else times

        for i in range(times):
            p = pins.pop(0)
            pins.append(p)

        return P(pins)

    def issubset(self,other):
        '''
        Return whether the set is subset of other set, in transpositional context.
        '''
        for t in range(12):
            count = len(self & Tn(other,t))
            if count == self.cardinality:
                return True
        return False

    def issuperset(self,other):
        '''
        Return whether the set is superset of other set, in transpositional context.
        '''
        for t in range(12):
            count = len(self & Tn(other,t))
            if count == other.cardinality:
                return True
        return False

    def invariant(self,operation,*arguments):
        '''
        Return the invariant subset with the operation.
        If the operation need arguments, the first supply to operation will
        always the 'self', and the rest can be supplied in 'arguments'.
        For example:
            s.invariant(TnI,8) -> TnI(self,8)
        '''
        if len(arguments) > 0:
            intersection = self & operation(self,*arguments)
        else:
            intersection = self & operation(self)

        return intersection

    def subsets(self,cardinality = None):
        '''
        Return all subsets with specified cardinality. If cardinality is omit,
        return all the subsets.
        '''

        subsets = []
        if cardinality == None:
            for entry in PRIME_FORM_TABLE:
                if len(entry[4]) < self.cardinality:
                    if self.issuperset(P[entry[4]]):
                        subsets.append(P[entry[4]])
        else:
            for entry in PRIME_FORM_TABLE:
                if len(entry[4]) == cardinality:
                    if self.issuperset(P[entry[4]]):
                        subsets.append(P[entry[4]])
        return subsets

from cmat.score import Note
P.__class__.__getitem__ = P.bybracket

def Tn(pcset,offset):                # Standard Transposition operation.
    '''
    Standard Trasposition operation
    '''
    offset %= 12
    offset = offset+12 if offset<0 else offset # Offset must be positive.

    pins = [(p + offset)%12 for p in pcset]

    return P(pins)


def TnI(pcset,axis):               # Standard TnI operation, invert using 'axis' as axis.
    '''
    Standard TnI operation.
    '''
    axis %= 12
    axis = axis+12 if axis<0 else axis # Axis must be positive
    axis *= 2

    pins = [axis-p for p in pcset]
    pins = [p+12 if p<0 else p for p in pins]

    return P(pins)


def T0(pcset):
    return Tn(pcset,0)

def T1(pcset):
    return Tn(pcset,1)

def T2(pcset):
    return Tn(pcset,2)

def T3(pcset):
    return Tn(pcset,3)

def T4(pcset):
    return Tn(pcset,4)

def T5(pcset):
    return Tn(pcset,5)

def T6(pcset):
    return Tn(pcset,6)

def T7(pcset):
    return Tn(pcset,7)

def T8(pcset):
    return Tn(pcset,8)

def T9(pcset):
    return Tn(pcset,9)

def T10(pcset):
    return Tn(pcset,10)

def T11(pcset):
    return Tn(pcset,11)

def T0I(pcset):
    return TnI(pcset,0)

def T1I(pcset):
    return TnI(pcset,1)

def T2I(pcset):
    return TnI(pcset,2)

def T3I(pcset):
    return TnI(pcset,3)

def T4I(pcset):
    return TnI(pcset,4)

def T5I(pcset):
    return TnI(pcset,5)

def T6I(pcset):
    return TnI(pcset,6)

def T7I(pcset):
    return TnI(pcset,7)

def T8I(pcset):
    return TnI(pcset,8)

def T9I(pcset):
    return TnI(pcset,9)

def T10I(pcset):
    return TnI(pcset,10)

def T11I(pcset):
    return TnI(pcset,11)

def Rp(pcset1,pcset2):
    '''
    Return common subset if exist, otherwise empty list was returned.
    '''
    subs = pcset1.subsets(pcset1.cardinality-1)
    common = []
    for s in subs:
        if s.issubset(pcset2):
            common.append(s)

    return common

def R0(pcset1,pcset2):
    '''
    Minimal similarity
    Return True if Ro Relation existed between two sets, else False.
    '''
    if pcset1.cardinality != pcset2.cardinality:
        return False

    icv1 = pcset1.icvector
    icv2 = pcset2.icvector

    for i in range(6):
        if icv1[i] == icv2[i]:
            return False
    return True

def R1(pcset1, pcset2):
    '''
    Maximal similarity
    Return True if R1 Relation existed between tow sets, else False.
    '''

    if pcset1.cardinality != pcset2.cardinality:
        return False

    icv1 = pcset1.icvector
    icv2 = pcset2.icvector

    matchpairs = []

    for i in range(6):
        if icv1[i] == icv2[i]:
            matchpairs.append(True)
        else:
            matchpairs.append(False)

    matchcount = matchpairs.count(True)
    if matchcount < 4 or matchcount == 6:
        return False
    else:
        mismatching = []
        for i in range(6):
            if matchpairs[i] == False:
                mismatching.append(i)

        mmpair1 = [icv1[mismatching[0]],icv2[mismatching[0]]]
        mmpair2 = [icv1[mismatching[1]],icv2[mismatching[1]]]
        mmpair2.reverse()

        if mmpair1 == mmpair2:
            return True
        else:
            return False

def R2(pcset1, pcset2):
    '''
    Maximal similarity
    Return True if R1 Relation existed between tow sets, else False.
    '''

    if pcset1.cardinality != pcset2.cardinality:
        return False

    icv1 = pcset1.icvector
    icv2 = pcset2.icvector

    matchpairs = []

    for i in range(6):
        if icv1[i] == icv2[i]:
            matchpairs.append(True)
        else:
            matchpairs.append(False)

    matchcount = matchpairs.count(True)
    if matchcount < 4 or matchcount == 6:
        return False
    else:
        mismatching = []
        for i in range(6):
            if matchpairs[i] == False:
                mismatching.append(i)

        mmpair1 = [icv1[mismatching[0]],icv2[mismatching[0]]]
        mmpair2 = [icv1[mismatching[1]],icv2[mismatching[1]]]
        mmpair2.reverse()
        if mmpair1 == mmpair2:
            return False
        else:
            return True



# Quote from Larry Solomon's website
PRIME_FORM_TABLE = [
[  0,    '0-1',     None,         None,                             [],          (0,0,0,0,0,0),    'Null set'],

[  1,    '1-1',     None,         None,                            [0],          (0,0,0,0,0,0),    'Unison'],

[  2,    '2-1',     None,         None,                          [0,1],          (1,0,0,0,0,0),    'Semitone'],
[  3,    '2-2',     None,         None,                          [0,2],          (0,1,0,0,0,0),    'Whole-tone'],
[  4,    '2-3',     None,         None,                          [0,3],          (0,0,1,0,0,0),    'Minor Third'],
[  5,    '2-4',     None,         None,                          [0,4],          (0,0,0,1,0,0),    'Major Third'],
[  6,    '2-5',     None,         None,                          [0,5],          (0,0,0,0,1,0),    'Perfect Fourth'],
[  7,    '2-6',        6,         None,                          [0,6],          (0,0,0,0,0,1),    'Tritone'],

[  8,    '3-1',     None,         None,                        [0,1,2],          (2,1,0,0,0,0),    'BACH /Chromatic Trimirror'],
[  9,    '3-2A',    None,         None,                        [0,1,3],          (1,1,1,0,0,0),    'Phrygian Trichord'],
[ 10,    '3-2B',    None,         None,                        [0,2,3],          (1,1,1,0,0,0),    'Minor Trichord'],
[ 11,    '3-3A',    None,         None,                        [0,1,4],          (1,0,1,1,0,0),    'Major-minor Trichord.1'],
[ 12,    '3-3B',    None,         None,                        [0,3,4],          (1,0,1,1,0,0),    'Major-minor Trichord.2'],
[ 13,    '3-4A',    None,         None,                        [0,1,5],          (1,0,0,1,1,0),    'Incomplete Major-seventh Chord.1'],
[ 14,    '3-4B',    None,         None,                        [0,4,5],          (1,0,0,1,1,0),    'Incomplete Major-seventh Chord.2'],
[ 15,    '3-5A',    None,         None,                        [0,1,6],          (1,0,0,0,1,1),    'Rite chord.2, Tritone-fourth.1'],
[ 16,    '3-5B',    None,         None,                        [0,5,6],          (1,0,0,0,1,1),    'Rite chord.1, Tritone-fourth.2'],
[ 17,    '3-6',     None,         None,                        [0,2,4],          (0,2,0,1,0,0),    'Whole-tone Trichord'],
[ 18,    '3-7A',    None,         None,                        [0,2,5],          (0,1,1,0,1,0),    'Incomplete Minor-seventh Chord'],
[ 19,    '3-7B',    None,         None,                        [0,3,5],          (0,1,1,0,1,0),    'Incomplete Dominant-seventh Chord.2'],
[ 20,    '3-8A',    None,         None,                        [0,2,6],          (0,1,0,1,0,1),    'Incomplete Dominant-seventh Chord.1/Italian-sixth'],
[ 21,    '3-8B',    None,         None,                        [0,4,6],          (0,1,0,1,0,1),    'Incomplete Half-dim-seventh Chord'],
[ 22,    '3-9',     None,         None,                        [0,2,7],          (0,1,0,0,2,0),    'Quartal Trichord'],
[ 23,    '3-10',    None,         None,                        [0,3,6],          (0,0,2,0,0,1),    'Diminished Chord'],
[ 24,    '3-11A',   None,         None,                        [0,3,7],          (0,0,1,1,1,0),    'Minor Chord'],
[ 25,    '3-11B',   None,         None,                        [0,4,7],          (0,0,1,1,1,0),    'Major Chord'],
[ 26,    '3-12',       4,         None,                        [0,4,8],          (0,0,0,3,0,0),    'Augmented Chord'],

[ 27,    '4-1',     None,         None,                      [0,1,2,3],          (3,2,1,0,0,0),    'BACH /Chromatic Tetramirror'],
[ 28,    '4-2A',    None,         None,                      [0,1,2,4],          (2,2,1,1,0,0),    'Major-second Tetracluster.2'],
[ 29,    '4-2B',    None,         None,                      [0,2,3,4],          (2,2,1,1,0,0),    'Major-second Tetracluster.1'],
[ 30,    '4-3',     None,         None,                      [0,1,3,4],          (2,1,2,1,0,0),    'Alternating Tetramirror'],
[ 31,    '4-4A',    None,         None,                      [0,1,2,5],          (2,1,1,1,1,0),    'Minor Third Tetracluster.2'],
[ 32,    '4-4B',    None,         None,                      [0,3,4,5],          (2,1,1,1,1,0),    'Minor Third Tetracluster.1'],
[ 33,    '4-5A',    None,         None,                      [0,1,2,6],          (2,1,0,1,1,1),    'Major Third Tetracluster.2'],
[ 34,    '4-5B',    None,         None,                      [0,4,5,6],          (2,1,0,1,1,1),    'Major Third Tetracluster.1'],
[ 35,    '4-6',     None,         None,                      [0,1,2,7],          (2,1,0,0,2,1),    'Perfect Fourth Tetramirror'],
[ 36,    '4-7',     None,         None,                      [0,1,4,5],          (2,0,1,2,1,0),    'Arabian Tetramirror'],
[ 37,    '4-8',     None,         None,                      [0,1,5,6],          (2,0,0,1,2,1),    'Double Fourth Tetramirror'],
[ 38,    '4-9',        6,         None,                      [0,1,6,7],          (2,0,0,0,2,2),    'Double Tritone Tetramirror'],
[ 39,    '4-10',    None,         None,                      [0,2,3,5],          (1,2,2,0,1,0),    'Minor Tetramirror'],
[ 40,    '4-11A',   None,         None,                      [0,1,3,5],          (1,2,1,1,1,0),    'Phrygian Tetrachord'],
[ 41,    '4-11B',   None,         None,                      [0,2,4,5],          (1,2,1,1,1,0),    'Major Tetrachord'],
[ 42,    '4-12A',   None,         None,                      [0,2,3,6],          (1,1,2,1,0,1),    'Harmonic-minor Tetrachord'],
[ 43,    '4-12B',   None,         None,                      [0,3,4,6],          (1,1,2,1,0,1),    'Major-third Diminished Tetrachord'],
[ 44,    '4-13A',   None,         None,                      [0,1,3,6],          (1,1,2,0,1,1),    'Minor-second Diminished Tetrachord'],
[ 45,    '4-13B',   None,         None,                      [0,3,5,6],          (1,1,2,0,1,1),    'Perfect-fourth Diminished Tetrachord'],
[ 46,    '4-14A',   None,         None,                      [0,2,3,7],          (1,1,1,1,2,0),    'Major-second Minor Tetrachord'],
[ 47,    '4-14B',   None,         None,                      [0,4,5,7],          (1,1,1,1,2,0),    'Perfect-fourth Major Tetrachord'],
[ 48,    '4-Z15A',  None,      '4-Z29',                      [0,1,4,6],          (1,1,1,1,1,1),    'All-interval Tetrachord.1'],
[ 49,    '4-Z15B',  None,      '4-Z29',                      [0,2,5,6],          (1,1,1,1,1,1),    'All-interval Tetrachord.2'],
[ 50,    '4-16A',   None,         None,                      [0,1,5,7],          (1,1,0,1,2,1),    'Minor-second Quartal Tetrachord'],
[ 51,    '4-16B',   None,         None,                      [0,2,6,7],          (1,1,0,1,2,1),    'Tritone Quartal Tetrachord'],
[ 52,    '4-17',    None,         None,                      [0,3,4,7],          (1,0,2,2,1,0),    'Major-minor Tetramirror'],
[ 53,    '4-18A',   None,         None,                      [0,1,4,7],          (1,0,2,1,1,1),    'Major-diminished Tetrachord'],
[ 54,    '4-18B',   None,         None,                      [0,3,6,7],          (1,0,2,1,1,1),    'Minor-diminished Tetrachord'],
[ 55,    '4-19A',   None,         None,                      [0,1,4,8],          (1,0,1,3,1,0),    'Minor-augmented Tetrachord'],
[ 56,    '4-19B',   None,         None,                      [0,3,4,8],          (1,0,1,3,1,0),    'Augmented-major Tetrachord'],
[ 57,    '4-20',    None,         None,                      [0,1,5,8],          (1,0,1,2,2,0),    'Major-seventh Chord'],
[ 58,    '4-21',    None,         None,                      [0,2,4,6],          (0,3,0,2,0,1),    'Whole-tone Tetramirror'],
[ 59,    '4-22A',   None,         None,                      [0,2,4,7],          (0,2,1,1,2,0),    'Major-second Major Tetrachord'],
[ 60,    '4-22B',   None,         None,                      [0,3,5,7],          (0,2,1,1,2,0),    'Perfect-fourth Minor Tetrachord'],
[ 61,    '4-23',    None,         None,                      [0,2,5,7],          (0,2,1,0,3,0),    'Quartal Tetramirror'],
[ 62,    '4-24',    None,         None,                      [0,2,4,8],          (0,2,0,3,0,1),    'Augmented Seventh Chord'],
[ 63,    '4-25',       6,         None,                      [0,2,6,8],          (0,2,0,2,0,2),    'French-sixth Chord'],
[ 64,    '4-26',    None,         None,                      [0,3,5,8],          (0,1,2,1,2,0),    'Minor-seventh Chord'],
[ 65,    '4-27A',   None,         None,                      [0,2,5,8],          (0,1,2,1,1,1),    'Half-diminished Seventh Chord'],
[ 66,    '4-27B',   None,         None,                      [0,3,6,8],          (0,1,2,1,1,1),    'Dominant-seventh/German-sixth Chord'],
[ 67,    '4-28',       3,         None,                      [0,3,6,9],          (0,0,4,0,0,2),    'Diminished-seventh Chord'],
[ 68,    '4-Z29A',  None,      '4-Z15',                      [0,1,3,7],          (1,1,1,1,1,1),    'All-interval Tetrachord.3'],
[ 69,    '4-Z29B',  None,      '4-Z15',                      [0,4,6,7],          (1,1,1,1,1,1),    'All-interval Tetrachord.4'],

[ 70,    '5-1',     None,         None,                    [0,1,2,3,4],          (4,3,2,1,0,0),    'Chromatic Pentamirror'],
[ 71,    '5-2A',    None,         None,                    [0,1,2,3,5],          (3,3,2,1,1,0),    'Major-second Pentacluster.2'],
[ 72,    '5-2B',    None,         None,                    [0,2,3,4,5],          (3,3,2,1,1,0),    'Major-second Pentacluster.1'],
[ 73,    '5-3A',    None,         None,                    [0,1,2,4,5],          (3,2,2,2,1,0),    'Minor-second Major Pentachord'],
[ 74,    '5-3B',    None,         None,                    [0,1,3,4,5],          (3,2,2,2,1,0),    'Spanish Pentacluster'],
[ 75,    '5-4A',    None,         None,                    [0,1,2,3,6],          (3,2,2,1,1,1),    'Blues Pentacluster'],
[ 76,    '5-4B',    None,         None,                    [0,3,4,5,6],          (3,2,2,1,1,1),    'Minor-third Pentacluster'],
[ 77,    '5-5A',    None,         None,                    [0,1,2,3,7],          (3,2,1,1,2,1),    'Major-third Pentacluster.2'],
[ 78,    '5-5B',    None,         None,                    [0,4,5,6,7],          (3,2,1,1,2,1),    'Major-third Pentacluster.1'],
[ 79,    '5-6A',    None,         None,                    [0,1,2,5,6],          (3,1,1,2,2,1),    'Oriental Pentacluster.1, Raga Megharanji (13161)'],
[ 80,    '5-6B',    None,         None,                    [0,1,4,5,6],          (3,1,1,2,2,1),    'Oriental Pentacluster.2'],
[ 81,    '5-7A',    None,         None,                    [0,1,2,6,7],          (3,1,0,1,3,2),    'DoublePentacluster.1, Raga Nabhomani (11415)'],
[ 82,    '5-7B',    None,         None,                    [0,1,5,6,7],          (3,1,0,1,3,2),    'Double Pentacluster.2'],
[ 83,    '5-8',     None,         None,                    [0,2,3,4,6],          (2,3,2,2,0,1),    'Tritone-Symmetric Pentamirror'],
[ 84,    '5-9A',    None,         None,                    [0,1,2,4,6],          (2,3,1,2,1,1),    'Tritone-Expanding Pentachord'],
[ 85,    '5-9B',    None,         None,                    [0,2,4,5,6],          (2,3,1,2,1,1),    'Tritone-Contracting Pentachord'],
[ 86,    '5-10A',   None,         None,                    [0,1,3,4,6],          (2,2,3,1,1,1),    'Alternating Pentachord.1'],
[ 87,    '5-10B',   None,         None,                    [0,2,3,5,6],          (2,2,3,1,1,1),    'Alternating Pentachord.2'],
[ 88,    '5-11A',   None,         None,                    [0,2,3,4,7],          (2,2,2,2,2,0),    'Center-cluster Pentachord.1'],
[ 89,    '5-11B',   None,         None,                    [0,3,4,5,7],          (2,2,2,2,2,0),    'Center-cluster Pentachord.2'],
[ 90,    '5-Z12',   None,      '5-Z36',                    [0,1,3,5,6],          (2,2,2,1,2,1),    'Locrian Pentamirror'],
[ 91,    '5-13A',   None,         None,                    [0,1,2,4,8],          (2,2,1,3,1,1),    'Augmented Pentacluster.1'],
[ 92,    '5-13B',   None,         None,                    [0,2,3,4,8],          (2,2,1,3,1,1),    'Augmented Pentacluster.2'],
[ 93,    '5-14A',   None,         None,                    [0,1,2,5,7],          (2,2,1,1,3,1),    'Double-seconds Triple-fourth Pentachord.1'],
[ 94,    '5-14B',   None,         None,                    [0,2,5,6,7],          (2,2,1,1,3,1),    'Double-seconds Triple-fourth Pentachord.2'],
[ 95,    '5-15',    None,         None,                    [0,1,2,6,8],          (2,2,0,2,2,2),    'Assymetric Pentamirror'],
[ 96,    '5-16A',   None,         None,                    [0,1,3,4,7],          (2,1,3,2,1,1),    'Major-minor-dim Pentachord.1'],
[ 97,    '5-16B',   None,         None,                    [0,3,4,6,7],          (2,1,3,2,1,1),    'Major-minor-dim Pentachord.2'],
[ 98,    '5-Z17',   None,      '5-Z37',                    [0,1,3,4,8],          (2,1,2,3,2,0),    'Minor-major Ninth Chord'],
[ 99,    '5-Z18A',  None,      '5-Z38',                    [0,1,4,5,7],          (2,1,2,2,2,1),    'Gypsy Pentachord.1'],
[100,    '5-Z18B',  None,      '5-Z38',                    [0,2,3,6,7],          (2,1,2,2,2,1),    'Gypsy Pentachord.2'],
[101,    '5-19A',   None,         None,                    [0,1,3,6,7],          (2,1,2,1,2,2),    'Javanese Pentachord'],
[102,    '5-19B',   None,         None,                    [0,1,4,6,7],          (2,1,2,1,2,2),    'Balinese Pentachord'],
[103,    '5-20A',   None,         None,                    [0,1,3,7,8],          (2,1,1,2,3,1),    'Balinese Pelog Pentatonic (12414), Raga Bhupala, Raga Bibhas'],
[104,    '5-20B',   None,         None,                    [0,1,5,7,8],          (2,1,1,2,3,1),    'Hirajoshi Pentatonic (21414), Iwato (14142), Sakura/Raga Saveri (14214)'],
[105,    '5-21A',   None,         None,                    [0,1,4,5,8],          (2,0,2,4,2,0),    'Syrian Pentatonic/Major-augmented Ninth Chord, Raga Megharanji (13134)'],
[106,    '5-21B',   None,         None,                    [0,3,4,7,8],          (2,0,2,4,2,0),    'Lebanese Pentachord/Augmented-minor Chord'],
[107,    '5-22',    None,         None,                    [0,1,4,7,8],          (2,0,2,3,2,1),    'Persian Pentamirror, Raga reva/Ramkali (13314)'],
[108,    '5-23A',   None,         None,                    [0,2,3,5,7],          (1,3,2,1,3,0),    'Minor Pentachord'],
[109,    '5-23B',   None,         None,                    [0,2,4,5,7],          (1,3,2,1,3,0),    'Major Pentachord'],
[110,    '5-24A',   None,         None,                    [0,1,3,5,7],          (1,3,1,2,2,1),    'Phrygian Pentachord'],
[111,    '5-24B',   None,         None,                    [0,2,4,6,7],          (1,3,1,2,2,1),    'Lydian Pentachord'],
[112,    '5-25A',   None,         None,                    [0,2,3,5,8],          (1,2,3,1,2,1),    'Diminished-major Ninth Chord'],
[113,    '5-23B',   None,         None,                    [0,3,5,6,8],          (1,2,3,1,2,1),    'Minor-diminished Ninth Chord'],
[114,    '5-26A',   None,         None,                    [0,2,4,5,8],          (1,2,2,3,1,1),    'Diminished-augmented Ninth Chord'],
[115,    '5-26B',   None,         None,                    [0,3,4,6,8],          (1,2,2,3,1,1),    'Augmented-diminished Ninth Chord'],
[116,    '5-27A',   None,         None,                    [0,1,3,5,8],          (1,2,2,2,3,0),    'Major-Ninth Chord'],
[117,    '5-27B',   None,         None,                    [0,3,5,7,8],          (1,2,2,2,3,0),    'Minor-Ninth Chord'],
[118,    '5-28A',   None,         None,                    [0,2,3,6,8],          (1,2,2,2,1,2),    'Augmented-sixth Pentachord.1'],
[119,    '5-28B',   None,         None,                    [0,2,5,6,8],          (1,2,2,2,1,2),    'Augmented-sixth Pentachord.2'],
[120,    '5-29A',   None,         None,                    [0,1,3,6,8],          (1,2,2,1,3,1),    'Kumoi Pentachord.2'],
[121,    '5-29B',   None,         None,                    [0,2,5,7,8],          (1,2,2,1,3,1),    'Kumoi Pentachord.1'],
[122,    '5-30A',   None,         None,                    [0,1,4,6,8],          (1,2,1,3,2,1),    'Enigmatic Pentachord.1'],
[123,    '5-30B',   None,         None,                    [0,2,4,7,8],          (1,2,1,3,2,1),    'Enigmatic Pentachord.2, Altered Pentatonic (14223)'],
[124,    '5-31A',   None,         None,                    [0,1,3,6,9],          (1,1,4,1,1,2),    'Diminished Minor-Ninth Chord'],
[125,    '5-31B',   None,         None,                    [0,2,3,6,9],          (1,1,4,1,1,2),    'Ranjaniraga/Flat-Ninth Pentachord'],
[126,    '5-32A',   None,         None,                    [0,1,4,6,9],          (1,1,3,2,2,1),    'Neapolitan Pentachord.1'],
[127,    '5-32B',   None,         None,                    [0,1,4,7,9],          (1,1,3,2,2,1),    'Neapolitan Pentachord.2'],
[128,    '5-33',    None,         None,                    [0,2,4,6,8],          (0,4,0,4,0,2),    'Whole-tone Pentamirror'],
[129,    '5-34',    None,         None,                    [0,2,4,6,9],          (0,3,2,2,2,1),    'Dominant-ninth/major-minor/Prometheus Pentamirror,Dominant Pentatonic(22332)'],
[130,    '5-35',    None,         None,                    [0,2,4,7,9],          (0,3,2,1,4,0),    '"Black Key" Pentatonic/Slendro/Bilahariraga/Quartal Pentamirror, Yo (23232)'],
[131,    '5-Z36A',  None,      '5-Z12',                    [0,1,2,4,7],          (2,2,2,1,2,1),    'Major-seventh Pentacluster.2'],
[132,    '5-Z36B',  None,      '5-Z12',                    [0,3,5,6,7],          (2,2,2,1,2,1),    'Minor-seventh Pentacluster.1'],
[133,    '5-Z37',   None,      '5-Z17',                    [0,3,4,5,8],          (2,1,2,3,2,0),    'Center-cluster Pentamirror'],
[134,    '5-Z38A',  None,      '5-Z18',                    [0,1,2,5,8],          (2,1,2,2,2,1),    'Diminished Pentacluster.1'],
[135,    '5-Z38B',  None,      '5-Z18',                    [0,3,6,7,8],          (2,1,2,2,2,1),    'Diminished Pentacluster.2'],

[136,    '6-1',     None,         None,                  [0,1,2,3,4,5],          (5,4,3,2,1,0),    'Chromatic Hexamirror/1st ord. all-comb (P6, Ib, RI5)'],
[137,    '6-2A',    None,         None,                  [0,1,2,3,4,6],          (4,4,3,2,1,1),    'comb I (b)'],
[138,    '6-2B',    None,         None,                  [0,2,3,4,5,6],          (4,4,3,2,1,1),    'comb I (1)'],
[139,    '6-Z3A',   None,      '6-Z36',                  [0,1,2,3,5,6],          (4,3,3,2,2,1),    None],
[140,    '6-Z3B',   None,      '6-Z36',                  [0,1,3,4,5,6],          (4,3,3,2,2,1),    None],
[141,    '6-Z4',    None,      '6-Z37',                  [0,1,2,4,5,6],          (4,3,2,3,2,1),    'comb RI (6)'],
[142,    '6-5A',    None,         None,                  [0,1,2,3,6,7],          (4,2,2,2,3,2),    'comb I (b)'],
[143,    '6-5B',    None,         None,                  [0,1,4,5,6,7],          (4,2,2,2,3,2),    'comb I (3)'],
[144,    '6-Z6',    None,      '6-Z38',                  [0,1,2,5,6,7],          (4,2,1,2,4,2),    'Double-cluster Hexamirror'],
[145,    '6-7',        6,         None,                  [0,1,2,6,7,8],          (4,2,0,2,4,3),    'Messiaen\'s mode 5 (114114), 2nd ord.all-comb(P3+9,I5,Ib,R6,RI2+8)'],
[146,    '6-8',     None,         None,                  [0,2,3,4,5,7],          (3,4,3,2,3,0),    '1st ord.all-comb (P6, I1, RI7)'],
[147,    '6-9A',    None,         None,                  [0,1,2,3,5,7],          (3,4,2,2,3,1),    'comb I (b)'],
[148,    '6-9B',    None,         None,                  [0,2,4,5,6,7],          (3,4,2,2,3,1),    'comb I (3)'],
[149,    '6-Z10A',  None,      '6-Z39',                  [0,1,3,4,5,7],          (3,3,3,3,2,1),    None],
[150,    '6-Z10B',  None,      '6-Z39',                  [0,2,3,4,6,7],          (3,3,3,3,2,1),    None],
[151,    '6-Z11A',  None,      '6-Z40',                  [0,1,2,4,5,7],          (3,3,3,2,3,1),    None],
[152,    '6-Z11B',  None,      '6-Z40',                  [0,2,3,5,6,7],          (3,3,3,2,3,1),    None],
[153,    '6-Z12A',  None,      '6-Z41',                  [0,1,2,4,6,7],          (3,3,2,2,3,2),    None],
[154,    '6-Z12B',  None,      '6-Z41',                  [0,1,3,5,6,7],          (3,3,2,2,3,2),    None],
[155,    '6-Z13',   None,      '6-Z42',                  [0,1,3,4,6,7],          (3,2,4,2,2,2),    'Alternating Hexamirror/comb RI7)'],
[156,    '6-14A',   None,      '6-Z14',                  [0,1,3,4,5,8],          (3,2,3,4,3,0),    'comb P (6)'],
[157,    '6-14B',   None,      '6-Z14',                  [0,3,4,5,7,8],          (3,2,3,4,3,0),    'comb P (6)'],
[158,    '6-15A',   None,         None,                  [0,1,2,4,5,8],          (3,2,3,4,2,1),    'comb I (b)'],
[159,    '6-15B',   None,         None,                  [0,3,4,6,7,8],          (3,2,3,4,2,1),    'comb I (5)'],
[160,    '6-16A',   None,         None,                  [0,1,4,5,6,8],          (3,2,2,4,3,1),    'comb I (3)'],
[161,    '6-16B',   None,         None,                  [0,2,3,4,7,8],          (3,2,2,4,3,1),    'Megha or "Cloud" Raga/comb.I (1)'],
[162,    '6-Z17A',  None,      '6-Z43',                  [0,1,2,4,7,8],          (3,2,2,3,3,2),    None],
[163,    '6-Z17B',  None,      '6-Z43',                  [0,1,4,6,7,8],          (3,2,2,3,3,2),    None],
[164,    '6-18A',   None,         None,                  [0,1,2,5,7,8],          (3,2,2,2,4,2),    'comb I (b)'],
[165,    '6-18B',   None,         None,                  [0,1,3,6,7,8],          (3,2,2,2,4,2),    'comb I (5)'],
[166,    '6-Z19A',  None,      '6-Z44',                  [0,1,3,4,7,8],          (3,1,3,4,3,1),    None],
[167,    '6-Z19B',  None,      '6-Z44',                  [0,1,4,5,7,8],          (3,1,3,4,3,1),    None],
[168,    '6-20',       4,         None,                  [0,1,4,5,8,9],          (3,0,3,6,3,0),    'Augmented scale,Genus tertium,3rd ord. all-comb(P2+6+10,I3+7+b,R4+8,RI1+5+9)'],
[169,    '6-21A',   None,         None,                  [0,2,3,4,6,8],          (2,4,2,4,1,2),    'comb I (1)'],
[170,    '6-21B',   None,         None,                  [0,2,4,5,6,8],          (2,4,2,4,1,2),    'comb I (3)'],
[171,    '6-22A',   None,         None,                  [0,1,2,4,6,8],          (2,4,1,4,2,2),    'comb I (b)'],
[172,    '6-22B',   None,         None,                  [0,2,4,6,7,8],          (2,4,1,4,2,2),    'comb I (5)'],
[173,    '6-Z23',   None,      '6-Z45',                  [0,2,3,5,6,8],          (2,3,4,2,2,2),    'Super-Locrian Hexamirror/comb RI (8)'],
[174,    '6-Z24A',  None,      '6-Z46',                  [0,1,3,4,6,8],          (2,3,3,3,3,1),    None],
[175,    '6-Z24B',  None,      '6-Z46',                  [0,2,4,5,7,8],          (2,3,3,3,3,1),    'Melodic-minor Hexachord'],
[176,    '6-Z25A',  None,      '6-Z47',                  [0,1,3,5,6,8],          (2,3,3,2,4,1),    'Locrian Hexachord/Suddha Saveriraga'],
[177,    '6-Z25B',  None,      '6-Z47',                  [0,2,3,5,7,8],          (2,3,3,2,4,1),    'Minor Hexachord'],
[178,    '6-Z26',   None,      '6-Z48',                  [0,1,3,5,7,8],          (2,3,2,3,4,1),    'Phrygian Hexamirror/comb RI (8)'],
[179,    '6-27A',   None,         None,                  [0,1,3,4,6,9],          (2,2,5,2,2,2),    'comb I (b)'],
[180,    '6-27B',   None,         None,                  [0,2,3,5,6,9],          (2,2,5,2,2,2),    'Pyramid Hexachord/comb I (1)'],
[181,    '6-Z28',   None,      '6-Z49',                  [0,1,3,5,6,9],          (2,2,4,3,2,2),    'Double-Phrygian Hexachord/comb RI (6)'],
[182,    '6-Z29',   None,      '6-Z50',                  [0,1,3,6,8,9],          (2,2,4,2,3,2),    'comb RI (9)'],
[183,    '6-30A',      6,         None,                  [0,1,3,6,7,9],          (2,2,4,2,2,3),    'Minor-bitonal Hexachord/comb R (6), I (5,b)'],
[184,    '6-30B',      6,         None,                  [0,2,3,6,8,9],          (2,2,4,2,2,3),    'Petrushka chord, Major-bitonal Hexachord, comb R (6), I (1,7)'],
[185,    '6-31A',   None,         None,                  [0,1,3,5,8,9],          (2,2,3,4,3,1),    'comb I (7)'],
[186,    '6-31B',   None,         None,                  [0,1,4,6,8,9],          (2,2,3,4,3,1),    'comb I (b)'],
[187,    '6-32',    None,         None,                  [0,2,4,5,7,9],          (1,4,3,2,5,0),    'Arezzo major Diatonic (221223), major hexamirror, quartal hexamirror, 1st ord.all-comb P (6), I (3), RI (9)'],
[188,    '6-33A',   None,         None,                  [0,2,3,5,7,9],          (1,4,3,2,4,1),    'Dorian Hexachord/comb I (1)'],
[189,    '6-33B',   None,         None,                  [0,2,4,6,7,9],          (1,4,3,2,4,1),    'Dominant-11th/Lydian Hexachord/comb I (5)'],
[190,    '6-34A',   None,         None,                  [0,1,3,5,7,9],          (1,4,2,4,2,2),    'Scriabin\'s Mystic Chord or Prometheus Hexachord/comb I (B)'],
[191,    '6-34B',   None,         None,                  [0,2,4,6,8,9],          (1,4,2,4,2,2),    'Harmonic Hexachord/Augmented-11th/comb I (7)'],
[192,    '6-35',       2,         None,                 [0,2,4,6,8,10],          (0,6,0,6,0,3),    'Wholetone scale/6th ord.all-comb.(P+IoddT, R+RIevenT)'],
[193,    '6-Z36A',  None,       '6-Z3',                  [0,1,2,3,4,7],          (4,3,3,2,2,1),    None],
[194,    '6-Z36B',  None,       '6-Z3',                  [0,3,4,5,6,7],          (4,3,3,2,2,1),    None],
[195,    '6-Z37',   None,       '6-Z4',                  [0,1,2,3,4,8],          (4,3,2,3,2,1),    'comb RI (4)'],
[196,    '6-Z38',   None,       '6-Z6',                  [0,1,2,3,7,8],          (4,2,1,2,4,2),    'comb RI (3)'],
[197,    '6-Z39A',  None,      '6-Z10',                  [0,2,3,4,5,8],          (3,3,3,3,2,1),    None],
[198,    '6-Z39B',  None,      '6-Z10',                  [0,3,4,5,6,8],          (3,3,3,3,2,1),    None],
[199,    '6-Z40A',  None,      '6-Z11',                  [0,1,2,3,5,8],          (3,3,3,2,3,1),    None],
[200,    '6-Z40B',  None,      '6-Z11',                  [0,3,5,6,7,8],          (3,3,3,2,3,1),    None],
[201,    '6-Z41A',  None,      '6-Z12',                  [0,1,2,3,6,8],          (3,3,2,2,3,2),    None],
[202,    '6-Z41B',  None,      '6-Z12',                  [0,2,5,6,7,8],          (3,3,2,2,3,2),    None],
[203,    '6-Z42',   None,      '6-Z13',                  [0,1,2,3,6,9],          (3,2,4,2,2,2),    'comb RI (3)'],
[204,    '6-Z43A',  None,      '6-Z17',                  [0,1,2,5,6,8],          (3,2,2,3,3,2),    None],
[205,    '6-Z43B',  None,      '6-Z17',                  [0,2,3,6,7,8],          (3,2,2,3,3,2),    None],
[206,    '6-Z44A',  None,      '6-Z19',                  [0,1,2,5,6,9],          (3,1,3,4,3,1),    'Schoenberg Anagram Hexachord'],
[207,    '6-Z44B',  None,      '6-Z19',                  [0,1,2,5,8,9],          (3,1,3,4,3,1),    'Bauli raga (133131)'],
[208,    '6-Z45',   None,      '6-Z23',                  [0,2,3,4,6,9],          (2,3,4,2,2,2),    'comb RI (6)'],
[209,    '6-Z46A',  None,      '6-Z24',                  [0,1,2,4,6,9],          (2,3,3,3,3,1),    None],
[210,    '6-Z46B',  None,      '6-Z24',                  [0,2,4,5,6,9],          (2,3,3,3,3,1),    None],
[211,    '6-Z47A',  None,      '6-Z25',                  [0,1,2,4,7,9],          (2,3,3,2,4,1),    None],
[212,    '6-Z47B',  None,      '6-Z25',                  [0,2,3,4,7,9],          (2,3,3,2,4,1),    'Blues mode.1 (321132)'],
[213,    '6-Z48',   None,      '6-Z26',                  [0,1,2,5,7,9],          (2,3,2,3,4,1),    'comb RI (2)'],
[214,    '6-Z49',   None,      '6-Z28',                  [0,1,3,4,7,9],          (2,2,4,3,2,2),    'Prometheus Neapolitan mode (132312), comb RI (4)'],
[215,    '6-Z50',   None,      '6-Z29',                  [0,1,4,6,7,9],          (2,2,4,2,3,2),    'comb RI (1)'],

[216,    '7-1',     None,         None,                [0,1,2,3,4,5,6],          (6,5,4,3,2,1),    'Chromatic Heptamirror'],
[217,    '7-2A',    None,         None,                [0,1,2,3,4,5,7],          (5,5,4,3,3,1),    None],
[218,    '7-2B',    None,         None,                [0,2,3,4,5,6,7],          (5,5,4,3,3,1),    None],
[219,    '7-3A',    None,         None,                [0,1,2,3,4,5,8],          (5,4,4,4,3,1),    None],
[220,    '7-3B',    None,         None,                [0,3,4,5,6,7,8],          (5,4,4,4,3,1),    None],
[221,    '7-4A',    None,         None,                [0,1,2,3,4,6,7],          (5,4,4,3,3,2),    None],
[222,    '7-4B',    None,         None,                [0,1,3,4,5,6,7],          (5,4,4,3,3,2),    None],
[223,    '7-5A',    None,         None,                [0,1,2,3,5,6,7],          (5,4,3,3,4,2),    None],
[224,    '7-5B',    None,         None,                [0,1,2,4,5,6,7],          (5,4,3,3,4,2),    None],
[225,    '7-6A',    None,         None,                [0,1,2,3,4,7,8],          (5,3,3,4,4,2),    None],
[226,    '7-6B',    None,         None,                [0,1,4,5,6,7,8],          (5,3,3,4,4,2),    None],
[227,    '7-7A',    None,         None,                [0,1,2,3,6,7,8],          (5,3,2,3,5,3),    None],
[228,    '7-7B',    None,         None,                [0,1,2,5,6,7,8],          (5,3,2,3,5,3),    None],
[229,    '7-8',     None,         None,                [0,2,3,4,5,6,8],          (4,5,4,4,2,2),    None],
[230,    '7-9A',    None,         None,                [0,1,2,3,4,6,8],          (4,5,3,4,3,2),    None],
[231,    '7-9B',    None,         None,                [0,2,4,5,6,7,8],          (4,5,3,4,3,2),    None],
[232,    '7-10A',   None,         None,                [0,1,2,3,4,6,9],          (4,4,5,3,3,2),    None],
[233,    '7-10B',   None,         None,                [0,2,3,4,5,6,9],          (4,4,5,3,3,2),    None],
[234,    '7-11A',   None,         None,                [0,1,3,4,5,6,8],          (4,4,4,4,4,1),    None],
[235,    '7-11B',   None,         None,                [0,2,3,4,5,7,8],          (4,4,4,4,4,1),    None],
[236,    '7-Z12',   None,      '7-Z36',                [0,1,2,3,4,7,9],          (4,4,4,3,4,2),    None],
[237,    '7-13A',   None,         None,                [0,1,2,4,5,6,8],          (4,4,3,5,3,2),    None],
[238,    '7-13B',   None,         None,                [0,2,3,4,6,7,8],          (4,4,3,5,3,2),    None],
[239,    '7-14A',   None,         None,                [0,1,2,3,5,7,8],          (4,4,3,3,5,2),    None],
[240,    '7-14B',   None,         None,                [0,1,3,5,6,7,8],          (4,4,3,3,5,2),    None],
[241,    '7-15',    None,         None,                [0,1,2,4,6,7,8],          (4,4,2,4,4,3),    None],
[242,    '7-16A',   None,         None,                [0,1,2,3,5,6,9],          (4,3,5,4,3,2),    None],
[243,    '7-16B',   None,         None,                [0,1,3,4,5,6,9],          (4,3,5,4,3,2),    None],
[244,    '7-Z17',   None,      '7-Z37',                [0,1,2,4,5,6,9],          (4,3,4,5,4,1),    None],
[245,    '7-Z18A',  None,      '7-Z38',                [0,1,2,3,5,8,9],          (4,3,4,4,4,2),    None],
[246,    '7-Z18B',  None,      '7-Z38',                [0,1,4,6,7,8,9],          (4,3,4,4,4,2),    None],
[247,    '7-19A',   None,         None,                [0,1,2,3,6,7,9],          (4,3,4,3,4,3),    None],
[248,    '7-19B',   None,         None,                [0,1,2,3,6,8,9],          (4,3,4,3,4,3),    None],
[249,    '7-20A',   None,         None,                [0,1,2,4,7,8,9],          (4,3,3,4,5,2),    'Chromatic Phrygian inverse (1123113)'],
[250,    '7-20B',   None,         None,                [0,1,2,5,7,8,9],          (4,3,3,4,5,2),    'Pantuvarali Raga (1321131), Chromatic Mixolydian (1131132), Chromatic Dorian/Mela Kanakangi (1132113)'],
[251,    '7-21A',   None,         None,                [0,1,2,4,5,8,9],          (4,2,4,6,4,1),    None],
[252,    '7-21B',   None,         None,                [0,1,3,4,5,8,9],          (4,2,4,6,4,1),    'Gypsy hexatonic (1312113)'],
[253,    '7-22',    None,         None,                [0,1,2,5,6,8,9],          (4,2,4,5,4,2),    'Persian, Major Gypsy, Hungarian Minor, Double Harmonic scale, Bhairav That, Mayamdavagaula Raga (all: 1312131), Oriental (1311312)'],
[254,    '7-23A',   None,         None,                [0,2,3,4,5,7,9],          (3,5,4,3,5,1),    None],
[255,    '7-23B',   None,         None,                [0,2,4,5,6,7,9],          (3,5,4,3,5,1),    'Tritone Major Heptachord'],
[256,    '7-24A',   None,         None,                [0,1,2,3,5,7,9],          (3,5,3,4,4,2),    None],
[257,    '7-24B',   None,         None,                [0,2,4,6,7,8,9],          (3,5,3,4,4,2),    'Enigmatic Heptatonic (1322211)'],
[258,    '7-25A',   None,         None,                [0,2,3,4,6,7,9],          (3,4,5,3,4,2),    None],
[259,    '7-25B',   None,         None,                [0,2,3,5,6,7,9],          (3,4,5,3,4,2),    None],
[260,    '7-26A',   None,         None,                [0,1,3,4,5,7,9],          (3,4,4,5,3,2),    None],
[261,    '7-26B',   None,         None,                [0,2,4,5,6,8,9],          (3,4,4,5,3,2),    None],
[262,    '7-27A',   None,         None,                [0,1,2,4,5,7,9],          (3,4,4,4,5,1),    None],
[263,    '7-27B',   None,         None,                [0,2,4,5,7,8,9],          (3,4,4,4,5,1),    'Modified Blues mode (2121132)'],
[264,    '7-28A',   None,         None,                [0,1,3,5,6,7,9],          (3,4,4,4,3,3),    None],
[265,    '7-28B',   None,         None,                [0,2,3,4,6,8,9],          (3,4,4,4,3,3),    None],
[266,    '7-29A',   None,         None,                [0,1,2,4,6,7,9],          (3,4,4,3,5,2),    None],
[267,    '7-29B',   None,         None,                [0,2,3,5,7,8,9],          (3,4,4,3,5,2),    None],
[268,    '7-30A',   None,         None,                [0,1,2,4,6,8,9],          (3,4,3,5,4,2),    'Neapolitan-Minor mode (1222131), Mela Dhenuka'],
[269,    '7-30B',   None,         None,                [0,1,3,5,7,8,9],          (3,4,3,5,4,2),    None],
[270,    '7-31A',   None,         None,                [0,1,3,4,6,7,9],          (3,3,6,3,3,3),    'Alternating Heptachord.1/Hungarian Major mode (3121212)'],
[271,    '7-31B',   None,         None,                [0,2,3,5,6,8,9],          (3,3,6,3,3,3),    'Alternating Heptachord.2'],
[272,    '7-32A',   None,         None,                [0,1,3,4,6,8,9],          (3,3,5,4,4,2),    'Harmonic-Minor mode (2122131), Spanish Gypsy, Mela Kiravani, Pilu That'],
[273,    '7-32B',   None,         None,                [0,1,3,5,6,8,9],          (3,3,5,4,4,2),    'Dharmavati Scale (2131221), Harmonic minor inverse (1312212), Mela Cakravana, Raga Ahir Bhairav'],
[274,    '7-33',    None,         None,               [0,1,2,4,6,8,10],          (2,6,2,6,2,3),    'Neapolitan-major mode (1222221)/Leading-Whole-tone mode (222211)'],
[275,    '7-34',    None,         None,               [0,1,3,4,6,8,10],          (2,5,4,4,4,2),    'Harmonic/Super-Locrian, Melodic minor ascending (1212222)/Aug.13th Heptamirror, Jazz Minor'],
[276,    '7-35',    None,         None,               [0,1,3,5,6,8,10],          (2,5,4,3,6,1),    'Major Diatonic Heptachord/Dominant-13th, Locrian (1221222), Phrygian (1222122), Major inverse'],
[277,    '7-Z36A',  None,      '7-Z12',                [0,1,2,3,5,6,8],          (4,4,4,3,4,2),    None],
[278,    '7-Z36B',  None,      '7-Z12',                [0,2,3,5,6,7,8],          (4,4,4,3,4,2),    None],
[279,    '7-Z37',   None,      '7-Z17',                [0,1,3,4,5,7,8],          (4,3,4,5,4,1),    None],
[280,    '7-Z38A',  None,      '7-Z18',                [0,1,2,4,5,7,8],          (4,3,4,4,4,2),    None],
[281,    '7-Z38B',  None,      '7-Z18',                [0,1,3,4,6,7,8],          (4,3,4,4,4,2),    None],

[282,    '8-1',     None,         None,              [0,1,2,3,4,5,6,7],          (7,6,5,4,4,2),    'Chromatic Octamirror'],
[283,    '8-2A',    None,         None,              [0,1,2,3,4,5,6,8],          (6,6,5,5,4,2),    None],
[284,    '8-2B',    None,         None,              [0,2,3,4,5,6,7,8],          (6,6,5,5,4,2),    None],
[285,    '8-3',     None,         None,              [0,1,2,3,4,5,6,9],          (6,5,6,5,4,2),    None],
[286,    '8-4A',    None,         None,              [0,1,2,3,4,5,7,8],          (6,5,5,5,5,2),    None],
[287,    '8-4B',    None,         None,              [0,1,3,4,5,6,7,8],          (6,5,5,5,5,2),    None],
[288,    '8-5A',    None,         None,              [0,1,2,3,4,6,7,8],          (6,5,4,5,5,3),    None],
[289,    '8-5B',    None,         None,              [0,1,2,4,5,6,7,8],          (6,5,4,5,5,3),    None],
[290,    '8-6',     None,         None,              [0,1,2,3,5,6,7,8],          (6,5,4,4,6,3),    None],
[291,    '8-7',     None,         None,              [0,1,2,3,4,5,8,9],          (6,4,5,6,5,2),    None],
[292,    '8-8',     None,         None,              [0,1,2,3,4,7,8,9],          (6,4,4,5,6,3),    None],
[293,    '8-9',        6,         None,              [0,1,2,3,6,7,8,9],          (6,4,4,4,6,4),    'Messiaen\'s mode 4 (11131113)'],
[294,    '8-10',    None,         None,              [0,2,3,4,5,6,7,9],          (5,6,6,4,5,2),    None],
[295,    '8-11A',   None,         None,              [0,1,2,3,4,5,7,9],          (5,6,5,5,5,2),    None],
[296,    '8-11B',   None,         None,              [0,2,4,5,6,7,8,9],          (5,6,5,5,5,2),    None],
[297,    '8-12A',   None,         None,              [0,1,3,4,5,6,7,9],          (5,5,6,5,4,3),    None],
[298,    '8-12B',   None,         None,              [0,2,3,4,5,6,8,9],          (5,5,6,5,4,3),    None],
[299,    '8-13A',   None,         None,              [0,1,2,3,4,6,7,9],          (5,5,6,4,5,3),    None],
[300,    '8-13B',   None,         None,              [0,2,3,5,6,7,8,9],          (5,5,6,4,5,3),    None],
[301,    '8-14A',   None,         None,              [0,1,2,4,5,6,7,9],          (5,5,5,5,6,2),    None],
[302,    '8-14B',   None,         None,              [0,2,3,4,5,7,8,9],          (5,5,5,5,6,2),    None],
[303,    '8-Z15A',  None,      '8-Z29',              [0,1,2,3,4,6,8,9],          (5,5,5,5,5,3),    None],
[304,    '8-Z15B',  None,      '8-Z29',              [0,1,3,5,6,7,8,9],          (5,5,5,5,5,3),    None],
[305,    '8-16A',   None,         None,              [0,1,2,3,5,7,8,9],          (5,5,4,5,6,3),    None],
[306,    '8-16B',   None,         None,              [0,1,2,4,6,7,8,9],          (5,5,4,5,6,3),    None],
[307,    '8-17',    None,         None,              [0,1,3,4,5,6,8,9],          (5,4,6,6,5,2),    None],
[308,    '8-18A',   None,         None,              [0,1,2,3,5,6,8,9],          (5,4,6,5,5,3),    None],
[309,    '8-18B',   None,         None,              [0,1,3,4,6,7,8,9],          (5,4,6,5,5,3),    None],
[310,    '8-19A',   None,         None,              [0,1,2,4,5,6,8,9],          (5,4,5,7,5,2),    None],
[311,    '8-19B',   None,         None,              [0,1,3,4,5,7,8,9],          (5,4,5,7,5,2),    None],
[312,    '8-20',    None,         None,              [0,1,2,4,5,7,8,9],          (5,4,5,6,6,2),    None],
[313,    '8-21',    None,         None,             [0,1,2,3,4,6,8,10],          (4,7,4,6,4,3),    None],
[314,    '8-22A',   None,         None,             [0,1,2,3,5,6,8,10],          (4,6,5,5,6,2),    None],
[315,    '8-22B',   None,         None,             [0,1,2,3,5,7,9,10],          (4,6,5,5,6,2),    'Spanish Octatonic Scale (r9) (12111222)'],
[316,    '8-23',    None,         None,             [0,1,2,3,5,7,8,10],          (4,6,5,4,7,2),    'Quartal Octachord, Diatonic Octad'],
[317,    '8-24',    None,         None,             [0,1,2,4,5,6,8,10],          (4,6,4,7,4,3),    None],
[318,    '8-25',       6,         None,             [0,1,2,4,6,7,8,10],          (4,6,4,6,4,4),    'Messiaen mode 6 (11221122)'],
[319,    '8-26',    None,         None,             [0,1,2,4,5,7,9,10],          (4,5,6,5,6,2),    'Spanish Phrygian (r9) (12112122)/ Blues mode.2 (21211212)'],
[320,    '8-27A',   None,         None,             [0,1,2,4,5,7,8,10],          (4,5,6,5,5,3),    None],
[321,    '8-27B',   None,         None,             [0,1,2,4,6,7,9,10],          (4,5,6,5,5,3),    None],
[322,    '8-28',       3,         None,             [0,1,3,4,6,7,9,10],          (4,4,8,4,4,4),    'Alternating Octatonic or Diminished scale (12121212)'],
[323,    '8-Z29A',  None,      '8-Z15',              [0,1,2,3,5,6,7,9],          (5,5,5,5,5,3),    None],
[324,    '8-Z29B',  None,      '8-Z15',              [0,2,3,4,6,7,8,9],          (5,5,5,5,5,3),    None],

[325,    '9-1',     None,         None,            [0,1,2,3,4,5,6,7,8],          (8,7,6,6,6,3),    'Chromatic Nonamirror'],
[326,    '9-2A',    None,         None,            [0,1,2,3,4,5,6,7,9],          (7,7,7,6,6,3),    None],
[327,    '9-2B',    None,         None,            [0,2,3,4,5,6,7,8,9],          (7,7,7,6,6,3),    None],
[328,    '9-3A',    None,         None,            [0,1,2,3,4,5,6,8,9],          (7,6,7,7,6,3),    None],
[329,    '9-3B',    None,         None,            [0,1,3,4,5,6,7,8,9],          (7,6,7,7,6,3),    None],
[330,    '9-4A',    None,         None,            [0,1,2,3,4,5,7,8,9],          (7,6,6,7,7,3),    None],
[331,    '9-4B',    None,         None,            [0,1,2,4,5,6,7,8,9],          (7,6,6,7,7,3),    None],
[332,    '9-5A',    None,         None,            [0,1,2,3,4,6,7,8,9],          (7,6,6,6,7,4),    None],
[333,    '9-5B',    None,         None,            [0,1,2,3,5,6,7,8,9],          (7,6,6,6,7,4),    None],
[334,    '9-6',     None,         None,           [0,1,2,3,4,5,6,8,10],          (6,8,6,7,6,3),    None],
[335,    '9-7A',    None,         None,           [0,1,2,3,4,5,7,8,10],          (6,7,7,6,7,3),    'Nonatonic Blues Scale (211111212)'],
[336,    '9-7B',    None,         None,           [0,1,2,3,4,5,7,9,10],          (6,7,7,6,7,3),    None],
[337,    '9-8A',    None,         None,           [0,1,2,3,4,6,7,8,10],          (6,7,6,7,6,4),    None],
[338,    '9-8B',    None,         None,           [0,1,2,3,4,6,8,9,10],          (6,7,6,7,6,4),    None],
[339,    '9-9',     None,         None,           [0,1,2,3,5,6,7,8,10],          (6,7,6,6,8,3),    'Raga Ramdasi Malhar (r2) (211122111)'],
[340,    '9-10',    None,         None,           [0,1,2,3,4,6,7,9,10],          (6,6,8,6,6,4),    None],
[341,    '9-11A',   None,         None,           [0,1,2,3,5,6,7,9,10],          (6,6,7,7,7,3),    None],
[342,    '9-11B',   None,         None,           [0,1,2,3,5,6,8,9,10],          (6,6,7,7,7,3),    'Diminishing Nonachord'],
[343,    '9-12',       4,         None,           [0,1,2,4,5,6,8,9,10],          (6,6,6,9,6,3),    'Tsjerepnin/Messiaen mode 3 (112112112)'],

[344,    '10-1',    None,         None,          [0,1,2,3,4,5,6,7,8,9],          (9,8,8,8,8,4),    'Chromatic Decamirror'],
[345,    '10-2',    None,         None,         [0,1,2,3,4,5,6,7,8,10],          (8,9,8,8,8,4),    None],
[346,    '10-3',    None,         None,         [0,1,2,3,4,5,6,7,9,10],          (8,8,9,8,8,4),    None],
[347,    '10-4',    None,         None,         [0,1,2,3,4,5,6,8,9,10],          (8,8,8,9,8,4),    None],
[348,    '10-5',    None,         None,         [0,1,2,3,4,5,7,8,9,10],          (8,8,8,8,9,4),    'Major-minor mixed (r7)'],
[349,    '10-6',       6,         None,         [0,1,2,3,4,6,7,8,9,10],          (8,8,8,8,8,5),    'Messiaen mode 7 (1111211112)'],

[350,    '11-1',    None,         None,       [0,1,2,3,4,5,6,7,8,9,10],     (10,10,10,10,10,5),    'Chromatic Undecamirror'],

[351,    '12-1',       1,         None,    [0,1,2,3,4,5,6,7,8,9,10,11],     (12,12,12,12,12,6),    'Chromatic Scale/Dodecamirror (111111111111)']]

