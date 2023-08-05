import sys
import os

environment = 'development'
filename = 'httpd.conf'

if sys.platform == 'win32':
    search_dirs = (os.getenv('PROGRAMFILES') + '/Apache Group/Apache2',)
    program_names = ('Apache.exe', 'httpd.exe')
    module_extensions = ('.so', '.dll')
else:
    search_dirs = ('/usr/local/apache2',)
    program_names = ('httpd',)
    module_extensions = ('.so')

# modules to try
module_list = (
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
    ('python_module', 'mod_python')
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
    httpdrun.generate_httpd_conf()
