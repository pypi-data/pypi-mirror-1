from twisted.cred import portal, checkers
from twisted.conch import manhole, manhole_ssh

def getFactory(namespace, **passwords):
    """Return a manhole SSH factory.

    With thanks to http://www.devshed.com/c/a/Python/SSH-with-Twisted/3/
    """
    realm = manhole_ssh.TerminalRealm()
    def getManhole(_):  return manhole.Manhole(namespace)
    realm.chainedProtocolFactory.protocolFactory = getManhole
    p = portal.Portal(realm)
    p.registerChecker(checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords))
    f = manhole_ssh.ConchFactory(p)
    return f

