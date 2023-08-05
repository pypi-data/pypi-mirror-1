from utils import Interface, Attribute

class AnnotationNotFoundError(Exception):
    """Requested annotation not found in store"""

class ITaggable(Interface):
    """
    entity that can be tagged
    """
    identifier = Attribute("a unique identifier in operative tagging scenario."\
                           "May be the tag itself")

class ITag(ITaggable):
    """
    entity that represents a tag
    """

class IUser(ITaggable):
    """
    entity that can tag
    """

class IItem(ITaggable):
    """
    entity that can be tagged
    """

class ITagger(Interface):
    """
    Utility class for adding, removing, and updating tags as
    annotations to a graph.

    A tag is an annotation represented by a string literal
    """
    
    ns = Attribute("collection of namespaces used by tagger")

    # shorthands for often used URIs

    # URIs used as active predicates(relationships)
    annotates = Attribute("URI for annotation relationship")
    authoredby = Attribute("URI for author relationship")
    identifies = Attribute("URI for canonical identification")

    # URIs used as passive predicates(identity)
    isannotation = Attribute("URI for annotation type")
    isbody = Attribute("URI for annotea:body type")
    isperson = Attribute("URI for person type")
    istag = Attribute("URI for tag type")
    tags = Attribute("URI for tagging relationship")
    
    def __init__(graph):
        """ @param graph: rdflib graph for tagging """

    def _annotate(item, author, body, context, related=None):
        """
        adds a annotation to the graph

        basic interface for annotation using Annotea Namespace

        @param item: item annotated
        @param author: person doing the annotating
        @param body: annotation itself
        @type body: resource
        @param context: context that annotation is active in
        @type related: tuple of type and resource for
                       subclass of annotea:related
        @param related: generic pointer to other resources
        """

    def getById(identifier, type_=None, context=None, create=True):
        """
        Retrieves a node from a graph, creating one if needs

        @param identifier: unique identifier
        @param type_: optional type for node creation
        @return uri for node for identifier
        """

    def _addTag(tag):
        """adds new tag to graph"""

    def _reap(tag):
        """ remove tag from graph if it is orphaned """
        
    def tagItem(item, tags, user, context, related=None):
        """
        retrieves or creates tags and applies it for all appropriate
        contexts
        """

    def delItemUserTag(item, user, tag, context=None):
        """ remove a tag from an item """

    def delete(obj, context=None):
        """
        removes all annotations for a tag, item or user
        
        @param obj: user, item, or tag
        @type obj: str identifier
        """
        
    def count(tag=None, user=None, item=None, context=None):
        """
        returns count for intersection
        """

    def getItemsFor(subject, context):
        """
        @rtype: list
        @return: tag uris
        """

    def getTagsFor(subject, context):
        """
        @rtype: list
        @return: tag uris
        """

    def getUsersFor(subject, context):
        """
        returns a list of user uris
        """
    
    def isGroup(id_, context=None):
        """ determines if an id is a group or not """
    
    def groupNodes(nodes, group=None, spec=None, context=None):
        """add 1-N tags to a group"""
    
    def ungroupNodes(nodes, group=None, context=None):
        """remove 1-N tags from a group or all groups"""
        
    def createRule(spec, context=None):
        """ create a rule to be interpretted by external system"""

    def setRule(node, rule, context=None):
        """set rule on node for later interpretation"""
    
    def removeRule(node, rule, context=None):
        """ remove rule from rdf node"""

    def ruleApplies(node, rule, context=None):
        """
        checks if rule applies to node
        
        @return boolean
        """
    
    def annotations(tag=None, user=None, item=None, context=None):
        """ annotations by intersection """
    
    def annotations_by(subject, context=None):
        """@return all annotations for a subject """
    
    def intersect(s1, s2, context=None):
        """
        generic 2 dimension intersection (in IUT order)::
        
        item, user >> all tags for user & item
        user, tag >> all items for user & tag
        item, tag >> all users for item & tag

        nonimplemented permutations::

        tag, tag  >> all users and items shared by both tags
        item, item >> all tags and users shared by both items
        user, user >> all tags and items shared by both users

        tag, RDF.type >> all ids for all type tagged with tag

        what the s1 and s2 represent in the graph and/or context
        determines typing. further permutations could occur by
        dispatch upon type of s1 and s2 for objects provided
        dispatched function converted objects to identifiers readable
        by self.getById
        """
    
    def getById(identifier, spec=None, context=None, create=False):
        """
        get a node by it's identifier

        *method is ruledispatch extensible*
        
        @param create: flag for autocreation of resource if resource
        not found
        @param create: boolean
        
        @param spec: rdf predicate and object for new node created
        @type spec: tuple
        """
