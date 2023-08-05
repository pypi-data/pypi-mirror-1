import sys
import os
import time
import re

__author__ = 'Alexandre Girao <alexgirao@gmail.com>'
__contributors__ = []
__copyright__ = '(C) 2006 Alexandre Girao'
__license__ = 'MIT License'
__url__ = 'http://www.python.org/pypi/httpdrun'
__version__ = '0.2.2'

import yaptu

import httpdconf

if sys.platform == 'win32':
    import win

def validate_httpdconf():
    def missing_var(varname):
        return 'configuration error, missing "%s" variable' % varname

    try:
        httpdconf.environment == None
    except AttributeError, a:
        raise Exception, missing_var('environment')

    try:
        httpdconf.filename == None
    except AttributeError, a:
        raise Exception, missing_var('filename')

validate_httpdconf()

def normalize_path(path):
    if sys.platform == 'win32':
        path = path.replace('\\','/')
        if path.startswith('/'):
            if path[2] == '/':      # msys path style: /c/ = c:, /d/ = d:, ...
                path = "%s:%s" % (path[1:2], path[2:])
        return path
    else:
        return path

def find_httpd_modules(modules):
    '''find_httpd_modules(modules)

Returns a list of available modules
'''
    valid_modules = []
    for dir in modules['search_dirs']:
        for (mod_name, mod_file) in modules['modules']:
            for ext in modules['modules_extensions']:
                path = normalize_path('%s/%s%s' % (dir, mod_file, ext))
                if os.path.isfile(path):
                    valid_modules.append((path, mod_name, mod_file, ext))
                    break
    return valid_modules

def find_httpd_program():
    for dir in httpdconf.httpd_search_dirs:
        for i in ['%s/%s' % (dir, j) for j in httpdconf.program_names]:
            path = normalize_path(os.path.join(dir,i))
            if os.path.isfile(path):
                return path
    raise Exception, "could not find apache program"

def find_mime_types():
    for i in ['%s/mime.types' % j for j in httpdconf.conf_search_dirs]:
        path = normalize_path(i)
        if os.path.isfile(path):
            return path
    raise Exception, "could not find mime.types"

def get_server_root():
    return normalize_path(os.path.dirname(httpdconf.__file__))

def get_default_document_root():
    return get_server_root() + '/www'

def get_log_dir():
    return get_server_root() + '/logs'

def get_config_file_path():
    return get_server_root() + '/' + httpdconf.filename

def check_required_directories():
    document_root = get_document_root()
    log_dir = get_log_dir()

    if os.path.exists(log_dir):
        if not os.path.isdir(log_dir):
            raise Exception("file \"%s\" is not a directory" % log_dir)
    else:
        print 'directory "%s" does not exist, creating...' % log_dir
        os.mkdir(log_dir)

    if os.path.exists(document_root):
        if not os.path.isdir(document_root):
            raise Exception("file \"%s\" is not a directory" % document_root)
    else:
        print 'directory "%s" does not exist, creating...' % document_root
        os.mkdir(document_root)

def get_document_root_from_httpd_conf():
    r1 = re.compile(r'^[\s]*DocumentRoot[\s]*"(.*)"[\s]*$')
    r2 = re.compile(r'^[\s]*DocumentRoot[\s]*([\d\w:/]*)[\s]*$')

    for line in open(get_config_file_path(),'r'):
        m = r1.match(line) or r2.match(line)
        if m:
            return m.group(1)

def get_document_root():
    if httpdconf.__dict__.has_key('document_root'):
        return httpdconf.document_root
    else:
        return get_default_document_root()

def generate_httpd_conf(confif_file_path=None):
    import re

    modules = []
    for i in httpdconf.module_list:
        for path, name, file, ext in find_httpd_modules(i):
            modules.append('''<IfModule !%s.c>
LoadModule %s "%s"
</IfModule>''' % (file, name, path)
                )

    modules = '\n'.join(modules)

    mime_types = find_mime_types()

    server_root = get_server_root()
    document_root = get_default_document_root()
    log_dir = get_log_dir()

    check_required_directories()

    match=re.compile('\${([^@]+)}')
    lines = httpdconf.template.split('\n')
    lines.insert(0,'# generated automatically in %s by httpdrun, do not edit.' % time.strftime('%Y-%m-%d %H:%M'))
    lines = [line+'\n' for line in lines]

    vars = locals().copy()
    vars.update(httpdconf.__dict__)

    if confif_file_path == None:
        cop = yaptu.copier(match, vars)
        cop.copy(lines)
    else:
        f = open(confif_file_path, "w")
        try:
            cop = yaptu.copier(match, vars, ouf=f)
            cop.copy(lines)
        finally:
            f.flush()       # just to ensure
            f.close()

def synchronize_httpd_conf():
    confif_file_path = get_config_file_path()
    if os.path.exists(confif_file_path):
        t1 = os.stat(confif_file_path)
        t2 = os.stat(httpdconf.__file__)
        if t1.st_mtime < t2.st_mtime:
            print 'updating %s' % confif_file_path
            generate_httpd_conf(confif_file_path)
        elif not httpdconf.__dict__.has_key('document_root'):
            # use default DocumentRoot
            doc_root = get_document_root_from_httpd_conf()
            if get_default_document_root() != doc_root:
                print 'invalid DocumentRoot, re-generating "%s"' % doc_root
                generate_httpd_conf(confif_file_path)
    else:
        print 'generating %s' % confif_file_path
        generate_httpd_conf(confif_file_path)

def start():
    synchronize_httpd_conf()
    check_required_directories()
    if sys.platform == 'win32':
        win.start()
    else:
        import subprocess
        httpd = find_httpd_program()
        exitcode = subprocess.call((httpd, '-d', get_server_root(), \
            '-f', httpdconf.filename, '-k', 'start'))
        print '%s exit code: %i' % (httpd, exitcode)

def stop():
    if sys.platform == 'win32':
        win.stop()
    else:
        import subprocess
        httpd = find_httpd_program()
        exitcode = subprocess.call((httpd, '-d', get_server_root(), \
            '-f', httpdconf.filename, '-k', 'stop'))
        print '%s exit code: %i' % (httpd, exitcode)

def restart():
    synchronize_httpd_conf()
    if sys.platform == 'win32':
        synchronize_httpd_conf()
        check_required_directories()
        win.restart()
    else:
        import subprocess
        httpd = find_httpd_program()
        exitcode = subprocess.call((httpd, '-d', get_server_root(), \
            '-f', httpdconf.filename, '-k', 'restart'))
        print '%s exit code: %i' % (httpd, exitcode)

if __name__=='__main__':
    generate_httpd_conf()
    #~ pass
