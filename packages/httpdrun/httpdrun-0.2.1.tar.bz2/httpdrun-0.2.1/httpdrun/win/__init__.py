import sys
import os
import time
import string
import subprocess

import pywintypes
import win32api
import win32con
import win32service

import services

import httpdrun
import httpdconf

def get_service_name():
    env = httpdconf.environment.lower()
    if env == 'development':
        return 'apache2-dev-' + os.getenv("USERNAME").lower().replace(' ', '_')
    else:
        return 'apache2-env-' + env.replace(' ', '_')

def get_base_httpd_args():
    return ['-d', httpdrun.get_server_root().lower(), '-f', httpdconf.filename.lower()]

def install_service(timeout=0):
    """ install a winnt/2k/2k3/xp/vista service """

    httpdrun.synchronize_httpd_conf()
    service_name = get_service_name()

    apache2dev = None
    try:
        apache2dev = services.ServiceControl(service_name)
    except services.ServiceDoesNotExist:
        pass        # do nothing, expected

    if isinstance(apache2dev, services.ServiceControl):
        raise Exception, 'service "%s" is already registered' % service_name

    print 'installing service "%s"' % service_name
    sys.stdout.flush()

    args = get_base_httpd_args()
    args.insert(0,httpdrun.find_httpd_program())
    args.extend(('-n', service_name, '-k', 'install'))
    subprocess.call(args)

    try:
        apache2dev = services.ServiceControl(service_name)
    except services.ServiceDoesNotExist:
        print 'failed to install service, please check for errors in configuration file'
        raise

def config_service():
    """ (re)configure a winnt/2k/2k3/xp/vista service """

    service_name = get_service_name()
    apache2dev = services.ServiceControl(service_name)
    
    print '(re)configuring service "%s"' % service_name
    sys.stdout.flush()

    args = get_base_httpd_args()
    args.insert(0,httpdrun.find_httpd_program())
    args.extend(('-n', service_name, '-k', 'config'))
    if subprocess.call(args) != 0:
        raise Exception, 'failed to re-configure service "%s"' % service_name

def uninstall_service():
    """ uninstall a winnt/2k/2k3/xp/vista service """

    service_name = get_service_name()
    apache2dev = services.ServiceControl(service_name)
    
    print 'uninstalling service "%s"' % service_name
    sys.stdout.flush()

    args = get_base_httpd_args()
    args.insert(0,httpdrun.find_httpd_program())
    args.extend(('-n', service_name, '-k', 'uninstall'))
    subprocess.call(args)

def start(timeout=0):
    """start(timeout=0)
timeout in seconds, 0 for no wait"""

    service_name = get_service_name()

    try:
        apache2dev = services.ServiceControl(service_name)
    except services.ServiceDoesNotExist:
        print 'failed to open service, will install'
        install_service()

    try:
        apache2dev = services.ServiceControl(service_name)
    except services.ServiceDoesNotExist:
        print 'failed to install service, aborting start'
        raise

    try:
        regkey = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE,
            "SYSTEM\\CurrentControlSet\\Services\\%s\Parameters" % service_name,
            0, win32con.KEY_READ)
    except pywintypes.error:
        print 'failed to open service registration key'
        raise

    regval = [string.lower(i) for i in win32api.RegQueryValueEx(regkey, "ConfigArgs")[0]]

    if regval != get_base_httpd_args():
        print 'configuration changed for service "%s", trying to reconfigure service' % service_name
        sys.stdout.flush()
        config_service()

    apache2dev.start(timeout)

def stop(timeout=0):
    """ timeout in seconds, 0 for no wait"""
    apache2dev = services.ServiceControl(get_service_name())
    apache2dev.stop(timeout)

def restart(timeout=60):
    """ timeout in seconds, 0 for no wait, 1 minute defaults"""
    apache2 = services.ServiceControl(get_service_name())
    apache2.restart(timeout)

def set_automatic_startup():
    "set_automatic_startup()\n"
    apache2 = services.ServiceControl(get_service_name())
    apache2.set_startup_option(win32service.SERVICE_AUTO_START)

def set_manual_startup():
    "set_manual_startup()\n"
    apache2 = services.ServiceControl(get_service_name())
    apache2.set_startup_option(win32service.SERVICE_DEMAND_START)

if __name__ == '__main__':
    install_service()
