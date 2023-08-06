from django import template

from djangohelpers.templatetags import TemplateTagNode
from staticblocks.models import StaticBlock

class GetStaticBlock(TemplateTagNode):

    noun_for = {"for":"name"}

    def __init__(self, varname, name):
        TemplateTagNode.__init__(self, varname, name=name)

    def execute_query(self, name):
        try:
            return StaticBlock.objects.get(name=name)
        except StaticBlock.DoesNotExist:
            return ''


register = template.Library()
register.tag('get_static_block', GetStaticBlock.process_tag)

