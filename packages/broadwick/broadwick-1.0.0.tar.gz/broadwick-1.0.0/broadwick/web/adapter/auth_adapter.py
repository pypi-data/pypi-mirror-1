from broadwick.web.utils import AuthenticationException
import logging

class BasicAuthRequestAdapter(object):
    """This is a the base class for simple role based authentication that uses
       the browser's basic dialog based authentication
       
       To create a sub-class just implement the login method 
       The request is amended with an auth attribute for check roles within requests
       
       to use a forwarded authenticated user:
           request.getHeader('x-forwarded-user')
       """
    def __init__(self, http_realm):
        self.http_realm = http_realm
    
    def before_request(self, request, resource, params):
        """Called by the resource before formatting"""
        session = request.getSession()
        request.hasRoles = lambda roles: self.hasRole(request, roles)
        if hasattr(resource.func, '_auth_roles'):
            if not hasattr(session, 'user_roles'):
                roles = self.login(request)
                if roles is None:                    
                    request.setResponseCode(401)
                    request.setHeader("www-authenticate",
                                      'Basic realm="%s"' % self.http_realm)
                    raise AuthenticationException('Please login...')
                session.user_roles = roles
            if not self.hasRole(request, resource.func._auth_roles):
                raise AuthenticationException('You do not have access to this page!')

    def after_request(self, request, result):
        """called by the resource after formatting"""
        pass
    
    def login(self, request):
        """Should return a list of roles if login was a success or None if not"""
        raise NotImplemented('sub-class responsibility')

    @classmethod
    def logout(self, request):
        session = request.getSession()
        if hasattr(session, 'user_roles'):
            try: del session.user_roles     
            except KeyError: pass
        session.expire()


    def hasRole(self, request, roles):
        session = request.getSession()
        for role in roles:
            if role in session.user_roles:
                logging.debug('authed %s for %s' % (request.getUser(),role))
                return True
        return False
        
        
class TupleAuthRequestAdapter(BasicAuthRequestAdapter):
    """Initialize with a list of tuples of (username, password, [role1,role2,roleN])"""
    def __init__(self, http_realm, users):
        BasicAuthRequestAdapter.__init__(self, http_realm)
        self.users = users
        
    def login(self, request):
        requestor = request.getHeader('x-forwarded-user')
        if requestor:
            logging.debug('x-forwarded-user: %s' % requestor)
            
            for user, password, roles in self.users:
                if user == requestor:
                    return roles
        for user, password, roles in self.users:
            if user == request.getUser() and password == request.getPassword():
                return roles
            
    

    
        