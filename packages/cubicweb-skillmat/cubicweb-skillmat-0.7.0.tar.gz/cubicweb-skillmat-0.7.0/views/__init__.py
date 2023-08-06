"""template-specific forms/views/actions/components"""
from cubicweb.web import uicfg
from cubicweb.web.formfields import IntField

from cubes.skillmat.entities.base import SKILLS

RATEVOCAB = [(l, unicode(v)) for v, l in sorted(SKILLS.items())]
uicfg.autoform_field_kwargs.tag_attribute(
    ('Masters', 'rate'),
    {'choices': RATEVOCAB,
     'internationalizable': True})

uicfg.autoform_section.tag_subject_of(('Talk', 'attended_by', '*'), 'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('Talk', 'attended_by', '*'), 'muledit', 'attributes')
