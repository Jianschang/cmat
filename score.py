from cmat.basic   import Quarters,C
from cmat.quality import major

# comments

class MBR(object):
    
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

    priority = {Key:0,Meter:1,Note:2,Rest:3} # Chord:4}

    @property
    def first(self):
        return self.items[0]

    @property
    def last(self):
        return self.items[-1]

    @property
    def end(self):
        ends = []
        for item in self.items:
            if hasattr(item,'duration'):
                ends.append(item.quarters + item.duration)
            else:
                ends.append(item.quarters)

        end = max(ends) if len(ends) > 0 else Quarters(0)
        return self.system.translate(end) if hasattr(self,'system') else end

    @property
    def count(self):
        return len(self.items)


    def insert(self,item,position=None):

        p = self.priority

        # insert at given pos or pos carried on item or stream end.
        if position is None:
            if hasattr(item,'position') and item.position is not None:
                pos = item.position
            else:
                pos = self.end
        else:
            pos = position

        # index criteria
        def after_pos(i):
            return i.position>pos or i.position==pos and p[type(i)]>p[type(item)]

        insert_point = self.index(after_pos)    # index returned starts from 1

        if insert_point is None:
            insert_point = self.count + 1


        self.items.insert(insert_point-1,item)

        # mark container, container always points to the first.
        if item._container is None:
            item._container = self

        # set position attribute
        item.position = pos

    def append(self, *items):
        for item in items:
            self.insert(item,self.end)

    def remove(self,item):
        self.items.remove(item)

    def filter(self,criteria):
        s = Stream()
        for item in filter(criteria,self):
            s.items.append(item)
        return s

    def find(self,criteria):
        for item in self.items:
            if criteria(item):
                return item
        else:
            return None

    def rfind(self,criteria):
        for item in reversed(self.items):
            if criteria(item):
                return item
        else:
            return None

    def index(self,criteria):
        for index,item in enumerate(self.items):
            if criteria(item):
                return index + 1    # index starts from 1
        else:
            return None

    def rindex(self,criteria):
        for index in reversed(range(self.count)):
            if criteria(self.items[index]):
                return index + 1    # index starts from 1
        else:
            return None

    def sort(self):
        self.items.sort(key=lambda i:[i.position,self.priority[type(i)]])

    def fr(self,position):
        if isinstance(position,MBR):
            return self.filter(lambda i:i.position >= position)
        else:
            return self.filter(lambda i:i.quarters >= position)

    def ut(self,position):
        if isinstance(position,MBR):
            return self.filter(lambda i:i.position < position)
        else:
            return self.filter(lambda i:i.quarters < position)



    def __init__(self, *items):

        self.items = []
        for item in items:
            self.insert(item)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self,item):
        return item in self.items

    def __getitem__(self,index):

        # index starts from 1
        if isinstance(index,slice):
            s1 = index.start-1 if index.start>0 else index.start
            s2 = index.stop-1 if index.stop>0 else index.stop
            return Stream(*self.items[s1:s2:index.step])

        else:
            if index>0:
                index -= 1
            return self.items[index]

    def __len__(self):
        return len(self.items)

    def __str__(self):
        lines = []
        for item in self.items:
            lines.append('{:<12} {:>24}'.format(str(item.position),str(item)))
        return '\n'.join(lines)

    def __repr__(self):
        return str(self)

class System(Stream):

    @property
    def keys(self):
        return self.filter(lambda i:isinstance(i,Key))

    @property
    def meters(self):
        return self.filter(lambda i:isinstance(i,Meter))

    def __init__(self,key=Key(C,major),meter=Meter(4,4)):

        super().__init__()

        self.insert(key,MBR(1))
        self.insert(meter,MBR(1))

        key.quarters   = Quarters(0)
        meter.quarters = Quarters(0)

        self.system = self

    def translate(self,position):

        reference = self.meters.ut(position).last

        bar_length  = reference.bar_length
        beat_length = reference.size.quarters

        if isinstance(position,MBR):
            q =  reference.quarters
            q += bar_length * (position.measure - reference.position.measure)
            q += beat_length * (position.beat - 1)
            q += position.remnant
            return q
        else:
            position = Quarters(position)
            distance = position - reference.quarters
            m = distance // bar_length + reference.position.measure
            b = distance %  bar_length // beat_length + 1
            r = distance %  beat_length

            return MBR(m,b,r)

    def set_meter(self,measure,meter):
        position = MBR(measure)
        quarters = self.translate(position)
        meters_followed = self.meters.filter(lambda m:m.position > position)

        realign = self.fr(position)

        if meters_followed.count > 0:
            realign = realign.ut(meters_followed.first.position)
        
        self.insert(meter,position)
        
        if meters_followed.count > 0:
            next_meter = meters_followed.first
            shift = -(next_meter.quarters - quarters) %  meter.bar_length
            items_followed = self.filter(lambda i:i.quarters >= next_meter.quarters \
                                                and not isinstance(i,Meter))
            
            for meter in meters_followed:
                meter.quarters += shift
            for item in items_followed:
                item.quarters  += shift
                
        for item in realign:
            item.quarters += -(item.quarters-quarters) % meter.bar_length


class Voice(Stream):
    pass
