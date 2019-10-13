from cmat.basic   import Interval
from cmat.quality import major,minor,perfect,augmented,diminished

unison     = Interval(1)
second     = Interval(2)
third      = Interval(3)
fourth     = Interval(4)
fifth      = Interval(5)
sixth      = Interval(6)
seventh    = Interval(7)
octave     = Interval(8)
nineth     = Interval(9)
tenth      = Interval(10)
eleventh   = Interval(11)
twelfth    = Interval(12)
thirteenth = Interval(13)
fourteenth = Interval(14)

P1 = perfect/unison
M2 = major/second
m2 = minor/second
M3 = major/third
m3 = minor/third
P4 = perfect/fourth
P5 = perfect/fifth
M6 = major/sixth
m6 = minor/sixth
M7 = major/seventh
m7 = minor/seventh
P8 = perfect/octave
M9 = major/nineth
m9 = minor/nineth

aug1 = augmented/unison
aug2 = augmented/second
aug3 = augmented/third
aug4 = augmented/fourth
aug5 = augmented/fifth
aug6 = augmented/sixth
aug7 = augmented/seventh
aug8 = augmented/octave
aug9 = augmented/nineth

dim1 = diminished/unison
dim2 = diminished/second
dim3 = diminished/third
dim4 = diminished/fourth
dim5 = diminished/fifth
dim6 = diminished/sixth
dim7 = diminished/seventh
dim8 = diminished/octave
dim9 = diminished/nineth

semitone  = Interval(1,1)
wholetone = Interval(1,2)

