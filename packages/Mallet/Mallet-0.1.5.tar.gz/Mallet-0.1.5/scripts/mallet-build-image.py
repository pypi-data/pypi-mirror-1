#!/usr/bin/python

import os
import sys
import stat
import shutil
import getopt
import logging

from mallet.utils import abort, call, write, writelines
from mallet.apt import install, PACKAGE_SHORTCUTS

logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG)


def usage():
    shortcuts = PACKAGE_SHORTCUTS.keys()
    shortcuts.sort()
    print """
Usage: %s --target=<directory> --install=<compontent1,component2>

Target is the destination directory where you want to create the host image.

Install is a comma-separated list of software componenents to install.  Choices
are: %s

Other (optional) parameters are:

    -d, --distribution=<distribution>
        The distribution is any valid Debian distribution supported by your
        copy of debootstrap; the default is 'lenny'.

    -h, --hostname=<hostname
        The hostname to set in the target; the default is 'mallet'.

    -m, --mirror=<mirror>
        The mirror is the actual URL to a Debian mirror near you.

    -l, --locales=<locale1,locale2>
        Locales is a comma-separated list of locales you want to generate on
        the host image; the default is 'en_US.UTF-8'.
""" % (sys.argv[0], ', '.join(shortcuts))


def parse_args():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htihdml:v",
                                   ["help", "target=", "install=", "hostname=",
                                    "distro=", "mirror=", "locales="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    target = None
    inst_pkgs = []
    distro = 'lenny'
    hostname = 'mallet'
    mirror = None
    locales = ['en_US.UTF-8 UTF-8']
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-i", "--install"):
            inst_pkgs = a.split(',')
        elif o in ("-h", "--hostname"):
            hostname = a
        elif o in ("-d", "--distribution"):
            distro = a
        elif o in ("-m", "--mirror"):
            mirror = a
        elif o in ("-l", "--locales"):
            locales = [' '.join([b, b[6:]]) for b in a.split(',')]
        else:
            assert False, "unhandled option"
    if not target:
        print 'You must specify a target directory.'
        usage()
        sys.exit(2)
    if not os.path.isabs(target):
        print 'Target must be an absolute path'
        usage()
        sys.exit(2)
    return target, inst_pkgs, hostname, distro, mirror, locales


def main():
    target, inst_pkgs, hostname, distro, mirror, locales = parse_args()
    for pkg_shortcut in inst_pkgs:
        assert(pkg_shortcut in PACKAGE_SHORTCUTS)

    if mirror:
        call(['debootstrap', distro, target, mirror])
    else:
        call(['debootstrap', distro, target])

    logging.info('Copying /etc/network/interfaces to target')
    shutil.copyfile('/etc/network/interfaces',
                    '%s/etc/network/interfaces' % target)

    logging.info('Chrooting to %s' % target)
    os.chroot(target)
    os.chdir('/')

    logging.info('Setting hostname')
    write('/etc/hostname', hostname)
    call(['hostname', '-F', '/etc/hostname'])

    logging.info('Creating /etc/hosts')
    write('/etc/hosts', """
127.0.0.1	localhost
127.0.1.1	%s

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
""" % hostname, append=False)

    logging.info('Adding /proc to /etc/fstab')
    writelines('/etc/fstab', ['proc /proc proc none 0 0'])

    logging.info('Mounting /proc')
    call(['mount', '-t', 'proc', 'none', '/proc'])

    logging.info('Updating package list')
    call(['apt-get', 'update'])

    logging.info('Disabling init scripts while in chroot')
    policy_rc = '/usr/sbin/policy-rc.d'
    writelines(policy_rc, ['#!/bin/sh', 'exit 101'])
    os.chmod(policy_rc, stat.S_IEXEC)

    logging.info('Installing and generating locales')
    writelines('/etc/locale.gen', locales)
    install(['locales'])
    install(['ssh', 'rsync', 'less', 'sudo', 'screen', 'host', 'python',
             'python-setuptools'])
    logging.info('Installing mallet')
    call(['easy_install', 'mallet'])

    logging.info('Installing additional packages')
    for pkg_shortcut in inst_pkgs:
        install(PACKAGE_SHORTCUTS[pkg_shortcut], check=False)

    if 'python' in inst_pkgs and 'postgres' in inst_pkgs:
        install(['python-psycopg2'])
    if 'python' in inst_pkgs and 'mysql' in inst_pkgs:
        install(['python-mysql'])
    if 'python' in inst_pkgs and 'memcache' in inst_pkgs:
        install(['python-memcache'])
    if 'python' in inst_pkgs and 'apache' in inst_pkgs:
        install(['libapache2-mod-wsgi'])
    if 'php' in inst_pkgs and 'postgres' in inst_pkgs:
        install(['php5-pgsql'])
    if 'php' in inst_pkgs and 'mysql' in inst_pkgs:
        install(['php5-mysql'])
    if 'php' in inst_pkgs and 'memcache' in inst_pkgs:
        install(['php5-memcache'])
    if 'php' in inst_pkgs and 'apache' in inst_pkgs:
        install(['libapache2-mod-php5'])

    if 'apache' in inst_pkgs:
        logging.info('Adding staging and development ports to apache config')
        write('/etc/apache2/ports.conf', """
NameVirtualHost *:8080
Listen 8080
NameVirtualHost *:8090
Listen 8090
""", append=True)

    logging.info('Creating clients group')
    call(['addgroup', 'clients'])

    logging.info('Creating sudoers file')
    writelines('/etc/sudoers', ['%clients ALL=NOPASSWD: /etc/init.d/apache2 '
               'reload, /etc/init.d/apache2 restart'])

    logging.info('Setting a root password')
    print 'Please choose a root password for your new system'
    passwd = call(['passwd'])

    logging.info('Cleaning up...')
    call(['apt-get', 'clean'])
    call(['umount', '/proc'])
    os.remove(policy_rc)


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
