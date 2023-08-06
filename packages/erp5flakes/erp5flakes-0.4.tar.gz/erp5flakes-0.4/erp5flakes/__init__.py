
import compiler
import sys
import os
from pyflakes.checker import Checker
from pyflakes import messages
import __builtin__

# we need Zope and ERP5Type to check code inside business templates
zope_software_home = os.environ.get('SOFTWARE_HOME',
                                    '/usr/lib/erp5/lib/python/')
sys.path.append(zope_software_home)
import ZODB
from ZODB.DemoStorage import DemoStorage
from OFS import XMLExportImport
customImporters = {  XMLExportImport.magic: XMLExportImport.importXML }
import Globals

# load ERP5Type ppml monkey patches
ppml_file = os.environ.get('ERP5Type.patches.ppml.__file__',
               os.path.join(zope_software_home,
                            'Products', 'ERP5Type', 'patches', 'ppml.py'))
execfile(ppml_file)

try:
    import transaction
    begin_transaction = transaction.begin
except ImportError:
    def begin_transaction():
        get_transaction().begin()

# by default, we ignore warnings about unused imports
fatal_messages = ( messages.ImportStarUsed, messages.UndefinedName,
           messages.DuplicateArgument, messages.RedefinedFunction )

def check(codeString, filename, bound_names=()):
    try:
        bound_names = [n for n in bound_names if not hasattr(__builtin__, n)]
        for name in bound_names:
            setattr(__builtin__, name, 1)
        try:
            tree = compiler.parse(codeString)
        except (SyntaxError, IndentationError):
            value = sys.exc_info()[1]
            try:
                (lineno, offset, line) = value[1][1:]
            except IndexError:
                print >> sys.stderr, 'could not compile %r' % (filename,)
                return 1
            if line.endswith("\n"):
                line = line[:-1]
            print >> sys.stderr, '%s:%d: could not compile' % (filename, lineno)
            print >> sys.stderr, line
            print >> sys.stderr, " " * (offset-2), "^"
            return 1
        else:
            warnings = 0
            w = Checker(tree, filename)
            w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
            for warning in w.messages:
                if isinstance(warning, fatal_messages):
                    warnings += 1
                    print warning
            return warnings
    finally:
        for name in bound_names:
            if hasattr(__builtin__, name):
                delattr(__builtin__, name)


def checkZopeProduct(path):
    warnings = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('.py'):
                filename = os.path.join(dirpath, filename)
                warnings += check(file(filename, 'U').read(), filename)
    return warnings


def getValidNames(py_script, blacklist_names=()):
    """Returns the list of known names for this python script.
    
    This includes scripts parameters, script bound names and restricted python
    utilities and auto-imported modules.

    A list of black listed names can be passed. The use case is to turn the use
    of 'context' in Workflow scripts an error.
    """
    name_list = []
    for n in py_script._bind_names._asgns.values():
        if n not in blacklist_names:
            name_list.append(n)
    for param in py_script.params().split(','):
        param = param.strip()
        if '=' in param:
            name_list.append(param.split('=')[0].strip())
        elif '*' in param:
            name_list.append(param.replace('*', ''))
        else:
            name_list.append(param)

    restricted_python_names = ['same_type', 'printed', 'string', 'test',
                                 'math', 'random', 'DateTime' ]
    return name_list + list(restricted_python_names)


def checkBusinessTemplate(path):
    """Checks python scripts in a business templates, from skin folder or
    workflow scripts.
    """
    global _connection
    _connection = None

    def _getConnection():
        """get a ZODB connection, open it if needed.
        """
        global _connection
        if _connection is not None:
            return _connection
        db = ZODB.DB(DemoStorage(quota=(1<<20)))
        _connection = db.open()
        begin_transaction()
        return _connection

    warnings = 0
    for dirpath, dirnames, filenames in \
            list(os.walk(os.path.join(path, 'SkinTemplateItem'))) + \
            list(os.walk(os.path.join(path, 'WorkflowTemplateItem'))):
        for filename in filenames:
            if not filename.endswith('.xml'):
                continue
            filename = os.path.join(dirpath, filename)
            file_obj = file(filename)
            try:
                if 'Products.PythonScripts.PythonScript' in file_obj.read():
                    file_obj.seek(0)
                    obj = _getConnection().importFile(file_obj,
                                        customImporters=customImporters)
                    blacklist_names = []
                    if 'WorkflowTemplateItem' in dirpath:
                        blacklist_names = ['context']
                    warnings += check(obj._body, filename,
                        getValidNames(obj, blacklist_names=blacklist_names))
            finally:
                file_obj.close()

    warnings += checkZopeProduct(os.path.join(path, 'TestTemplateItem'))
    warnings += checkZopeProduct(os.path.join(path, 'ExtensionTemplateItem'))
    warnings += checkZopeProduct(os.path.join(path, 'DocumentTemplateItem'))
    warnings += checkZopeProduct(os.path.join(path, 'PropertySheetTemplateItem'))
    warnings += checkZopeProduct(os.path.join(path, 'ConstraintTemplateItem'))

    return warnings


def isProduct(path):
    return os.path.exists(os.path.join(path, '__init__.py'))

def isBusinessTemplate(path):
    return os.path.exists(os.path.join(path, 'bt', 'revision'))

def main():
    warnings = 0
    for arg in sys.argv[1:]:
        if isProduct(arg):
            warnings += checkZopeProduct(arg)
        elif isBusinessTemplate(arg):
            warnings += checkBusinessTemplate(arg)
        else:
            print >> sys.stderr, 'ignoring path', arg

    raise SystemExit(warnings > 0)

# vim: sw=4
