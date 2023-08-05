    >>> import pdb; st = pdb.set_trace

========
 tagger
========

"tag:: A stylized signature, normally done in one color. The simplest
    and most prevalent type of graffiti, a tag is often done in a
    color that contrasts sharply with its background. Tag can also be
    used as a verb meaning "to sign". Writers often tag on or beside
    their pieces, following the practice of traditional artists who
    sign their artwork. "

From Wikipedia, the free encyclopedia

Introduction
============

tagger is a python package for rdf based taxonomy/folksonomy tools,
based around the use of annotations to describe "tags".  It utilizes
existing namespaces(FOAF, Annotea) to create a system for managing and
applying tags in building folksonomies.

Put most simply the Tagger class wraps rdflib's ConjunctiveGraph.  

    >>> from tagger.tag import Tagger
    >>> from rdflib import ConjunctiveGraph as Graph
    >>> g = Graph()
    >>> tagger=Tagger(g)
    >>> item, user1 = 'item1_id', 'user1'
    >>> nodes = tagger.tag_item(item, user1, ['bongo', 'java', 'smoothie', 'bongo'])
    >>> len(nodes) == 3
    True

Now let's see the tags on the item.  The getters are generic
functions; they automatically determine whether an id belongs to a
user or a tag::

    >>> tagger.items_for_tag('bongo')
    set(['item1_id'])
    
    >>> tagger.items_for_user('user1')
    set(['item1_id'])

    >>> tagger.tags_for_user('user1') == set(['bongo', 'java', 'smoothie'])
    True

    >>> tagger.tags_for_item('item1_id') == set(['bongo', 'java', 'smoothie'])
    True

    >>> tagger.users_for_item('item1_id')
    set(['user1'])

    >>> tagger.users_for_tag('smoothie')
    set(['user1'])

    >>> tagger.delete_tag(item, user1, 'java')

    >>> tagger.tags_for_user('user1') == set(['smoothie', 'bongo'])
    True

Now lookups for java should return nothing::

    >>> tagger.users_for_tag('java')
    set([])

    >>> tagger.count('java')
    0


Now let's try some more deletions.  this will remove all annotations
for this item (all that are currently stored in fact)::

    >>> tagger.delete(item)
    >>> tagger.users_for_tag(item)
    set([])

Likewhise, all triples are not referenced by other content should
also be removed::

    >>> print tagger._xml()
    <?xml version="1.0" encoding="utf-8"?>
    <rdf:RDF
      xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    />

Now let's try something fancier::

    >>> item2 = "item2"
    >>> user2 = "user2"
    >>> user3 = "user3"
    >>> nodes = tagger.tag_item(item2, user2, ['wow'])
    >>> nodes = tagger.tag_item(item2, user3, ['wow'])
    >>> tagger.users_for_tag('wow') == set((user2, user3))
    True

    >>> tagger.users_for_tag('wow') == tagger.users_for_item(item2)
    True

    >>> nodes = tagger.tag_item(item, user2, ['wow'])
    >>> tagger.getItemsFor('wow') == set((item, item2))
    True

Now that we have some tags loaded, let's test the intersection
methods. first, the count method::

    >>> tagger.count(tag='wow')
    3
    
    >>> tagger.count(tag='wow', user=user2)
    2

    >>> tagger.count(user=user1, tag='wow')
    0

    >>> tagger.count(item=item2, tag='wow')
    2

    >>> nodes = tagger.tag_item(item2, user2, ['krazy', 'crunk'])

The intersection method itself::

    >>> tagger.intersect(item2, user2) == set(['wow', 'krazy', 'crunk'])
    True

    >>> tagger.intersect(item2, user3)
    set(['wow'])


Filtering
---------

To facilitate interaction with other systems, tagger allows for
additional triples to be added when creating annotation. Likewhise,
all queries accept an argument `spec`, a set of predicates and
objects that can be used to limit a return set.

for example, we can create a node representing a category in the tagger
namespace and add a tag with this ::

    >>> from rdflib import Literal, RDF
    >>> iscategory = tagger.ns.tagger['category']
    >>> groupid = tagger._create('Group1', (RDF.type, iscategory))
    >>> of_category = tagger.ns.tagger['of-category']
    >>> t = tagger.tag_item(item2, user2, ['bucket'], spec=((of_category, groupid),))

'groupinfo' could also be passed as a dictionary(if the method is not memoized)::

    >>> t = tagger.tag_item(item2, user2, ['pail'], spec={of_category: groupid})
    >>> control = tagger.tag_item(item, user1, ['pail', 'bucket'])

Then results may be filtered for the group::

    >>> tagger.getTagsFor(user2, spec={of_category:groupid})
    set(['bucket', 'pail'])

    >>> tagger.getItemsFor('pail', spec={of_category:groupid})
    set(['item2'])

    >>> tagger.intersect(item2, user2, spec=((of_category,groupid),))
    set(['bucket', 'pail'])

Queries also accept tuples of triples to extend queries. How a query
may be extended depends on the query itself.  For example, we'll look
up all the tags for item2 that are in the category defined by the the
id 'Group1'.  `getTagsFor` uses a `_bridge_query` that looks like this:

select = "?return"
t1 = ("?a", ipred, node)
t2 = ("?a", rpred, "?target")
t3 = ("?target", RDF.ID, "?return")

We can create a helper function that takes a human readable id and a
predicate to format a tuple of triples to allow us to query tags by
group id (for all tagger queries, '?a' represents the annotea
annotation)::

    >>> def specifier(id_, pred, var="?bbb"):
    ...     return ((var, RDF.ID, Literal(id_)),
    ...             ('?a', pred, var))

    >>> t=tagger.tag_item(item2, user2, ['monkies'], spec={of_category:groupid})
    >>> tagger.getTagsFor(item2, spec=specifier('Group1', of_category))
    set(['bucket', 'monkies', 'pail'])

We can add a simple access rule to the 'monkies' annotation, and
constrain the return further::

    >>> is_access_rule = tagger.ns.tagger['access-rule']
    >>> has_rule = tagger.ns.tagger['has-access-rule']
    >>> tagger._create('restricted', spec=(RDF.type, is_access_rule))
    u'...'

Before we add the rule, nothing should come back::

    >>> spec = specifier('restricted', has_rule, '?rule') + specifier('Group1',of_category)
    >>> tagger.getTagsFor(item2, spec=spec)
    set([])

After adding the rule to the annotation, we should get some monkies::

    >>> mid = tuple(tagger.annotations(tag="monkies"))[0]
    >>> ('monkies', mid) in t
    True

    >>> rule = tagger.get('restricted')
    >>> tagger.graph.add((mid, has_rule, rule))
    >>> tagger.getTagsFor(item2, spec=spec)
    set(['monkies'])


Deletion
--------

Let's makes sure delete only deletes what it is suppose to::

    >>> tagger.delete(item2)
    >>> tagger.tags_for_item(item2)
    set([])

    >>> tagger.delete(item)
    >>> tagger.tags_for_item(item)
    set([])

    >>> print tagger._xml()
    <?xml version="1.0" encoding="utf-8"?>
    <rdf:RDF
      xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    />

    >>> len(g)
    0

