from dm.view.manipulator import BaseManipulator
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
import dm.webkit as webkit
from kforge.ioc import *
from kforge.exceptions import KforgeCommandError
import re
import kforge.re
import kforge.command

class PersonManipulator(DomainObjectManipulator):

    def isPersonName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.re.personName)
        if not pattern.match(field_data):
            msg = "This field can only contain alphanumerics, "
            msg += "underscores, hyphens, and dots."
            raise webkit.ValidationError(msg)

    def isReservedPersonName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.re.reservedPersonName)
        if pattern.match(field_data):
            msg = "This field is reserved and can not be registered."
            raise webkit.ValidationError(msg)

    def isAvailablePersonName(self, field_data, all_data):
        command = kforge.command.AllPersonRead(field_data)
        try:
            command.execute()
        except KforgeCommandError:
            pass
        else:
            message = "Person name is already being used by another person."
            raise webkit.ValidationError(message)

    def isMatchingPassword(self, field_data, all_data):
        password = all_data['password']
        passwordconfirmation = all_data['passwordconfirmation']
        if not (password == passwordconfirmation):
            raise webkit.ValidationError("Passwords do not match.")

    def isMatchingEmail(self, field_data, all_data):
        email = all_data['email']
        emailconfirmation = all_data['emailconfirmation']
        if not (email == emailconfirmation):
            raise webkit.ValidationError("Emails do not match.")

    def isCaptchaCorrect(self, field_data, all_data):
        if self.dictionary['captcha.enable']:
            word = all_data['captcha']
            hash = all_data['captchahash']
            if not word and not hash:
                raise webkit.ValidationError("Captcha failure.")
            read = kforge.command.CaptchaRead(hash)
            try:
                read.execute()
            except KforgeCommandError, inst: 
                raise webkit.ValidationError("Captcha failure.")
            captcha = read.object
            if not captcha.checkWord(word):
                raise webkit.ValidationError("Captcha failure.")


class PersonCreateManipulator(PersonManipulator):

    def buildFields(self):
        self.fields.append(
            webkit.TextField(
                field_name="name", 
                is_required=True, 
                validator_list=[
                    self.isPersonName, 
                    self.isReservedPersonName, 
                    self.isAvailablePersonName, 
                    self.isTwoCharsMin,
                    self.isTwentyCharsMax,
                ]
            )
        )
        self.fields.append(
            webkit.PasswordField(
                field_name="password", 
                is_required=True, 
                validator_list=[
                    self.isFourCharsMin,
                ]
            )
        )
        self.fields.append(
            webkit.PasswordField(
                field_name="passwordconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingPassword
                ]
            )
        )
        self.fields.append(
            webkit.TextField(
                field_name="fullname", 
                is_required=True
            )
        )
        self.fields.append(
            webkit.EmailField(
                field_name="email", 
                is_required=True
            )
        )
        self.fields.append(
            webkit.EmailField(
                field_name="emailconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingEmail
                ]
            ) 
        )
        if self.dictionary['captcha.enable']:
            self.fields.append(
                webkit.TextField(
                    field_name="captcha", 
                    is_required=isCaptchaEnabled, 
                    validator_list=[
                        self.isCaptchaCorrect
                    ]
                ) 
            )
            self.fields.append(
                webkit.HiddenField(
                    field_name="captchahash", 
                    is_required=False,
                )   
            )

class PersonUpdateManipulator(PersonManipulator):

    def buildFields(self):
        self.fields.append(
            webkit.PasswordField(
                field_name="password", 
                is_required=False, 
                validator_list=[
                    self.isFourCharsMin,
                ]
            )
        )
        self.fields.append(
            webkit.PasswordField(
                field_name="passwordconfirmation", 
                is_required=False, 
                validator_list=[
                    self.isMatchingPassword
                ]
            )
        )
        self.fields.append(
            webkit.TextField(
                field_name="fullname", 
                is_required=True
            )
        )
        self.fields.append(
            webkit.EmailField(
                field_name="email", 
                is_required=True
            )
        )


class ProjectManipulator(DomainObjectManipulator):

    def isProjectName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.re.projectName)
        if not pattern.match(field_data):
            msg = "This field can only contain lowercase letters or numbers."
            raise webkit.ValidationError(msg)

    def isReservedProjectName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.re.reservedProjectName)
        if pattern.match(field_data):
            msg = "This field is reserved and can not be registered."
            raise webkit.ValidationError(msg)

    def isAvailableProjectName(self, field_data, all_data):
        command = kforge.command.AllProjectRead(field_data)
        try:
            command.execute()
        except KforgeCommandError:
            pass
        else:
            message = "Project name is already being used by another project."
            raise webkit.ValidationError(message)


class ProjectCreateManipulator(ProjectManipulator):

    def buildFields(self):
        self.fields = (
            webkit.TextField(
                field_name="title", 
                is_required=True
            ),
            webkit.SelectMultipleField(
                field_name="licenses", 
                is_required=True,
                choices=self.listRegisteredLicenses(),
                size=4,
            ),
            webkit.LargeTextField(
                field_name="description", 
                is_required=True,
                validator_list=[
                ]
            ),
            webkit.TextField(
                field_name="name", 
                is_required=True, 
                maxlength=15,
                validator_list=[
                    self.isProjectName, 
                    self.isAvailableProjectName, 
                    self.isReservedProjectName, 
                    self.isThreeCharsMin,
                    self.isFifteenCharsMax,
                ]
            ),
        )

    def listRegisteredLicenses(self):
        command = kforge.command.LicenseList()
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(l.id, l.name) for l in command.licenses]


class ProjectUpdateManipulator(ProjectManipulator):

    def buildFields(self):
        self.fields = (
            webkit.TextField(
                field_name="title", 
                is_required=True
            ),
            webkit.SelectMultipleField(
                field_name="licenses", 
                is_required=True,
                choices=self.listRegisteredLicenses(),
                size=4,
            ),
            webkit.LargeTextField(
                field_name="description", 
                is_required=True,
                validator_list=[
                ]
            ),
        )

    def listRegisteredLicenses(self):
        command = kforge.command.LicenseList()
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(l.id, l.name) for l in command.licenses]


class MemberEditManipulator(BaseManipulator):

    def __init__(self):
        self.fields = (
            webkit.SelectField(
                field_name="role", 
                is_required=True,
                choices=self.listRegisteredRoles(),
            ),
        )

    def listRegisteredRoles(self):
        command = kforge.command.RoleList()
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(r.name, r.name) for r in command.roles]


class ServiceManipulator(HasManyManipulator):

    def isServiceName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.re.serviceName)
        if not pattern.match(field_data):
            msg = "This field can only contain alphanumerics, "
            msg += "underscores, and hyphens."
            raise webkit.ValidationError(msg)

    def isAvailableServiceName(self, field_data, all_data):
        serviceName = all_data['name']
        service = self.domainObject
        if self.domainObject and (service.name == serviceName):
            return True
        project = self.objectRegister.owner
        if not serviceName in project.services:
            return True
        else:
            message = "A service called '%s' already exists." % (serviceName)
            message += " Please choose another service name."
            raise webkit.ValidationError(message)


class ServiceCreateManipulator(ServiceManipulator):

    def buildFields(self):
        self.fields = (
            webkit.SelectField(
                field_name="plugin", 
                is_required=True,
                choices=self.listPlugins(),
            ),
            webkit.TextField(
                field_name="name", 
                is_required=False,
                validator_list=[
                    self.isServiceName,
                    self.isAvailableServiceName,
                ]
            ),
        )

    def listPlugins(self):
        command = kforge.command.ProjectPluginList(self.objectRegister.owner)
        try:
            command.execute()
        except KforgeCommandError:
            return []
        else:
            return [(p.name, p.name) for p in command.results]


class ServiceUpdateManipulator(ServiceManipulator):

    def buildFields(self):
        self.fields = (
            webkit.TextField(
                field_name="name", 
                is_required=False,
                validator_list=[
                    self.isServiceName,
                    self.isAvailableServiceName,
                ]
            ),
        )


class ServiceExtnManipulator(HasManyManipulator):

    def isAttrExcluded(self, metaAttr):
        # super() doesn't work, hence:
        if HasManyManipulator.isAttrExcluded(self, metaAttr):
            return True 
        if metaAttr.name == 'service':
            return True
        return False

    def create(self, data):
        # extn object created by plugin event handlers
        self.update(data)  

