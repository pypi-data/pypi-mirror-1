"""pluggable mixins for the Cubicweb classification schemes package

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


try:
    from cubicweb.web import FACETTES
except ImportError:
    # cubicweb.web not available
    pass
else:
    from cubicweb.common import mixins

    def kwvocab_from_rset(rset):
        vocabbyscheme = {}
        for e in rset.entities():
            # take care, rset may contains entities which are not Keyword
            try:
                svocab = vocabbyscheme.setdefault(e.classification, [])
            except AttributeError:
                continue
            svocab.append( (e.eid, e.view('combobox')) )
        vocab = []
        for i, (scheme, svocab) in enumerate(vocabbyscheme.iteritems()):
            vocab += sorted(svocab, key=lambda x: x[1])
            if i < len(vocabbyscheme) - 1:
                # insert separators
                vocab.append( (None, '----') )
        return  'eid', vocab

    FACETTES.add( ('applied_to', 'object', 'name', kwvocab_from_rset) )


    class ClassifiableMixIn(object):
        """base mixin providing helper methods for classifiable entities.
        This mixin will be automatically set on class supporting the 'applied_to'
        object relation
        """
        def filterform_vocabulary(self, rtype, x, var, rqlst, args, cachekey):
            """vocabulary method controling generic table filter form

            see AnyEntity.filterform_vocabulary docstring for more information
            """
            from cubicweb.web.views.searchrestriction import insert_attr_select_relation
            if x == 'object' and rtype == 'applied_to':
                rql = insert_attr_select_relation(rqlst, var, rtype, 'name')
                rset = self.req.execute(rql, args, cachekey)
                return kwvocab_from_rset(rset)
            return super(ClassifiableMixIn, self).filterform_vocabulary(
                rtype, x, var, rqlst, args, cachekey)

    mixins.MI_REL_TRIGGERS[('applied_to', 'object')] = ClassifiableMixIn
