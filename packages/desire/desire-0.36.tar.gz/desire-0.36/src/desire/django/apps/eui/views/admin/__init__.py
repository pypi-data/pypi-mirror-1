from desire.django.apps.eui.views.base import DesireView
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

class DesireAdminView(AdminView, DesireView):
    pass

class DesireAdminIndexView(AdminIndexView, DesireView):
    pass

class DesireAdminModelView(AdminModelView, DesireView):
    pass

class DesireAdminListView(AdminListView, DesireView):
    pass 

class DesireAdminCreateView(AdminCreateView, DesireView):
    pass

class DesireAdminReadView(AdminReadView, DesireView):
    pass

class DesireAdminUpdateView(AdminUpdateView, DesireView):
    pass

class DesireAdminDeleteView(AdminDeleteView, DesireView):
    pass

class DesireAdminListHasManyView(AdminListHasManyView, DesireView):
    pass

class DesireAdminCreateHasManyView(AdminCreateHasManyView, DesireView):
    pass

class DesireAdminReadHasManyView(AdminReadHasManyView, DesireView):
    pass

class DesireAdminUpdateHasManyView(AdminUpdateHasManyView, DesireView):
    pass

class DesireAdminDeleteHasManyView(AdminDeleteHasManyView, AdminView):
    pass


def index(request):
    view = DesireAdminIndexView(request=request)
    return view.getResponse()

def model(request):
    view = DesireAdminModelView(request=request)
    return view.getResponse()

def list(request, className):
    view = DesireAdminListView(
        request=request,
        domainClassName=className,
    )
    return view.getResponse()

def create(request, className):
    view = DesireAdminCreateView(
        request=request,
        domainClassName=className,
    )
    return view.getResponse()

def read(request, className, objectKey):
    view = DesireAdminReadView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def update(request, className, objectKey):
    view = DesireAdminUpdateView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def delete(request, className, objectKey):
    view = DesireAdminDeleteView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
    )
    return view.getResponse()

def listHasMany(request, className, objectKey, hasMany):
    view = DesireAdminListHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
    )
    return view.getResponse()

def createHasMany(request, className, objectKey, hasMany):
    view = DesireAdminCreateHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
    )
    return view.getResponse()

def readHasMany(request, className, objectKey, hasMany, attrKey):
    view = DesireAdminReadHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()

def updateHasMany(request, className, objectKey, hasMany, attrKey):
    view = DesireAdminUpdateHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()

def deleteHasMany(request, className, objectKey, hasMany, attrKey):
    view = DesireAdminDeleteHasManyView(
        request=request,
        domainClassName=className,
        domainObjectKey=objectKey,
        hasManyName=hasMany,
        hasManyKey=attrKey,
    )
    return view.getResponse()


viewDict = {}
viewDict['ListView']   = DesireAdminListView
viewDict['CreateView'] = DesireAdminCreateView
viewDict['ReadView']   = DesireAdminReadView
viewDict['UpdateView'] = DesireAdminUpdateView
viewDict['DeleteView'] = DesireAdminDeleteView

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

