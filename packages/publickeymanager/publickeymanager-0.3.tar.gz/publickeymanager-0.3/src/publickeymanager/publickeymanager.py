from ConfigParser import SafeConfigParser
from optparse import OptionParser
from functools import partial
import os
import copy
import StringIO
import paramiko
import getpass
import time

class Server(object):
    """Holds server information."""

    def __init__(self, hostname, user, access, keys):
        self.hostname = hostname
        self.user = user
        self.access = access
        self.authorized_keys = self.generate_authorized_keys(keys)

    def generate_authorized_keys(self, keys):
        """Generates a authorized_key file."""

        output = StringIO.StringIO()
        for user in self.access:
            output.write(keys[user] + '\n')
        authorized_keys = output.getvalue()
        output.close()
        return authorized_keys


def parse_config(filename, keys_dir):
    """Parse the configuration file.

    Extracts the keys from the filenames and parses
    the server directives.
    """

    def parse_server(server, users=None):
        """Parses a server in the configuration file."""

        if users == None:
            users = set()

        if not config.has_option(server, 'hostname') or not config.has_option(
            server, 'user'):
            print "Server %s is missing options hostname and/or user" % (
                    server)
            return

        server_users = copy.copy(users)
        if config.has_option(server, 'access'):
            for user in data_get(server, 'access'):
                server_users.add(user)
        if config.has_option(server, 'groups'):
            for group in data_get(server, 'groups'):
                for user in data_get('group:users', group):
                    server_users.add(user)
        hostname = data_get(server, 'hostname')[0]
        login_user = data_get(server, 'user')[0]
        return Server(hostname, login_user, server_users, keys)

    def data_get(section, keyword):
        """A simple parser which returns a list."""

        return [i for i in config.get(section, keyword).split('\n') if i != '']


    config = SafeConfigParser()
    config.read(filename)

    if not config.has_section('keys'):
        raise Exception, 'No keys specified in the configuration file.'

    # put the public keys in a dict
    keys = {}
    for name in config.options('keys'):
        keys[name] = open(os.path.join(keys_dir, data_get('keys', name)[0])
                          ).read().strip('\n')

    # group groups and servers
    groups = []
    servers = []
    for section in config.sections():
        if ':' in section:
            ident, name = section.split(':')
            if ident == 'group' and name != 'users':
                groups.append(section)
            elif ident == 'server':
                servers.append(section)

    #holds instances of Server
    servers_instance = []

    # First, get a list of all servers and parse those
    # Second, get a list of all servers in all groups and parse those

    for group in groups:
        if not config.has_option(group, 'servers'):
            print "%s has no servers." % (group)
            continue
        users = set()

        if config.has_option(group, 'user_groups'):
            user_groups = data_get(group, 'user_groups')

            for i in user_groups:
                for user in data_get('group:users', i):
                    if not keys.has_key(user):
                        print "User %s doesn't have a key" % (user)
                    else:
                        users.add(user)

        if config.has_option(group, 'access'):
            for user in data_get(group, 'access'):
                if not keys.has_key(user):
                    print "User %s doesn't have a key" % (user)
                else:
                    users.add(user)

        for server in data_get(group, 'servers'):
            parsed = parse_server('server:' + server, users)
            if len(users) < 1:
                parsed = False
                print "Server update %s failed: zero users defined." % (server)
            if parsed:
                servers.remove('server:' + server)
                servers_instance.append(parsed)


    for server in servers:
        parsed = parse_server(server)
        if parsed:
            servers_instance.append(parsed)

    return servers_instance


def upload(server, ssh_key):
    """Upload the authorized_keys file to the server."""

    def close_connection():
        """Ssh and sftp connection closer."""
        sftp.close()
        ssh.close()

    # set up ssh and sftp connection
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    #connect checks for keys in the following order:
    # pkey, ssh_agent, id_rsa or id_dsa in ~/.ssh.
    ssh.connect(server.hostname, username=server.user, pkey=ssh_key)
    sftp = ssh.open_sftp()
    #change dir and push authorized keys file.
    sftp.chdir('.ssh')
    f = sftp.open('keys', mode='w')
    f.write(server.authorized_keys)
    f.close()

    # check authorized keys file write.
    f = sftp.open('keys')
    contents = f.read()
    f.close()
    if not contents == server.authorized_keys:
        print 'ERROR: No update of server %s' %(server.hostname)
        close_connection()
        return

    # Let authorized_keys and keys have the same permissions.
    ssh.exec_command('chmod --reference=.ssh/authorized_keys '
                     '.ssh/keys')
    # Check if permission change went correct.
    stdin, stdout, stderr = ssh.exec_command(
        'ls -l .ssh/{authorized_keys,keys}')
    read = stdout.read()
    permission  = [ line.split(' ')[0] for line in read.split('\n')]
    if permission[0] != permission[1]:
        print ( 'ERROR: No update of server %s. '
              'Unable to change file permissions.') %(server.hostname)
        close_connection()
        return

    # move uploaded keysfile to authorized_keys via shell. This is done
    # to have an atomic operation.
    shell = ssh.invoke_shell()
    shell.send('cd .ssh\n')
    shell.send('mv keys authorized_keys\n')
    # mv didn't complete before the close, so a sleep(1) is needed.
    time.sleep(1)
    shell.close()

    # check if move went correct.
    keyfile = sftp.open('authorized_keys')
    contents2 = keyfile.read()
    keyfile.close()
    if contents != contents2:
        print 'ERROR: server %s: Copy of keys file to authorized_keys was unsuccessfull.' % (server.hostname)
        close_connection()
        return
    print 'Update: server %s: successfull' % (server.hostname)
    close_connection()


def main():

    def initialize_private_key(pkey_class, key_name, password = None):
        """Wrapper to initialize private ssh key."""
        return pkey_class.from_private_key_file(key_name, password=password)

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                      help="Configuration file, defaults to key.cfg",
                      metavar="FILE")
    parser.add_option("-k", "--key", dest="ssh_key",
                      help="Specify ssh key, defaults to keys in .ssh",
                      metavar="ssh_key")
    parser.add_option("-d", "--dir", dest="key_dir",
                      help=("Specify directory to look for public keys, "
                            "defaults to ./keys."),
                      metavar="key_dir")


    (options, args) = parser.parse_args()
    if options.config == None:
        options.config = 'key.cfg'

    if options.key_dir == None:
        options.key_dir = 'keys'

    if not os.path.exists(options.key_dir):
        print "Key dir: '%s' does not exist." % (options.key_dir)
        return

    ssh_key = None
    if options.ssh_key:
        for pkey_class in (paramiko.RSAKey, paramiko.DSSKey):
            initialize_wrap = partial(initialize_private_key, pkey_class,
                                      options.ssh_key)
            try:
                ssh_key = initialize_wrap()
            except paramiko.PasswordRequiredException:
                password = getpass.getpass('Ssh Key Password: ')
                try:
                    ssh_key = initialize_wrap(password=password)

                except paramiko.SSHException:
                    print 'Wrong password'

            except paramiko.SSHException:
                pass

    servers = parse_config(options.config, options.key_dir)

    # Push config to servers
    for server in servers:
        upload(server, ssh_key)

if __name__ == '__main__':
    main()
