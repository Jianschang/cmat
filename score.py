from numbers        import Real
from collections    import namedtuple
from collections.abc import Iterable
from fractions      import Fraction
from itertools      import chain
from re             import match

from cmat.basic     import Quarters,NoteType,Duration,C
from cmat.duration  import whole
from cmat.quality   import major

__all__ = ['MBR','Key','Meter','Note','Rest','Chord',
           'Metrical','Stream','Voice','Part','Score']

MAXIMUM = 256


def _extract(self,*args,**kw):

    args = list(args)
    types = [int,float,Fraction,Quarters,MBR,type(None)]

    pos = []
    while len(args)>0 and type(args[0]) in types:
        if len(pos) == 3: break
        pos.append(args.pop(0))

    if len(pos) == 0:
        pos = None
    elif type(pos[0]) in [MBR,Quarters,type(None)]:
        pos = pos[0]
    elif type(pos[0]) is int:
        pos = MBR(*pos)
    else:
        pos = Quarters(*pos)

    args.insert(0,pos)

    return args,kw

def adapt_to_quarters(func):

    def wrapper(self,*args,**kw):
        args,kw = _extract(self,*args,**kw)

        if isinstance(args[0],MBR):
            args[0] = self.system.translate(args[0])

        return func(self,*args,**kw)

    return wrapper

def adapt_to_mbr(func):

    def wrapper(self,*args,**kw):
        args,kw = _extract(self,*args,**kw)

        if isinstance(args[0],Quarters):
            args[0] = self.system.translate(args[0])

        return func(self,*args,**kw)

    return wrapper

def adapt_to_position(func):

    def wrapper(self,*args,**kw):
        args,kw = _extract(self,*args,**kw)
        return func(self,*args,**kw)

    return wrapper

class MBR(object):
    @property
    def measure(self): return self._m

    @property
    def beat(self): return self._b

    @property
    def remnant(self): return self._r

    @property
    def tuple(self):
        return (self.measure,self.beat,self.remnant)

    @property
    def size(self):
        return [len(str(n)) for n in self.tuple]

    def format(self,size):
        m,b,r = self.tuple
        ms,bs,rs = size
        return '{:>{}}:{:>{}}:{:<{}}'.format(m,ms,b,bs,r,rs)

    def __init__(self,measure,beat=1,remnant=Fraction(0)):
        self._m = measure
        self._b = beat
        self._r = remnant

    def __str__(self):
        return '{}:{}:{}'.format(self.measure,self.beat,self.remnant)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self,other):
        if other is None:
            return False
        else:
            return self.tuple == other.tuple

    def __gt__(self,other):
        return self.tuple > other.tuple

    def __lt__(self,other):
        return self.tuple < other.tuple

    def __ge__(self,other):
        return self > other or self == other

    def __le__(self,other):
        return self < other or self == other

class StreamItem(object):

    @property
    def priority(self):

        priorities = {Key:0,Meter:1,Note:2,Chord:3,Rest:4,StreamItem:MAXIMUM}
        try:
            p = priorities[self.type]
        except KeyError:
            p = MAXIMUM

        return p

    @property
    def type(self):
        return self.__class__

    @property
    def position(self):
        if self.site is None or isinstance(self.site,Metrical) is False:
            return self.quarters
        else:
            return self.mbr

    @position.setter
    @adapt_to_position
    def position(self,pos):
        if isinstance(pos,MBR):
            self.mbr = pos
        else:
            self.quarters = pos

    @property
    def quarters(self):
        return self._q

    @quarters.setter
    def quarters(self,quar):
        self._q = quar
        if self.site is not None and isinstance(self.site,Metrical) is True:
            self.synchronize()

    @property
    def mbr(self):
        return self._m

    @mbr.setter
    def mbr(self,mbr):
        self._m = mbr
        self.synchronize(reversed=True)

    def synchronize(self,reversed=False):
        if self.site is not None and isinstance(self.site,Metrical) is True:
            if reversed:
                self._q = self.site.system.translate(self.mbr)
            else:
                self._m = self.site.system.translate(self.quarters)

    def dump(self,attr_paths):
        texts = []
        for path in attr_paths:
            for opt in path.split('/'):
                node  = self
                nodes = opt.split('.')

                while len(nodes) > 0:
                    if nodes[0] == 'self':
                        nodes = ['self']
                    elif nodes[0] == 'rest' and self.type is Rest:
                        nodes = ['rest']
                    else:
                        try:
                            node = getattr(node,nodes[0])
                        except AttributeError:
                            node  = None
                            nodes = [nodes[0]]
                    name = nodes.pop(0)

                if node is not None: break

            if name == 'dots':
                t = {0:'',1:'dotted',2:'double dotted',3:'triple dotted'}[node]
            elif name == 'rest':
                t = 'rest'
            else:
                t = '' if node is None else str(node)

            texts.append(t)

        return texts

    def __init__(self):

        self._q = None
        self._m = None

        self.site = None

    def __str__(self):
        return 'StreamItem Abstract Class'

    def __repr__(self):
        return str(self)


class Note(StreamItem):

    @property
    def priority(self):
        v = self.voice if hasattr(self,'voice') else MAXIMUM
        p = self.pitch
        return (self.quarters,super().priority,v,-p.number,-p.MIDI)

    @property
    def duration(self):
        return self._d

    @duration.setter
    def duration(self,dur):
        self._d = dur if isinstance(dur,Duration) else Duration(dur)

    @property
    def copy(self):
        return Note(self.duration.copy,self.pitch)

    def __init__(self,dur,pitch):

        super(Note,self).__init__()

        self.duration = dur
        self.pitch = pitch

    def __str__(self):
        return '{} {}'.format(self.duration,self.pitch)



class Chord(StreamItem):
    pass

class Rest(StreamItem):

    @property
    def priority(self):
        v = self.voice if hasattr(self,'voice') else MAXIMUM
        return (self.quarters,super().priority,v)

    @property
    def duration(self):
        return self._d

    @duration.setter
    def duration(self,dur):
        self._d = dur if isinstance(dur,Duration) else Duration(dur)

    @property
    def copy(self):
        return Rest(self.duration.copy)

    def __init__(self,dur):

        super(Rest,self).__init__()

        self.duration = dur

    def __str__(self):
        return '{} rest'.format(self.duration)

class Key(StreamItem):

    @property
    def priority(self):
        return (self.quarters,super().priority)

    @property
    def tonic(self):
        return self._t

    @property
    def mode(self):
        return self._mod

    @property
    def copy(self):
        return Key(self.tonic,self.mode)

    def __init__(self,tonic,mode=major):

        super(Key,self).__init__()

        self._t = tonic
        self._mod = mode

    def __str__(self):
        return '{} {}'.format(self.tonic,self.mode)

    def __eq__(self,tonality):
        if isinstance(tonality,Key):
            return self.tonic == tonality.tonic and self.mode == tonality.mode
        else:
            return False

class Meter(StreamItem):

    @property
    def priority(self):
        return (self.quarters,super().priority)

    @property
    def count(self):
        return self._c

    @property
    def beat(self):
        return self._b

    @property
    def bar_length(self):
        return self.beat * self.count

    @property
    def copy(self):
        return Meter(self.count,self.beat)

    def __init__(self,count,beat):

        super(Meter,self).__init__()

        self._c = count

        if isinstance(beat,int):
            self._b = NoteType(4/beat)
        else:
            self._b = beat

    def __str__(self):
        return '{}/{}'.format(self.count,int(whole/self.beat))

    def __eq__(self,meter):
        if isinstance(meter,Meter):
            return self.count == meter.count and self.beat == meter.beat
        else:
            return False


class Metrical(object):

    class Measure(object):

        def __init__(self,site):
            self.site = site

        def __getitem__(self,num):
            if isinstance(num,int):
                return self.site.filter(lambda i:i.mbr.measure == num)
            elif isinstance(num,Iterable):
                return self.site.filter(lambda i:i.mbr in num)
            elif isinstance(num,slice):
                rang = list(range(num.start,num.stop,num.step))
                return self.iste.filter(lambda i:i.mbr in rang)
            else:
                raise IndexError('invalid measure number.')

        def __str__(self):
            first = self.site.first.mbr.measure
            end   = self.site.last.mbr.measure
            return 'Measure from {} to {}.'.format(first,end)

        def __repr__(self):
            return str(self)

    @property
    def system(self):
        return self._system

    @system.setter
    def system(self,stream):

        if self.system is not None: self.system.site.remove(self)
        self._system = stream

        if stream is not None: stream.site.append(self)

        self.synchronize()

    def synchronize(self,reversed=False):
        for i in self:i.synchronize(reversed)

    def quantize(self,grid):

        if self.system is None:
            return

        for i in self:
            i._q = self.system.griding(i.quarters,grid).quarters

        self.synchronize()

    def __init__(self):

        super(Metrical,self).__init__()

        self._system = None
        self.measures = Metrical.Measure(self)

class Stream(object):

    @property
    def count(self):
        return len(self)

    @property
    def starting(self):
        return self.first.quarters if self.count > 0 else Quarters(0)

    @property
    def end(self):
        endpoints = [i.quarters+i.duration if hasattr(i,'duration') else i.quarters
                                            for i in self]
        return max(endpoints) if len(endpoints) > 0 else Quarters(0)

    @property
    def copy(self):
        pass

    @property
    def items(self):
        return self._items

    @property
    def first(self):
        return self.items[0]

    @property
    def last(self):
        return self.items[-1]

    @adapt_to_quarters
    def insert(self,position,item):
        if position is None:
            if item.quarters is None:
                raise RuntimeError('insert position was not specified.')
            else:
                position = item.quarters

        if item.site is None: item.site = self
        if item.quarters != position: item.quarters = position

        for i in self:
            if i.priority >= item.priority:
                self.items.insert(self.items.index(i),item)
                break
        else:
            self.items.append(item)

    def remove(self,item):
        self.items.remove(item)

    def append(self,item):
        self.insert(self.end,item)

    def find(self,criteria):
        for i in self:
            try:
                if criteria(i): return i
            except:
                continue
        else:
            return None

    def rfind(self,criteria):
        for i in reversed(self.items):
            try:
                if criteria(i): return i
            except:
                continue
        else:
            return None

    def filter(self,criteria):
        s = self.__class__()
        s._system = self.system

        for i in self:
            try:
                if criteria(i): s.items.append(i)
            except:
                continue

        return s

    @adapt_to_quarters
    def since(self,position):
        return self.filter(lambda i:i.quarters >= position)

    @adapt_to_quarters
    def until(self,position):
        if position == 0:
            return self.filter(lambda i:i.quarters <= position)
        else:
            return self.filter(lambda i:i.quarters < position)

    def sort(self):
        self.items.sort(key=lambda i:i.priority)

    def shift(self,distance):
        for i in self:
            i.quarters += distance

    def quantize(self,grid):
        for i in self:
            dev = i.quarters % grid
            if dev > grid / 2:
                i.quarters += grid-dev
            else:
                i.quarters -= dev

    def dump(self,attributes,pos_reserved=[],alignment=None):

        num_cols = len(attributes)
        if alignment is None: alignment = '<' * num_cols

        rows = []
        pos   = pos_reserved
        items = self.items
    
        pi,pc = 0,len(pos)
        ii,ic = 0,len(items)

        while pi < pc or ii < ic:

            if ii >= ic and pi < pc or pi < pc and pos[pi] < items[ii].position:
                rows.append([''] * num_cols)
                pi += 1
            else:
                rows.append(items[ii].dump(attributes))
                if pi < pc and pos[pi] == items[ii].position:
                    pi += 1
                ii += 1

        # matrix rotation
        columns = list(zip(*rows))

        # formatting
        formatted = []
        for attr,col,alg in zip(attributes,columns,alignment):

            # skip empty column
            if all([i=='' for i in col]): continue

            # position column
            if attr in ('position','quarters','mbr'):

                formatted.append(_position_format(col))

            else:
                # other fields
                w = max([len(cell) for cell in col])
                formatted.append(['{:{a}{w}}'.format(c,a=alg,w=w) for c in col])

        return formatted

    def __init__(self):

        super(Stream,self).__init__()

        self._items = []
        self.site = None

    def __getitem__(self,index):

        if isinstance(index,slice):
            start,stop,step = index.start,index.stop,index.step
            if start > 0: start -= 1
            if stop  > 0: stop  -= 1
            return self.items[start:stop:step]

        elif isinstance(index,int):
            if index > 0: index -= 1
            return self.items[index]

        else:
            return self.items[index]

    def __contains__(self,item):
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __str__(self):

        attrs = ['position','duration.dots','duration.base','duration.tuplet',
                 'pitch/rest/pitches/self']

        align = '<>><>'

        texts = self.dump(attrs,alignment=align)
        texts = [' '.join(fields) for fields in zip(*texts,)]
        return '\n'.join(texts)

    def __repr__(self):
        return str(self)

class System(Metrical,Stream):

    @property
    def keys(self):
        return self.filter(lambda i:i.type is Key)

    @property
    def meters(self):
        return self.filter(lambda i:i.type is Meter)

    @adapt_to_position
    def get_context(self,position):

        Context = namedtuple('Context',['key','meter'])

        if isinstance(position,MBR):
            if position == MBR(1):
                key=self.rfind(lambda i:i.type is Key and i.mbr <= position)
                meter=self.rfind(lambda i:i.type is Meter and i.mbr<=position)
            else:
                key=self.rfind(lambda i:i.type is Key and i.mbr < position)
                meter=self.rfind(lambda i:i.type is Meter and i.mbr < position)
        else:
            if position == Quarters(0):
                key=self.rfind(lambda i:i.type is Key and i.quarters <= position)
                meter=self.rfind(lambda i:i.type is Meter and i.quarters <= position)
            else:
                key=self.rfind(lambda i:i.type is Key and i.quarters < position)
                meter=self.rfind(lambda i:i.type is Meter and i.quarters < position)

        return Context(key,meter)

    @adapt_to_position
    def translate(self,position):

        if isinstance(position,MBR) and position == MBR(1): return Quarters(0)
        if isinstance(position,Quarters) and position == Quarters(0): return MBR(1)

        meter = self.get_context(position).meter
        if meter is None: raise RuntimeError('meter was not found.')

        b = meter.bar_length
        t = meter.beat.quarters
        r = meter.quarters

        if isinstance(position,MBR):

            r += b * (position.measure-meter.mbr.measure)
            r += t * (position.beat - 1)
            r += t *  position.remnant

            return r

        elif isinstance(position,Quarters):

            d = position - r
            m = d // b + meter.mbr.measure
            b = d  % b // t + 1
            r = Fraction(d%t,t).limit_denominator()

            return MBR(m,b,r)

    @adapt_to_quarters
    def griding(self,position,grid):

        Position = namedtuple('Position',['quarters','mbr'])

        m = self.system.get_context(position).meter

        if isinstance(grid,Quarters):
            g = grid
        elif isinstance(grid,NoteType):
            g = grid.quarters
        elif isinstance(grid,str):
            if grid.lower() == 'measure':
                g = m.bar_length
            elif grid.lower() == 'beat':
                g = m.beat.quarters
            else:
                raise ValueError('unrecognized grid setting.')
            d = position - m.quarters

        dev = d % g
        if dev > g/2:
            position += (g-dev)
        else:
            position -= dev

        return Position(position,self.system.translate(position))

    @adapt_to_quarters
    def insert(self,position,item):
        existed = self.find(lambda i:i.type is item.type and i.quarters == position)
        if existed is not None: self.items.remove(existed)

        super().insert(position,item)

        if item.type is Meter:

            next = self.find(lambda i:i.type is Meter and i.quarters > position)
            if next is not None:
                split = next.quarters
                shift = -(split-position)%item.bar_length
                for s in self.site:
                    s.since(split).shift(shift)
                self.since(position).until(split).quantize('measure')
            else:
                self.since(position).quantize('measure')

            for s in self.site:
                s.synchronize()

    def remove(self,item):
        super().remove(item)

        if item.type is Meter:

            next = self.find(lambda i:i.type is Meter and i.quarters>item.quarters)
            prev = self.find(lambda i:i.type is Meter and i.quarters<item.quarters)

            if prev is not None:
                if next is not None:
                    split = next.quarters
                    shift = -(split-prev.quarters)%prev.bar_length
                    for s in self.site:
                        s.since(split).shift(shift)
                    self.since(item.quarters).until(split).quantize('measure')
                else:
                    self.since(item.quarters).quantize('measure')

        for s in self.site:
            s.synchronize()

    def filter(self,criteria):
        s = System(None,None)
        s._system = self.system

        for i in self.items:
            try:
                if criteria(i):
                    s.items.append(i)
            except:
                continue

        return s

    def __init__(self,key=Key(C,major),meter=Meter(4,4)):

        super(System,self).__init__()

        self.site = []
        self.system = self

        if key is not None:
            key.site = self
            key._q   = Quarters(0)
            key._m   = MBR(1)
            self.items.append(key)

        if meter is not None:
            meter.site = self
            meter._q   = Quarters(0)
            meter._m   = MBR(1)
            self.items.append(meter)

class Voice(Metrical,Stream):
    @property
    def number(self):
        return self._number

    @number.setter
    def number(self,num):
        self._number = num
        for i in self: i.voice = num

    @adapt_to_quarters
    def insert(self,position,item):

        item.voice = self.number
        super().insert(position,item)

        head = tail = item.quarters
        if hasattr(item,'duration'): tail += item.duration.quarters

        collied = []

        for i in self:

            if i is item: continue

            begin = end = i.quarters
            if hasattr(i,'duration'): end += i.duration

            if head  <= begin <  tail and begin < end or \
               head  <  end   <  tail or \
               begin <= head  <  end  or \
               begin <  tail  <= end  and head < tail:
                collied.append(i)

        for i in collied: self.remove(i)

    def filter(self,criteria):

        v = Voice(num=self.number)
        v._system = self.system

        for i in self:
            try:
                if criteria(i):
                    v.items.append(i)
            except:
                continue

        return v

    def __init__(self,num=1,sys=None):
        super(Voice,self).__init__()

        self._number = num
        self.system  = System() if sys is None else sys

    def __str__(self):

        sys = self.system.since(self.starting).until(self.end)
        s   = Stream()
        s._items = self.items + sys.items
        s.sort()

        attrs = ['position','duration.dots','duration.base','duration.tuplet',
                 'pitch/rest/pitches/self']

        align = '<>><>'

        texts = s.dump(attrs,alignment=align)
        texts = [' '.join(fields) for fields in zip(*texts,)]

        return '\n'.join(texts)

class Part(Metrical,Stream):

    class VoicesList(object):

        def keys(self):
            return self._voices.keys()

        def values(self):
            return self._voices.values()

        def items(self):
            return self._voices.items()

        def condense(self):
            empty = []
            for n in self.keys():
                if self[n].count == 0:
                    empty.append(n)

            for n in empty:
                del self._voices[n]

        def __init__(self,site):
            self._voices = {}
            self.site = site

        def __getitem__(self,num):
            if isinstance(num,int):
                try:
                    return self._voices[num]
                except KeyError:
                    self._voices[num] = Voice(num=num,sys=self.site.system)
                    return self._voices[num]
            elif isinstance(num,Iterable):
                p = Part(name=self.site.name,sys=self.site.system)
                for n in num:
                    p.voices[n] = self.site.voices[n]
                return p
            elif isinstance(num,slice):
                p = Part(name=self.site.name,sys=self.site.system)
                for n in range(num.start,num.stop,num.step):
                    p.voices[n] = self.site.voices[n]
                return p
            else:
                raise KeyError('invalid voice number.')

        def __setitem__(self,num,voice):
            voice.system = self.site.system
            self._voices[num] = voice

        def __delitem__(self,num):
            if self[num] in self.site.system.site:
                self.site.system.site.remove(self[num])
            del self._voices[num]

        def __iter__(self):
            return iter(self._voices)

        def __str__(self):
            numbers = ','.join([str(n) for n in self._voices.keys()])
            return 'Voices:%s' % numbers

        def __repr__(self):
            return str(self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,name):
        self._name = name

    @property
    def instrument(self):
        return self._inst

    @instrument.setter
    def instrument(self,name):
        self._inst = name

    @property
    def system(self):
        return self._system

    @system.setter
    def system(self,stream):

        self._system = stream

        for v in self.voices.values():
            v.system = stream

    @property
    def items(self):
        items = list(chain(*self.voices.values()))
        items.sort(key=lambda i:i.priority)
        return items

    @adapt_to_quarters
    def insert(self,position,item,voice=1):
        try:
            self.voices[voice].insert(position,item)
        except:
            self.voices[voice] = Voice(num=voice,sys=self.system)
            self.voices[voice].insert(position,item)

    def remove(self,item):
        v = self.voices[item.voice]
        v.remove(item)
        if v.count == 0:
            del self.voices[item.voice]
            v.system = None

    def append(self,item,voice=1):
        try:
            self.voices[voice].insert(self.voices[voice].end,item)
        except KeyError:
            self.voices[voice] = Voice(num=voice,sys=self.system)
            self.voices[voice].insert(self.voices[voice].end,item)

    def filter(self,criteria):

        p = Part(name=self.name,sys=self.system)
        for n,v in self.voices.items():
            p.voices[n] = v.filter(criteria)
        p.voices.condense()
        return p

    def __init__(self,name=None,sys=None):
        super(Part,self).__init__()
        self._name  = name
        self.voices = Part.VoicesList(self)
        self.system = System() if sys is None else sys

    def __str__(self):

        # positions for all items
        positions  = list(set([i.position for i in self.items]))
        positions.sort()

        # item dumps
        columns = []
        attributes = ['duration.dots','duration.base','duration.tuplet',
                      'pitch/pitches/rest/self']

        alignments = '>><>'

        numbers = list(self.voices.keys())
        numbers.sort()

        for n in reversed(numbers):
            texts = self.voices[n].dump(attributes,pos_reserved=positions,
                                                     alignment=alignments)
            columns.append([' '.join(fields) for fields in zip(*texts,)])

        # remove empty column
        columns = [col for col in columns if len(col) > 0]

        # combine item data columns
        texts = [' '.join(cols) for cols in zip(*columns,)]

        # get position and text of system track
        sys = self.system.since(self.starting).until(self.end)
        sys_pos = [i.position for i in sys]
        sys_str = [str(i) for i in sys]

        # blending sys and part items
        for pos in positions:
            if len(sys_pos) == 0: break
            if pos >= sys_pos[0]:
                for idx in range(len(positions)):
                    if positions[idx] is pos: break
                positions.insert(idx,sys_pos.pop(0))
                texts.insert(idx,sys_str.pop(0))

        positions += sys_pos
        texts += sys_str

        if len(texts)>0:
            max_width = max([len(s) for s in texts])
            texts = [s.rjust(max_width) for s in texts]
        else:
            return ''

        # formatted position texts
        fd_pos = _position_format([str(p) for p in positions])

        # combine pos and texts
        texts = [' '.join([p,t]) for p,t in zip(fd_pos,texts)]
        return '\n'.join(texts)

class Score(Metrical,Stream):

    def items(self):
        pass

def _position_format(texts):

    # formatting position texts
    parts = []

    for c in chain(*texts):
        if c == ':' or c == '.' or c == "'": break
    else:
        return ''

    if c == ':':
        # mbr format
        for text in texts:
            if text == '' or text.isspace():
                fields = ['','','']
            else:
                fields = text.split(':')
            parts.append(fields)

        m,b,r=[max(w)for w in zip(*[[len(f)for f in entry]for entry in parts])]
        layout = '{:0>%d}:{:0>%d}:{:<%d}' % (m,b,r)
        texts = [' '*(m+b+r+2) if part[0]=='' else layout.format(*part)
                    for part in parts]
    else:
        # quarters format
        for text in texts:
            if text == '' or text.isspace():
                p1,p2 = '',''
            else:
                p1 = text.split('.')[0].split("'")[0]
                w1 = len(p1)
                p2 = '.0' if p1 == text else text[w1:]
            parts.append([p1,p2])

        i,d=[max(w)for w in zip(*[[len(f)for f in entry] for entry in parts])]
        layout = '{:0>%d}{:<%d}' % (i,d)
        texts = [' '*(i+d) if part[0] == '' else layout.format(*part)
                    for part in parts]

    return texts

