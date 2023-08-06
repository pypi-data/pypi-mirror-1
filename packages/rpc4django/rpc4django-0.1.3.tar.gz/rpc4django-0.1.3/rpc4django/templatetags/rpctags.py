'''
RPCTags
-------

Creates a template tag that can handle restructured text

`reST <http://docutils.sourceforge.net/rst.html>`_ format
'''

from django import template
from django.utils.safestring import mark_safe

# all custom tag libraries must have this
register = template.Library()

def resttext(text):
    '''
    Returns the passed text in 
    `reST <http://docutils.sourceforge.net/rst.html>`_ format
    '''
    
    overrides = {
        'inital_header_level' : 3,
        'report_level': 5,   # 0 reports everything, 5 reports nothing
    }
    
    try:
        from docutils.core import publish_parts
        parts = publish_parts(source=text, writer_name='html', \
                              settings_overrides=overrides)
        return mark_safe(parts['fragment'])
    except ImportError:
        return text
    
resttext.is_safe = True
register.filter('resttext', resttext)
