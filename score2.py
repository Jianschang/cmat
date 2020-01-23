class Measurement(object):
'''
Interface for accessing music stream by measure.
'''

    def __init__(self,stream):
        self._stream = stream

    def __getitem__(self,*args):

        s = self._stream
        l = len(args)

        if l > 0:

            if l == 1:
                i = args[0]
                if type(i) is int:
                    return s.filter(lambda e:e.position.measure == i)
                elif type(i) is slice:
                    return s.filter(lambda e:i.start<=e.position.measure<i.stop)
                else:
                    raise IndexError('invalid index number.')
            else:
                return s.filter(lambda e: e.position.measure in args)

        else:
            raise IndexError('missing measure number.')

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
        grd = p[type(item)]

        ip = 0
        while (self.items[ip].position,p[type(self.items[ip])]) <= (pos,grd):
            if ip >= self.count:
                break

            ip += 1

        if item.site is None:
            item.site = self

        item.position = pos

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

        layouts = [i.layout(['position','duration','text']) for i in self]
        columns = [max(w) for w in zip(*layouts)]

        layout = '{:>%d}\t {:>%d}\t {:<%d}' % (*columns)

        lines = []
        for i in self:
            lines.append(i.formatted(layout,('position','duration','text')))

        return '\n'.join(lines)

    def __repr__(self):
        return str(self)

class System(stream):

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
        overwrite = self.filter(lambda i:i.type is item.type and i.position=position)
        if len(overwrite) > 0:
            for item in overwrite:
                self.items.remove(item)

        # insert
        super().insert(position,item)

        # rearrange item positions for meter change
        if item.type is Meter:
            next = self.meters.since(position)
            if len(next) > 0:
                next  = next[-1]
                shift = (next.quarters - quarters) % item.bar_length
                # push afterward items after next meter accordingly
                self.since(next.position).shift(shift)

                realignment = self.since(position).until(next.position)

            else:
                realignment = self.since(position)

            # align to measure boundary for items between inserted and next meter
            realigment.align(grid='measure')

    def remove(self,item):
        pass

    def filter(self,criteria):
        s = System(None,None)
        for item in self:
            if criteria(item):
                s.items.append(item)

        s.system = self.system

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
                ref = self.meters.filter(lambda m:m.position<=position)[-1]
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
                ref = self.meters.filter(lambda m:m.quarters<=position)[-1]
                bl  = ref.bar_length
                bt  = ref.size.quarters
                d   = position - ref.quarters
                m   = d // bl + ref.mbr.measure
                b   = d  % bl // bt + 1
                r   = d  % bt
                return MBR(m,b,r)

