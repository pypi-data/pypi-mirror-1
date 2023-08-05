"""Simple SSH command transport with callback support
"""

__author__ = 'Drew Smathers <drew smathers at gmail com>'

from twisted.conch.ssh import transport, userauth, connection, common, keys, channel
from twisted.internet import defer, protocol, reactor
from twisted.python import log
import struct, sys, getpass, os

class SSHTransport(transport.SSHClientTransport):
    """Enables SSH transport with flexible authentication: 
    username/passwords or public and private key-based.
    """

    def verifyHostKey(self, hostKey, fingerprint):
        print 'host key fingerprint: %s' % fingerprint
        return defer.succeed(1)

    def connectionSecure(self):
        self.requestService(
            SSHUserAuth(self.factory.user,
                Connection(self.factory.command, self.factory.datahandler),
                keys_file=self.factory.keys_file,
                host=self.factory.host))

class SSHTransportFactory(protocol.ReconnectingClientFactory):
    """SSH Transport factory. Uses SSHTransport as protocol.
    """
    protocol = SSHTransport

    def __init__(self, user, host, datahandler=None, keys_file=None, command='true'):
        self.user = user
        self.host = host
        self.datahandler = datahandler or (lambda d : None)
        self.keys_file = keys_file
        self.command = command


class SSHUserAuth(userauth.SSHUserAuthClient):

    def __init__(self, user, instance, host=None, keys_file=None):
        self.user = user
        self.host = host
        self.keys_file = keys_file
        userauth.SSHUserAuthClient.__init__(self, user, instance)

    def getPassword(self):
        return defer.succeed(getpass.getpass("%s@%s's password: " % (self.user, self.host)))
            
    def getPublicKey(self):
        if not self.keys_file:
            return
        if self.keys_file[:1] == '~':
            path = os.path.expanduser(self.keys_file)
        else:
            path = os.path.abspath(self.keys_file)
        if not os.path.exists(path) or self.lastPublicKey:
            # the file doesn't exist, or we've tried a public key
            return
        return keys.getPublicKeyString(path+'.pub')

    def getPrivateKey(self):
        if self.keys_file[:1] == '~':
            path = os.path.expanduser(self.keys_file)
        else:
            path = os.path.abspath(self.keys_file)
        return defer.succeed(keys.getPrivateKeyObject(path))

class Connection(connection.SSHConnection):

    def __init__(self, command, datahandler):
        self.command = command
        self.datahandler = datahandler
        connection.SSHConnection.__init__(self)

    def serviceStarted(self):
        self.openChannel(Channel(self.command, self.datahandler,
            2**16, 2**15, self))

class Channel(channel.SSHChannel):
    name = 'session'
    def __init__(self, command, datahandler, *args):
        self.command = command
        self.datahandler = datahandler
        channel.SSHChannel.__init__(self, *args)
    def openFailed(self, reason):
        log.error('Failed opening connection : ' + reason)
    def channelOpen(self, data):
        self.welcome = data
        print self.welcome
        d = self.conn.sendRequest(self, 'exec', common.NS(self.command), wantReply=1)
    def dataReceived(self, data):
        log.msg('rcv data: %s' % data)
        self.datahandler(data)
    def closed(self):
        log.msg('losing connection')
        self.loseConnection()

# Test
# USAGE python sshcmds.py logfile user,host,color ... 
def main():
    from xix.utils import console
    color_wheel = ('green', 'blue', 'brown', 'magenta', 'cyan', 'red')
    tile = 0
    def gotdata(color, hostname):
        class _Data(object):
            last = ''
            def __call__(self, data):
                d = data
                if self.last:
                    d = self.last + data
                    self.last = ''
                noterm = d[-1] != '\n'
                lines = d.split('\n')
                if noterm:
                    self.last = lines.pop()
                    if not self.last.strip():
                        self.last = lines.pop()
                for line in lines:
                    if line:
                        print console.format('[%s]' % hostname, color), line
        return _Data()
    cmd = sys.argv[1]
    for a in sys.argv[2:]:
        tks = a.split(',')
        if len(tks) == 3:
            username,host,color = tks
        else:
            username,host = tks
            color = color_wheel[tile % len(color_wheel)]
            tile += 1
        print username, host, color
        reactor.connectTCP(host, 22, SSHTransportFactory(username, host,
            keys_file='~/.ssh/id_rsa',
            datahandler = gotdata(getattr(console, 'FG%s' % color.upper()), host),
            command=cmd))
    reactor.run()


if __name__ == '__main__':
    main()


