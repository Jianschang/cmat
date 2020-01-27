from cmat.basic import Pitch, PitchClass, Accidental, Interval
from cmat.basic import NoteType, Tuplet, Duration
from cmat.basic import Triad

from cmat.basic import C,Cn,Cs,Cx,Cb,Cbb,D,Dn,Ds,Dx,Db,Dbb
from cmat.basic import E,En,Es,Ex,Eb,Ebb,F,Fn,Fs,Fx,Fb,Fbb
from cmat.basic import G,Gn,Gs,Gx,Gb,Gbb,A,An,As,Ax,Ab,Abb
from cmat.basic import B,Bn,Bs,Bx,Bb,Bbb

from cmat.basic import natural, sharp, flat

from cmat.interval import unison, second, third, fourth, fifth
from cmat.interval import sixth, seventh, octave, semitone, wholetone

from cmat.quality  import double,triple
from cmat.quality  import major, minor, perfect, augmented, diminished
#from cmat.quality  import harmonic, melodic, chromatic

from cmat.duration import whole,half,quarter,eighth,sixteenth,dotted
from cmat.tuplet   import triplet

from cmat import pitch
from cmat import interval
from cmat import tuplet
from cmat import duration
from cmat import key

from cmat.score  import MBR,Key,Meter,Stream,System #,Voice
from cmat.syntax import rest
_all__ = [
           # sub modules
           'pitch','interval','duration','tuplet','triad','key',

           # basic types
           'Pitch','PitchClass','Accidental','NoteType','Duration',
           'Tuplet','Interval','Triad','Construct',

           # pitch class
           'C','Cn','Cs','Cx','Cb','Cbb',
           'D','Dn','Ds','Dx','Db','Dbb',
           'E','En','Es','Ex','Eb','Ebb',
           'F','Fn','Fs','Fx','Fb','Fbb',
           'G','Gn','Gs','Gx','Gb','Gbb',
           'A','An','As','Ax','Ab','Abb',
           'B','Bn','Bs','Bx','Bb','Bbb',

           # accidentals
           'sharp','flat','natural',

           # intervals
           'unison','second','third','fourth',
           'fifth','sixteeth','seventh','octave',
           'semitone','wholetone',

           # interval and key qualities
           'major','minor','perfect','augmented','diminished',
           'double','triple',

           # note types
           'whole','half','quarter','eighth','sixteenth',
           # modifier and tuplets
           'dotted','triplet',

           # score
           'MBR','Key','Meter','Stream','rest'
           
           ]

mr = MBR
