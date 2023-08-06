import rdflib

class OnlineAccount(object):

    def __init__(self, graph=None, node=None):

    	self.accountServiceHomepage = ""
    	self.accountName = ""
    	self.accountProfilePage = ""
        if graph and node:
            for homepage in graph.objects(subject=node, predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/accountServiceHomepage')):
                self.accountServiceHomepage = unicode(homepage)
            for name in graph.objects(subject=node, predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/accountName')):
                self.accountName = unicode(name)
            for profilepage in graph.objects(subject=node, predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/accountProfilePage')):
                self.accountProfilePage = unicode(profilepage)
