import os
import sys
import fnmatch
basePath = os.path.abspath(os.path.dirname(sys.argv[0]))

def getDataFiles(dest, basePath, pathOffset, glob = '*.*'):
    """
    Get all files matching glob from under pathOffset put give their pathes
    relative to basePath
    """
    result = []
    pathToWalk = os.path.join(basePath, pathOffset)
    for root, dirs, files in os.walk(pathToWalk):
        if not '.svn' in root:
            toffset = root[len(basePath)+1:]
            toffsetForDest = root[len(pathToWalk)+1:]
            tfileNames = fnmatch.filter(files, glob)
            fileList = [os.path.join(toffset, fname) for fname in tfileNames]
            tdest = os.path.join(dest, toffsetForDest)
            result.append( (tdest, fileList) )
    return result

def getPackages(basePath):
    result = []
    for root, dirs, files in os.walk(basePath):
        if not '.svn' in root and '__init__.py' in files:
            toffset = root[len(basePath)+1:]
            result.append( toffset )
    return result

def getScripts(basePath, offset):
    """
    Assumes all scripts are in base directory
    """
    scriptsList = []
    scriptsDir = os.path.join(basePath, offset)
    for fileName in os.listdir(scriptsDir):
        if not ('.svn' in fileName or '.bak' in fileName):
            scriptsList.append(os.path.join(offset, fileName))
    return scriptsList 

if __name__ == '__main__':
    # print getDataFiles('var/www/media', basePath, 'src/kforge/django/media')
    # print getPackages(basePath + '/src')
    print getScripts(basePath, 'bin')
