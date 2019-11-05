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

'''
class StreamItem(object):
    
    @property
    def position(self):
        return self._quarters if self._position is None else self._position

    @position.setter
    def position(self,pos):
        if isinstance(pos,MBR):
            self._position = pos
            if self._container is not None and hasattr(self._container,'system'):
                self._quarters = self._container.system.translate(pos)
        else:
            self._quarters = pos
            if self._container is not None and hasattr(self._container,'system'):
                self._position = self._container.system.translate(pos)

    @property
    def quarters(self):
        return self._quarters

    @quarters.setter
    def quarters(self,pos):
        self._quarters = pos
        if self._container is not None and hasattr(self._container,'system'):
            self._position = self._container.system.translate(pos)

    def __init__(self):
        self._container = None
        self._position  = None
        self._quarters  = None
'''

class StreamItem(object):

    def __init__(self):
    
        self._position  = None
        self._quarters  = None
        self._container = None

    @property
    def position(self):
        return self._quarters if self._position is None else self._position

    @position.setter
    def position(self,position):
        from cmat.basic import Quarters
        
        if isinstance(position,MBR):
            self._position = position
            if self._container is not None and hasattr(self._container,'system'):
                self._quarters = self._container.system.translate(position)
        else:
            self._quarters = Quarters(position)
            if self._container is not None and hasattr(self._container,'system'):
                self._position = self._container.system.translate(position)

    @property
    def quarters(self):
        return self._quarters

    @quarters.setter
    def quarters(self,quarters):
        self._quarters = quarters
        if self._container is not None and hasattr(self._container,'system'):
            self._position = self._container.system.translate(quarters)

class Meter(StreamItem):

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

        super().__init__()

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

class Key(StreamItem):

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
        
        super().__init__()
        
        self._tonic = tonic
        self._mode  = mode if mode is not None else major

    def __str__(self):
        return '{} {}'.format(str(self.tonic),str(self.mode))

    def __repr__(self):
        return str(self)

class Note(StreamItem):
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

        super().__init__()

        self.pitch = pitch
        self._duration = dur if isinstance(dur,Duration) else Duration(dur)

    def __str__(self):
        return ' '.join([str(s) for s in (self.duration,self.pitch)])

    def __repr__(self):
        return str(self)


class Rest(StreamItem):
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

        super().__init__()

        self._duration = dur if type(dur) is Duration else Duration(dur)

    def __str__(self):
        return '{} rest'.format(self.duration)

    def __repr__(self):
        return str(self)

class Stream(object):

    insert_priority = {Key:0,Meter:1,Note:2,Rest:3} # Chord:4}
    
    @property
    def first(self):
        return self[1]

    @property
    def last(self):
        return self[-1]

    @property
    def end(self):
        from cmat.basic import Quarters
    
        stop = []
        for item in self:
            if hasattr(item,'duration'):
                stop.append(item.quarters + item.duration)
            else:
                stop.append(item.quarters)

        end = max(stop) if len(stop) > 0 else Quarters(0)
        return self.system.translate(end) if hasattr(self,'system') else end    
        
    @property
    def count(self):
        return len(self)

    def insert(self,item,position):
        ip = self.insert_priority
        
        insert_index = self.index(lambda i: i.position >  position or (\
                                            i.position == position and \
                                            ip[type(i)] > ip[type(item)]))

        if insert_index is None:
            insert_index = self.count + 1

        self.items.insert(insert_index - 1,item)

        item._container = self
        item.position = position

    def append(self,*items):

        for item in items:
            self.insert(item,self.end)
    
    def remove(self,criteria,position=None):
        candidates = self if position is None else self.filter(lambda i: i.position == position)
        
        if callable(criteria):
            candidates = candidates.filter(criteria)
        elif isinstance(criteria,type):
            candidates = candidates.filter(lambda i: type(i) is criteria)
        else:
            candidates = candidates.filter(lambda i: i is criteria)
        
        for item in candidates:
            self.items.remove(item)

    def filter(self,criteria):
        s = self.__class__()
        for item in filter(criteria,self):
            s.items.append(item)
        return s

    def find(self,criteria):
        from inspect import isfunction
        
        if isinstance(criteria,type):
            t = criteria
            criteria = lambda i: isinstance(i,t)
        elif isfunction(criteria):
            pass
        else:
            obj = criteria
            criteria = lambda i: i is obj

        for item in self:
            if criteria(item):
                return item
        else:
            return None

    def rfind(self,criteria):
        from inspect import isfunction
        
        if isinstance(criteria,type):
            t = criteria
            criteria = lambda i: isinstance(i,t)
        elif isfunction(criteria):
            pass
        else:
            obj = criteria
            criteria = lambda i: i is obj
            
        for item in reversed(self):
            if criteria(item):
                return item
        else:
            return None

    def index(self,criteria):
        from inspect import isfunction
        
        if isinstance(criteria,type):
            t = criteria
            criteria = lambda i: isinstance(i,t)
        elif isfunction(criteria):
            pass
        else:
            obj = criteria
            criteria = lambda i: i is obj


        for index,item in enumerate(self):
            if criteria(item):
                return index + 1
        else:
            return None

    def rindex(self,criteria):
        from inspect import isfunction
        
        if isinstance(criteria,type):
            t = criteria
            criteria = lambda i: isinstance(i,t)
        elif isfunction(criteria):
            pass
        else:
            obj = criteria
            criteria = lambda i: i is obj

        for index in range(self.count,0,-1):
            if criteria(self[index]):
                return index
        else:
            return None

    def sort(self):
        self.items.sort(key=lambda i: [i.position, self.insert_priority[type(i)]])
    
    def fr(self,position):
        return self.filter(lambda i: i.position >= position)

    def ut(self,position):
        return self.filter(lambda i: i.position < position)

    def __init__(self,*items):
        self.items = []
        for item in items:
            if hasattr(item,'position') and item.position is not None:
                self.insert(item,item.position)
            else:
                self.append(item)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self,item):
        return item in self.items

    def __getitem__(self,index):
        if isinstance(index,slice):
            start = index.start-1 if index.start>0 else index.start
            stop  = index.stop -1 if index.stop >0 else index.stop
            return Stream(*self.items[start:stop:index.step])
        else:
            if index > 0:
                index -= 1
            return self.items[index]

    def __len__(self):
        return len(self.items)
        
    def __str__(self):

        lines = []
        for item in self:
            lines.append('{:<12} {:>24}'.format(str(item.position),str(item)))
        
        return '\n'.join(lines)
                                                
    def __repr__(self):
        return str(self)

'''
class System(Stream):    
    @property
    def end(self):
        
        stops = []
        for item in self:
            if hasattr(item,'duration'):
                stops.append(self.translate(item.quarters + item.duration))
            else:
                stops.append(item.position)
        
        return max(stops) if len(stops) > 0 else MBR(1)

    def translate(self,position):
        meter = self.get_meter(position)
        if meter is None:
            raise RuntimeError('reference meter not found.')
            
        beat       = meter.size
        bar_length = meter.bar_length
        
        if isinstance(position,MBR):
            m = position.measure - meter.position.measure
            b = position.beat - 1
            r = position.remnant
            return meter.quarters + bar_length*m + beat*b + r
        else:
            m = (position - meter.quarters) // bar_length + meter.position.measure
            b = (position - meter.quarters) % bar_length // beat + 1
            r = (position - meter.quarters) % bar_length % beat
            return MBR(m,b,r)

    def __init__(self,key=Key(C,major),meter=Meter(4,4)):
        from cmat.basic import Quarters
        
        self.items = []
        self.system = self
        
        if key is not None:
            key._quarters = Quarters(0)
            key._position = MBR(1)
            key._container = self
            self.items.append(key)
        if meter is not None:
            meter._quarters = Quarters(0)
            meter._position = MBR(1)
            meter._container = self
            self.items.append(meter)

    def __str__(self):

        lines = []
        for item in self:
            lines.append('{:<12} {:>24}'.format(str(item.position),str(item)))
        
        return '\n'.join(lines)

    def get_meter(self,position):
        meters = self.filter(lambda i: type(i) is Meter)
        if len(meters) == 0:
            return None

        if isinstance(position,MBR):
            return meters.rfind(lambda i: getattr(i,'position') < position \
                                       or getattr(i,'position') == self.first.position)
        else:
            return meters.rfind(lambda i: getattr(i,'quarters') < position \
                                       or getattr(i,'quarters') == self.first.quarters)
        
    def get_key(self,position):
        keys = self.filter(lambda i: type(i) is Key)
        if isinstance(position,MBR):
            return keys.rfind(lambda i: getattr(i,'position') < position \
                                     or getattr(i,'position') == self.first.position)
        else:
            return keys.rfind(lambda i: getattr(i,'quarters') < position \
                                     or getattr(i,'quarters') == self.first.quarters)
    
    def set_meter(self,measure,meter):
        position = MBR(measure)
        
        next_meter  = self.filter(lambda i: type(i) is Meter).find(lambda i: i.position > position)
        split_point = position if next_meter is None else next_meter.position

        existed = self.find(lambda m: type(m) is Meter and m.position == position)
        if existed is not None:
            self.items.remove(existed)

        self.insert(position,meter)

        shift = -(next_meter.quarters-meter.quarters)%meter.bar_length if next_meter is not None else 0

        for item in self.filter(lambda i: meter.position < i.position < split_point):
            item.quarters += -(item.quarters-meter.quarters) % meter.bar_length

        for m in self.filter(lambda i: type(i) is Meter and i.position >= split_point):
            m.quarters = m.quarters + shift
        
        for item in self.filter(lambda i: type(i) is not Meter and i.position >= split_point):
            item.quarters += shift

    def set_key(self,measure,key):
        position = MBR(measure)
        
        existed = self.find(lambda i: type(i) is key and i.position == position)
        if existed is not None:
            self.remove(existed)
        
        self.insert(position,key)

    def del_key(self,measure):
        position = MBR(measure)
        
        existed = self.find(lambda i: type(i) is Key and i.position == position)
        if existed is not None:
            self.remove(existed)
    
    def del_meter(self,measure):
        position = MBR(measure)
        
        existed = self.find(lambda i: type(i) is Meter and i.position == position)
        if existed is not None:
            before   = self.get_meter(position)
            temporal = before.copy
            self.set_meter(position.measure,temporal)
            self.remove(temporal)

    def filter(self,criteria):
        s = System(key=None,meter=None)
        for i in filter(criteria,self):
            s.items.append(i)
        return s
'''


class System(Stream):

    @property
    def keys(self):
        return self.filter(lambda i: isinstance(i,Key))

    @property
    def meters(self):
        return self.filter(lambda i: isinstance(i,Meter))

    def insert(self,item,measure,beat=1,remnant=0):
        position = MBR(measure,beat,remnant)
        
        super().insert(item,position)
    
    def remove(self,criteria,measure=None,beat=1,remnant=0):
        position = None if measure is None else MBR(measure,beat,remnant)
        
        super().remove(criteria,position)
        
    def filter(self,criteria):
        s = System(key=None,meter=None)
        for item in filter(criteria,self):
            s.items.append(item)
        return s

    def fr(self,measure,beat=1,remnant=0):
        position = MBR(measure,beat,remnant)
        return self.filter(lambda i: i.position >= position)

    def ut(self,measure,beat=1,remnant=0):
        position = MBR(measure,beat,remnant)
        return self.filter(lambda i: i.position < position)
        
    def translate(self,position):
        if isinstance(position,MBR):
            start = self.first.position
            meter = self.meters.filter(lambda i:i.position<position or i.position==start).last
        else:
            start = self.first.quarters
            meter = self.meters.filter(lambda i:i.quarters<position or i.quarters==start).last
        beat_length = meter.size.quarters
        bar_length  = meter.bar_length

        if isinstance(position,MBR):
            m = bar_length * (position.measure - meter.position.measure)
            b = beat_length * (position.beat-1)
            
            return meter.quarters + m + b + position.remnant

        else:
            d = position - meter.quarters
            m = d // bar_length
            b = d % bar_length // beat_length
            r = d % beat_length
            m += meter.position.measure
            
            return MBR(m,b+1,r)

    def __init__(self,key=Key(C,major),meter=Meter(4,4),starting=1):
        super().__init__()
        if key is not None:
            self.insert(key,starting)
            key.quarters = 0
        if meter is not None:
            self.insert(meter,starting)
            meter.quarters = 0

        self.system = self

class Voice(Stream):

    @property
    def voice_number(self):
        return self._voice_number
    
    @property
    def end(self):
        
        stops = []
        for item in self:
            if hasattr(item,'duration'):
                stops.append(self.system.translate(item.quarters+item.duration))
            else:
                stops.append(item.position)
        
        return max(stops) if len(stops) > 0 else MBR(1)
        
    @property
    def notes(self):
        return list(self.filter(lambda i: type(i) is Note))

    def filter(self,criteria):
        s = Voice(self.voice_number,self.system)
        for i in filter(criteria,self):
            s.insert(i.position,i)
        return s

    def fr(self,position):
        sys = System(key=None,meter=None)
        
        p2  = MBR(position.measure)
        key = self.find(lambda k: type(k) is Key and k.position == p2)
        if key is None:
            key = self.system.get_key(p2).copy
        key = key.copy
        key._position = p2    
        key._quarters = self.system.translate(p2)
        key._container = sys
        sys.items.append(key)
        
        meter = self.find(lambda m: type(m) is Meter and m.position == p2)
        if meter is None:
            meter = self.system.get_meter(p2)
        meter = meter.copy
        meter._position = p2
        meter._quarters = self.system.translate(p2)
        meter._container = sys

        sys.items.append(meter)
 
        for item in self.system.filter(lambda i: i.position > p2):
            sys.insert(item.position,item)
       
        v = Voice(self.voice_number,sys)
        
        for i in filter(lambda i: i.position >= position,self):
            v.insert(i.position,i)

        return v

    def to(self,position):
        v = Voice(self.voice_number,self.system.to(position))
        for i in filter(lambda i: i.position < position,self):
            v.insert(i.position,i)
        
    def measure(self,start,stop=None):
        
        stop  = MBR(start+1) if stop is None else MBR(stop)
        start = MBR(start)
        
        return self.fr(start).to(stop)

    def set_meter(self,measure,meter):
        pass

    def set_key(self,measure,meter):
        pass

    def del_meter(self,measure):
        pass

    def del_key(self,measure):
        pass

    def __init__(self,voice_num = 1, sys = None):

        self._voice_number = voice_num
        self.system = System() if sys is None else sys
        
        super().__init__()

    def __str__(self):
        i = j = 0
        lines = []
        while i < len(self) or j < len(self.system):
            if i >= len(self):
                lines.append('{:<12} {:>24}'.format(str(self.system[j].position),str(self.system[j])))
                j += 1
            elif j >= len(self.system):
                lines.append('{:<12} {:>24}'.format(str(self[i].position),str(self[i])))
                i += 1
            elif self[i].position < self.system[j].position:
                lines.append('{:<12} {:>24}'.format(str(self[i].position),str(self[i])))
                i += 1
            else:
                lines.append('{:<12} {:>24}'.format(str(self.system[j].position),str(self.system[j])))
                j += 1
        return '\n'.join(lines)
