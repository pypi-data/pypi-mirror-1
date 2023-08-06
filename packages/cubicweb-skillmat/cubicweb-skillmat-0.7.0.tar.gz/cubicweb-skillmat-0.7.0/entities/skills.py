"""eskilmat specific entities

:organization: Logilab
:copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.decorators import cached

from cubicweb.mixins import TreeMixIn
from cubicweb.interfaces import ICalendarable
from cubicweb.entities import AnyEntity

from cubes.folder.entities import Folder
from cubes.skillmat.interfaces import ISkill

class Masters(AnyEntity):
    __regid__ = 'Masters'
    fetch_attrs = ('rate', 'foruser', 'skill')

    def dc_title(self):
        return u'%s: %s' % (self.skill[0].name, self.rate)

    def dc_long_title(self):
        return u'%s / %s' % (self.foruser[0].dc_title(), self.dc_title())


class Technology(TreeMixIn, AnyEntity):
    __regid__ = 'Technology'
    __implements__ = (ISkill,)
    fetch_attrs = ('name',)
    tree_attribute = 'filed_under'

    def skill_categories(self):
        # XXX what if we have a skill tree with depth > 1
        return self.filed_under


class Skill(Folder):
    __implements__ = (ISkill,)

    def skill_categories(self):
        return [self]

class Talk(AnyEntity):
    __regid__ = 'Talk'
    __implements__ = (ICalendarable,)
    fetch_attrs = ('subject', 'description', 'talktime')

    def dc_title(self):
        return u'%s' % (self.subject)

    @property
    def start(self):
        return self.talktime

    @property
    def stop(self):
        return self.talktime
