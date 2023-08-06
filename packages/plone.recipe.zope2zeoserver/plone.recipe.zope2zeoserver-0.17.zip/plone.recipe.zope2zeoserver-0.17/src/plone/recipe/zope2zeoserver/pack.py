# zeopack wrapper

import sys
from ZEO.scripts import zeopack

def main(host, port, socket_path=''):
    for arg in sys.argv:
        if arg[:2] in [ "-h", "-U" ]:
            break
    else:
        if socket_path:
            sys.argv.extend(["-U", socket_path])
        else:
            sys.argv.extend(["-h", str(host), "-p", str(port)])
    zeopack.main()

if __name__ == "__main__":
    main()
