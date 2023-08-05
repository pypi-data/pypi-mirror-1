# drop_privileges - Drop root privileges on a POSIX system.
#
# Author: Hartmut Goebel <h.goebel@goebel-consult.de>
# Based on some code by Gavin Baker: <http://antonym.org/node/100>
# and some ideas taken from <www.cherrypy.org>.
# Licence: MIT
# 
# Copyright (c) 2005 by Gavin Baker
# Copyright (c) 2007 by Hartmut Goebel
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software. #
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import logging
import os, pwd, grp

def drop_privileges(uid_name='nobody', gid_name='nogroup',
                    umask=077, logger=None):
    """Drop privileges. POSIX only."""

    def names():
        return (pwd.getpwuid(os.getuid())[0], 
                grp.getgrgid(os.getgid())[0])
    
    if logger is None:
        logger = logging.getLogger() # use root logger

    logger.debug('started as %s/%s', *names())

    starting_uid = os.getuid()
    if starting_uid != 0:
        # We're not root so, like, whatever dude
        starting_uid_name = pwd.getpwuid(starting_uid)[0]
        logger.info("already running as %r", starting_uid_name)
    else:
        # started as root, drop privs and become the specified user/group

        # Get the uid/gid from the name
        running_uid = pwd.getpwnam(uid_name)[2]
        running_gid = grp.getgrnam(gid_name)[2]

        # Try setting the new uid/gid
        try:
            # set gid first!
            os.setgid(running_gid)
        except OSError, e:
            logger.error('Could not set effective group id: %s', e)

        try:
            os.setuid(running_uid)
        except OSError, e:
            logger.error('Could not set effective user id: %s', e)

        logger.info('running as %s/%s', *names())

        # Ensure a very convervative umask
        old_umask = os.umask(umask)
        logger.info('umask old: %03o, new: %03o', old_umask, umask)

# Test it
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    drop_privileges(logger=logging.getLogger('server'))
    
