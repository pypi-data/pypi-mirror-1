from interfaces import ITagger, AnnotationNotFoundError

from rdflib import Graph
from rdflib import BNode, URIRef, Namespace, RDFS, RDF, Literal

from rdflib.sparql.graphPattern import GraphPattern
from rdflib.sparql.sparqlGraph import SPARQLGraph
from utils import any, all, nscollection, set_intersect, utcnow, implements

import dispatch
import memojito

from dispatch import strategy
from dispatch_predicates import IS_TAG, IS_USER, IS_ITEM,  ITEM_USER

class Tagger(object):
    __doc__ = ITagger.__doc__ 

    implements(ITagger)

    ns = nscollection()

    ns.tagger = Namespace(u"http://xmlns.openplans.org/tagger#")
    ns.annotea = Namespace(u'http://www.w3.org/2000/10/annotation-ns#')
    ns.dc = Namespace(u'http://purl.org/dc/elements/1.1/')
    ns.foaf = Namespace(u"http://xmlns.com/foaf/0.1/")

    annotates = ns.annotea['annotates']
    annotation = ns.annotea['Annotation']
    authoredby = ns.annotea['author']
    body = ns.annotea['body']
    created = ns.annotea['created']
    modified = ns.annotea['modified']

    isperson = ns.foaf['Person']
    istag = ns.foaf['topic']
    iscontent = ns.tagger['Content']
    
    tags = ns.dc['subject']
    related = ns.annotea['related']

    appliesto = ns.tagger['appliesTo']
    associated = ns.tagger['associated']

    def __init__(self, graph):
        self.graph = graph
        self.ns.bindAll(graph)
        
    @property
    def sparql(self):
        return SPARQLGraph(self.graph)

    def query(self, select, where):
        return self.sparql.query(select, GraphPattern(where))

    @memojito.clearafter
    def tag_item(self, item, user, tags, spec=None):
        anodes = []
        for tag in tags:
            ritem = self.get_create(item, spec=(RDF.type, self.iscontent))
            rauthor = self.get_create(user, spec=(RDF.type, self.isperson))
            rbody = self.get_create(tag, spec=(RDF.type, self.istag))
            anodes.append(self._annotate(ritem, rauthor, rbody, spec=spec))
        return set(tuple(zip(tags, anodes)))

    def delete_tag(self, item, user, tag):
        "See tagger.interfaces.ITagger"
        ritem = self.get(item)
        rauthor = self.get(user)
        rbody = self.get(tag)

        iut = [ritem, rauthor, rbody]
        if not self._any(iut): # tag non-existent
            return
        
        if not self._all(iut):
            iut = dict(zip(('item', 'user', 'tag'), iut))
            raise "pathological storage mismatch (missing data): %s" %iut

        result = self._lookup_annotation(ritem, rauthor, rbody) 
        assert result, AnnotationNotFoundError("No annotations for %s %s %s" %(item, user, tag))
        annotation = result[0]
        tails = self.graph.predicate_objects(subject=annotation)
        triples = ((annotation,) + tail for tail in tails)
        self._remove_triples(triples, reap=True)

    def delete(self, obj):
        "See tagger.interfaces.ITagger"
        node = self.get(obj)
        subjects = list(self.annotations_by(obj))
        subjects.append(node)

        triples = []
        [triples.extend(self._by_subject(node)) \
         for node in subjects]
        
        self._remove_triples(triples, reap=True)

    def count(self, tag=None, user=None, item=None):
        return len(self.annotations(tag=tag, user=user, item=item))

    @memojito.memoize
    def is_rdf_type(self, id_, predicate):
        """ finds where """
        node = self.get(id_)
        if node:
            preds = (x for x in self.graph.predicates(object=node))
            return predicate in preds

    # generic getter declarations
    #
    # these may be extended in the conventional fashion(subclassing)
    # or imported and extended by predicate. for example:
    #
    # @Tagger.getItemsFor.when("subject=='yo momma'")
    # def myNewExtension(self, subject, ...
        
    @dispatch.generic()
    def get_id(self, identifier):
        "See tagger.interfaces.ITagger"

    @dispatch.generic()
    def getItemsFor(self, subject, spec=None):
        "See tagger.interfaces.ITagger"
        
    @dispatch.generic()
    def getTagsFor(self, subject, spec=None):
        "See tagger.interfaces.ITagger"
    
    @dispatch.generic()
    def getUsersFor(self, subject, spec=None):
        "See tagger.interfaces.ITagger"

    @dispatch.generic()
    def annotations(self, tag=None, user=None, item=None, spec=None):
        "See tagger.interfaces.ITagger"

    @dispatch.generic()
    def annotations_by(self, subject, spec=None):
        "See tagger.interfaces.ITagger"

    @dispatch.generic()
    def intersect(self, s1, s2, spec=None):
        "See tagger.interfaces.ITagger"
        
    @dispatch.generic()
    def _to_triples(self, spec, subject=None):
        """
        coerces object into rdfish triples 
        """

    @get_id.when("self._any([isinstance(identifier, unicode), isinstance(identifier, str), isinstance(identifier, int)])")
    def _get_id_str(self, identifier):
        return Literal(identifier)
    
    @memojito.memoize    
    def get(self, obj):
        id_ = self.get_id(obj)
        rdfid = self.graph.value(predicate=RDF.ID, object=id_)
        return rdfid

    def _create(self, obj, spec=None):
        identifier = self.get_id(obj)
        rdfid = BNode()
        triples = []
        if spec:
            triples = self._to_triples(spec, subject=rdfid)
        triples += (rdfid, RDF.ID, identifier),
        [self.graph.add(triple) for triple in triples]
        return rdfid

    @memojito.memoize    
    def get_create(self, obj, spec=None, create=False):
        identifier = self.get_id(obj)
        rdfid = self.get(identifier)
        if not rdfid:
            predicate, object_ = None, None
            rdfid = self._create(identifier, spec=spec)
        return rdfid

    # annotations

    @annotations.when(strategy.default)
    def _all_annotations(self, tag=None, user=None, item=None):
        return set(self.graph.subjects(predicate=RDF.type, object=self.annotation))

    @annotations.when("self._any((tag, user, item))")
    def _annotation_intersection(self, tag=None, user=None, item=None, spec=None):
        """@return: all annotations for an intersection """
        a_by = self.annotations_by
        node_sets = []
        for obj in (tag, user, item,):
            if obj:
                anodes = a_by(obj)
                node_set = anodes and set(anodes) or set()
                node_sets.append(node_set)
        if node_sets:
            return reduce(self._set_intersect, node_sets)

    # intersections

    @intersect.when(ITEM_USER %('s1', 's2'))
    @memojito.memoize
    def _user_item_intersection(self, s1, s2, spec=None):
        ritem = self.get(s1)
        rauthor = self.get(s2)

        gettags = "?tag"
        where =[("?a", RDF.type, self.annotation),
                 ("?a", self.authoredby, rauthor),
                 ("?a", self.annotates, ritem),
                 ("?a", self.body, "?tagid"),
                 ("?tagid", RDF.ID, "?tag"),]

        if spec:
            where.extend(self._to_triples(spec, subject='?a'))

        literals = self.query(gettags, list(where))
        tags=[str(literal) for literal in literals]
        return set(tags)

    @intersect.when(strategy.default)
    def _nullintersection(self, s1, s2, spec=None):
        return set()

    # query shortcuts

    def _bridge_query(self, node, ipred, rpred, spec=None):
        """
        find all of ids for all objects of 'rpred'-icate in
        annotations node is object of 'ipred'-icate

        @param node: known node inside an annotation
        @type node: uri
 
        @param ipred: predicate of interest
        @type ipred: uri

        @param rpred: predicate of desire return
        @type rpred: uri
        """
        select = "?return"
        t1 = ("?a", ipred, node)
        t2 = ("?a", rpred, "?target")
        t3 = ("?target", RDF.ID, "?return")
        pattern = [t1, t2, t3]
        if spec:
            pattern.extend(self._to_triples(spec, subject="?a"))
        return self.query(select, pattern)

    def construct_getter(ipred, rpred):
        """
        a function factory for our generic function dispatchies

        used to create single return functions(all of x for (y))

        @param ipred: predicate of interest
        @type ipred: uri

        @param rpred: predicate of desire return
        @type rpred: uri
        """
        def wrapper(f):
            def surrogate(self, subject, spec=None):
                node = self.get(subject)
                if not node and isinstance(subject, unicode):
                    node = subject
                literals = self._bridge_query(node, ipred, rpred, spec)
                return set([str(literal) for literal in literals])        
            surrogate.__name__ = f.__name__
            surrogate.__doc__ = f.__doc__
            return surrogate
        return wrapper

    def construct_annotation_by(pred):
        def wrapper(f):
            def surrogate(self, subject, spec=None):
                node = self.get(subject)
                select = "?a"
                pattern = [("?a", pred, node)]
                if spec:
                    pattern.extend(self._to_triples(spec, subject="?a"))
                return self.query(select, pattern)
            surrogate.__name__ = f.__name__
            surrogate.__doc__ = f.__doc__
            return surrogate
        return wrapper

    # register default functions for when no generic matches the
    # subject

    for gen in (getTagsFor, getUsersFor, getItemsFor, annotations_by):
        gen.when(strategy.default)(lambda self, subject, spec=None: set())

    # -- apply constructor, register generics --

    @annotations_by.when(IS_TAG %'subject')
    @construct_annotation_by(body)
    def _all_annotations_for_tag(self, subject, spec=None):
        """@return all annotations for a tag """

    @annotations_by.when(IS_ITEM %'subject')
    @construct_annotation_by(annotates)
    def _all_annotations_for_item(self, subject, spec=None):
        """@return all annotations for a tag """

    @annotations_by.when(IS_USER %'subject')
    @construct_annotation_by(authoredby)
    def _all_annotations_for_user(self, subject, spec=None):
        """@return all annotations for a tag """

    @getItemsFor.when(IS_TAG %'subject')
    @construct_getter(body, annotates)
    def _get_items_for_tag(self, subject, spec=None):
        """ returns id for items tags by string:subject """

    @getItemsFor.when(IS_USER %'subject')
    @construct_getter(authoredby, annotates)
    def _get_items_for_user(self, subject, spec=None):
        """ for item for user id """

    @getUsersFor.when(IS_TAG %'subject')
    @construct_getter(body, authoredby)
    def _users_for_tag(self, subject, spec=None):
        """ for item for user id """

    @getUsersFor.when(IS_ITEM %'subject')
    @construct_getter(annotates, authoredby)
    def _get_users_for_item(self, subject, spec=None):
        """ for item for user id """

    @getTagsFor.when(IS_ITEM %'subject')
    @construct_getter(annotates, body)
    def _get_tags_for_item(self, subject, spec=None):
        """ for item for user id """

    @getTagsFor.when(IS_USER %'subject')
    @construct_getter(authoredby, body)
    def _get_tags_for_user(self, subject, spec=None):
        """ for item for user id """

    # utility methods

    _set_intersect = staticmethod(set_intersect)
    _any=staticmethod(any)
    _all=staticmethod(all)

    def _xml(self):
        """
        for testing 
        """
        return self.graph.serialize(format='pretty-xml')

    def _lookup_annotation(self, ritem, rauthor, rbody, spec=None):
        select=("?a",)
        t1 = ("?a", self.annotates, ritem)
        t2 = ("?a", self.authoredby, rauthor)
        t3 = ("?a", self.body, rbody)
        where = [t1, t2, t3]
        if spec:
            where.extend(self._to_triples(spec, subject='?a'))
        return self.query(select, where)

    def _add_modtime_if_dup(_annotate):
        """
        this decorator does a conversion from identifiers to nodes for
        item, author and body and abstracts the short-circuit logic
        for preventing duplicate annotations.

        if a dup is found, a new modtime is added.
        """
        def _annwrapper(self, item, author, body, spec=None):
            now = Literal(utcnow())
            result = self._lookup_annotation(item, author, body)
            if result:
                annotation = result[0]
                t = (result[0], self.modified, now)
                self.graph.add(t)
                return annotation
            return _annotate(self, item, author, body, now, spec=spec)
        return _annwrapper

    @_add_modtime_if_dup
    def _annotate(self, item, author, body, when, spec=None):
        """ expects pure rdf """
        annotation = BNode()
        triples = ((annotation, RDF.type, self.annotation),
                   (annotation, self.annotates, item),
                   (annotation, self.authoredby, author),
                   (annotation, self.body, body),
                   (annotation, self.created, when))

        self._add_triples(triples)
        if spec:
            triples = self._to_triples(spec, subject=annotation)
            for triple in triples:
                self.graph.add(triple) 
        return annotation

    @_to_triples.when("isinstance(spec, tuple) and len(spec) and not isinstance(spec[0], tuple)")
    def _tuple_len2_to_triple(self, spec, subject=None):
        return self._to_triples((spec,), subject=subject)

    @_to_triples.when("isinstance(spec, tuple) and len(spec) and len(spec[0])==3")
    def _tuple_len3_to_triple(self, spec, subject=None):
        return spec

    @_to_triples.when("isinstance(spec, tuple) and len(spec) and len(spec[0])==2")
    def _tuplelist_len2_to_triple(self, spec, subject=None):
        if not subject:
            subject = BNode()
        return [(subject, p, o) for p, o in spec]
    
    @_to_triples.when("isinstance(spec, list)")
    def _list_to_triples(self, spec, subject=None): 
        return self._to_triples(tuple(spec), subject=subject)       

    @_to_triples.when("isinstance(spec, dict)")
    def _dict_to_triples(self, spec, subject=None): 
        """
        converts a dict of pred/obj pairs to a triple
        @param spec: set of predicates and object
        @type spec: dict
        @param subject: node 
        @type subject: string
        """
        return self._to_triples(tuple(spec.items()), subject=subject)

    @memojito.clearafter
    def _add_triples(self, triples, set=False):
        add = self.graph.add
        if set:
            add = self.graph.set
        [add(t) for t in triples]

    @memojito.clearafter
    def _remove_triples(self, triples, reap=True):
        for t in triples:
            self.graph.remove(t)
            rdfid = self.get(t[2])
            if reap and rdfid:
                self._reap(rdfid)

    def _reap(self, id_=None):
        gr = self.graph
        remove = gr.remove

        preds = len([True for x in gr.predicates(object=id_)])
        if not preds:
            orphans = gr.predicate_objects(subject=id_)
            for pred, obj in orphans:
                remove((id_, pred, obj)) 
                self._reap(obj)

    def _by_subject(self, node):
        get_tails = self.graph.predicate_objects
        return [(node,) + tail for tail in get_tails(subject=node)]



