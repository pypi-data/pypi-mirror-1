import sys

if __name__ == '__main__':
    if sys.platform == 'win32':
        import apctrl_win
        apctrl_win.uninstall_service()
