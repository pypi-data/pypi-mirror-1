from django import template
from object_links.models import Menu
from django.template import Node
register = template.Library()

def get_menu(parser, token):
    bits = token.contents.split()
    return MenuNode(bits[1], bits[3])

class MenuNode(Node):
    def __init__(self, menu_name, varname):
        self.menu_name = menu_name
        self.varname = varname
        
    def render(self, context):
        context[self.varname] = Menu.objects.get(key=self.menu_name)
        return ''

get_menu = register.tag(get_menu)
    
#-----------
def display_menu(context, menu_name):
    menu = Menu.objects.get(key=menu_name)
    page = ''
    section = ''
    try:
        page = context['page']
        section = page.section
    except:
        pass
    return {'links': menu.links.all(), 'menu': menu, 'page':page, 'section':section}

display_menu = register.inclusion_tag('object_links/menu_display.html', takes_context=True)(display_menu)
        
