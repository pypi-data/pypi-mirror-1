from dm.accesscontrol import SystemAccessController
from kforge.exceptions import *

class ProjectAccessController(SystemAccessController):
    "Introduces project member role to access controller."

    def isAccessAuthorised(self, project=None, **kwds):
        self.project = project
        return super(ProjectAccessController, self).isAccessAuthorised(**kwds)

    def assertAccessAuthorised(self):
        if self.isProjectRoleAuthorised(): # Check member's role first to help
            raise AccessIsAuthorised       # speed svn commits for developers.
        super(ProjectAccessController, self).assertAccessAuthorised()

    def isProjectRoleAuthorised(self):
        if not self.project:
            if self.debug:
                self.logger.debug("Access not authorised by project.")
            return False
        if self.isPersonAuthorisedOnProject():
            return True
        if self.isPersonNotVisitor():  # To avoid repetition.
            if self.isVisitorAuthorisedOnProject():
                return True
        return False
            
    def isPersonAuthorisedOnProject(self):
        if self.project in self.person.memberships:
            membership = self.person.memberships[self.project]
            if self.isRoleAuthorised(membership.role):
                if self.debug:
                    msg = "Access authorised by project membership."
                    self.logger.debug(msg)
                return True
        if self.debug:
            msg = "Access not authorised by project membership for person."
            self.logger.debug(msg)
        return False
        
    def isPersonNotVisitor(self):
        return self.person.name != self.getVisitor().name
            
    def isVisitorAuthorisedOnProject(self):
        visitor = self.getVisitor()
        if self.project in visitor.memberships:
            membership = visitor.memberships[self.project]
            if self.isRoleAuthorised(membership.role):
                if self.debug:
                    msg = "Access authorised by visitor project membership."
                    self.logger.debug(msg)
                return True
        if self.debug:
            msg = "Access not authorised by project membership for visitor."
            self.logger.debug(msg)
        return False


