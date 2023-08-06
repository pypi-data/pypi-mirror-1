__doc__ = '''
A simple compiled templating language which uses SAX events for input and
output and supports substantially the same features of TAL, METAL and Zope's
internationalization extensions. See `curtain.template.Template` for
more informations.

:Variables:
    ns : unicode
        The namespace of Curtain.
'''

ns = u'http://curtain.sourceforge.net/NS/curtain'

from template import Template, Location
