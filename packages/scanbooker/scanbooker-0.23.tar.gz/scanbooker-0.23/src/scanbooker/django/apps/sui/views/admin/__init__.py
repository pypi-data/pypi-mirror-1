from scanbooker.django.apps.sui.views.base import ScanBookerView
from dm.view.admin import AdminView
from dm.view.admin import AdminIndexView
from dm.view.admin import AdminModelView
from dm.view.admin import AdminListView
from dm.view.admin import AdminCreateView
from dm.view.admin import AdminReadView
from dm.view.admin import AdminUpdateView
from dm.view.admin import AdminDeleteView
from dm.view.admin import AdminListHasManyView
from dm.view.admin import AdminCreateHasManyView
from dm.view.admin import AdminReadHasManyView
from dm.view.admin import AdminUpdateHasManyView
from dm.view.admin import AdminDeleteHasManyView

class ScanBookerAdminView(AdminView, ScanBookerView):
    pass

class ScanBookerAdminIndexView(AdminIndexView, ScanBookerView):
    pass

class ScanBookerAdminModelView(AdminModelView, ScanBookerView):
    pass

class ScanBookerAdminListView(AdminListView, ScanBookerView):
    pass 

class ScanBookerAdminCreateView(AdminCreateView, ScanBookerView):
    pass

class ScanBookerAdminReadView(AdminReadView, ScanBookerView):
    pass

class ScanBookerAdminUpdateView(AdminUpdateView, ScanBookerView):
    pass

class ScanBookerAdminDeleteView(AdminDeleteView, ScanBookerView):
    pass

class ScanBookerAdminListHasManyView(AdminListHasManyView, ScanBookerView):
    pass

class ScanBookerAdminCreateHasManyView(AdminCreateHasManyView, ScanBookerView):
    pass

class ScanBookerAdminReadHasManyView(AdminReadHasManyView, ScanBookerView):
    pass

class ScanBookerAdminUpdateHasManyView(AdminUpdateHasManyView, ScanBookerView):
    pass

class ScanBookerAdminDeleteHasManyView(AdminDeleteHasManyView, AdminView):
    pass


def index(request):
    view = ScanBookerAdminIndexView(request=request)
    return view.getResponse()

def model(request):
    view = ScanBookerAdminModelView(request=request)
    return view.getResponse()

def list(request, className):
    view = ScanBookerAdminListView(
        request=request,
        domainClassName=className,
    )
    return view.getResponse()

def create(request, className):
    view = ScanBookerAdminCreateView(
        request=request,
        domainClassName=className,
    )
    return view.getResponse()

def read(request, className, objectKey):
    view = ScanBookerAdminReadView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def update(request, className, objectKey):
    view = ScanBookerAdminUpdateView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def delete(request, className, objectKey):
    view = ScanBookerAdminDeleteView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def listHasMany(request, className, objectKey, hasMany):
    view = ScanBookerAdminListHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
    )
    return view.getResponse()

def createHasMany(request, className, objectKey, hasMany):
    view = ScanBookerAdminCreateHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
    )
    return view.getResponse()

def readHasMany(request, className, objectKey, hasMany, attrKey):
    view = ScanBookerAdminReadHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()

def updateHasMany(request, className, objectKey, hasMany, attrKey):
    view = ScanBookerAdminUpdateHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()

def deleteHasMany(request, className, objectKey, hasMany, attrKey):
    view = ScanBookerAdminDeleteHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()


viewDict = {}
viewDict['ListView']   = ScanBookerAdminListView
viewDict['CreateView'] = ScanBookerAdminCreateView
viewDict['ReadView']   = ScanBookerAdminReadView
viewDict['UpdateView'] = ScanBookerAdminUpdateView
viewDict['DeleteView'] = ScanBookerAdminDeleteView

def view(request, caseName, actionName, className, objectKey):
    if caseName == 'model':
        viewClassName = actionName.capitalize() + 'View'
        viewClass = viewDict[viewClassName]
        viewArgs = []
        if className:
            viewArgs.append(className)
            if objectKey:
                viewArgs.append(objectKey)
        view = viewClass(request=request)
        return view.getResponse(*viewArgs)
    raise Exception, "Case '%s' not supported." % caseName

