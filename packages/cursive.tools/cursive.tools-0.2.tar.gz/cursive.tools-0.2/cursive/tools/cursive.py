"""The `cursive` command-line program itself."""

import sys
from optparse import OptionParser
from pkg_resources import iter_entry_points

from docutils.nodes import GenericNodeVisitor
from docutils import core
from docutils.writers import Writer

textual_nodes = set([ 'block_quote', 'paragraph',
                      'list_item', 'term', 'definition_list_item', ])

class Section(object):
    """Maintains a counter of how many words are in a section.

    This class can be used to accumulate information about a section of
    an RST file as it is processed.  A slot is provided for the section
    title, and a counter is kept for the number of words.

    """
    def __init__(self):
        self.title = ''
        self.words = 0
        self.subsections = []

    def create_subsection(self):
        """Return a new object representing our next subsection."""
        ss = Section()
        self.subsections.append(ss)
        return ss

    def add_text(self, text):
        """Record text (by counting words) belonging to this section."""
        self.words += len(text.split())

    def total(self):
        """Compute how many words in this section and its subsections."""
        return sum([ self.words ] + [ ss.words for ss in self.subsections ])

    def report(self):
        """Return a string reporting on this section and its subsections."""
        title = self.title
        if len(title) > 58:
            title = title[:57] + '\\'
        wordstr = str(self.total())
        dots = '.' * (68 - len(title) - len(wordstr) - 7)
        return ('%s %s %s words\n' % (title, dots, wordstr) +
                ''.join( '    ' + ss.report() for ss in self.subsections ))

class MyVisitor(GenericNodeVisitor):
    """A Visitor class; see the docutils for more details.

    Each time a section is entered or exited, the ``self.sections``
    stack grows or shrinks, so that the current section is always at the
    stack's top.  Titles and text are both handed over to the current
    Section object to be remembered.  When everything is over, and our
    own ``astext()`` method is called, we return a little report showing
    how many words per section the document contains.

    """
    def __init__(self, *args, **kw):
        self.sections = [ Section() ]
        GenericNodeVisitor.__init__(self, *args, **kw)

    def visit_title(self, node):
        self.sections[-1].title = node.astext()

    def visit_section(self, node):
        sections = self.sections
        ss = sections[0].create_subsection()
        sections.append(ss)

    def depart_section(self, node):
        self.sections.pop()

    def visit_Text(self, node):
        if node.parent.tagname in textual_nodes:
            self.sections[-1].add_text(node.astext())

    def default_visit(self, node): pass
    def default_departure(self, node): pass

    def astext(self):
        return self.sections[0].report()

class MyWriter(Writer):
    """Boilerplate attaching our Visitor to a docutils document."""
    def translate(self):
        visitor = MyVisitor(self.document)
        self.document.walkabout(visitor)
        self.output = '\n' + visitor.astext() + '\n'

def wc_command():
    """Word count."""
    core.publish_cmdline(writer=MyWriter())

def console_script_cursive():
    """Command-line script printing how many words are in a document."""

    parser = OptionParser()
    (options, args) = parser.parse_args()

    commands = {'wc': wc_command}
    for point in iter_entry_points(group='cursive.commands', name=None):
        commands[point.name] = point.load()

    if not args or args[0] not in commands:
        print("Welcome to cursive, the suite of tools for authors"
              " using Restructured Text!\n")
        for name, func in sorted(commands.items()):
            docline = func.__doc__.split('\n')[0].strip().strip('.')
            print(' {0} - {1}'.format(name, docline))
        sys.exit(2)

    command = commands[args[0]]
    del sys.argv[1]
    command()
