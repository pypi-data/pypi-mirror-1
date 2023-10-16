import os, sys
from pkg_resources import resource_filename

from zicbee.core.zutils import DEBUG

import web
import web.wsgiserver
from zicbee.player.webplayer import webplayer, web_db_index

def do_serve(pure=False):
    """ Create a ZicDB instance
    parameters:
        pure (default: False): just start DB serving, no player
    """
    # chdir to serve files at the right place

    p = os.path.dirname(resource_filename('zicbee.ui.web', 'static'))
    os.chdir( p )

    # let's do webplayer

    sys.argv = ['zicdb', '0.0.0.0:9090']
    try:
        print "Running webplayer from", __file__
        if pure:
            urls = ('/db/(.*)', 'web_db_index',
                    '/(.*)', 'web_db_index')
        else:
            urls = ('/db/(.*)', 'web_db_index',
                    '/(.*)', 'webplayer')
        app = web.application(urls, locals())
        app.run()
    except:
        DEBUG()
        print os.kill(os.getpid(), 9)
        #print 'kill', os.getpid()

