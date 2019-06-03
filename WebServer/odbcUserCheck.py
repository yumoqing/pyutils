import pyodbc as db
db.lowercase = True
from zope.interface import implements, Interface, Attribute
from twisted.cred.checkers import ICredentialsChecker

from twisted.internet import defer
from twisted.python import failure, log
from twisted.cred import error, credentials


class ODBCUserChecker:
    """
    An extremely simple credentials checker.

    This is only of use in one-off test programs or examples which don't
    want to focus too much on how credentials are verified.

    You really don't want to use this for anything else.  It is, at best, a
    toy.  If you need a simple credentials checker for a real application,
    see L{FilePasswordDB}.
    """

    implements(ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)

    def __init__(self, odbcstr,checkSQL):
        self.odbc_str = odbcstr
        self.checkPasswordSQL = checkSQL

    def addUser(self, username, password):
        self.users[username] = password

    def _cbPasswordMatch(self,matched,username):
        if matched:
            return username
        else:
            return failure.Failure(error.UnauthorizedLogin())
            
    def requestAvatarId(self, credentials):
        print( "ODBCUserChecker() check user",credentials.username)
        try:
            conn = db.connect(self.odbc_str)
            cur = conn.cursor()
            cur.execute(self.checkPasswordSQL,credentials.username)
            r = cur.fetchone()
            if r is None:
                cur.close()
                conn.close()
                return defer.fail(error.UnauthorizedLogin())
            cur.close()
            conn.close()
            return defer.maybeDeferred(credentials.checkPassword, r.password
                    ).addCallback(self._cbPasswordMatch, credentials.username)
            
        except Exception as e:
            print( e,self.checkPasswordSQL)
            return defer.fail(error.UnauthorizedLogin())
        
        if credentials.username in self.users:
            return defer.maybeDeferred(
                credentials.checkPassword,
                self.users[credentials.username]).addCallback(
                self._cbPasswordMatch, str(credentials.username))
        else:
            return defer.fail(error.UnauthorizedLogin())

