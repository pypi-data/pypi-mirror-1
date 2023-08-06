from scanbooker.django.apps.sui.views.registry import ScanBookerRegistryUpdateView

class SettingsUpdateView(ScanBookerRegistryUpdateView):

    def __init__(self, **kwds):
        super(SettingsUpdateView, self).__init__(
            registryPath='settings/default',
            actionName='update',
            **kwds
        )

def update(request):
    view = SettingsUpdateView(request=request)
    return view.getResponse()
