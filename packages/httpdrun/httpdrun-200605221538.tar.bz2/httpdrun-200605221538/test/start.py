
import sys
from os.path import join, dirname, abspath

sys.path.insert(1, abspath(join(dirname(abspath(__file__)), '..', 'build', 'lib')))

import httpdrun
httpdrun.start()
