'''ReST in Peace. A library to make using ReStructured Text easy.'''

from docutils.core import publish_parts
from docutils.writers.html4css1 import Writer

from . import settings

def render(text, **kwargs) :
    '''Render a piece of ReStructuredText as HTML.'''

    overrides = {
        'report_level' : settings.REPORT_LEVEL,
        'initial_header_level' : settings.INITIAL_HEADER_LEVEL,
        'doctitle_xform' : settings.REMOVE_INITIAL_HEADER,
        'footnote_references' : settings.FOOTNOTE_REFERENCES,
        'tab_width' : settings.TAB_WIDTH,
    }

    overrides.update(kwargs)

    return publish_parts(
        text,
        writer = Writer(),
        settings_overrides = overrides,
    )['body']
