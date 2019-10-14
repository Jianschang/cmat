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
            return s[0] if len(s)==1 else s


class System(object):

    def get_meter(self,position):
        chk = 'mbr' if isinstance(position,MBR) else 'position'

        for m in reversed(self.meters.items):
            if getattr(m,chk) < position:
                return m
        else:
            return None

    def get_key(self,position):
        chk = 'mbr' if isinstance(position,MBR) else 'position'
        
        for k in reversed(self.keys):
            if getattr(k,chk) < position:
                return k
        else:
            return None        

    def set_meter(self,measure,meter):
        from cmat.basic import Quarters

        mbr = MBR(measure)
        pos = Quarters(0) if measure == 1 else self.translate(mbr)

        meter.mbr = mbr
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
            self.meters.remove(item)

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

        i = j = 0

        k = self.keys.items
        m = self.meters.items

        kl = len(k)
        ml = len(m)

        while i < kl or j < ml:

            if i >= kl:
                item = m[j]
                j += 1
            elif j >= ml:
                item = k[i]
                i += 1
            elif k[i].position <= m[j].position:
                item = k[i]
                i += 1
            else:
                item = m[j]
                j += 1

            s = '{:<{wd1}} {:>{wd2}}'.format(str(item.mbr),str(item),
                                                        wd1=col1,wd2=col2)
            lines.append(s)

        return '\n'.join(lines)
        
    def __repr__(self):
        return str(self)

'''
class Stream(object):

    @property
    def end(self):

        from cmat.basic import Quarters

        if len(self) == 0:
            return Quarters(0)

        endings = []
        for i in self:
            if hasattr(i,'duration'):
                endings.append(i.position+i.duration)
            else:
                endings.append(i.position)

        return max(endings)

    @property
    def first(self):
        return self[0] if len(self)>0 else None

    @property
    def last(self):
        return self[-1] if len(self)>0 else None

    @property
    def copy(self):
        c = Stream()
        
        for i in self:
            if hasattr(i,'copy'):
                c.insert(i.position,i.copy)
            else:
                c.insert(i.position,i)
        return c

    def append(self,*items):
        for item in items:
            self.insert(self.end,item)

    def insert(self,position,item):
        from cmat.basic import Quarters
        item.position = position if isinstance(position,Quarters) else Quarters(position)
        insert_index  = self.index(filter=lambda i: i.position>position)
        if insert_index is None: insert_index = len(self)
        self.items.insert(insert_index,item)

    def remove(self,item):
        self.items.remove(item)
        del  item.position

    def index(self,item=None,pos=None,type=None,filter=None,reverse=False):

        idxs = range(len(self))
        if reverse:
            idxs = reversed(idxs)

        for i in idxs:
            if item is not None and item is not self[i]:
                continue
            if pos  is not None and pos != self[i].position:
                continue
            if type is not None and not isinstance(self[i],type):
                continue
            if filter is not None and filter(self[i]) is not True:
                continue
            return i
        else:
            return None

    def filter(self,pos=None,type=None,filter=None):

        s = Stream()
        for i in range(len(self)):
            if pos  is not None and pos != self[i].position:
                continue
            if type is not None and not isinstance(self[i],type):
                continue
            if filter is not None and filter(self[i]) is not True:
                continue
            s.insert(self[i].position,self[i])
        return s

    def sort(self):
        self.items.sort(key=lambda i: i.position)

    def __init__(self,*items):
        self.items = []

        for item in self:
            self.append(item)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self,index):
        return self.items[index]

    def __setitem__(self,index,item):
        item.position     = self.items[index].position
        self.items[index] = item

        del self.items[index].position

    def __len__(self):
        return len(self.items)

    def __contains__(self,item):
        return item in self.items

    def __str__(self):
        lines = []
        if len(self) == 0: return ''
        col_pos_wd = max([len(str(i.position)) for i in self])
        col_dur_wd = max([len(str(i.duration)) for i in self if hasattr(i,'duration')])
        col_rst_wd = max([len(str(i).split(' ')[-1]) for i in self])
        
        for item in self:
            pos = '{:<{width}}'.format(str(item.position),width=col_pos_wd)
            dur = '{:>{width}}'.format(str(item.duration),width=col_dur_wd) \
                if hasattr(item,'duration') else ' '*col_dur_wd
            rst = '{:>{width}}'.format(str(item).split(' ')[-1],width=col_rst_wd)
            
            lines.append('{} {} {}'.format(pos,dur,rst))
        return '\n'.join(lines)

    def __repr__(self):
        return str(self)


    def _is_occupied(self,position,item):
        
        #is the space which will used for insertion occupied.
        #return occupied item if True, otherwise return False.
        
        p1 = p2 = position
        if hasattr(item,'duration'): p2 += item.duration

        for i in self:
            p3 = p4 = i.position
            if hasattr(i,'duration'): p4 += i.duration

            if self._is_colliding(p1,p2,p3,p4):
                return i
        else:
            return False

    def _is_colliding(self,p1,p2,p3,p4):
        
        whether two item are collding with each other: 
            item1 starts at p1 and end at p2,
            item2 starts at p3 and end at p4.
        
        if p1 < p3 < p2 or p1 < p4 < p2:
            return True
        if p3 < p1 < p4 or p3 < p2 < p4:
            return True
        return False

    def _has_collisions(self):
        from itertools import combinations
        collisions = []
        for i1,i2 in combinations(self,2):
            p1 = p2 = i1.position
            p3 = p4 = i2.position
            if hasattr(i1,'duration'): p2 += i1.duration
            if hasattr(i2,'duration'): p4 += i2.duration
            if self._is_colliding(p1,p2,p3,p4):
                collisions.append((i1,i2))
        return collisions
        

    def _exclude(self,position,item):
        pass

class System(Stream):

    @property
    def end(self):
        try:
            return self.translate(super().end)
        except RuntimeError:
            return MBR(1,1,0)

    @property
    def copy(self):
        c = System(key=None,meter=None)

        for i in self:
            if hasattr(i,'copy'):
                c.insert(i.mbr,i.copy)
            else:
                c.insert(i.mbr,i)
        return c

    def append(self,item):
        self.insert(self.end,item)

    def insert(self,pos,item):
        if isinstance(pos,MBR):
            item.mbr = pos
            try:
                pos = self.translate(pos)
            except RuntimeError:
                if hasattr(item,'position') and item.position is not None:
                    pos = item.position
                else:
                    raise RuntimeError('No available time signature for confirm the position')
        else:
            try:
                item.mbr = self.translate(pos)
            except RuntimeError:
                if not hasattr(item,'mbr') or item.mbr is None:
                    raise RuntimeError('No available itme signature for confirm the mbr.')
                    
        super().insert(pos,item)

    def remove(self,item):
        super().remove(item)
        del item.mbr

    def filter(self,pos=None,type=None,filter=None):
        s = System(key=None,meter=None)
        for it in self:
            if pos is not None and it.position != pos:
                continue
            if type is not None and not isinstance(it,type):
                continue
            if filter is not None and filter(it) is not True:
                continue
            s.insert(it.position,it)

        return s

    def get_key(self,pos):
        start = MBR(1,1,0)

        keys = self.filter(filter=lambda i: isinstance(i,Key))
        for k in reversed(keys):
            if isinstance(pos,MBR):
                if k.mbr == start or k.mbr < pos:
                    return k
            else:
                if k.position == 0 or k.position < pos:
                    return k
        else:
            return None

    def get_meter(self,pos):
        start = MBR(1,1,0)

        meters = self.filter(filter=lambda i: isinstance(i,Meter))
        for m in reversed(meters):
            if isinstance(pos,MBR):
                if m.mbr == start or m.mbr < pos:
                    return m
            else:
                if m.position == 0 or m.position < pos:
                    return m
        else:
            return None

    def set_key(self,measure,key):
        insert_point = MBR(measure)
        self.insert(insert_point,key)

    def set_meter(self,measure,meter):
        insert_point = MBR(measure)
        self.insert(insert_point,meter)

        next  = self.index(meter)+1
        shift = 0

        for i in range(next,len(self)):

            if isinstance(self[i],Meter):
                shift = -(self[i].position-meter.position)%(meter.size*meter.count)
                for item in self[i:]:
                    item.position += shift
                break
            elif self._priority[type(self[i])] < 2:
                shift = -(self[i].position-meter.position)%(meter.size*meter.count)
                self[i].position += shift
            else:
                self[i].position += shift

        for item in self[next:]:
            item.mbr = self.translate(item.position)



    def translate(self,pos):
        meter = self.get_meter(pos)
        if meter is None:
            raise RuntimeError('No available time signature for reference.')
            #return Quarters(0) if isinstance(pos,MBR) else MBR(1,1,0)

        beat_size  = meter.size
        bar_length = beat_size * meter.count

        meter_pos  = meter.position
        meter_mbr  = meter.mbr

        if isinstance(pos,MBR):
            mbr = pos
            pos = meter_pos

            pos += bar_length * (mbr.measure-meter_mbr.measure)
            pos += beat_size  * (mbr.beat - meter_mbr.beat)
            pos += mbr.remnant

            return pos

        else:
            distance = pos - meter_pos
            m = distance // bar_length
            b = (distance % bar_length) // beat_size
            r = (distance % bar_length) %  beat_size

            return MBR(meter_mbr.measure+m,meter_mbr.beat+b,meter_mbr.remnant+r)         

    def __init__(self,key=Key(C,major),meter=Meter(4,4)):

        from cmat.basic import Quarters

        super().__init__()

        if key is not None:
            key.mbr = MBR(1,1,0)
            key.position = Quarters(0)
            super().append(key)

        if meter is not None:
            meter.mbr = MBR(1,1,0)
            meter.position = Quarters(0)
            super().append(meter)

    def __str__(self):
        lines = []
        
        col_ms_wid = max([len(str(i.mbr.measure)) for i in self])
        col_bt_wid = max([len(str(i.mbr.beat)) for i in self])
        col_rm_wid = max([len(str(i.mbr.remnant)) for i in self])
        
        col_it_wid = max([len(str(i)) for i in self])
        
        for i in self:
            mbr = '{:0>{mw}}:{:0>{bw}}:{:0<{rw}}'.format(i.mbr.measure,i.mbr.beat,str(i.mbr.remnant),
                                                         mw = col_ms_wid,
                                                         bw = col_bt_wid,
                                                         rw = col_rm_wid)
            itm = '{:>{width}}'.format(str(i),width=col_it_wid)
            
            lines.append('{} {}'.format(mbr,itm))
        return '\n'.join(lines)


class Voice(Stream):
    @property
    def voice(self):
        return self._voice_number

    @property
    def end(self):
        try:
            return self.translate(super().end)
        except RuntimeError:
            return MBR(1,1,0)


    def append(self,item):
        self.insert(self.end,item)

    def insert(self,mbr,item):
        if self._colliding(mbr,item):
            raise RuntimeError('colliding with existed.')
        for p,i in self._grouping(mbr,item):
            super().insert(p,i)
            i.mbr = system.translate(p)


    def remove(self,item):
        pass

    def index(self,item):
        pass

    def filter(self,item):
        pass

    def _grouping(self,mbr,item):
        pass

    def _colliding(self,mbr,item):
        pass

    def __init__(self,vn=1,system=None):
        self._voice_number = vn
        self._system = System() if system is None else system

    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

'''




