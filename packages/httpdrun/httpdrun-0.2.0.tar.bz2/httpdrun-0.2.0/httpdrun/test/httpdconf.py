import sys
import os

environment = 'development'
filename = 'httpd.conf'

if sys.platform == 'win32':
    _programs = os.getenv('PROGRAMFILES')
    httpd_search_dirs = (_programs + '/Apache Group/Apache2/bin',)
    modules_search_dirs = (_programs + '/Apache Group/Apache2/modules',)
    conf_search_dirs = (_programs + '/Apache Group/Apache2/conf',)
    program_names = ('Apache.exe', 'httpd.exe')
    modules_extensions = ('.so', '.dll')
    # for php4 to work, you will need:
    #   put "c:/php4" and "c:/php4/sapi" on the environment path
    #   restart computer, so new environment path will start working for services
    php4dir = "c:/php4"
    php_search_dirs = (php4dir, php4dir + '/sapi')
else:
    httpd_search_dirs = ('/usr/local/apache2/bin',)
    modules_search_dirs = ('/usr/local/apache2/modules',)
    conf_search_dirs = ('/usr/local/apache2/conf',)
    program_names = ('httpd',)
    modules_extensions = ('.so')
    php_search_dirs = None

module_list = (
    {
        'search_dirs': modules_search_dirs,
        'modules_extensions': modules_extensions,
        'modules':  (
            ('access_module', 'mod_access'),
            ('actions_module', 'mod_actions'),
            ('alias_module', 'mod_alias'),
            ('asis_module', 'mod_asis'),
            ('auth_module', 'mod_auth'),
            ('autoindex_module', 'mod_autoindex'),
            ('cgi_module', 'mod_cgi'),
            ('dir_module', 'mod_dir'),
            ('env_module', 'mod_env'),
            ('imap_module', 'mod_imap'),
            ('include_module', 'mod_include'),
            ('isapi_module', 'mod_isapi'),
            ('log_config_module', 'mod_log_config'),
            ('mime_module', 'mod_mime'),
            ('negotiation_module', 'mod_negotiation'),
            ('setenvif_module', 'mod_setenvif'),
            ('userdir_module', 'mod_userdir'),
            ('rewrite_module', 'mod_rewrite'),
            ('status_module', 'mod_status'),
            ('info_module', 'mod_info'),
            ('auth_anon_module', 'mod_auth_anon'),
            ('auth_dbm_module', 'mod_auth_dbm'),
            ('auth_digest_module', 'mod_auth_digest'),
            ('dav_module', 'mod_dav'),
            ('dav_fs_module', 'mod_dav_fs'),
            ('vhost_alias_module', 'mod_vhost_alias'),
            ('python_module', 'mod_python'),
            )
        },
    {
        'search_dirs': php_search_dirs,
        'modules_extensions': modules_extensions,
        'modules':  (
            ('php4_module', 'php4apache2'),
            )
        }
    )

worker = {
    'StartServers':  1,
    'MinSpareThreads': 5,
    'MaxSpareThreads': 5,
    'ThreadsPerChild': 5,
    'MaxRequestsPerChild': 0,
    'MaxClients': 5
    }

template = '''
Listen 8000

LogLevel debug

DocumentRoot "${document_root}"

DirectoryIndex index.php index.html

${modules}

TypesConfig "${mime_types}"

<IfModule worker.c>
    StartServers         ${worker['StartServers']}
    MinSpareThreads      ${worker['MinSpareThreads']}
    MaxSpareThreads      ${worker['MaxSpareThreads']}
    ThreadsPerChild      ${worker['ThreadsPerChild']}
    MaxRequestsPerChild  ${worker['MaxRequestsPerChild']}
    MaxClients           ${worker['MaxClients']}
</IfModule>

<IfModule prefork.c>
    StartServers            5
    MinSpareServers         5
    MaxSpareServers         5
    MaxClients              10
    MaxRequestsPerChild     0
</IfModule>

<IfModule mpm_winnt.c>
    ThreadsPerChild         10
    MaxRequestsPerChild     0
</IfModule>

<IfModule mod_status.c>
    ExtendedStatus On

    <Location /server-status>
        SetHandler server-status
        Order deny,allow
        Deny from all
        Allow from localhost
        Allow from 10.0.0.0/8
        Allow from 192.168.0.0/16
    </Location>
</IfModule>

<IfModule mod_info.c>
    <Location /server-info>
        SetHandler server-info
        Order deny,allow
        Deny from all
        Allow from localhost
        Allow from 10.0.0.0/8
        Allow from 192.168.0.0/16
    </Location>
</IfModule>

#<IfModule mod_php4.c>      # this is for apache1
<IfModule sapi_apache2.c>
    AddType application/x-httpd-php .php
    PHPINIDir "${php4dir}"
</IfModule>

<Directory "${document_root}">
    Options Indexes FollowSymLinks
    AllowOverride All
    Order deny,allow
    Deny from all
    Allow from localhost
    Allow from 10.0.0.0/8
    Allow from 192.168.0.0/16
</Directory>
'''

if __name__ == '__main__':
    import httpdrun
    def show_usage():
        print '%s (%s)' % (sys.argv[0], '|'.join(options.keys()))
    options = {
        'show_config': lambda: httpdrun.generate_httpd_conf(),
        'start': lambda: httpdrun.start(),
        'stop': lambda: httpdrun.stop(),
        'restart': lambda: httpdrun.restart()
        }
    if sys.platform == 'win32':
        options['uninstall'] = lambda: httpdrun.win.uninstall_service()
    if len(sys.argv) == 2:
        options.get(sys.argv[1], show_usage)()
    else:
        show_usage()
