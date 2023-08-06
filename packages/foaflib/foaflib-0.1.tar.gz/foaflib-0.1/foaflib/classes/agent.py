import rdflib
from rdflib.Graph import ConjunctiveGraph as Graph
from urllib import urlopen

from foaflib.classes.onlineaccount import OnlineAccount

_SINGLETONS = """gender openid birthday pubkeyAddress""".split()
_BASIC_MULTIS = """mbox mbox_sha1sum jabberID aimChatID icqChatID yahooChatID msnChatID weblog tipjar made holdsAccount""".split()

class Agent(object):

    def __init__(self, path=None):

        for name in _BASIC_MULTIS:
            setattr(self, "_get_%ss" % name, self._make_getter(name))
            setattr(Agent, "%ss" % name, property(self._make_property_getter(name)))
            setattr(self, "add_%s" % name, self._make_adder(name))
            setattr(self, "del_%s" % name, self._make_deler(name))
        self._graph = Graph()
        if path:
            self._graph.parse(path)
            for topic in self._graph.objects(predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/primaryTopic')):
                self._me = topic

    # Things you can only reasonably have one of - gender, birthday, first name, etc. - are termed
    # "singletons".  Singletion I/O is handled purely through __getattr__ and __setattr__, below.
    def __getattr__(self, name):
        if name in _SINGLETONS:
            for raw in self._graph.objects(subject=self._me, predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name)):
                return unicode(raw)
            return None
        raise AttributeError, name
            
    def __setattr__(self, name, value):
        if name in _SINGLETONS:
            self._graph.remove((self._me, rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name), None))
            self._graph.add((self._me, rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name), value))
        else:
            object.__setattr__(self, name, value)

    # Stuff you might have more than one of - weblogs, accounts, friends, etc. - are handled by a
    # combination of the property decorator and add/del methods.

    def _make_getter(self, name):
        def method():
            return [unicode(x) for x in self._graph.objects(subject=self._me, predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name))]
        return method

    def _make_property_getter(self, name):
        def method(self):
            return [unicode(x) for x in self._graph.objects(subject=self._me, predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name))]
        return method

    def _make_adder(self, name):
        def method(value):
            self._graph.add((self._me, rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name), rdflib.URIRef(value)))
        return method

    def _make_deler(self, name):
        def method(value):
            self._graph.remove((self._me, rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name), rdflib.URIRef(value)))
        return method

    def _build_account(self, acct):
        if isinstance(acct, rdflib.BNode):
            return OnlineAccount(self._graph, acct)
        elif isinstance(acct, rdflib.URIRef):
            account = OnlineAccount()
            account.accountServiceHomepage = unicode(acct)
	    return account
        return OnlineAccount()

    def _get_accounts(self):
        for raw_account in self._graph.objects(predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/holdsAccount')):
            account = self._build_account(raw_account)
            if account:
                yield account

    accounts = property(_get_accounts)

    def add_account(self, account):
        x = rdflib.BNode()
        self._graph.add((x, rdflib.URIRef("http://xmlns.com/foaf/0.1/accountServiceHomepage"), rdflib.URIRef(account.accountServiceHomepage)))
        self._graph.add((x, rdflib.URIRef("http://xmlns.com/foaf/0.1/accountName"), rdflib.URIRef(account.accountName)))
        if account.accountProfilePage:
            self._graph.add((x, rdflib.URIRef("http://xmlns.com/foaf/0.1/accountProfilePage"), rdflib.URIRef(account.accountProfilePage)))
        self._graph.add((self._me, rdflib.URIRef("http://xmlns.com/foaf/0.1/holdsAccount"), x))

    # Serialisation
    def get_xml_string(self):
        self._graph.serialize()

    def save_as_xml_file(self, filename):
        self._graph.serialize(filename)

    # Account stuff
