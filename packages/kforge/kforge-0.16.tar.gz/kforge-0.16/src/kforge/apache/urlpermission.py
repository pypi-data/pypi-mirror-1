from kforge.ioc import *
import kforge.command
import kforge.exceptions
import kforge.accesscontrol

logger     = RequiredFeature('Logger')
dictionary = RequiredFeature('SystemDictionary')

def normalizeUrlPath(reqUri):
    if reqUri[-1] == '/':
        reqUri = reqUri[:-1]
    return reqUri

def isAllowedAccess(personName, reqUri, httpMethod):
    urlPath = normalizeUrlPath(reqUri)
    if len(urlPath.split('/')) > 2:
        read = kforge.command.PersonRead(personName)
        read.execute()
        person = read.person
        service = getService(urlPath)
        if not service:
            return False
        project = service.project
        plugin = service.plugin
        actionName = getActionName(httpMethod)
        controller = kforge.accesscontrol.ProjectAccessController()
        return controller.isAuthorised(
            person=person,
            actionName=actionName,
            protectedObject=plugin,
            project=project,
        )
    # everything with fewer than two segments is ok (e.g. /project)
    return True

def getVisitorName(personName, password):
    """
    Get name to use for authentication given a personName and password.
    
    @return: personName if we can authenticate, visitor name otherwise
    """
    cmd = kforge.command.PersonAuthenticate(personName, password)
    try:
        cmd.execute()
    except kforge.exceptions.KforgeCommandError:
        personName = dictionary['visitor']
    return personName

def getService(urlPath):
    """
    Get service domain object which we are trying to access
    """
    url_scheme = kforge.url.UrlScheme()
    #todo: use kforge.url?
    projectName, serviceName = url_scheme.decodeServicePath(urlPath)
    read = kforge.command.ProjectRead(projectName)
    read.execute()
    project = read.project
    if serviceName in project.services:
        return project.services[serviceName]
    else:
        return None

def getActionName(httpMethod):
    registry = RequiredFeature('DomainRegistry')
    readList = ['GET', 'PROPFIND', 'OPTIONS', 'REPORT']
    if httpMethod in readList:
        return 'Read'
    else:
        return 'Update'

