
""" A low-level windows service management library
"""

import sys
import os

import time
import win32api
import win32con
import win32service

# from http://msdn.microsoft.com/library/default.asp?url=/library/en-us/dllproc/base/enum_service_status_str.asp
#
# typedef struct _ENUM_SERVICE_STATUS {
#   LPTSTR lpServiceName;
#   LPTSTR lpDisplayName;
#   SERVICE_STATUS ServiceStatus;
# } ENUM_SERVICE_STATUS, 
#  *LPENUM_SERVICE_STATUS;
#
# lpServiceName
#     The name of a service in the service control manager database.
#     The maximum string length is 256 characters. The service control
#     manager database preserves the case of the characters, but service
#     name comparisons are always case insensitive. A slash (/),
#     backslash (\), comma, and space are invalid service name characters.
# 
# lpDisplayName
#     A display name that can be used by service control programs, such
#     as Services in Control Panel, to identify the service. This string
#     has a maximum length of 256 characters. The name is case-preserved
#     in the service control manager. Display name comparisons are always
#     case-insensitive.
# 
# ServiceStatus
#     A SERVICE_STATUS structure that contains status information for
#     the lpServiceName service. 
#

# from http://msdn.microsoft.com/library/default.asp?url=/library/en-us/dllproc/base/service_status_str.asp
#
# typedef struct _SERVICE_STATUS {
#   DWORD dwServiceType;
#   DWORD dwCurrentState;
#   DWORD dwControlsAccepted;
#   DWORD dwWin32ExitCode;
#   DWORD dwServiceSpecificExitCode;
#   DWORD dwCheckPoint;
#   DWORD dwWaitHint;
# } SERVICE_STATUS, 
#  *LPSERVICE_STATUS;
#
# dwServiceType
#     SERVICE_FILE_SYSTEM_DRIVER
#       0x00000002          The service is a file system driver.
#     SERVICE_KERNEL_DRIVER
#       0x00000001          The service is a device driver.
#     SERVICE_WIN32_OWN_PROCESS
#       0x00000010          The service runs in its own process.
#     SERVICE_WIN32_SHARE_PROCESS
#       0x00000020          The service shares a process with other services.
# 
#     If the service type is either SERVICE_WIN32_OWN_PROCESS or
#     SERVICE_WIN32_SHARE_PROCESS, and the service is running in 
#     the context of the LocalSystem account, the following type
#     may also be specified.
# 
#     SERVICE_INTERACTIVE_PROCESS
#       0x00000100 	        The service can interact with the desktop.
#
# dwCurrentState
#     SERVICE_CONTINUE_PENDING
#       0x00000005 	        The service continue is pending.
#     SERVICE_PAUSE_PENDING
#       0x00000006 	        The service pause is pending.
#     SERVICE_PAUSED
#       0x00000007 	        The service is paused.
#     SERVICE_RUNNING
#       0x00000004 	        The service is running.
#     SERVICE_START_PENDING
#       0x00000002 	        The service is starting.
#     SERVICE_STOP_PENDING
#       0x00000003 	        The service is stopping.
#     SERVICE_STOPPED
#       0x00000001 	        The service is not running.
#
# dwControlsAccepted
#     Control codes the service accepts and processes in its handler function.
#     A user interface process can control a service by specifying a control
#     command in the ControlService or ControlServiceEx function. By default,
#     all services accept the SERVICE_CONTROL_INTERROGATE value.
# 
#     SERVICE_ACCEPT_NETBINDCHANGE
#       0x00000010 	        The service is a network component that can accept
#                           changes in its binding without being stopped and restarted.
# 
#                           This control code allows the service to receive 
#                           SERVICE_CONTROL_NETBINDADD, SERVICE_CONTROL_NETBINDREMOVE,
#                           SERVICE_CONTROL_NETBINDENABLE, and 
#                           SERVICE_CONTROL_NETBINDDISABLE notifications.
# 
#                           Windows NT:  This value is not supported.
#
#     SERVICE_ACCEPT_PARAMCHANGE
#       0x00000008 	        The service can reread its startup parameters without
#                           being stopped and restarted.
# 
#                           This control code allows the service to receive 
#                           SERVICE_CONTROL_PARAMCHANGE notifications.
# 
#                           Windows NT:  This value is not supported.
# 
#     SERVICE_ACCEPT_PAUSE_CONTINUE
#       0x00000002 	        The service can be paused and continued.
# 
#                           This control code allows the service to receive 
#                           SERVICE_CONTROL_PAUSE and SERVICE_CONTROL_CONTINUE notifications.
#
#     SERVICE_ACCEPT_PRESHUTDOWN
#       0x00000100 	        The service can perform preshutdown tasks.
# 
#                           This control code enables the service to receive 
#                           SERVICE_CONTROL_PRESHUTDOWN notifications. Note that
#                           ControlService and ControlServiceEx cannot send this 
#                           notification; only the system can send it.
# 
#                           Windows Server 2003 and Windows XP/2000:  This value is not supported.
# 
#     SERVICE_ACCEPT_SHUTDOWN
#       0x00000004 	        The service is notified when system shutdown occurs.
# 
#                           This control code allows the service to receive 
#                           SERVICE_CONTROL_SHUTDOWN notifications. Note that ControlService
#                           and ControlServiceEx cannot send this notification; only the
#                           system can send it.
#
#     SERVICE_ACCEPT_STOP
#       0x00000001 	        The service can be stopped.
# 
#                           This control code allows the service to receive 
#                           SERVICE_CONTROL_STOP notifications.
# 
#     This value can also contain the following extended control codes, which are supported 
#     only by HandlerEx. (Note that these control codes cannot be sent by ControlService
#     or ControlServiceEx.)
# 
#     SERVICE_ACCEPT_HARDWAREPROFILECHANGE
#       0x00000020 	        The service is notified when the computer's hardware profile has
#                           changed. This enables the system to send 
#                           SERVICE_CONTROL_HARDWAREPROFILECHANGE notifications to the service.
# 
#                           Windows NT:  This value is not supported.
# 
#     SERVICE_ACCEPT_POWEREVENT
#       0x00000040 	        The service is notified when the computer's power status has
#                           changed. This enables the system to send SERVICE_CONTROL_POWEREVENT
#                           notifications to the service.
# 
#                           Windows NT:  This value is not supported.
# 
#     SERVICE_ACCEPT_SESSIONCHANGE
#       0x00000080          The service is notified when the computer's session status
#                           has changed. This enables the system to send 
#                           SERVICE_CONTROL_SESSIONCHANGE notifications to the service.
#
#                           Windows 2000/NT:  This value is not supported.
#
# dwWin32ExitCode
#     Error code the service uses to report an error that occurs when
#     it is starting or stopping. To return an error code specific to
#     the service, the service must set this value to ERROR_SERVICE_SPECIFIC_ERROR 
#     to indicate that the dwServiceSpecificExitCode member contains
#     the error code. The service should set this value to NO_ERROR when
#     it is running and on normal termination.
# dwServiceSpecificExitCode
#     Service-specific error code that the service returns when an error
#     occurs while the service is starting or stopping. This value is ignored
#     unless the dwWin32ExitCode member is set to ERROR_SERVICE_SPECIFIC_ERROR.
# dwCheckPoint
#     Check-point value the service increments periodically to report its
#     progress during a lengthy start, stop, pause, or continue operation.
#     For example, the service should increment this value as it completes
#     each step of its initialization when it is starting up. The user interface
#     program that invoked the operation on the service uses this value to track
#     the progress of the service during a lengthy operation. This value is not
#     valid and should be zero when the service does not have a start, stop,
#     pause, or continue operation pending.
# dwWaitHint
#     Estimated time required for a pending start, stop, pause, or continue operation,
#     in milliseconds. Before the specified amount of time has elapsed, the service
#     should make its next call to the SetServiceStatus function with either an
#     incremented dwCheckPoint value or a change in dwCurrentState. If the amount
#     of time specified by dwWaitHint passes, and dwCheckPoint has not been
#     incrementedor dwCurrentState has not changed, the service control manager or
#     service control program can assume that an error has occurred.
#

#   DWORD dwServiceType;
#   DWORD dwCurrentState;
#   DWORD dwControlsAccepted;
#   DWORD dwWin32ExitCode;
#   DWORD dwServiceSpecificExitCode;
#   DWORD dwCheckPoint;
#   DWORD dwWaitHint;

def get_service_type_name(service_type):
    return {
        '1': 'SERVICE_KERNEL_DRIVER',
        '2': 'SERVICE_FILE_SYSTEM_DRIVER',
        '16': 'SERVICE_WIN32_OWN_PROCESS',
        '32': 'SERVICE_WIN32_SHARE_PROCESS',
    }[str(service_type & 0xff)]

class ServiceStatus(object):
    def __init__(self, service_status):
        self.update(service_status)
    def update(self, service_status):
        self.service_type = service_status[0]
        self.current_state = service_status[1]
        self.control_is_accepted = service_status[2]
        self.win32_exit_code = service_status[3]
        self.service_specific_exit_code = service_status[4]
        self.check_point = service_status[5]
        self.wait_hint = service_status[6]
    def __repr__(self):
        return 'service type: %s (0x%x), current state: %i, control is accepted: %i, win32 exit code: %i, service specific exit code: %i, check point: %i, wait hint: %i' % (
            get_service_type_name(self.service_type), self.service_type, self.current_state,
            self.control_is_accepted, self.win32_exit_code,
            self.service_specific_exit_code, self.check_point, self.wait_hint)

class ServiceInfo(object):
    def __init__(self, enum_service_status):
        self.name = enum_service_status[0]
        self.display = enum_service_status[1]
        self.status = ServiceStatus(enum_service_status[2])

    def __repr__(self):
        return '%s "%s": %s' % (self.name, self.display, self.status)

class ServiceDoesNotExist(Exception):
    pass

class ServiceControl(ServiceInfo):
    def __init__(self, name, machinename=None, dbname=None):
        self.manager = win32service.OpenSCManager(machinename, dbname, win32service.SC_MANAGER_ALL_ACCESS)
        services = win32service.EnumServicesStatus(self.manager)
        name_lower = name.lower()
        match = [i for i in services if i[0].lower() == name_lower or i[1].lower() == name_lower]
        if len(match) == 0:
            raise ServiceDoesNotExist, 'service "%s" does not exist' % name
        ServiceInfo.__init__(self,match[0])
        self.handle = win32service.OpenService(self.manager, self.name, win32service.SERVICE_ALL_ACCESS)

    def update_status(self):
        self.status.update(win32service.QueryServiceStatus(self.handle))

    def is_running(self):
        self.update_status()
        return self.status.current_state == win32service.SERVICE_RUNNING

    def wait_for(self, state, timeout):
        self.update_status()
        while self.status.current_state != state:
            time.sleep(1)
            timeout -= 1
            if timeout == 0:
                raise Exception, 'timeout'
            self.update_status()

    def start(self,timeout=0):
        win32service.StartService(self.handle, None)
        if timeout > 0:
            self.wait_for(win32service.SERVICE_RUNNING, timeout)

    # >>> [i for i in dir(win32service) if i.startswith('SERVICE_CONTROL')]
    # ['SERVICE_CONTROL_CONTINUE', 'SERVICE_CONTROL_INTERROGATE',
    #  'SERVICE_CONTROL_PAUSE', 'SERVICE_CONTROL_SHUTDOWN', 'SERVICE_CONTROL_STOP']

    def stop(self,timeout=0):
        win32service.ControlService(self.handle, win32service.SERVICE_CONTROL_STOP)
        if timeout > 0:
            self.wait_for(win32service.SERVICE_STOPPED, timeout)

    def restart(self,timeout=60):       # timeout in seconds
        self.stop(timeout)
        self.start(timeout)

    def pause(self, timeout=0):
        self.status.update(win32service.ControlService(self.handle, win32service.SERVICE_CONTROL_PAUSE))
        if timeout > 0:
            self.wait_for(win32service.SERVICE_PAUSED, timeout)

    def resume(self, timeout=0):
        self.status.update(win32service.ControlService(self.handle, win32service.SERVICE_CONTROL_CONTINUE))
        if timeout > 0:
            self.wait_for(win32service.SERVICE_RUNNING, timeout)

    def shutdown(self):
        self.status.update(win32service.ControlService(self.handle, win32service.SERVICE_CONTROL_SHUTDOWN))

    def get_startup_option(self):
        # Start     REG_DWORD     Start constant
        # Specifies the starting values for the service as follows:
        # 
        # START TYPE     LOADER     MEANING
        # 
        # 0x0            Kernel     Represents a part of the
        # (Boot)                    driver stack for the boot
        #                           (startup) volume and must
        #                           therefore be loaded by the
        #                           Boot Loader.
        # 
        # 0x1            I/O        Represents a driver to be loaded
        # (System)       subsystem  at Kernel initialization.
        # 
        # 0x2            Service    To be loaded or started
        # (Auto load)    Control    automatically for all startups,
        #                Manager    regardless of service type.
        # 
        # 0x3            Service    Available, regardless of type,
        # (Load on       Control    but will not be started until
        # demand)        Manager    the user starts it (for example,
        #                           by using the Devices icon in
        #                           Control Panel).
        # 
        # 0x4            Service    NOT TO BE STARTED UNDER ANY
        # (disabled)     Control    CONDITIONS.
        #                Manager        
        #
        """ Possible return values
            0 = win32service.SERVICE_BOOT_START
            1 = win32service.SERVICE_SYSTEM_START
            2 = win32service.SERVICE_AUTO_START
            3 = win32service.SERVICE_DEMAND_START
            4 = win32service.SERVICE_DISABLED
        """
        regkey = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\" + self.name, 0, win32con.KEY_READ)
        regval = win32api.RegQueryValueEx(regkey, "Start")[0]
        win32api.RegCloseKey(regkey)
        return regval

    def set_startup_option(self, option):
        """ Possible option values
            0 = win32service.SERVICE_BOOT_START
            1 = win32service.SERVICE_SYSTEM_START
            2 = win32service.SERVICE_AUTO_START
            3 = win32service.SERVICE_DEMAND_START
            4 = win32service.SERVICE_DISABLED
        """
        if not option in range(0,5):
            raise Exception, 'invalid argument'
        win32service.ChangeServiceConfig(self.handle,
            win32service.SERVICE_NO_CHANGE, option,
            win32service.SERVICE_NO_CHANGE, None,
            None, 0, None, None, None, self.name) 

def get_services_list(machinename=None, dbname=None):
    services = win32service.EnumServicesStatus(
        win32service.OpenSCManager(machinename, dbname,
        win32service.SC_MANAGER_ALL_ACCESS))
    return [ServiceInfo(i) for i in services]

def show_services(machinename=None, dbname=None):
    services = get_services_list(machinename, dbname)
    for s in services:
        print s

if __name__ == '__main__':
    #~ show_services()
    apache2 = ServiceControl('Apache2')
    #~ apache2.restart()
    apache2.set_startup_option(win32service.SERVICE_DEMAND_START)
    print apache2.get_startup_option()
