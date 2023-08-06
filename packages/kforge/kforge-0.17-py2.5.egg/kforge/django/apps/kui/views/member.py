from kforge.django.apps.kui.views.projectHasMany import ProjectHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
from kforge.django.apps.kui.views import manipulator

class MemberView(ProjectHasManyView):

    hasManyClassName = 'Member'

    def __init__(self, **kwds):
        super(MemberView, self).__init__(hasManyName='members', **kwds)

    def setContext(self):
        super(MemberView, self).setContext()
        self.context.update({
            'member' : self.getAssociationObject(),
        })

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/project/%s/members/' % self.domainObjectKey


class MemberListView(MemberView, AbstractListHasManyView):

    templatePath = 'member/list'
    
    def canAccess(self):
        return self.canReadProject()


class MemberCreateView(MemberView, AbstractCreateHasManyView):

    templatePath = 'member/create'
    
    def canAccess(self):
        return self.canCreateMember()

    def makePostManipulateLocation(self):
        return '/project/%s/%s/' % (
            self.domainObjectKey, self.hasManyName
        )

    def getManipulatorClass(self):
        return manipulator.MemberCreateManipulator


class MemberUpdateView(MemberView, AbstractUpdateHasManyView):

    templatePath = 'member/update'
    
    def canAccess(self):
        return self.canUpdateMember()

    def makePostManipulateLocation(self):
        return '/project/%s/%s/' % (
            self.domainObjectKey, self.hasManyName
        )

    def getManipulatorClass(self):
        return manipulator.MemberUpdateManipulator


class MemberDeleteView(MemberView, AbstractDeleteHasManyView):

    templatePath = 'member/delete'
    
    def canAccess(self):
        return self.canDeleteMember()

    def makePostManipulateLocation(self):
        return '/project/%s/%s/' % (
            self.domainObjectKey, self.hasManyName
        )


def list(request, projectName=''):
    view = MemberListView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def create(request, projectName=''):
    view = MemberCreateView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def update(request, projectName='', personName=''):
    view = MemberUpdateView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()
    
def delete(request, projectName='', personName=''):
    view = MemberDeleteView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()

