from mallet.utils import call


PACKAGE_SHORTCUTS = {
    'apache': ['apache2', 'libapache2-mod-fcgid'],
    'postgres': ['postgresql'],
    # python and setuptools must be installed for mallet support
    'python': ['ipython', 'python-imaging'],
    'mysql': ['mysql'],
    # 'php5' pkg includes apache deps, so just install the CLI
    'php': ['php5-cli'],
    'memcache': ['memcached', 'libmemcache0'],
}


def install(pkgs, check=True):
    """
    Installs the specified package(s) using aptitude, the Debian package
    management tool.
    """
    call(['aptitude', '--assume-yes', 'install'] + pkgs, check=check)
