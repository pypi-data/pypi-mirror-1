from dm.view.rpc import RegistryAutocompleterView, RegistryAutocompleter
from dm.view.rpc import RegistryAutoappenderView
from dm.view.rpc import RegistryAutodeleteView
from dm.view.rpc import RegistryAttrupdateView

def autocomplete(request):
    view = RegistryAutocompleterView(
        request=request,
        completer=RegistryAutocompleter(),
        queryName='queryString',
    )
    return view.getResponse()

def autoappend(request):
    view = RegistryAutoappenderView(
        request=request,
    )
    return view.getResponse()

def autodelete(request):
    view = RegistryAutodeleteView(
        request=request,
    )
    return view.getResponse()

def attrupdate(request):
    view = RegistryAttrupdateView(
        request=request,
    )
    return view.getResponse()

