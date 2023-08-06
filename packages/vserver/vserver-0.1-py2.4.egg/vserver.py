r'''Python interface to Linux-VServer for managing hosting systems.

Example:

>>> import vserver
>>> test1 = vserver.HostingVServer(u'test1')
>>> test1.build(ip=u'10.0.0.1',
...             fqdn=u'test1.localhost',
...             mirror=u'http://ftp.fr.debian.org/debian/',
...             timezone=u'Europe/Paris')
>>> test1.install_ssh()
>>> test1.delete()  # dangerous!
'''

__version__      = '0.1'
__author__       = 'Volker Grabsch'
__author_email__ = 'vog@notjusthosting.com'
__url__          = 'http://www.profv.de/python-vserver/'
__classifiers__  = '''
                   Development Status :: 5 - Production/Stable
                   Environment :: Console
                   Intended Audience :: Developers
                   Intended Audience :: System Administrators
                   License :: OSI Approved :: MIT License
                   Operating System :: POSIX :: Linux
                   Programming Language :: Python
                   Topic :: Software Development :: Libraries :: Python Modules
                   Topic :: System :: Installation/Setup
                   Topic :: System :: Systems Administration
                   Topic :: Utilities
                   '''
__license__      = '''
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject
to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import subprocess
import os
import urllib2
import re

def parent_property(name):
    def _get(self):
        return getattr(self.p, name)
    def _set(self, value):
        setattr(self.p, name, value)
    return property(_get, _set)

class Error(RuntimeError):

    def __init__(self, message_format, *args):
        self._message = message_format % tuple(args)

    def __str__(self):
        return self._message.encode('UTF-8')

def text_table(format, table):
    widths = [max(len(table_row[col])
                  for table_row in table)
              for col in xrange(len(table[0]) - 1)]
    return u''.join(format % (tuple(s + (u' ' * (widths[col] - len(s)))
                                   for col, s in enumerate(table_row[:-1]))
                              + (table_row[-1],))
                    + u'\n'
                    for table_row in table)

class System(object):

    def __init__(self):
        pass

    def read_uri(self, uri):
        f = urllib2.urlopen(uri)
        try:
            return f.read().decode('UTF-8')
        finally:
            f.close()

    def read_binary(self, path):
        if path[0] != u'/':
            raise Error(u'Not an absolute path: %s', path)
        f = file(path.encode('UTF-8'), 'r')
        try:
            return f.read()
        finally:
            f.close()

    def write_binary(self, path, mode, binary):
        if path[0] != u'/':
            raise Error(u'Not an absolute path: %s', path)
        try:
            current_mode = os.stat(path.encode('UTF-8')).st_mode  & 07777
            if current_mode != mode:
                raise Error(u'File already exists with different mode: %s\n'
                            u'\n'
                            u'Current mode:  %04o\n'
                            u'Expected mode: %04o',
                            path, current_mode, mode)
        except OSError, e:
            pass
        fd = os.open(path.encode('UTF-8'), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, mode)
        f = os.fdopen(fd, 'w')
        try:
            f.write(binary)
        finally:
            f.close()
            # set mode again, because os.open() never sets suid/sgid/sticky bits
            os.chmod(path.encode('UTF-8'), mode)

    def run(self, command, input=None, allowed_returncodes=None):
        if isinstance(command, basestring):
            raise Error(u'The command should be given as list, not string: %r',
                        command)
        if input is None:
            stdin = file(os.devnull, 'r')
        else:
            stdin = subprocess.PIPE
            input = input.encode('UTF-8')
        try:
            process = subprocess.Popen(
                [arg.encode('UTF-8') for arg in command],
                bufsize=0,
                stdin=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
                shell=False,
                cwd=None,
                env={u'PATH': os.getenv(u'PATH')},
                universal_newlines=False,
            )
        except OSError, e:
            raise Error(u'Command %r: %s', command, e)
        output, error = process.communicate(input)
        output = output.decode('UTF-8')
        error = error.decode('UTF-8')
        returncode = process.returncode
        if allowed_returncodes is None:
            allowed_returncodes = [0]
        if returncode not in allowed_returncodes:
            raise Error(u'Command failed: %r\n\nReturn code: %i\n\nOutput:\n%s\n\nError:\n%s',
                        command, returncode, output.strip('\n'), error.strip('\n'))
        return returncode, output.decode('UTF-8')

class VServer(object):

    def __init__(self, name):
        self.p = System()
        self._name = name
        self._dirs = {}

    def read_uri(self, uri):
        return self.p.read_uri(uri)

    def _one_line(self, text):
        if text == u'':
            raise Error(u'Empty line.')
        if u'\n' in text[:-1]:
            raise Error(u'Multiple lines where a single line was expected:\n%s', text.strip(u'\n'))
        if text[-1] != u'\n':
            raise Error(u'Incomplete line: %s', text)
        return text[:-1]

    def _path(self, path_type, path):
        if path[0] != u'/':
            raise Error(u'Not an absolute path: %s', path)
        if not self._dirs.has_key(path_type):
            returncode, output = self.p.run([u'vserver-info', self._name, path_type])
            self._dirs[path_type] = self._one_line(output)
        return self._dirs[path_type] + path

    def _read_cfg(self, path):
        return self.p.read_binary(self._path(u'CFGDIR', path)).decode('UTF-8')

    def _write_cfg(self, path, mode, content):
        self.p.write_binary(self._path(u'CFGDIR', path), mode, content.encode('UTF-8'))

    def read_binary(self, path):
        return self.p.read_binary(self._path(u'VDIR', path))

    def write_binary(self, path, mode, binary):
        self.p.write_binary(self._path(u'VDIR', path), mode, binary)

    def read(self, path):
        return self.read_binary(path).decode('UTF-8')

    def write(self, path, mode, content):
        self.write_binary(path, mode, content.encode('UTF-8'))

    def read_one_line(self, path):
        return self._one_line(self.read(path))

    def write_one_line(self, path, mode, line):
        if u'\n' in line:
            raise Error(u'Invalid line break in: %r', line)
        self.write(path, mode, u'%s\n' % (line,))

    def read_table(self, path, regex):
        regex = re.compile(regex)
        return tuple(regex.match(line).groups()
                     for line in self.read(path).splitlines())

    def write_table(self, path, mode, format, table):
        widths = [max(len(table_row[col])
                      for table_row in table)
                  for col in xrange(len(table[0]) - 1)]
        self.write(path, mode,
            u''.join(format % (tuple(s + (u' ' * (widths[col] - len(s)))
                                     for col, s in enumerate(table_row[:-1]))
                               + (table_row[-1],))
                     + u'\n'
                     for table_row in table)
        )

    def run(self, command, input=None, allowed_returncodes=None):
        return self.p.run([u'vserver', self._name, u'exec'] + command,
                          input, allowed_returncodes)

    def _get_running(self):
        returncode, output = self.p.run([u'vserver', self._name, u'running'],
                                        allowed_returncodes=[0, 1])
        return (returncode == 0)

    def _set_running(self, running):
        if running:
            self.p.run([u'vserver', self._name, u'start'])
        else:
            self.p.run([u'vserver', self._name, u'stop'])

    running = property(_get_running, _set_running)

    def _get_start_on_boot(self):
        try:
            mark = self._read_cfg(u'/apps/init/mark')
        except IOError, e:
            return False
        if mark == u'default\n':
            return True
        elif mark == u'':
            return False
        else:
            raise Error(u'Unexpected init mark: %r', mark)

    def _set_start_on_boot(self, start_on_boot):
        if start_on_boot:
            self._write_cfg(u'/apps/init/mark', 0644, u'default\n')
        else:
            self._write_cfg(u'/apps/init/mark', 0644, u'')

    start_on_boot = property(_get_start_on_boot, _set_start_on_boot)

    def build(self, ip, fqdn, interface, method):
        self.p.run([u'vserver', self._name, u'build',
                    u'--hostname', self._name,
                    u'--interface', interface,
                    u'-m'] + method)
        self.write(u'/etc/hosts', 0644,
            u'%s  %s %s\n' % (ip, fqdn, self._name)
        )
        self._write_cfg(u'/fstab', 0644,
            # disable ramdisk /tmp
            u'none  /proc     proc    defaults        0 0\n'
            u'none  /dev/pts  devpts  gid=5,mode=620  0 0\n'
        )
        self.running = True

    def delete(self):
        self.p.run([u'vserver', self._name, u'delete'],
                   input=u'Y\n')

class DebianVServer(object):

    def __init__(self, name):
        self.p = VServer(name)
        self._updated = False

    def read_uri(self, uri):
        return self.p.read_uri(uri)

    # system
    def _get_timezone(self):
        return self.p.read_one_line(u'/etc/timezone')

    def _set_timezone(self, timezone):
        self.p.write_binary(u'/etc/localtime', 0644,
            self.p.read_binary(u'/usr/share/zoneinfo/%s' % (timezone,))
        )
        self.p.write_one_line(u'/etc/timezone', 0644, timezone)

    timezone = property(_get_timezone, _set_timezone)

    # ssh
    _ssh_host_key_paths = (
        (u'/etc/ssh/ssh_host_dsa_key',     0600),
        (u'/etc/ssh/ssh_host_dsa_key.pub', 0644),
        (u'/etc/ssh/ssh_host_rsa_key',     0600),
        (u'/etc/ssh/ssh_host_rsa_key.pub', 0644),
    )

    def _get_ssh_host_keys(self):
        return dict((path, self.p.read(path))
                    for path, mode in self._ssh_host_key_paths)

    def _set_ssh_host_keys(self, ssh_host_keys):
        for path, mode in self._ssh_host_key_paths:
            self.p.write(path, mode, ssh_host_keys[path])

    ssh_host_keys = property(_get_ssh_host_keys, _set_ssh_host_keys)

    def _get_ssh_config(self):
        return self.p.read_table(u'/etc/ssh/sshd_config', u'([^# ]*)\s*(.*)')

    def _set_ssh_config(self, ssh_config):
        self.p.write_table(u'/etc/ssh/sshd_config', 0644, u'%s  %s', ssh_config)

    ssh_config = property(_get_ssh_config, _set_ssh_config)

    # apt
    def _get_apt_sources(self):
        return self.p.read_table(u'/etc/apt/sources.list', u'(\S+)\s+(\S+)\s+(\S+)\s+(.+)')

    def _set_apt_sources(self, sources):
        self.p.write_table(u'/etc/apt/sources.list', 0644, u'%s  %s  %s  %s', sources)
        self._updated = False
        self._update()

    apt_sources = property(_get_apt_sources, _set_apt_sources)

    def add_apt_keys(self, keys):
        self.p.run([u'apt-key', u'add', u'-'], input=keys)

    def _update(self):
        if not self._updated:
            self.p.run([u'aptitude', u'update', u'-y'])
            self._updated = True

    def safe_upgrade(self):
        self._update()
        self.p.run([u'aptitude', u'safe-upgrade', u'-y'])

    def install(self, *packages):
        self._update()
        self.p.run([u'aptitude', u'install', u'-y', u'-R'] + list(packages))

    # services
    def start_service(self, service):
        self.p.run([u'/etc/init.d/%s' % (service,), u'start'])

    def stop_service(self, service):
        self.p.run([u'/etc/init.d/%s' % (service,), u'stop'])

    def set_service(self, service, script):
        self.p.write(u'/etc/init.d/%s' % (service,), 0755, script)
        self.p.run([u'update-rc.d', service, u'defaults'])

    def _get_running_services(self):
        returncode, output = self.p.run([u'netstat', u'-lnp'])
        return output.splitlines()

    running_services = property(_get_running_services)

    # user
    def add_user(self, user):
        self.p.run([u'useradd', u'-m', u'--', user])

    def del_user(self, user):
        self.p.run([u'userdel', u'-r', u'--', user])

    def set_user_password(self, user, password):
        if password is None:
            self.p.run([u'passwd', u'-l', u'--', user])
        else:
            self.p.run([u'chpasswd'], input=(u'%s:%s\n' % (user, password)))

    # zope
    def add_zope_instance(self, version, user, admin_password):
        self.p.run([u'su', u'-', user, u'-c',
                    u"dzhandle -z'%s' make-instance default -m manual -u '%s:%s'"
                    % (version, u'admin', admin_password)])

    # vserver
    running = parent_property(u'running')
    start_on_boot = parent_property(u'start_on_boot')

    def build(self, ip, fqdn, mirror, suite):
        self.p.build(ip, fqdn, u'dummy0:%s/32' % (ip,), [
            u'debootstrap', u'--',
            u'-m', mirror,
            u'-d', suite,
        ])
        self.add_apt_keys(self.read_uri(u'http://backports.org/debian/archive.key'))
        self.apt_sources = (
            (u'deb', mirror,                              u'%s'           % (suite,), u'main contrib non-free'),
            (u'deb', u'http://security.debian.org/',      u'%s/updates'   % (suite,), u'main contrib non-free'),
            (u'deb', u'http://www.backports.org/debian/', u'%s-backports' % (suite,), u'main contrib non-free'),
        )
        self.safe_upgrade() # security upgrades

    def delete(self):
        self.p.delete()

class HostingVServer(object):

    def __init__(self, name):
        self.p = DebianVServer(name)

    def build(self, ip, fqdn, mirror, timezone):
        self.p.build(ip, fqdn, mirror, u'lenny')
        self.p.start_on_boot = True
        self.p.timezone = timezone
        self.p.set_user_password(u'root', None)
        self.p.install(
            u'less', u'vim', u'curl', u'w3m', u'rsync', u'mmv',
            u'htop', u'mc', u'pwgen', u'bzip2', u'gcc', u'make',
            u'locales-all',
            u'subversion',
            u'mercurial', u'python-pygments',
            u'darcs',
            u'git-core', u'cogito',
        )
        running_services = self.p.running_services
        if len(running_services) != 4:
            raise Error(u'Unexpected running services:\n%s',
                        u'\n'.join(running_services))

    def delete(self):
        self.p.delete()

    def install_ssh(self, keys_vserver=None):
        self.p.install(u'openssh-server', u'openssh-client')
        self.p.stop_service(u'ssh')
        self.p.ssh_config = self.p.ssh_config + (
            (u'PermitRootLogin', u'no'),
            (u'UseDNS',          u'no'),
        )
        if keys_vserver is not None:
            self.p.ssh_host_keys = keys_vserver.p.ssh_host_keys
        self.p.start_service(u'ssh')

    def install_zope2(self, user, password, admin_password):
        self.p.install(
            u'python-4suite',
            u'python-egenix-mxdatetime',
            u'python-egenix-mxtools',
            u'python-ldap',
            u'python-mysqldb',
            u'python-pgsql',
            u'python-psyco',
            u'python-psycopg2',
            u'python-pyopenssl',
            u'python-tz',
            u'python-unit',
            u'python-xml',
            u'zope2.10',
        )
        self.p.set_service(u'zope-users', ur'''#!/bin/sh

VERSION='2.10'
USERS=`getent passwd | awk -F: '$3 >= 1000 && $3 < 2000 {print $1}'`

case "$1" in
    start)
        for USER in $USERS; do
            echo -e -n "Start zope instance of user $USER:\t"
            su - "$USER" -c "~/zope/instance/zope$VERSION/default/bin/zopectl start"
        done
        ;;
    stop)
        for USER in $USERS; do
            echo -e -n "Stop zope instance of user $USER:\t"
            su - "$USER" -c "~/zope/instance/zope$VERSION/default/bin/zopectl stop"
        done
        ;;
    restart)
        "$0" stop
        "$0" start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
''')
        self.p.add_user(user)
        self.p.set_user_password(user, password)
        self.p.add_zope_instance(u'2.10', user, admin_password)
        self.p.start_service(u'zope-users')

def _test():
    '''Run all doc tests of this module.'''
    import doctest, vserver
    return doctest.testmod(vserver)

if __name__ == '__main__':
    _test()
