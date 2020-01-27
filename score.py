
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
    def position(self,*position):
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
    def mbr(self,*mbr):
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

    def formatted(self,layout,arg_names):

        parts = []
        for arg_path in arg_names:
            arg  = self
            args = arg_path.split('.')
            while len(args)>0:
                try:
                    arg = getattr(arg,args[0])
                except AttributeError:
                    arg  = ''
                    args = [args[0]]

                arg_name = args.pop(0)

            if arg_name == 'measure':
                parts.append(str(arg))
            elif arg_name == 'beat':
                parts.append(str(arg))
            elif arg_name == 'dots':
                arg = {0:'',1:'dotted',2:'double dotted',3:'triple dotted'}[arg]
                parts.append(arg)
            elif arg_name == 'decimal':
                s = str(arg)
                parts.append(s[s.index('.'):])
            else:
                parts.append(str(arg) if arg is not None else '')

        return layout.format(*parts)



    def layout(self,arg_names):

        layouts = []
        for arg_path in arg_names:
            arg  = self
            args = arg_path.split('.')
            while len(args)>0:
                try:
                    arg = getattr(arg,args[0])
                except AttributeError:
                    arg  = ''
                    args = [args[0]]

                arg_name = args.pop(0)

            if arg_name == 'measure':
                layouts.append(len(str(arg)))
            elif arg_name == 'beat':
                layouts.append(len(str(arg)))
            elif arg_name == 'dots':
                arg = {0:'',1:'dotted',2:'double dotted',3:'triple dotted'}[arg]
                layouts.append(len(arg))
            elif arg_name == 'decimal':
                layouts.append(len(str(arg))-1)
            else:
                layouts.append(len(str(arg)) if arg is not None else 0)

        return layouts

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


class Measurement(object):
    '''
    Interface for accessing music stream by measure.
    '''

    def __init__(self,stream):
        self._stream = stream

    def __getitem__(self,*args):

        arg = args[0]
        s = self._stream

        if type(arg) is int:
            return s.filter(lambda e:e.mbr.measure == arg)
        elif type(arg) is slice:
            return s.filter(lambda e:arg.start<=e.mbr.measure<arg.stop)
        elif type(arg) is tuple:
            return s.filter(lambda e:e.mbr.measure in arg)
        else:
            raise IndexError('invalid index number.')


class Stream(object):

    priority = {MeasureSeprator:0,Key:1,Meter:2,Note:3,Rest:4}

    @property
    def count(self):
        return len(self.items)

    @property
    def end(self):
        loc = [i.quarters+i.duration if hasattr(i,'duration') else i.quarters \
                    for i in self]
        end = max(loc) if len(loc) > 0 else Quarters(0)

        return self.system.translate(end) if hasattr(self,'system') \
                                          and self.system is not None else end

    @property
    def copy(self):
        copy = Stream()

        if hasattr(self,'system'):
            copy.system = copy if self.system is self else self.system.copy

        for item in self:
            copy.insert(item.position,item.copy)

    def filter(self,criteria):
        s = Stream()

        if hasattr(self,'system') and self.system is not None:
            s.system = self.system

        for item in self:
            if criteria(item):
                s.items.append(item)

        return s

    def since(self,*position):
        position = time(position)
        if isinstance(position,MBR): position = self.system.translate(position)

        s = self.filter(lambda i: i.quarters >= position)
        return s

    def until(self,*position):
        position = time(position)
        if isinstance(position,MBR): position = self.system.translate(position)

        s = self.filter(lambda i: i.quarters < position)
        return s


    def at(self,*position):
        position = time(position)
        if isinstance(position,MBR): position = self.system.translate(position)

        s = self.filter(lambda i: i.quarters == position)
        return list(s.items)

    def insert(self,*args):
        p = self.priority
        item = args[-1]

        if not isinstance(item,StreamItem):
            raise RuntimeError('missing or invalid item.')

        pos = time(args[:-1])
        if isinstance(pos,MBR):
            if hasattr(self,'system') and self.system is not None:
                pos = self.translate(pos)
            else:
                raise RuntimeError('no metric information.')

        grd = p[type(item)]

        ip = 0
        while ip < self.count:
            if (self.items[ip].quarters,p[type(self.items[ip])]) >= (pos,grd):
                break

            ip += 1

        if item.site is None:
            item.site = self

        item.quarters = pos

        self.items.insert(ip,item)

    def append(self,item):
        self.insert(self.end,item)

    def remove(self,item):
        self.items.remove(item)

    def shift(self,amount):
        meters = self.filter(lambda i:i.type is Meter)
        for m in meters:
            m.quarters += amount

        others = self.filter(lambda i:i.type is not Meter)
        for i in others:
            i.quarters += amount

    def align(self,sys,grid):
        from cmat.basic import NoteType

        for item in self:

            meter = sys.get_context(item.position).meter

            if isinstance(grid,Quarters):
                pass
            elif isinstance(grid,NoteType):
                grid = grid.quarters
            elif grid == 'beat':
                grid = meter.size.quarters

            elif grid == 'measure':
                grid = meter.bar_length

            amount = -(item.quarters - meter.quarters) % grid
            item.quarters += amount


    def sort(self):
        self.items.sort(key=lambda i:(i.quarters,self.priority[type(i)]))

    def __init__(self,*items):
        self.items = []

        for item in items:
            if item.position is None:
                self.append(item)
            else:
                self.insert(item.position,item)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self,item):
        return item in self.items

    def __getitem__(self,index):
        if isinstance(index,slice):
            start = index.start-1 if index.start>0 else index.start
            stop  = index.stop -1 if index.stop >0 else index.stop
            return Stream(*self.items[start:stop])
        else:
            if index > 0: index -= 1
            return self.items[index]

    def __len__(self):
        return len(self.items)

    def __str__(self):

        if self.count == 0:
            return ''

        layouts = []
        for i in self:

            # choice between the decimal or fraction representation of position
            if len(str(i.quarters.decimal))-1 < len(str(i.quarters.fractional)):
                dec = 'quarters.decimal'
            else:
                dec = 'quarters.fractional'

            layouts.append(i.layout(['quarters.integral',
                                      dec,
                                     'duration',
                                     'text']))

        # set column widths
        columns = [max(w) for w in zip(*layouts)]

        # set layout pattern
        layout = '{:>%d}.{:<%d}\t {:>%d}\t {:<%d}' % (*columns,)

        lines = []
        for i in self:

            # choice between the decimal or fraction representation of position
            if len(str(i.quarters.decimal))-1 <= len(str(i.quarters.fractional)):
                dec = 'quarters.decimal'
            else:
                dec = 'quarters.fractional'
            # build the line
            lines.append(i.formatted(layout,('position.integral',
                                              dec,
                                             'duration',
                                             'text')))

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

        for item in self:
            s.insert(item.position,item.copy)

        return s

    def insert(self,*args):

        # extract item
        if len(args) > 0:
            item = args[-1]
            if not isinstance(item,StreamItem):
                raise RuntimeError('missing or invalid item.')
        else:
            raise RuntimeError('missing position and item.')

        # extract position
        position = time(args[:-1])

        # check position format
        if isinstance(position,MBR):
            quarters = self.system.translate(position)
        else:
            quarters = position
            position = self.system.translate(position)

        # remove occupied same type item
        overwrite=self.filter(lambda i:i.type==item.type and i.position==position)
        if len(overwrite) > 0:
            for item in overwrite:
                self.items.remove(item)

        # insert
        super().insert(quarters,item)

        # rearrange item positions for meter change
        if item.type is Meter:
            next = self.meters.filter(lambda m:m.quarters>quarters)
            if len(next) > 0:
                next   = next[1]
                amount = -(next.quarters - quarters) % item.bar_length
                # push afterward items after next meter accordingly
                self.since(next.quarters).shift(amount)

                realignment = self.since(quarters).until(next.quarters)

            else:
                realignment = self.since(quarters)

            # align to measure boundary for items between inserted and next meter
            realignment.align(sys=realignment.system,grid='measure')

    def remove(self,item):

        quarters = item.quarters

        self.items.remove(item)
        ref = self.get_context(quarters).meter

        if item.type is Meter:
            next = self.meters.filter(lambda m:m.quarters>quarters)
            if len(next) > 0:
                next   = next[1]
                amount = -(next.quarters - ref.quarters) % ref.bar_length
                self.since(next.quarters).shift(amount)

                realignment = self.since(quarters).until(next.quarters)
            else:
                realignment = self.since(quarters)

            realignment.align(sys=realignment.system,grid='measure')

    def filter(self,criteria):
        s = System(None,None)
        for item in self:
            if criteria(item):
                s.items.append(item)

        s.system = self.system

        return s

    def get_context(self,*position):
        from collections import namedtuple
        Context = namedtuple('Context',['key','meter'])

        position = time(position)

        if isinstance(position,MBR):
            position = self.translate(position)

        key = self.keys.filter(lambda k:k.quarters <= position)
        key = key[-1] if len(key)>0 else None
        meter = self.meters.filter(lambda m:m.quarters <= position)
        meter = meter[-1] if len(meter)>0 else None

        return Context(key,meter)


    def translate(self,*position):
        position = time(position)

        if isinstance(position,MBR):
            if position == MBR(1):
                return Quarters(0)
            else:
                ref = self.meters.filter(lambda m:m.position<position)[-1]
                bl  = ref.bar_length
                bt  = ref.size.quarters
                q   = ref.quarters
                q  += bl * (position.measure-ref.mbr.measure)
                q  += bt * (position.beat - 1)
                q  += position.remnant
                return q

        elif isinstance(position,Quarters):
            if position == 0:
                return MBR(1)
            else:
                ref = self.meters.filter(lambda m:m.quarters<position)[-1]
                bl  = ref.bar_length
                bt  = ref.size.quarters
                d   = position - ref.quarters
                m   = d // bl + ref.mbr.measure
                b   = d  % bl // bt + 1
                r   = d  % bt
                return MBR(m,b,r)

    def __init__(self,key=Key(C,major),meter=Meter(4,4),*items):

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

        for item in items:
            self.insert(item.position,item)

    def __str__(self):

        if self.count == 0:
            return ''

        layouts = []
        for i in self:

            if len(str(i.mbr.remnant.decimal))-1<len(str(i.mbr.remnant.fractional)):
                dec = 'mbr.remnant.decimal'
            else:
                dec = 'mbr.remnant.fractional'

            layouts.append(i.layout(['mbr.measure',
                                     'mbr.beat',
                                      dec,
                                     'text']))

        # set column widths
        columns = [max(w) for w in zip(*layouts)]

        # set layout pattern
        layout = '{:>%d}:{:>%d}:{:<%d}\t {:>%d}' % (*columns,)

        lines = []
        for i in self:

            # choice between the decimal or fraction representation of position
            if len(str(i.mbr.remnant.decimal))-1<len(str(i.mbr.remnant.fractional)):
                dec = 'mbr.remnant.decimal'
            else:
                dec = 'mbr.remnant.fractional'
            # build the line
            lines.append(i.formatted(layout,('mbr.measure',
                                             'mbr.beat',
                                              dec,
                                             'text')))

        return '\n'.join(lines)


'''
class Voice(Stream):

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self,num):
        self._number = num

        for item in self:
            item.vn = num

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

    def insert(self,*args):

        item = args[-1]
        if not isinstance(item,StreamItem):
            raise RuntimeError('missing or invalid item.')

        position = time(args[:-1])

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

    def set(self,*args):
        item = args[-1]
        if not isinstance(item,StreamItem):
            raise RuntimeError('missing or invalid item.')

        position = time(args[:-1])

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
        self.number = num
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

        layouts = [i.layout(['position.measure',
                             'position.beat',
                             'position.remnant',
                             'duration.dots',
                             'duration.base',
                             'duration.tuplet',
                             'text']) \
                   for i in s if type(i) not in [MeasureSeprator]]

        w1 = max([layout[0] for layout in layouts])
        w2 = max([layout[1] for layout in layouts])
        w3 = max([layout[2] for layout in layouts])
        w4 = max([layout[3] for layout in layouts])
        w5 = max([layout[4] for layout in layouts])
        w6 = max([layout[5] for layout in layouts])
        w7 = max([layout[6] for layout in layouts])

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

            lines.append(i.formatted(layout,
                              ['position.measure',
                               'position.beat',
                               'position.remnant',
                               'duration.dots',
                               'duration.base',
                               'duration.tuplet',
                               'text']))

        return '\n'.join(lines)
'''

class Voice(Stream):

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self,num):
        self._number = num

        for item in self:
            item.vn = num

    @property
    def measure(self):
        return self._measure

    @property
    def measures(self):
        return self._measure

    @property
    def copy(self):
        s = Voice(sys=self.system.copy,num=self.number)
        for item in self:
            s.insert(item.position,item.copy)
        return s

    def filter(self,criteria):
        s = Voice(sys=self.system,num=self.number)
        for item in self:
            if criteria(item):
                s.items.append(item)
        return s

    def insert(self, *args):
        item = args[-1]

        if not isinstance(item,StreamItem):
            raise RuntimeError('missing or invalid item.')

        pos = time(args[:-1])

        if isinstance(pos,MBR):
            quarters = self.system.translate(pos)
        else:
            quarters = pos

        # head and tail of insertion
        head = tail = quarters
        if hasattr(item,'duration'):
            tail += item.duration.quarters

        # detect possible collision
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

                collided.append(i)

        # remove collided
        for i in collided:
            self.remove(i)

        item.vn = self.number

        super().insert(quarters,item)


    def empty(self):
        for item in [i for i in self]:
            self.remove(item)

    def __init__(self,sys=None,num=1):

        super().__init__()

        self._measure = Measurement(self)

        self.number = num
        self.system = System() if sys is None else sys


    def __str__(self):

        if self.count == 0:
            return ''

        layouts = []
        for i in self:
            if len(str(i.mbr.remnant.decimal))-1<len(str(i.mbr.remnant.fractional)):
                dec = 'mbr.remnant.decimal'
            else:
                dec = 'mbr.remnant.fractional'

            layouts.append(i.layout(['mbr.measure',
                                     'mbr.beat',
                                      dec,
                                     'duration.dots',
                                     'duration.base',
                                     'duration.tuplet',
                                     'text']))

        # set column widths
        columns = [max(w) for w in zip(*layouts)]

        # build layout pattern
        layout ='{:>%d}:{:>%d}:{:<%d}\t {:>%d} {:>%d} {:<%d}\t {:>%d}' % (*columns,)

        lines = []
        for i in self:
            if len(str(i.mbr.remnant.decimal))-1<len(str(i.mbr.remnant.fractional)):
                dec = 'mbr.remnant.decimal'
            else:
                dec = 'mbr.remnant.fractional'

            lines.append(i.formatted(layout,['mbr.measure',
                                             'mbr.beat',
                                              dec,
                                             'duration.dots',
                                             'duration.base',
                                             'duration.tuplet',
                                             'text']))

        return '\n'.join(lines)



class Voices(object):

    def add(self,voice):
        self._voices.append(voice)

    def remove(self,voice):
        self._voices.remove(voice)

    def __init__(self):
        self._voices = []

    def __getitem__(self,*args):

        for arg in args:
            if isinstance(arg,int):
                for v in self:
                    if v.number == arg:
                        return v
                else:
                    raise IndexError('index out of range.')

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


    '''
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)
    '''

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

    def since(self,*position):
        pos = time(position)

        if isinstance(pos,MBR):
            return self.filter(lambda i:i.position>=pos)
        else:
            return self.filter(lambda i:i.quarters>=pos)

    def until(self,*position):
        pos = time(position)

        if isinstance(pos,MBR):
            return self.filter(lambda i:i.position<pos)
        else:
            return self.filter(lambda i:i.quarters<pos)

    def __init__(self,sys=None):
        self.system = System() if sys is None else sys
        self.voices = Voices()
        self.voices.add(Voice(sys=self.system,num=1))

    def __iter__(self):
        pass

    def __str__(self):
        # setting start and stop boundary
        # add measure seprator item
        # set context key and meter if necessary
        # merge
        # calculate layout measurement
        # construct text line
        pass

    def __repr__(self):
        pass
    

def time(p):

    if type(p) is tuple and 0 < len(p) < 4:
        if len(p) == 1:
            p = p[0]
            if type(p) is Quarters:
                return p
            elif type(p) is MBR:
                return p
            elif type(p) is int:
                return MBR(p)
            elif type(p) is float:
                return Quarters(p)
            else:
                raise RuntimeError('incorrect time format.')

        elif len(p) == 2:
            return MBR(p[0],p[1],0)
        else:
            return MBR(p[1],p[1],p[2])
    else:
        raise RuntimeError('missing or incorrect time format.')


