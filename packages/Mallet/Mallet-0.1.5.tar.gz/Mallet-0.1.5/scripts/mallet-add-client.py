#!/usr/bin/python

import os
import sys
import stat
import shutil
import logging
import subprocess

from mallet.utils import call, write

logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG)


def main():
    name = sys.argv[1]

    logging.info('Creating user account')
    call(['useradd', '-G', 'clients', '-m', name])
    # TODO add configuration option for database type
    logging.info('Creating database user')
    call(['sudo', '-u', 'postgres', 'createuser', '--no-superuser',
          '--createdb', '--no-createrole', name])

    # TODO add configuration option for apache
    logging.info('Adding Apache configuration')
    call(['sudo', '-u', name, 'mkdir', '/home/%s/apache.conf.d/' % name])
    apache_conf = """
# Include user-controlled apache configs
Include /home/%(name)s/apache.conf.d/*
""" % {'name': name}
    write('/etc/apache2/sites-available/%s' % name, apache_conf)
    call(['a2ensite', name])
    call(['/etc/init.d/apache2', 'reload'])

    logging.info('Setting password for user')
    print 'Please choose a UNIX password for the "%s" user' % name
    call(['passwd', name])


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise
    except SystemExit, e: # sys.exit()
        raise
    except Exception, e:
        raise
