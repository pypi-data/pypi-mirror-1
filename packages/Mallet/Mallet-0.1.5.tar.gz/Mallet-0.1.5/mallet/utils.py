import sys
import logging
import subprocess


def abort(msg):
    """
    Logs the specified error message and aborts the current process execution.
    """
    logging.error(msg)
    sys.exit(1)


def call(command, *args, **kwargs):
    """
    Calls the given command, which is passed as a list of the command name and
    arguments (e.g., ['ls', '-l', '/tmp']) using the subprocess module.  If
    check=True is specified (the default), the method will raise an exception
    if the command's result code is non-zero.
    """
    check = kwargs.pop('check', True)
    logging.debug('Running `%s`' % ' '.join(command))
    if check:
        subprocess.check_call(command, *args, **kwargs)
    else:
        return subprocess.call(command, *args, **kwargs)


def write(path, text, append=True):
    """
    Writes the specified text to the specified file path.  If append=True is
    specified (the default), the file is not truncated when opened.
    """
    f = open(path, append and 'a' or 'w')
    f.write(text)
    f.close()


def writelines(path, lines, append=True):
    """
    Writes the specified lines, separated by new lines, to the specified file
    path.  If append=True is specified (the default), the file is not truncated
    when opened.
    """
    f = open(path, append and 'a' or 'w')
    f.writelines([line + '\n' for line in lines + ['']])
    f.close()
