from turbogears import identity, redirect, visit
from turbogears import expose, controllers
import turbogears
import cherrypy

from openid.consumer import consumer
from openid.consumer.discover import DiscoveryFailure
import urllib2
import urlparse

def flatten(dictionary, inner_dict):
    """
    Given a dictionary like this:
        {'a':1, 'b':2, 'openid': {'i':1, 'j':2}, 'c': 4},
    flattens it to have:
        {'a':1, 'b':2, 'openid.i':1, 'openid.j':2, 'c':4}
    """
    if dictionary.has_key(inner_dict):
        d = dictionary.pop(inner_dict)
        for k in d.iterkeys():
            dictionary[inner_dict +'.' + k] = d[k]

class OpenIDLoginController(controllers.Controller):
    def __init__(self, User, VisitIdentity, openid_path = None, store = None, trust_root = None):
        self.User = User
        self.VisitIdentity = VisitIdentity

        if not openid_path:
            openid_path = turbogears.url("/openid")
        self.openid_path = openid_path

        self._store = store
        if not store:
            try:
                self.store.createTables()
            except:
                pass

        self._trust_root = trust_root

    def getStore(self):
        if self._store:
            return self._store

        from pysqlite2 import dbapi2 as sqlite
        from openid.store import sqlstore
        con = sqlite.connect('openid.db')
        return sqlstore.SQLiteStore(con)
    store = property(getStore)

    def get_trust_root(self):
        base = cherrypy.request.base
        if self._trust_root:
            return urlparse.urljoin(base, self._trust_root)
        return urlparse.urljoin(base, "/")

    trust_root = property(get_trust_root)

    def openId(self, session):
        return consumer.Consumer(session, self.store)

    @expose(template="tgopenidlogin.templates.login")
    def login(self, forward_url = None, msg = None, identity_url = None, *args, **kw):
        if forward_url == "login":
            forward_url = None

        if not forward_url:
            forward_url = cherrypy.request.path

        if not msg:
            if identity.was_login_attempted():
                msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
            elif identity.get_identity_errors():
                msg=_("You must provide your credentials before accessing "
                   "this resource.")
            else:
                msg=_("Please log in.")
                forward_url= cherrypy.request.headers.get("Referer", "/")

        parameters = cherrypy.request.params.copy()
        rm_from_param = ["forward_url", "identity_url", "openid", "nonce", "login"]
        for to_rm in rm_from_param:
            if to_rm in parameters:
                del parameters[to_rm]
            
        cherrypy.response.status=403
        return dict(message=msg, logging_in=True,
                    original_parameters=parameters,
                    forward_url=forward_url, openid_path = self.openid_path)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")

    @expose()
    def loginBegin(self, identity_url, forward_url = "/", **kw):
        """Called when user clicks OK on the login form."""
        openId = self.openId(cherrypy.session)
        try:
            authrequest = openId.begin(identity_url)
        except DiscoveryFailure, e:
            return self.login(forward_url = forward_url, msg = str(e))

        authrequest.addExtensionArg('sreg', 'optional', 'nickname,email')
        authrequest.addExtensionArg('sreg', 'policy_url', 'http://www.google.com')

        returnUri = self.openIdReturnUri(cherrypy.session, forward_url)

        openIdUri = authrequest.redirectURL(self.trust_root, returnUri)
        raise redirect(openIdUri)

    def openIdReturnUri(self, session, forward_url):
        """Given an OpenID request information object, return a URI on this server."""
        import urllib
        forward_url = urllib.urlencode({'forward_url': forward_url})

        base = cherrypy.request.base
        openid_path = urlparse.urljoin(base, self.openid_path)

        return '%s/loginFinish?%s' % (openid_path, forward_url)

    @expose()
    def loginFinish(self, forward_url, **kws):
        openId = self.openId(cherrypy.session)
        flatten(kws, 'openid')
        flatten(kws, 'openid.sreg')
        response = openId.complete(kws)

        if response.status == 'success':
            u = self.User.get_by(user_name=kws['openid.identity'])
            if not u:
                u = self.User(user_name=kws['openid.identity'])

            user_info = response.extensionResponse('sreg')
            if user_info.has_key('email'):
                u.email_address = user_info['email']
            if user_info.has_key('nickname'):
                u.display_name = user_info['nickname']

            u.save()

            visit_key = visit.current().key
            link = self.VisitIdentity.get_by(visit_key=visit_key)
            if not link:
                link = self.VisitIdentity(visit_key=visit_key, user_id=u.user_id)
            else:
                link.user_id = u.user_id
            link.save()

            raise redirect(forward_url)

        identity.set_login_attempted(True)
        return self.login(forward_url=forward_url)
