import dm.dom.session
from dm.dom.meta import DateTime
import mx.DateTime

class Session(dm.dom.session.Session):

    scheduleBookmark = DateTime(default=mx.DateTime.now)

