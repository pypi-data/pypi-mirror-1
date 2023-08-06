from dm.dom.stateful import *

class Week(DatedStatefulObject):

    isUnique = True
    
    starts = RDate()
    isPublished = Boolean()
    notesPublic = MarkdownText()
    notesPrivate = MarkdownText()
    
    registerKeyName = 'starts'

