from kforge.django.apps.kui.views.projectHasMany import ProjectHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
from kforge.django.apps.kui.views import manipulator

class ServiceView(ProjectHasManyView):

    hasManyClassName = 'Service'
            
    def __init__(self, **kwds):
        super(ServiceView, self).__init__(hasManyName='services', **kwds)

    def setContext(self):
        super(ServiceView, self).setContext()
        self.context.update({
            'service' : self.getAssociationObject(),
            'canCreateService': self.canCreateService(),
            'canUpdateService': self.canUpdateService(),
            'canDeleteService': self.canDeleteService(),
        })

    def setMinorNavigationItem(self):
        if self.hasManyKey:
            self.minorNavigationItem = '/project/%s/services/%s/' % (
                self.domainObjectKey, self.hasManyKey
            )
        else:
            self.minorNavigationItem = '/project/%s/services/' % (
                self.domainObjectKey
            )

    def makePostManipulateLocation(self):
        return '/project/%s/services/' % (
            self.domainObjectKey
        )

    def serviceExtendsDomainModel(self):
        service = self.getAssociationObject()
        if not service:
            return False
        if not service.plugin.extendsDomainModel():
            return False
        return True
        

class ServiceListView(ServiceView, AbstractListHasManyView):

    templatePath = 'service/list'
         
    def canAccess(self):
        return self.canReadProject()


class ServiceCreateView(ServiceView, AbstractCreateHasManyView):

    templatePath = 'service/create'
    
    def canAccess(self):
        return self.canCreateService()
        
    def makePostManipulateLocation(self):
        if self.serviceExtendsDomainModel():
            return '/project/%s/services/%s/extn/create/' % (
                self.domainObjectKey,
                self.getAssociationObject().name
            )
        else:
            return '/project/%s/services/%s/' % (
                self.domainObjectKey,
                self.getAssociationObject().name
            )

    def getManipulatorClass(self):
        return manipulator.ServiceCreateManipulator


class ServiceReadView(ServiceView, AbstractReadHasManyView):

    templatePath = 'service/read'

    def canAccess(self):
        return self.canReadService()


class ServiceUpdateView(ServiceView, AbstractUpdateHasManyView):

    templatePath = 'service/update'

    def canAccess(self):
        return self.canUpdateService()

    def makePostManipulateLocation(self):
        if self.serviceExtendsDomainModel():
            return '/project/%s/services/%s/extn/update/' % (
                self.domainObjectKey,
                self.getAssociationObject().name,
            )
        else:
            return '/project/%s/services/%s/' % (
                self.domainObjectKey,
                self.getAssociationObject().name,
            )

    def getManipulatorClass(self):
        return manipulator.ServiceUpdateManipulator


class ServiceDeleteView(ServiceView, AbstractDeleteHasManyView):

    templatePath = 'service/delete'

    def canAccess(self):
        return self.canDeleteService()


class ServiceExtnView(ServiceView):

    def getManipulatorClass(self):
        return manipulator.ServiceExtnManipulator

    def getManipulatedObjectRegister(self):
        service = self.getAssociationObject()
        return service.getExtnRegister()

    def getManipulatedDomainObject(self):
        service = self.getAssociationObject()
        return service.getExtnObject()

    def makePostManipulateLocation(self):
        return '/project/%s/services/%s/' % (
            self.domainObjectKey,
            self.hasManyKey,
        )


class ServiceExtnCreateView(ServiceExtnView, ServiceCreateView):

    templatePath = 'serviceExtn/create'


class ServiceExtnUpdateView(ServiceExtnView, ServiceUpdateView):

    templatePath = 'serviceExtn/update'


def list(request, projectName=''):
    view = ServiceListView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()

def create(request, projectName):
    view = ServiceCreateView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def read(request, projectName, serviceName):
    view = ServiceReadView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()
    
def update(request, projectName, serviceName):
    view = ServiceUpdateView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()
    
def delete(request, projectName, serviceName):
    view = ServiceDeleteView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()

def extnCreate(request, projectName, serviceName):
    view = ServiceExtnCreateView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()

def extnUpdate(request, projectName, serviceName):
    view = ServiceExtnUpdateView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=serviceName,
    )
    return view.getResponse()

