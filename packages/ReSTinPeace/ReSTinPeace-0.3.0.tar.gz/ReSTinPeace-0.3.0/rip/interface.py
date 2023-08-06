from . import settings

def initialize_arguments(parser) :
    '''Initialization of argparser for above settings.'''

    group = parser.add_argument_group('Core', 'Core ReStructured Text Processing Options')

    group.add_argument(
        '--report-level',
        action = 'store',
        type = int,
        default = settings.REPORT_LEVEL,
        help = 'DocUtils reporting level. [{0}]'.format(settings.REPORT_LEVEL),
    )

    group.add_argument(
        '--initial-header-level',
        action = 'store',
        type = int,
        default = settings.INITIAL_HEADER_LEVEL,
        choices = (1, 2, 3, 4, 5, 6),
        help = 'Header level of first heading.  [{0}]'.format(settings.INITIAL_HEADER_LEVEL),
    )

    group.add_argument(
        '--remove-initial-header',
        action = 'store_true',
        default = settings.REMOVE_INITIAL_HEADER,
        help = 'Whether to ignore initial header as document title.  [{0}]'.format(settings.REMOVE_INITIAL_HEADER),
    )

    group.add_argument(
        '--footnote-references',
        action = 'store',
        choices = ('superscript', 'brackets'),
        default = settings.FOOTNOTE_REFERENCES,
        help = 'Method of displaying footnote references.  [{0}]'.format(settings.FOOTNOTE_REFERENCES),
    )

    group.add_argument(
        '--tab-width',
        action = 'store',
        type = int,
        default = settings.TAB_WIDTH,
        help = 'Number of spaces to expand a tab to.  [{0}]'.format(settings.TAB_WIDTH),
    )

    return parser

def namespace_callback(namespace) :
    '''Act on the supplied arguments for core settings.'''

    settings.REPORT_LEVEL = namespace.report_level
    settings.INITIAL_HEADER_LEVEL = namespace.initial_header_level
    settings.REMOVE_INITIAL_HEADER = namespace.remove_initial_header
    settings.FOOTNOTE_REFERENCES = namespace.footnote_references
    settings.TAB_WIDTH = namespace.tab_width

