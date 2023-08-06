from scanbooker.django.apps.sui.views.base import ScanBookerView

class MySpaceView(ScanBookerView):

    templatePath = 'myspace'
    majorNavigationItem = '/myspace/'
    minorNavigationItem = '/myspace/'

    def __init__(self, **kwds):
        super(MySpaceView, self).__init__(**kwds)

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'My Notes', 'url': '/myspace/'}
        ]

    def canAccess(self):
        return self.canReadSystem()

    def setContext(self, **kwds):
        super(MySpaceView, self).setContext(**kwds)
        self.context.update({
        })


def myspace(request):
    view = MySpaceView(request=request)
    return view.getResponse()

