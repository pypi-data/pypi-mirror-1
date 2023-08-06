import time
import logging
import os
from os.path import join
import sys

curdir = LOGDIR = os.path.realpath(os.path.dirname(__file__))
logfile = join(LOGDIR, 'xap.log')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=logfile,
                    filemode='wa')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

import afpy.xap.settings

def main():
    if len(sys.argv) > 1:
        settings.SQLURI = sys.argv[1]
    from afpy.xap.xapindexer import start_server
    from afpy.xap.xapindexer import stop_server

    logging.debug('Running xapian server.')
    try:
        start_server()
    except Exception, e:
        logging.debug('failed to start %s' % str(e))
        raise e

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

    stop_server()
    logging.debug('Xapian server stopped.')

if __name__ == '__main__':
    main()

