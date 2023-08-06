"""base entities extension for skillmat

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from datetime import date, timedelta

from cubicweb.entities import authobjs


SKILLS = {0 : _("I don't want to learn this technology"),
          1 : _('I know nothing about this technology'),
          2 : _('Just beginning whith this technology'),
          3 : _('I start on this technology, and I can help'),
          4 : _('I am doing well, selfworking'),
          5 : _('I can conduct a training course')}


class SkillmatCWUserMixIn(object):

    def skill_info(self, skillname):
        rset = self._cw.execute('Any M,R WHERE M is Masters, M rate R, M foruser U, '
                                'M skill S, S name %(name)s, U eid %(u)s',
                                {'name': skillname, 'u': self.eid})
        if rset:
            return rset.get_entity(0, 0)
        return None

    def add_masters_url(self, skilleid, **kwargs):
        linkto = ('foruser:%s:subject' % self.eid,
                  'skill:%s:subject' % skilleid)
        return self._cw.build_url('add/Masters', __linkto=linkto, **kwargs)

    def mastered_skills(self, threshold=5):
        """return the list of mastered skills
        """
        rql = 'Any S,N WHERE M skill S, S name N, M rate >= %(r)s, M foruser U, U eid %(u)s'
        rset = self._cw.execute(rql, {'r': threshold, 'u': self.eid})
        return rset.entities()

class SkillmatCWUser(SkillmatCWUserMixIn, authobjs.CWUser):
    pass
