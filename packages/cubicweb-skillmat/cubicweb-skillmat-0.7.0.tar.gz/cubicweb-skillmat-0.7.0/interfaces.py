"""skillmat interfaces"""

from logilab.common.interface import Interface

class ISkill(Interface):
    """base interface for Technology / Skill"""
    
    def skill_categories(self):
        """returns skill's categories"""

