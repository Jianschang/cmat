
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
        position = time(position)
        if isinstance(position, MBR):
            self.mbr = position
        else:
            self.quarters = Quarters(position)

    @property
    def quarters(self):
        return self._quarters

    @quarters.setter
    def quarters(self,quarters):
        quarters = Quarters(quarters)
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
        mbr = time(mbr)
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


    def formatted(self,layout):
        if hasattr(self,'position'):
            if isinstance(self.position,MBR):
                m = str(self.position.measure)
                b = str(self.position.beat)
                r = '0  ' if self.position.remnant==0 else str(self.position.remnant)
            else:
                m = str(self.position)
                b = r = ''
        else:
            m = b = r = ''

        if hasattr(self,'duration'):
            d = {0:'',1:'dotted',
                 2:'double dotted',
                 3:'triple dotted'}[self.duration.dots]
            a = str(self.duration.base)
            if self.duration.tuplet is None:
                t = ''
            else:
                t = str(self.duration.tuplet)
        else:
            d = a = t = ''

        data = self.text if hasattr(self,'text') else ''

        return layout.format(m,b,r,d,a,t,data)

    @property
    def layout(self):
        if hasattr(self,'position'):
            if isinstance(self.position,MBR):
                m = len(str(self.position.measure))
                b = len(str(self.position.beat))
                r = len(str(self.position.remnant))
            else:
                m = len(str(self.position))
                b = r = 0
        else:
            m = b = r = 0

        if hasattr(self,'duration'):
            d = {0:0,1:len('dotted'),
                 2:len('double dotted'),
                 3:len('triple dotted')}[self.duration.dots]
            a = len(str(self.duration.base))
            if self.duration.tuplet is None:
                t = 0
            else:
                t = len(str(self.duration.tuplet))
        else:
            d = a = t = 0

        data = len(self.text) if hasattr(self,'text') else 0

        return (m,b,r,d,a,t,data)

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
        p = time(position)

        if isinstance(p,MBR):
            p = self.system.translate(p)

        ip = self.index(lambda i:[i.quarters,g[type(i)]]>[p,g[type(item)]])
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
        position = time(position)
        if isinstance(position,MBR):
            position = self.system.translate(position)
        s = self.filter(lambda i:i.quarters >= position)
        s._starting = position
        return s

    def until(self,position):
        position = time(position)
        if isinstance(position,MBR):
            position = self.system.translate(position)

        s = self.filter(lambda i:i.quarters < position)
        s._stopping = position
        return s

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

        position = time(position)

        if isinstance(position,MBR):
            position = self.translate(position)
        key   = self.keys.rfind(lambda k:k.quarters <= position)
        meter = self.meters.rfind(lambda m:m.quarters < position)

        return Context(key,meter)        
        
        
    def translate(self,position):

        position = time(position)

        if isinstance(position,MBR) and position == MBR(1):
            return Quarters(0)
        elif isinstance(position,Quarters) and position == 0:
            return MBR(1)

        if isinstance(position,MBR):
            reference = self.meters.rfind(lambda m:m.mbr < position)
        else:
            reference = self.meters.rfind(lambda m:m.quarters < position)

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

        position = time(position)

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

        position = time(position)

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

    @property
    def copy(self):
        s = Voice(sys=self.system.copy,num=self.number)

        for item in self.items:
            s.insert(item.position,item.copy)

        return s

    def filter(self,criteria):
        v = Voice(self.system,self.number)
        for item in self.items:
            if criteria(item):
                v.items.append(item)

        if hasattr(self,'_starting'):
            v._starting = self._starting
        if hasattr(self,'_stopping'):
            v._stopping = self._stopping

        return v

    def insert(self,position,item):

        position = time(position)

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

        item.vn = self.number
        super().insert(quarters,item)

    def set(self,position,item):

        position = time(position)

        self.system.set(position,item)

        if item.type is Meter:
            for i in self.since(position):
                i.quarters = i.quarters


    def measure(self,measure):
        return self.since(MBR(measure)).until(MBR(measure+1))

    def measures(self,start,stop=None):
        if stop is None:
            stop = start

        return self.since(MBR(start)).until(MBR(stop+1))

    def empty(self):
        for i in self:
            i.site.remove(i)

    def __init__(self,sys=None,num=1):
        super().__init__()
        self._number = num
        self.system = System() if sys is None else sys

    def __str__(self):

        s = []

        start = MBR(1)
        stop  = self.end if self.end > self.system.end else self.system.end

        # setting start and stop boundary
        if hasattr(self,'_starting'):
            start = self._starting
            if not isinstance(start,MBR):
                start = self.system.translate(start)
        else:
            if self.count > 0:
                start = self.first.mbr
            if self.system.count > 0:
                if self.system.first.mbr < start:
                    start = self.system.first.mbr

        if hasattr(self,'_stopping'):
            stop = self._stopping
            if not isinstance(stop,MBR):
                stop = self.system.translate(stop)
        else:
            if self.count > 0:
                stop = MBR(self.last.mbr.measure+1)
            if self.system.count > 0:
                if stop < MBR(self.system.last.mbr.measure+1):
                    stop = MBR(self.system.last.mbr.measure+1)

        # adding measure seprators
        for n in range(start.measure,stop.measure):
            mbr = MBR(n)
            qar = self.system.translate(mbr)
            msp = MeasureSeprator()
            msp._mbr = mbr
            msp._quarters = qar
            s.append(msp)


        # adding context key and meter signature if needed.
        sys = self.system.since(MBR(start.measure)).until(MBR(stop.measure))
        context = self.system.get_context(start)

        if sys.meters.count==0 or sys.meters.first.mbr.measure > start.measure:
            m = context.meter.copy
            m.site = context.meter.site
            m._mbr = MBR(start.measure)
            m._quarters = self.system.translate(m._mbr)
            
            s.append(m)
        if sys.keys.count==0 or sys.keys.first.mbr.measure > start.measure:
            k = context.key.copy
            k.site = context.key.site
            k._mbr = MBR(start.measure)
            k._quarters = self.system.translate(k._mbr)
            s.append(k)

        # adding system track items
        s += sys

        # adding self items
        s += self

        # sort the list
        s.sort(key=lambda i:[i.quarters,self.priority[type(i)]])

        # calculate column widths

        layouts = [i.layout for i in s if type(i) not in [MeasureSeprator]]

        w1 = max([layout[0] for layout in layouts])
        w2 = max([layout[1] for layout in layouts])
        w3 = max([layout[2] for layout in layouts])
        w4 = max([layout[3] for layout in layouts])
        w5 = max([layout[4] for layout in layouts])
        w6 = max([layout[5] for layout in layouts])
        w7 = max([layout[6] for layout in layouts])

        # construct format string
        #layout = '[:>{:d}]:[:>{:d}]:[:<{:d}] \t' \
        #         '[:>{:d}] [:>{:d}] [:<{:d}] \t' \
        #         '[:>{:d}]'.format(w1,w2,w3,w4,w5,w6,w7)
        #layout = layout.replace('[','{').replace(']','}')

        layout = '{:>%d}:{:>%d}:{:<%d}\t{:>%d} {:>%d} {:<%d}\t' \
                 '{:>%d}' % (w1,w2,w3,w4,w5,w6,w7)
        total  = len(layout.format('','','','','','','').expandtabs())


        sep = '-[{}]-'

        lines = []

        for i in s:
            if i.type is MeasureSeprator:
                head = sep.format(i.mbr.measure)
                lines.append(head.ljust(total,'-'))
                continue
            elif i.type in (Key,Meter):
                lines.append('{:>{w}}'.format(str(i),w=total))
                continue

            lines.append(i.formatted(layout))

        return '\n'.join(lines)

class Voices(object):

    def add(self,voice):
        if self.occupied(voice.number):
            self.remove(self[voice.number])

        self._voices.append(voice)

    def remove(self,voice):
        self._voices.remove(voice)

    def occupied(self,number):
        for v in self:
            if v.number == number
                return True
        else:
            return False

    def __init__(self):
        self._voices = []

    def __getitem__(self,*args):

        for arg in args:
            if isinstance(arg,int):
                for v in self:
                    if v.number == arg:
                        return v

            elif isinstance(arg,slice):
                start = slice.start-1 if slice.start > 0 else slice.start
                stop  = slice.stop-1 if slice.stop > 0 else slice.stop
                step  = slice.step

                vs = Voices()
                for v in self._voices[start:stop:step]:
                    vs.add(v)
                return vs 

            elif isinstance(arg,tuple):
                vs = Voices()
                for n in arg:
                    vs.add(self[n])
                return vs                

    def __iter__(self):
        return iter(self._voices)

    def __str__(self):
        pass

    def __repr__(self):
        return str(self)


class Part(object):

    def add(self,voice):
        voice.system = self.system
        self.voices.add(voice)

    def remove(self,voice):
        self.voices.remove(voice)

    def filter(self,criteria):

        p = Part(self.system)

        for v in self.voices:
            p.add(v.filter(criteria))

        return p

    def since(self,position):
        pos = time(position)

        if isinstance(pos,MBR):
            return self.filter(lambda i:i.position>=pos)
        else:
            return self.filter(lambda i:i.quarters>=pos)

    def until(self,position):
        pos = time(position)

        if isinstance(pos,MBR):
            return self.filter(lambda i:i.position<pos)
        else:
            return self.filter(lambda i:i.quarters<pos)

    def __init__(self,sys=None):
        self.system = System() if sys is None else sys
        self.voices = Voices()

    def __iter__(self):
        pass

    def __str__(self):
        # setting start and stop boundary
        # add measure seprator item
        # set context key and meter if necessary
        # merge
        # calculate layout measurement
        # construct text line

    def __repr__(self):
        pass
    

def time(p):

    if type(p) is Quarters:
        return p
    elif type(p) is MBR:
        return p
    elif type(p) is int:
        return MBR(p)
    elif type(p) is float:
        return Quarters(p)
    elif type(p) is tuple:
        if len(p) < 3:
            return MBR(p[0],p[1],0)
        else:
            return MBR(p[0],p[1],p[2])
    else:
        raise TypeError('unrecognized time form.')


