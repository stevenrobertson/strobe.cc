# -*- coding: utf-8 -*-
"""
    The Pygments reStructuredText directive
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This fragment is a Docutils_ 0.5 directive that renders source code
    (to HTML only, currently) via Pygments.

    To use it, adjust the options below and copy the code into a module
    that you import on initialization.  The code then automatically
    registers a ``sourcecode`` directive that you can use instead of
    normal code blocks like this::

        .. sourcecode:: python

            My code goes here.

    If you want to have different code styles, e.g. one with line numbers
    and one without, add formatters with their names in the VARIANTS dict
    below.  You can invoke them instead of the DEFAULT one by using a
    directive option::

        .. sourcecode:: python
            :linenos:

            My code goes here.

    Look at the `directive documentation`_ to get all the gory details.

    .. _Docutils: http://docutils.sf.net/
    .. _directive documentation:
       http://docutils.sourceforge.net/docs/howto/rst-directives.html

    :copyright: Copyright 2006-2010 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# Options
# ~~~~~~~

# Set to True if you want inline CSS styles instead of classes
INLINESTYLES = True

from pygments.formatters import HtmlFormatter, LatexFormatter

# The default formatter
DEFAULT = (HtmlFormatter(noclasses=INLINESTYLES, linenos=True),
           LatexFormatter(linenos=True))

# Add name -> formatter pairs for every variant you want to use
VARIANTS = {
    'nolinenos': (HtmlFormatter(noclasses=INLINESTYLES, linenos=False),
                  LatexFormatter(linenos=True)),
}


from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer

class Pygments(Directive):
    """ Source code syntax hightlighting.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = dict([(key, directives.flag) for key in VARIANTS])
    has_content = True

    def _run(self, content, lexer_name):
        try:
            lexer = get_lexer_by_name(lexer_name)
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()
        # take an arbitrary option if more than one is given
        formatter = self.options and VARIANTS[self.options.keys()[0]] or DEFAULT
        html = highlight(u'\n'.join(content), lexer, formatter[0])
        # hang the indents for strobe.cc
        html = '<div class="blockcode">%s</div>' % html
        latex = formatter[1].get_style_defs() + \
                highlight(u'\n'.join(content), lexer, formatter[1])
        return [nodes.raw('', html, format='html'),
                nodes.raw('', latex, format='latex')]

    def run(self):
        self.assert_has_content()
        return self._run(self.content, self.arguments[0])

class PygmentsFile(Pygments):
    """Source code syntax highlighting from file."""
    required_arguments = 2
    has_content = False

    def run(self):
        try:
            fobj = open(self.arguments[0])
            contents = fobj.read()
            fobj.close()
            return self._run([contents], self.arguments[1])
        except IOError:
            print "Warning: error opening file %s." % (self.arguments[0],)
            return []

directives.register_directive('code', Pygments)
directives.register_directive('codefile', PygmentsFile)

