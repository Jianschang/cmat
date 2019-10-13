from cmat.basic  import NoteType
from cmat.syntax import Modifier

whole        = NoteType(4)
half         = NoteType(2)
quarter      = NoteType(1)
eighth       = NoteType(1/2)
sixteenth    = NoteType(1/4)
thirtySecond = NoteType(1/8)
sixtyFourth  = NoteType(1/16)

dotted       = Modifier('dotted')
