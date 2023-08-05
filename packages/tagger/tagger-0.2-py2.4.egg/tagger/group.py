from utils import any, all, nscollection, set_intersect, utcnow, implements

from dispatch_predicates import IS_GROUP

from tagger.tag import Tagger 

class TaggerContrained(Tagger):
    ns = nscollection()     
    isgroup = ns.tagger['taggroup']
    groupedby = ns.tagger['groupedBy']
    isrule = ns.tagger['Rule']

    def __init__(self, graph):
        self.graph = graph
        self.ns.bindAll(graph)

    # @dispatch.generic()
    # def removeRule(self, node, rule):
    #     "See tagger.interfaces.ITagger"

    # @dispatch.generic()
    # def setRule(self, node, rule):
    #     "See tagger.interfaces.ITagger"

    # @dispatch.generic()
    # def ruleApplies(self, node, rule):
    #     "See tagger.interfaces.ITagger"

    @dispatch.generic()
    def isGroup(self, id_):
        "See tagger.interfaces.ITagger"

    # @dispatch.generic()
    # def groupNodes(self, nodes, group=None, spec=None):
    #     "See tagger.interfaces.ITagger"

    # @dispatch.generic()
    # def ungroupNodes(self, nodes, group=None):
    #     "See tagger.interfaces.ITagger"

    @dispatch.generic()    
    def createRule(self, spec):
        "See tagger.interfaces.ITagger"

    # @groupNodes.when("not group")
    # def anon_groupNodes(self, nodes, group=None, spec=None):
    #     if not spec:
    #         spec = dict()
    #     group = BNode()
    #     self.graph.add((group, RDF.type, self.isgroup))
    #     add = self.graph.add
    #     [add((group, key, spec[key])) for key in spec.keys()]
    #     return self.groupNodes(nodes, group=group)

    # @groupNodes.when(strategy.default)
    # def group_groupNodes(self, nodes, group=None, spec=None):
    #     triples = ((node, self.groupedby, group) for node in nodes)
    #     self._addTriples(triples)
    #     return group

    # @isGroup.when(strategy.default)
    # def isGroupNode(self, id_):
    #     """ we have a bare node id """
    #     subj = self.graph.subjects(predicate=self.groupedby,
    #                                object=id_)
    #     return bool([x for x in subj])

    # @isGroup.when("self.get(id_)")
    # def isGroupId(self, id_):
    #     node = self.get(id_)
    #     if node:
    #         return self.isGroup(node)
    #     return False

    # @ungroupNodes.when("not group")
    # def allgroups_ungroupNodes(self, nodes, group=None):
    #     triples = []
    #     for node in nodes:
    #         sp = (node, self.groupedby)
    #         objs = self.graph.objects(subject=node, predicate=self.groupedby)
    #         [triples.append(sp + (ob,)) for ob in objs]
    #     self._removeTriples(triples)

    # @ungroupNodes.when("isinstance(group, str) or isinstance(group, unicode)")
    # def groupid_ungroupNodes(self, nodes, group=None):
    #     triples = [(node, self.groupedby, group) for node in nodes]
    #     self._removeTriples(triples)

    ##     @getTagsFor.when("self.isGroup(subject)")
##     @construct_getter(groupedby, body)
##     def _getTagsForGroup(self, subject):
##         """ all tags for a group """

    # @getGroupsFor.when(IS_TAG %'subject')
    # @construct_getter(annotates, groupedby)
    # def _getGroupsForTag(self, subject):
    #     """all groups for a tags (no intersections)"""

    # @getGroupsFor.when(IS_USER %'subject')
    # @construct_getter(authoredby, groupedby)
    # def _getGroupsForUser(self, subject):
    #     """all groups for a tags (no intersections)"""

    @getGroupsFor.when(strategy.default)    
    def _getGroupsForAssociations(self, subject):
        '''handles straight node ids'''
        node = self.get(subject)
        return self.graph.subjects(predicate=self.associated,
                                  object=node)
##    # rule handling

##     @createRule.when(strategy.default)
##     def _default_createRule(self, spec):
##         mapping = dict(label=RDFS.label,
##                        comment=RDFS.comment,
##                        id = RDF.ID)
##         newspec = {RDFS.subClassOf:self.isrule}
##         newspec[RDF.type]=self.ns.tagger[spec['klass']]
        
##         [newspec.update({val:spec[key]}) \
##          for key, val in mapping.items() if spec.has_key(key)]
        
##         return self.createRule(newspec)

    @createRule.when('isinstance(spec, dict)')
    def _dict_createRule(self, spec):
        subject = self.get_create(spec[RDF.ID])
        triples = self._to_triples(spec, subject=subject)
        if subject:
            self._addTriples(triples, set=True)
        else:
            self._addTriples(triples)
            subject = triples[0][0]
        return subject

    # @ruleApplies.when(strategy.default)
    # def _default_ruleApplies(self, node, rule):
    #     test = self.graph.value(predicate=self.appliesto, object=node)
    #     return  rule == test

    # @setRule.when(strategy.default)
    # def _default_setRule(self, node, rule):
    #     # self.graph.set((rule, self.appliesto, node)) # broken in rdflib
    #     self.graph.add((rule, self.appliesto, node)) 

    # @removeRule.when(strategy.default)
    # def _default_removeRule(self, node, rule):
    #     self.graph.remove((rule, self.appliesto, node))

    @dispatch.generic()
    def getGroupsFor(self, subject):
        "See tagger.interfaces.ITagger"
