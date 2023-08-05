from dm.view.manipulator import BaseManipulator
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
from dm.view.manipulator import djangoforms
from dm.view.manipulator import djangovalidators
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
            raise djangovalidators.ValidationError(msg)

    def isReservedPersonName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.re.reservedPersonName)
        if pattern.match(field_data):
            msg = "This field is reserved and can not be registered."
            raise djangovalidators.ValidationError(msg)

    def isAvailablePersonName(self, field_data, all_data):
        command = kforge.command.AllPersonRead(field_data)
        try:
            command.execute()
        except KforgeCommandError:
            pass
        else:
            message = "Person name is already being used by another person."
            raise djangovalidators.ValidationError(message)

    def isMatchingPassword(self, field_data, all_data):
        password = all_data['password']
        passwordconfirmation = all_data['passwordconfirmation']
        if not (password == passwordconfirmation):
            raise djangovalidators.ValidationError("Passwords do not match.")

    def isMatchingEmail(self, field_data, all_data):
        email = all_data['email']
        emailconfirmation = all_data['emailconfirmation']
        if not (email == emailconfirmation):
            raise djangovalidators.ValidationError("Emails do not match.")

    def isCaptchaCorrect(self, field_data, all_data):
        if self.dictionary['captcha.enable']:
            word = all_data['captcha']
            hash = all_data['captchahash']
            if not word and not hash:
                raise djangovalidators.ValidationError("Captcha failure.")
            read = kforge.command.CaptchaRead(hash)
            try:
                read.execute()
            except KforgeCommandError, inst: 
                raise djangovalidators.ValidationError("Captcha failure.")
            captcha = read.object
            if not captcha.checkWord(word):
                raise djangovalidators.ValidationError("Captcha failure.")


class PersonCreateManipulator(PersonManipulator):

    def buildFields(self):
        self.fields.append(
            djangoforms.TextField(
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
            djangoforms.PasswordField(
                field_name="password", 
                is_required=True, 
                validator_list=[
                    self.isFourCharsMin,
                ]
            )
        )
        self.fields.append(
            djangoforms.PasswordField(
                field_name="passwordconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingPassword
                ]
            )
        )
        self.fields.append(
            djangoforms.TextField(
                field_name="fullname", 
                is_required=True
            )
        )
        self.fields.append(
            djangoforms.EmailField(
                field_name="email", 
                is_required=True
            )
        )
        self.fields.append(
            djangoforms.EmailField(
                field_name="emailconfirmation", 
                is_required=True, 
                validator_list=[
                    self.isMatchingEmail
                ]
            ) 
        )
        if self.dictionary['captcha.enable']:
            self.fields.append(
                djangoforms.TextField(
                    field_name="captcha", 
                    is_required=isCaptchaEnabled, 
                    validator_list=[
                        self.isCaptchaCorrect
                    ]
                ) 
            )
            self.fields.append(
                djangoforms.HiddenField(
                    field_name="captchahash", 
                    is_required=False,
                )   
            )

class PersonUpdateManipulator(PersonManipulator):

    def buildFields(self):
        self.fields.append(
            djangoforms.PasswordField(
                field_name="password", 
                is_required=False, 
                validator_list=[
                    self.isFourCharsMin,
                ]
            )
        )
        self.fields.append(
            djangoforms.PasswordField(
                field_name="passwordconfirmation", 
                is_required=False, 
                validator_list=[
                    self.isMatchingPassword
                ]
            )
        )
        self.fields.append(
            djangoforms.TextField(
                field_name="fullname", 
                is_required=True
            )
        )
        self.fields.append(
            djangoforms.EmailField(
                field_name="email", 
                is_required=True
            )
        )


class ProjectManipulator(DomainObjectManipulator):

    def isProjectName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.re.projectName)
        if not pattern.match(field_data):
            msg = "This field can only contain lowercase letters or numbers."
            raise djangovalidators.ValidationError(msg)

    def isReservedProjectName(self, field_data, all_data):
        pattern = re.compile('^%s$' % kforge.re.reservedProjectName)
        if pattern.match(field_data):
            msg = "This field is reserved and can not be registered."
            raise djangovalidators.ValidationError(msg)

    def isAvailableProjectName(self, field_data, all_data):
        command = kforge.command.AllProjectRead(field_data)
        try:
            command.execute()
        except KforgeCommandError:
            pass
        else:
            message = "Project name is already being used by another project."
            raise djangovalidators.ValidationError(message)


class ProjectCreateManipulator(ProjectManipulator):

    def buildFields(self):
        self.fields = (
            djangoforms.TextField(
                field_name="title", 
                is_required=True
            ),
            djangoforms.SelectMultipleField(
                field_name="licenses", 
                is_required=True,
                choices=self.listRegisteredLicenses(),
                size=4,
            ),
            djangoforms.LargeTextField(
                field_name="description", 
                is_required=True,
                validator_list=[
                ]
            ),
            djangoforms.TextField(
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
            djangoforms.TextField(
                field_name="title", 
                is_required=True
            ),
            djangoforms.SelectMultipleField(
                field_name="licenses", 
                is_required=True,
                choices=self.listRegisteredLicenses(),
                size=4,
            ),
            djangoforms.LargeTextField(
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
            djangoforms.SelectField(
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
            raise djangovalidators.ValidationError(msg)

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
            raise djangovalidators.ValidationError(message)


class ServiceCreateManipulator(ServiceManipulator):

    def buildFields(self):
        self.fields = (
            djangoforms.SelectField(
                field_name="plugin", 
                is_required=True,
                choices=self.listPlugins(),
            ),
            djangoforms.TextField(
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
            djangoforms.TextField(
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

