import rdflib
from rdflib.Graph import ConjunctiveGraph as Graph
from urllib import urlopen

from foaflib.classes.agent import Agent

_SINGLETONS = "title name nick givenname firstName surname family_name homepage geekcode meyersBriggs dnaChecksum plan".split()
_BASIC_MULTIS = "schoolHomepage workplaceHomepage img currentProject pastProject publications isPrimaryTopicOf page made workInfoHomepage interest".split()

class Person(Agent):

    def __init__(self, uri=None):

	Agent.__init__(self)
        for name in _BASIC_MULTIS:
            setattr(self, "_get_%ss" % name, self._make_getter(name))
            setattr(Person, "%ss" % name, property(self._make_property_getter(name)))
            setattr(self, "add_%s" % name, self._make_adder(name))
            setattr(self, "del_%s" % name, self._make_deler(name))

        self._graph = Graph()
        self._error = False
        if uri:
            self.uri = uri
            try:
                self._graph.parse(uri)
                self._find_me_node()
            except:
                self._error = True
        else:
            self.uri = ""
            self._setup_profile()

    def _setup_profile(self):
        x = rdflib.BNode()
        self._graph.add((x, rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.URIRef('http://xmlns.com/foaf/0.1/PersonalProfileDocument')))
        self._graph.add((x, rdflib.URIRef('http://webns.net/mvcb/generatorAgent'), rdflib.URIRef('http://code.google.com/p/foaflib')))
        self._graph.add((x, rdflib.URIRef('http://xmlns.com/foaf/0.1/primaryTopic'), rdflib.URIRef('#me')))
        self._graph.add((rdflib.URIRef('#me'), rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.URIRef('http://xmlns.com/foaf/0.1/Person')))
        self._me = rdflib.URIRef('#me')

    def _get_people(self):
        return self._graph.subjects(rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.URIRef('http://xmlns.com/foaf/0.1/Person'))

    def _find_me_node(self):
        # Check for a PersonalProfileDocument
        for doc in self._graph.subjects(predicate=rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), object=rdflib.URIRef('http://xmlns.com/foaf/0.1/PersonalProfileDocument')):
            for topic in self._graph.objects(subject=doc, predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/primaryTopic')):
                self._me = topic
                return
        # Check for a single Person
        if len(list(self._get_people())) == 1:
            for person in self._get_people():
                self._me = person
                return
        # Return someone who isn't known by anyone else in this graph - the best we can do?
        for person in self._get_people():
            knowers = self._graph.subjects(rdflib.URIRef('http://xmlns.com/foaf/0.1/knows'), person)
            if len(list(knowers)) == 0:
                self._me = person
                return
            
    # Things you can only reasonably have one of - gender, birthday, first name, etc. - are termed
    # "singletons".  Singletion I/O is handled purely through __getattr__ and __setattr__, below.
    def __getattr__(self, name):
        if name in _SINGLETONS:
            for raw in self._graph.objects(subject=self._me, predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name)):
                return unicode(raw)
            return None
        return Agent.__getattr__(self, name)
            
    def __setattr__(self, name, value):
        if name in _SINGLETONS:
            self._graph.remove((self._me, rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name), None))
            self._graph.add((self._me, rdflib.URIRef('http://xmlns.com/foaf/0.1/%s' % name), value))
        else:
            Agent.__setattr__(self, name, value)


    def _build_friend(self, raw_friend):
        if isinstance(raw_friend, rdflib.URIRef):
            return Person(unicode(raw_friend))
        elif isinstance(raw_friend, rdflib.BNode):
            # If a "seeAlso" gives us the URI of the friend's FOAF profile, use that
            for uri in self._graph.objects(subject=raw_friend, predicate=rdflib.URIRef("http://www.w3.org/2000/01/rdf-schema#seeAlso")):
                return Person(unicode(uri))
            # Otherwise just build a Person up from what we have
                f = Person()
                for (s,p,o) in self._graph.triples((raw_friend, None, None)):
                    f._graph.add((f._get_primary_topic(),p,o))
                return f 

    def _get_friends(self):
        for raw_friend in self._graph.objects(predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/knows')):
            friend = self._build_friend(raw_friend)
            if friend:
                yield friend
    friends = property(_get_friends)

    def add_friend(self, friend):
        x = rdflib.BNode()
        self._graph.add((self._me, rdflib.URIRef('http://xmlns.com/foaf/0.1/knows'), x))
        self._graph.add((x, rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), rdflib.URIRef('http://xmlns.com/foaf/0.1/Person')))
        if friend.name:
            self._graph.add((x, rdflib.URIRef('http://xmlns.com/foaf/0.1/name'), friend.name))
        if friend.homepage:
            self._graph.add((x, rdflib.URIRef('http://xmlns.com/foaf/0.1/homepage'), friend.homepage))
        for mbox in friend.mboxs:
            self._graph.add((x, rdflib.URIRef('http://xmlns.com/foaf/0.1/mbox'), mbox))
        for mbox_sha1sum in friend.mbox_sha1sums:
            self._graph.add((x, rdflib.URIRef('http://xmlns.com/foaf/0.1/mbox_sha1sum'), mbox_sha1sum))
        if friend.uri:
            self._graph.add((x, rdflib.URIRef("http://www.w3.org/2000/01/rdf-schema#seeAlso"), friend.uri))

    def _build_fast_friend(self, raw_friend):
        if isinstance(raw_friend, rdflib.URIRef):
            return Person(unicode(raw_friend))
        elif isinstance(raw_friend, rdflib.BNode):
            f = Person()
            for (s,p,o) in self._graph.triples((raw_friend, None, None)):
                f._graph.add((f._get_primary_topic(),p,o))
            return f 

    def _get_fast_friends(self):
        for raw_friend in self._graph.objects(predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/knows')):
            friend = self._build_fast_friend(raw_friend)
            if friend:
                yield friend
    fast_friends = property(_get_fast_friends)

    def _build_fastest_friend(self, raw_friend):
        if isinstance(raw_friend, rdflib.URIRef):
            return None
        elif isinstance(raw_friend, rdflib.BNode):
            f = Person()
            for (s,p,o) in self._graph.triples((raw_friend, None, None)):
                f._graph.add((f._get_primary_topic(),p,o))
            return f 

    def _get_fastest_friends(self):
        for raw_friend in self._graph.objects(predicate=rdflib.URIRef('http://xmlns.com/foaf/0.1/knows')):
            friend = self._build_fastest_friend(raw_friend)
            if friend:
                yield friend
    fastest_friends = property(_get_fastest_friends)

    # Serialisation
    def get_xml_string(self, format="rdf/xml"):
        return self._graph.serialize(format=format)

    def save_as_xml_file(self, filename, format="rdf/xml"):
        self._graph.serialize(filename, format=format)
