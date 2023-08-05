
import sys
from os.path import join, dirname, abspath

sys.path.insert(1, abspath(join(dirname(abspath(__file__)), '..', 'build', 'lib')))

import httpdrun
try:
    httpdrun.win.uninstall_service()
except:
    pass
