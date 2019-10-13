class Word(object):                                                       # Word

    def __init__(self,name):
        self._name = name

    def __str__(self):
        return self._name

    def __repr__(self):
        return str(self)

    def __eq__(self,word):
        if isinstance(word,Word):
            return self._name == word._name
        else:
            return NotImplemented

    def __sub__(self,obj):
        return self.__truediv__(obj)

    def __truediv__(self,obj):
        return Construct(self,obj).conclude()

rest = Word('rest')

class Qualifier(Word):
    pass

class Modifier(Word):
    pass

class Construct(object):
    @property
    def parts(self):
        return self._parts

    @property
    def size(self):
        return len(self._parts)

    def append(self,part):
        self._parts.append(part)

    def match(self,pattern):
        #set_trace()
        for i,p in enumerate(pattern):
            if i >= self.size: return True
            s = self[i]

            if type(p) is type:
                if not isinstance(s,p): return False
            elif hasattr(p,'__iter__'):
                if not any([isinstance(s,b) if type(b) is type else s==b for b in p]):
                    return False
            elif s!=p:
                return False
        else:
            return True

    def conclude(self):
        from cmat.basic     import Accidental,PitchClass,Pitch
        from cmat.basic     import Interval,NoteType,Duration,Tuplet
        from cmat.basic     import sharp,flat
        from cmat.quality   import perfect,major,minor,augmented,diminished
        from cmat.quality   import double,triple,quadruple

        from cmat.duration  import dotted
        from cmat.score     import Note,Rest

        if self.match([double,(sharp,flat)]):
            m,acc = self.parts
            return Accidental(acc.alternation*2)

        elif self.match((PitchClass,Accidental)):
            pc,acc = self._parts
            return PitchClass(pc.degree,acc)

        elif self.match((PitchClass,double,(sharp,flat))):
            if len(self)<3: return self
            p,w,a = self._parts
            return PitchClass(p.degree,Accidental(a.alternation*2))

        elif self.match(((major,minor,perfect,augmented,diminished),Interval)):
            w,i = self._parts
            s,t = i.steps,i.semitones

            n = [None,0,2,4,5,7,9,11,12,14,16,17,19,21,23]
            t = n[s]

            if s in (1,4,5,8,11,12):
                if   w == perfect: return Interval(s,t)
                elif w == augmented: return Interval(s,t+1)
                elif w == diminished: return Interval(s,t-1)
            else:
                if   w == major: return Interval(s,t)
                elif w == minor: return Interval(s,t-1)
                elif w == diminished: return Interval(s,t-2)
                elif w == augmented: return Interval(s,t+1)

        elif self.match(((double,triple,quadruple),(diminished,augmented),Interval)):
            if len(self)<3: return self
            m,w,i = self._parts
            s,t   = i.steps,i.semitones

            n = [None,0,2,4,5,7,9,11,12,14,16,17,19,21,23]
            t = n[s]

            if s in (1,4,5,8,11,12):
                if   (m,w) == (double,diminished):    return Interval(s,t-2)
                elif (m,w) == (triple,diminished):    return Interval(s,t-3)
                elif (m,w) == (quadruple,diminished): return Interval(s,t-4)
                elif (m,w) == (double,augmented):     return Interval(s,t+2)
                elif (m,w) == (triple,augmented):     return Interval(s,t+3)
                elif (m,w) == (triple,augmented):     return Interval(s,t+4)
            else:
                if   (m,w) == (double,diminished):    return Interval(s,t-3)
                elif (m,w) == (triple,diminished):    return Interval(s,t-4)
                elif (m,w) == (quadruple,diminished): return Interval(s,t-5)
                elif (m,w) == (double,augmented):     return Interval(s,t+2)
                elif (m,w) == (triple,augmented):     return Interval(s,t+3)
                elif (m,w) == (triple,augmented):     return Interval(s,t+4)

        elif self.match((dotted,NoteType)):
            d,b = self._parts
            return Duration(b,1)
        elif self.match((NoteType,Tuplet)):
            b,t = self._parts
            return Duration(b,0,t)
        elif self.match((Duration,Tuplet)):
            d,t = self._parts
            return Duration(d.base,d.dots,t)
        elif self.match(((double,triple),dotted,NoteType)):
            if len(self)<3: return self
            m,d,b = self._parts
            if   m == double: return Duration(b,2)
            elif m == triple: return Duration(b,3)
        elif self.match((Duration,Pitch)):
            from cmat.score import Note
            d,p = self._parts
            return Note(d,p)
        elif self.match((NoteType,Pitch)):
            from cmat.score import Note
            n,p = self._parts
            return Note(Duration(n),p)
        elif self.match((Duration,rest)):
            from cmat.score import Rest
            d,p = self._parts
            return Rest(d)
        elif self.match((NoteType,rest)):
            from cmat.score import Rest
            n,p = self._parts
            return Rest(Duration(n))


        else:
            raise ValueError('unrecognized combination:{}'.format(self))

    def __init__(self,*parts):
        self._parts = []
        for p in parts:
            self._parts.append(p)

    def __str__(self):
        return  ' '.join([str(p) for p in self._parts])

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self._parts)

    def __getitem__(self,index):
        return self._parts[index]

    def __iter__(self):
        return iter(self._parts)

    def __sub__(self,other):
        return self.__truediv__(other)

    def __truediv__(self,other):
        self.append(other)
        return self.conclude()


