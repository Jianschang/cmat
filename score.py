
from cmat.basic   import Quarters, C
from cmat.quality import major

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

        self._measure = measure
        self._beat    = beat
        self._remnant = Quarters(remnant)

    def __str__(self):

        remnant = '0' if self.remnant==0 else str(self.remnant).strip('0')
        return '{}:{}:{}'.format(self.measure,self.beat,remnant)

    def __repr__(self):
        return str(self)

    def __eq__(s,o):
        return [s.measure,s.beat,s.remnant]==[o.measure,o.beat,o.remnant]

    def __gt__(s,o):
        return [s.measure,s.beat,s.remnant]>[o.measure,o.beat,o.remnant]

    def __lt__(s,o):
        return [s.measure,s.beat,s.remnant]<[o.measure,o.beat,o.remnant]

    def __ge__(s,o):
        return s > o or s == o

    def __le__(s,o):
        return s < o or s == o


class StreamItem(object):

    @property
    def position(self):
        if self.site is not None:
            if hasattr(self.site,'system') and self.site.system is not None:
                return self._mbr
        return self._quarters

    @position.setter
    def position(self,position):
        if isinstance(position, MBR):
            self.mbr = position
        else:
            self.quarters = Quarters(position)

    @property
    def quarters(self):
        return self._quarters

    @quarters.setter
    def quarters(self,quarters):
        if self.site is not None:
            if hasattr(self.site,'system') and self.site.system is not None:
                self._quarters = quarters
                self._mbr = self.site.system.translate(quarters)
                return
        self._quarters = quarters
        self._mbr = None

        if self.site is not None:
            self.site.sort()

    @property
    def mbr(self):
        return self._mbr

    @mbr.setter
    def mbr(self,mbr):
        if self.site is not None:
            if hasattr(self.site,'system') and self.site.system is not None:
                self._mbr = mbr
                self._quarters = self.site.system.translate(mbr)
                self.site.sort()
                return

        raise RuntimeError('Can not interpret MBR info without system track.')

    @property
    def type(self):
        return self.__class__

    def __init__(self):
        self._mbr = None
        self._quarters = None
        self.site = None

class MeasureSeprator(StreamItem):
    @property
    def text(self):
        return ''

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

    @property
    def text(self):
        return str(self)

    def __init__(self,count,size):

        from cmat.basic import NoteType
        super().__init__()

        self._count = count
        if isinstance(size,int):
            self._size = NoteType(4/size)
        elif isinstance(size,NoteType):
            self._size = size
        else:
            raise TypeError('requires int or NoteType.')

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

    @property
    def text(self):
        return str(self)

    def __init__(self,tonic,mode=major):

        super().__init__()

        self._tonic = tonic
        self._mode  = mode

    def __str__(self):
        return '{} {}'.format(self.tonic,self.mode)

    def __repr__(self):
        return str(self)

class Note(StreamItem):

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self,dur):
        from cmat.basic import Duration
        self._duration = dur if isinstance(dur,Duration) else Duration(dur)

    @property
    def copy(self):
        return Note(self.duration.copy,self.pitch)

    @property
    def text(self):
        return str(self.pitch)

    def __init__(self,dur,pitch):
        from cmat.basic import Duration

        super().__init__()
        self.pitch = pitch
        self.duration = dur

    def __str__(self):
        return '{} {}'.format(self.duration,self.pitch)

    def __repr__(self):
        return str(self)

class Rest(StreamItem):
    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self,dur):
        from cmat.basic import Duration
        self._duration = dur if isinstance(dur,Duration) else Duration(dur)

    @property
    def copy(self):
        return Rest(self.duration.copy)

    @property
    def text(self):
        return 'rest'

    def __init__(self,dur):
        from cmat.basic import Duration

        super().__init__()
        self._duration = dur

    def __str__(self):
        return '{} rest'.format(self.duration)

    def __repr__(self):
        return str(self)

class Stream(object):

    priority   = {MeasureSeprator:0,Key:1,Meter:2,Note:3,Rest:4}

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

        if hasattr(self,'system') and self.system is not None:
            return self.system.translate(end)
        else:
            return end

    @property
    def count(self):
        return len(self.items)

    @property
    def copy(self):
        s = Stream()

        if hasattr(self,'system'):
            s.system = s if self.system is self else self.system.copy

        for item in self.items:
            s.insert(item.position,item.copy)

        return s

    def insert(self,position,item):
        g = self.priority
        p = position

        ip = self.index(lambda i:[i.position,g[type(i)]]>[p,g[type(item)]])
        ip = self.count if ip is None else ip-1

        if item.site is None:
            item.site = self

        item.position = p

        self.items.insert(ip,item)

    def append(self,item):
        self.insert(self.end,item)

    def remove(self,item):
        self.items.remove(item)

    def filter(self,criteria):
        s = Stream()
        for item in self.items:
            if criteria(item):
                s.items.append(item)

        if hasattr(self,'system') and self.system is not None:
            s.system = self.system

        return s

    def find(self,criteria):
        for item in self.items:
            if criteria(item):
                return item
        else:
            return None

    def index(self,criteria):
        for index,item in enumerate(self.items):
            if callable(criteria) and criteria(item):
                return index + 1
            elif criteria is item:
                return index + 1
        else:
            return None

    def rfind(self,criteria):
        for item in reversed(self.items):
            if criteria(item):
                return item
        else:
            return None

    def rindex(self,criteria):
        for index in reversed(range(self.count)):
            if callable(criteria) and criteria(self.items[index]):
                return index + 1
            elif criteria is self.items[index]:
                return index + 1
        else:
            return None

    def sort(self):
        self.items.sort(key=lambda i:[i.quarters,self.priority[type(i)]])

    def align(self,grid='m'):
        if hasattr(self,'system') and self.system is not None:
            meters = self.system.meters
            for item in self:
                refs=meters.filter(lambda m:m is not item \
                                        and m.quarters<=item.quarters)
                if refs.count == 0:
                    continue
                    raise RuntimeError('no meter was found.')
                else:
                    ref = refs.last

                if isinstance(grid,Quarters):
                    pass
                elif hasattr(grid,'quarters'):
                    g = grid.quarters
                elif grid == 'm':
                    g = ref.bar_length
                elif grid == 'b':
                    g = ref.size
                else:
                    raise RuntimeError('invalid grid size.')
                shift = -(item.quarters-ref.quarters) % g

                item.quarters += shift

    def shift(self,amount):
        for m in self.meters:
            m.quarters += amount
        for i in self.filter(lambda i:i.type!=Meter):
            i.quarters += amount

    def since(self,position):
        if isinstance(position,MBR):
            return self.filter(lambda i:i.mbr >= position)
        else:
            return self.filter(lambda i:i.quarters >= position)

    def until(self,position):
        if isinstance(position,MBR):
            return self.filter(lambda i:i.mbr < position)
        else:
            return self.filter(lambda i:i.quarters < position)

    def __init__(self,*items):
        self.items = []
        for item in items:
            if item.position is not None:
                self.insert(item.position,item)
            else:
                self.append(item)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self):
        return item in self.items

    def __getitem__(self,index):
        if isinstance(index,slice):
            s1 = index.start-1 if index.start>0 else index.start
            s2 = index.stop-1  if index.stop >0 else index.stop
            return Stream(*self.items[s1:s2:index.step])
        else:
            if index > 0:
                index -= 1
            return self.items[index]

    def __len__(self):
        return len(self.items)

    def __str__(self):

        if self.count == 0:
            return ''

        w1=max([len(str(i.position)) for i in self])
        w2=[len(str(i.duration)) for i in self if hasattr(i,'duration')]
        w2=max(w2) if len(w2)>0 else 0
        w3=max([len(str(i.text)) for i in self])

        lines = []
        for item in self:
            p = str(item.position)
            d = str(item.duration) if hasattr(item,'duration') else ''
            t = str(item.text)
            lines.append('{:<{c1}}\t{:>{c2}}\t{:>{c3}}'.format(p,d,t,
                                                   c1=w1,c2=w2,c3=w3))

        return '\n'.join(lines)

    def __repr__(self):
        return str(self)


class System(Stream):
    @property
    def keys(self):
        return self.filter(lambda i:i.type is Key)
    
    @property
    def meters(self):
        return self.filter(lambda i:i.type is Meter)

    @property
    def copy(self):
        s = System(None,None)

        if hasattr(self,'system'):
            s.system = s if self.system is self else self.system.copy

        for item in self.items:
            s.insert(item.position,item.copy)

        return s

    def filter(self,criteria):
        s = System(key=None,meter=None)
        for item in self:
            if criteria(item):
                s.items.append(item)

        s.system = self.system

        return s
        
    def __init__(self,key=Key(C,major),meter=Meter(4,4)):

        super().__init__()

        if key is not None:
            if key.position is None:
                key._quarters = Quarters(0)
                key._mbr = MBR(1)
            if not hasattr(key,'site') or key.site is None:
                key.site = self
            self.items.append(key)

        if meter is not None:
            if meter.position is None:
                meter._quarters = Quarters(0)
                meter._mbr = MBR(1)
            if not hasattr(meter,'site') or meter.site is None:
                meter.site = self
            self.items.append(meter)

        self.system = self


    def get_context(self,position):
        from collections import namedtuple
        Context = namedtuple('Context',['key','meter'])

        if isinstance(position,MBR):
            key   = self.keys.rfind(lambda k:k.mbr <= position)
            meter = self.meters.rfind(lambda m:m.mbr <= position)
        else:
            key   = self.keys.rfind(lambda k:k.quarters <= position)
            meter = self.meters.rfind(lambda m:m.quarters < position)

        return Context(key,meter)        
        
        
    def translate(self,position):

        if isinstance(position,MBR) and position == MBR(1):
            return Quarters(0)
        elif isinstance(position,Quarters) and position == 0:
            return MBR(1)

        reference = self.get_context(position).meter
        #meters = self.meters.until(position)
        #reference = meters.last if meters.count > 0 else self.meters.first

        bar_length  = reference.bar_length
        beat_length = reference.size.quarters

        if isinstance(position,MBR):
            q =  reference.quarters
            q += bar_length * (position.measure - reference.mbr.measure)
            q += beat_length * (position.beat - 1)
            q += position.remnant
            return q
        else:
            position = Quarters(position)
            distance = position - reference.quarters
            m = distance // bar_length + reference.mbr.measure
            b = distance %  bar_length // beat_length + 1
            r = distance %  beat_length

            return MBR(m,b,r)

    def set(self,position,item):
        if not isinstance(position,MBR):
            position = self.system.translate(position)
        position = MBR(position.measure)
        quarters = self.system.translate(position)

        self.insert(position,item)

        if item.type is Meter:
            following = self.meters.find(lambda m:m.position>position)
            if following is not None:
                shift = -(following.quarters - quarters)%item.bar_length

                realign = self.since(position).until(following.position)
                self.since(following.position).shift(shift)
            else:
                realign = self.since(position)

            realign.align()

            # refreshing mbr info
            for i in self.since(position):
                i.quarters = i.quarters

    def insert(self,position,item):
        
        existed = self.find(lambda i:i.type is item.type and i.position==position)
        if existed is not None:
            self.remove(existed)
        
        super().insert(position,item)

    def remove(self,item):
        super().remove(item)

        position = item.position
        previous = self.meters.rfind(lambda m:m.position < position)

        if item.type is Meter and previous is not None:
            following = self.meters.find(lambda m:m.position>position)
            if following is not None:
                shift = -(following.quarters-previous.quarters)%previous.bar_length
                realign = self.since(position).until(following.position)
                self.since(following.position).shift(shift)
            else:
                realign = self.since(position)

            realign.align()

            # refreshing mbr info
            for i in self.since(position):
                i.quarters = i.quarters

class Voice(Stream):

    @property
    def number(self):
        return self._number

    def filter(self,criteria):
        v = Voice(self.system,self.number)
        for item in self.items:
            if criteria(item):
                v.items.append(item)
        return v

    def insert(self,position,item):
        item.vn = self.number

        if isinstance(position,MBR):
            quarters = self.system.translate(position)
        else:
            quarters = position

        # head and tail position of inserting item.
        head = tail = quarters
        if hasattr(item,'duration'):
            tail += item.duration.quarters

        # remove if collided
        collided = []
        for i in self:

            # begin and end of item
            begin = end = i.quarters
            if hasattr(i,'duration'):
                end += i.duration.quarters

            if head  <= begin <  tail and begin < end or \
               head  <  end   <= tail or \
               begin <= head  <  end  or \
               begin <  tail  <= end  and head < tail:

                # collided
                collided.append(i)

        for i in collided:
            self.remove(i)

        super().insert(position,item)

    def set(self,position,item):
        self.system.set(position,item)

        if item.type is Meter:
            for i in self.since(position):
                i.quarters = i.quarters


    def measure(self,measure):
        return self.since(MBR(measure)).until(MBR(measure+1))

    def empty(self):
        for i in self:
            i.site.remove(i)

    def __init__(self,sys=None,num=1):
        super().__init__()
        self._number = num
        self.system = System() if sys is None else sys

    def __str__(self):

        s = []

        if self.count == 0:
            m = self.system.last.mbr.measure
        else:
            m = max([self.last.mbr.measure,self.system.last.mbr.measure])

        for n in range(1,m+1):
            m = MBR(n)
            q = self.system.translate(m)
            ms = MeasureSeprator()
            ms._mbr = m
            ms._quarters = q

            s.append(ms)

        s += self
        s += self.system

        s.sort(key=lambda i:[i.quarters,self.priority[type(i)]])

        w1=max([len(str(i.position)) for i in s])
        w2=[len(str(i.duration)) for i in s if hasattr(i,'duration')]
        w2=max(w2) if len(w2)>0 else 0
        w3=max([len(str(i.text)) for i in s])

        t = '{:<{c1}}\t{:>{c2}}\t{:>{c3}}'.format('-','-','-',c1=w1,c2=w2,c3=w3)
        t = len(t.expandtabs())
        sep = '-Measure: {} -'

        lines = []

        for i in s:
            if i.type is MeasureSeprator:
                head = sep.format(i.mbr.measure)
                lines.append(head.ljust(t,'-'))
                continue

            p = str(i.position)
            d = str(i.duration) if hasattr(i,'duration') else ''
            x = str(i.text)
            lines.append('{:<{c1}}\t{:>{c2}}\t{:>{c3}}'.format(p,d,x,
                                                   c1=w1,c2=w2,c3=w3))

        return '\n'.join(lines)
