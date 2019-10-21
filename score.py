from cmat.basic   import C
from cmat.quality import major

# comments

class MBR(object):

    from cmat.basic import Quarters
    
    @property
    def measure(self):
        return self._measure

    @property
    def beat(self):
        return self._beat

    @property
    def remnant(self):
        return self._remnant

    def __init__(self,measure,beat=1,remnant=Quarters(0)):

        from numbers import Real
        from cmat.basic import Quarters

        self._measure = measure
        self._beat    = beat

        if type(remnant) is Quarters:
            self._remnant = remnant
        elif hasattr(remnant,'quarters'):
            self._remnant = remnant.quarters
        elif isinstance(remnant,Real):
            self._remnant = Quarters(remnant)
        else:
            raise TypeError('requires numerical remnant.')

    def __str__(self):
        if self.remnant == 0:
            remnant = '0'
        else:
            remnant = '{}/{}'.format(self.remnant.numerator,
                                     self.remnant.denominator)
        return '{}:{}:{}'.format(self.measure,self.beat,remnant)

    def __repr__(self):
        return str(self)

    def __eq__(self,other):
        if type(other) is MBR:
            return self.measure == other.measure \
               and self.beat    == other.beat    \
               and self.remnant == other.remnant
        else:
            return False

    def __gt__(self,other):
        if self.measure > other.measure:
            return True
        elif self.measure < other.measure:
            return False
        elif self.beat > other.beat:
            return True
        elif self.beat < other.beat:
            return False
        elif self.remnant > other.remnant:
            return True
        else:
            return False

    def __ge__(self,other):
        if self.measure > other.measure:
            return True
        elif self.measure < other.measure:
            return False
        elif self.beat > other.beat:
            return True
        elif self.beat < other.beat:
            return False
        elif self.remnant >= other.remnant:
            return True
        else:
            return False

    def __lt__(self,other):
        if self.measure < other.measure:
            return True
        elif self.measure > other.measure:
            return False
        elif self.beat < other.beat:
            return True
        elif self.beat > other.beat:
            return False
        elif self.remnant < other.remnant:
            return True
        else:
            return False

    def __le__(self,other):
        if self.measure < other.measure:
            return True
        elif self.measure > other.measure:
            return False
        elif self.beat < other.beat:
            return True
        elif self.beat > other.beat:
            return False
        elif self.remnant <= other.remnant:
            return True
        else:
            return False

class Meter(object):

    @property
    def count(self):
        return self._count

    @property
    def size(self):
        return self._size

    @property
    def bar_length(self):
        return self.size * self.count
        
    @property
    def copy(self):
        return Meter(self.count,self.size)

    def __init__(self,count,size):

        from cmat.basic import NoteType

        self._count = count
        if isinstance(size,int):
            self._size = NoteType(4/size)
        elif isinstance(size,NoteType):
            self._size  = size
        else:
            raise TypeError('beat size requires int or NoteType.')

    def __str__(self):

        from cmat.duration import whole

        count = str(self.count)
        size  = str(int(whole/self.size))
        return '{}/{}'.format(count,size)

    def __repr__(self):
        return str(self)

class Key(object):

    from cmat.quality import major

    @property
    def tonic(self):
        return self._tonic

    @property
    def mode(self):
        return self._mode

    @property
    def copy(self):
        return Key(self.tonic,self.mode)

    def __init__(self,tonic,mode=major):
        self._tonic = tonic
        self._mode  = mode if mode is not None else major

    def __str__(self):
        return '{} {}'.format(str(self.tonic),str(self.mode))

    def __repr__(self):
        return str(self)

class Note(object):
    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self,dur):

        from cmat.basic import NoteType, Duration

        if isinstance(dur,NoteType):
            self._duration = Duration(dur)
        else:
            self._duration = dur

    @property
    def copy(self):
        return Note(self.duration.copy,self.pitch)

    def __init__(self,dur,pitch):

        from cmat.basic import Duration

        self.pitch = pitch
        self._duration = dur if isinstance(dur,Duration) else Duration(dur)

    def __str__(self):

        return ' '.join([str(s) for s in (self.duration,self.pitch)])

    def __repr__(self):
        return str(self)


class Rest(object):
    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self,dur):

        from cmat.basic import NoteType

        if isinstance(dur,NoteType):
            self._duration = Duration(dur)
        else:
            self._duration = dur

    @property
    def copy(self):
        return Rest(self.duration.copy)

    def __init__(self,dur):

        from cmat.basic import Duration

        self._duration = dur if type(dur) is Duration else Duration(dur)

    def __str__(self):
        return '{} rest'.format(self.duration)

    def __repr__(self):
        return str(self)

class Stream(object):

    _priority = {Key:0,Meter:1,Note:2,Rest:3}

    @property
    def end(self):

        from cmat.basic import Quarters

        if len(self) == 0:
            return Quarters(0)

        end = Quarters(0)
        for i in self:
            stop = i.position + i.duration if hasattr(i,'duration') else i.position
            if end < stop:
                end = stop

        return end

    def append(self,item):
        self.insert(self.end,item)

    def insert(self,position,item):

        item.position = position

        for idx,itm in enumerate(self):
            if itm.position >= position and self._priority[type(itm)] >= self._priority[type(item)]:
                break
        else:
            idx = len(self)

        self.items.insert(idx,item)

    def remove(self,item):
        self.items.remove(item)

    def filter(self,criteria):

        s = Stream()

        for item in self:
            if criteria(item):
                s.insert(item.position,item)

        return s

    def sort(self):
        self.items.sort(key=lambda x: x.position+self._priority[type(x)]/1000)

    def __init__(self, *items):
        self.items = []
        for item in items:
            self.append(item)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self,item):
        return item in self.items

    def __str__(self):
        
        if len(self) == 0: return ''
        
        col1 = [len(str(i.position)) for i in self]
        col2 = [len(str(i.duration)) if hasattr(i,'duration') else 0 for i in self]
        col3 = [len(str(i)) - col2[c] for c,i in enumerate(self)]
        
        wid1 = max(col1)
        wid2 = max(col2)
        wid3 = max(col3)
        
        lines = []
        
        for c,item in enumerate(self):
            pos = '{:<{width}}'.format(str(item.position),width=wid1)
            dur = '{:>{width}}'.format(str(item.duration),width=wid2) \
                if hasattr(item,'duration') else ' '*wid2
            rst = '{:>{width}}'.format(str(item)[col2[c]:],width=wid3)
            
            lines.append('{} {} {}'.format(pos,dur,rst))
        return '\n'.join(lines)
    
    def __repr__(self):
        return str(self)
    
    def __getitem__(self,index):

        if isinstance(index,slice):
            return self.filter(lambda i: index.start<=i.position<index.stop)
        else:
            s = self.filter(lambda i: i.position==index).items
            if len(s) == 0:
                return None
            elif len(s) == 1:
                return s[0]
            else:
                return s


class System(object):

    def get_meter(self,position):
        chk = 'mbr' if isinstance(position,MBR) else 'position'
        org = MBR(1) if isinstance(position,MBR) else 0
        for m in reversed(self.meters.items):
            if getattr(m,chk) < position:
                return m
            elif getattr(m,chk) == org:
                return m
        else:
            return None

    def get_key(self,position):
        chk = 'mbr' if isinstance(position,MBR) else 'position'
        org = MBR(1) if isinstance(position,MBR) else 0
        for k in reversed(self.keys):
            if getattr(k,chk) < position:
                return k
            elif getattr(k,chk) == org:
                return k
        else:
            return None        

    def set_meter(self,measure,meter):
        from cmat.basic import Quarters

        mbr = MBR(measure)
        pos = Quarters(0) if measure == 1 else self.translate(mbr)

        meter.mbr = mbr
        existed = self.meters[pos]
        if existed is not None:
            self.meters.items.remove(existed)
            
        self.meters.insert(pos,meter)

        # adjust measure boudary of followed keys&meters
        for m in self.meters:
            if m.position > meter.position:
                next = m
                break
        else:
            next = None

        if next is not None:
            shift = -(next.position-meter.position)%meter.bar_length

            for k in self.keys.filter(lambda k: meter.position<k.position<next.position):
                k.position += -(k.position-meter.position)%meter.bar_length
                k.mbr = self.translate(k.position)

            for k in self.keys.filter(lambda k: k.position >= next.position):
                k.position += shift
                k.mbr = self.translate(k.position)
            for m in self.meters.filter(lambda m: m.position >= next.position):
                m.position += shift
                m.mbr = self.translate(m.position)

        else:
            shift = Quarters(0)

            for k in self.keys.filter(lambda k: k.position > meter.position):
                k.position += -(k.position-meter.position)%meter.bar_length
                k.mbr = self.translate(k.position)

        return shift

    def set_key(self,measure,key):
        from cmat.basic import Quarters

        mbr = MBR(measure)
        pos = Quarters(0) if measure == 1 else self.translate(mbr)
        
        key.mbr = mbr
        existed = self.keys[pos]
        if existed is not None:
            self.keys.items.remove(existed)
        self.keys.insert(pos,key)


    def translate(self,position):
        meter = self.get_meter(position)
        
        if meter is None:
            raise RuntimeError('No reference meter found.')

        beat_size  = meter.size
        bar_length = meter.bar_length

        meter_pos  = meter.position
        meter_mbr  = meter.mbr

        if isinstance(position,MBR):
            mbr = position
            position = meter_pos

            position += bar_length * (mbr.measure-meter_mbr.measure)
            position += beat_size  * (mbr.beat - meter_mbr.beat)
            position += mbr.remnant

            return position

        else:
            distance = position - meter_pos
            m = distance // bar_length
            b = (distance % bar_length) // beat_size
            r = (distance % bar_length) %  beat_size

            return MBR(meter_mbr.measure+m,meter_mbr.beat+b,meter_mbr.remnant+r)


    def remove(self,item):
        if type(item) is Key:
            self.keys.remove(item)
        elif type(item) is Meter:
            meter = self.get_meter(item.position)
            self.set_meter(meter.mbr.measure,meter)
            self.meters.remove(meter)

    def __init__(self,key=Key(C,major),meter=Meter(4,4)):
        self.meters = Stream()
        self.keys   = Stream()

        self.set_key(1,key)
        self.set_meter(1,meter)
        
    def __str__(self):
        
        from itertools import chain
        col1 = max([len(str(i.mbr)) for i in chain(self.keys,self.meters)])
        col2 = max([len(str(i)) for i in chain(self.keys,self.meters)])
        
        lines = []
        for item in self:
            lines.append('{:<{wd1}} {:>{wd2}}'.format(str(item.mbr),str(item),wd1=col1,wd2=col2))
        return '\n'.join(lines)
        
    def __repr__(self):
        return str(self)
        
    def __iter__(self):
        from itertools import chain
        items = list(chain(self.keys,self.meters))
        items.sort(key=lambda x: x.position)
        
        return iter(items)

class Voice(Stream):

    @property
    def end(self):
        return self.system.translate(super().end)
        
    @property
    def voice_number(self):
        return self._voice_number
        
    @property
    def copy(self):
        v = Voice(vc=self.voice_number,sys=self.system)
        for item in self:
            v.insert(item.posoition,item)
        return v
        
    def append(self,item):
        self.insert(self.end,item)
    
    def insert(self,pos,item):

        if self._is_occupied(pos,item):
            raise RuntimeError('collided with existed items.')
        '''
        for item in self:
            if item.position > pos:
                insert_point = self.items.index(item)
        else:
            insert_point = len(self.items)
        '''
        supe().insert(pos,item)
        
    def remove(self,item):
        self.items.remove(item)

    def _is_occupied(self,position,item):
        p1 = p2 = self.system.translate(position)
        if hasattr(item,'duration'):
            p2 = p2+item.duration

        for i in self:
            p3 = p4 = self.system.translate(i.position)
            if hasattr(i,'duration'):
                p4 = p4+i.duration

            if self._is_colliding(p1,p2,p3,p4):
                return i
        else:
            return False

    def _is_colliding(self,p1,p2,p3,p4):
        if p1 < p3 < p2 or p1 < p4 < p2:
            return True
        if p3 < p1 < p4 or p3 < p2 < p4:
            return True
        return False4

    def __init__(self,vc=1,sys=None):
        self._voice_number = vc
        self.system = System() if sys is None else sys
        super().__init__()
        


