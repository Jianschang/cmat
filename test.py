from cmat import *
from cmat.score import *
from cmat.pitch import *

s = Stream()

s.append(quarter/C4)
s.append(dotted/eighth/E4)
s.append(sixteenth/G4)
s.append(quarter/rest)
s.append(eighth/F4)
s.append(eighth/Eb4)

s.append(Meter(2,4))
s.append(half/G4)
s.append(dotted/quarter/Ab4)
s.append(eighth/Bb4)

