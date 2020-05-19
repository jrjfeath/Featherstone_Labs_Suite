import sys
import os
CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(CWD,'Scripts'))
sys.path.append(os.path.join(CWD,'Icons'))
sys.path.append(os.path.join(CWD,'Launch'))

Pass = 0
try:
    import PyQt4
    Pass = 1
except ImportError:
    pass

try:
    import PyQt5
    Pass = 2
except ImportError:
    pass

if Pass == 0:
    print('Cannot load pyqt library')
    sys.exit()
if Pass == 1:
    from Launch_PyQt4 import main
    main()
if Pass == 2:
    from Launch_PyQt5 import main
    main()