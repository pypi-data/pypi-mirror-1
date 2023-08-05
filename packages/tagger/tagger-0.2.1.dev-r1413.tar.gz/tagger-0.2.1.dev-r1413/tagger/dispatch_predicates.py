"""
tagger.Tagger depends on a number of string predicates used by
RuleDispatch to determine identity of string arguments. These
predicates have been collected here for cleanliness.
"""
IS_TAG = "self.is_rdf_type(%s, self.body)"
IS_USER = "self.is_rdf_type(%s, self.authoredby)"
IS_ITEM = "self.is_rdf_type(%s, self.annotates)"
ITEM_USER = '%s and %s' %(IS_ITEM, IS_USER)
IS_GROUP = "self.isGroup(%s)"
