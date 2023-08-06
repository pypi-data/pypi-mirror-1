"""skillmat boxes

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import implements, match_user_groups

from cubicweb.web.box import EditRelationBoxTemplate


class EditWishesBox(EditRelationBoxTemplate):
    __regid__ = 'edit-wishes'
    __select__ = (EditRelationBoxTemplate.__select__
                  & implements('CWUser') & match_user_groups('owners'))

    rtype = 'wishes_to_learn'
    target = 'object'

    def unrelated_entities(self, euser):
        """filter skills for which the user already knows"""
        entities = super(EditWishesBox, self).unrelated_entities(euser)
        mastered = set(entity.eid for entity in euser.mastered_skills())
        return [entity for entity in entities if entity.eid not in mastered]


class EditAttendedByBox(EditRelationBoxTemplate):
    __regid__ = 'edit-attended-by'
    __select__ = EditRelationBoxTemplate.__select__ & implements('Talk')

    rtype = 'attended_by'
    target = 'object'

    ## Todo : replace + et - in this box by a comprehensive label

  #   def w_related(self, box, entity):
#         """appends existing relations to the `box`"""
#         rql = 'DELETE S %s O WHERE S eid %%(s)s, O eid %%(o)s' % self.rtype
#         related = self.related_entities(entity)
#         for etarget in related:
#             box.append(self.box_item(entity, etarget, rql, u'assiste'))
#         return len(related)
    
#     def w_unrelated(self, box, entity):
#         """appends unrelated entities to the `box`"""
#         rql = 'SET S %s O WHERE S eid %%(s)s, O eid %%(o)s' % self.rtype
#         for etarget in self.unrelated_entities(entity):
#             box.append(self.box_item(entity, etarget, rql, u'n\'assite pas'))
  
   
