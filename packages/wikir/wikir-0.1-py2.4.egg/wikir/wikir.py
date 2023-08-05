
"""core"""

import re, pydoc
import docutils.core
from docutils import nodes
from docutils.nodes import SparseNodeVisitor
from docutils.writers import Writer
wiki_word_re = re.compile(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)+')
auto_url_re = re.compile(r'^(http|https|ftp)\://')
    
class WikiWriter(Writer):
    def translate(self):
        visitor = WikiVisitor(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
        
class WikiVisitor(SparseNodeVisitor):
    """visits RST nodes and transforms into Moin Moin wiki syntax.
    
    swiped from the nose project, originally written by Jason Pellerin.
    """
    def __init__(self, document):
        SparseNodeVisitor.__init__(self, document)
        self.list_depth = 0
        self.list_item_prefix = None
        self.indent = self.old_indent = ''
        self.output = []
        self.preformat = False
        self.section_level = 0
        self.topic_classes = []
        
    def astext(self):
        return ''.join(self.output)
    
    def visit_comment(self, node):
        """ Throw away comments, there is no Wiki syntax for them. """
        raise nodes.SkipNode

    def visit_Text(self, node):
        #print "Text", node
        data = node.astext()
        if not self.preformat:
            data = data.lstrip('\n\r')
            data = data.replace('\r', '')
            data = data.replace('\n', ' ')
        self.output.append(data)
    
    def _visit_list(self, node, bullet):
        self.list_depth += 1
        self.list_item_prefix = ('  ' * self.list_depth) + bullet + ' '
    
    def visit_bullet_list(self, node):
        self._visit_list(node, '*')
    
    def visit_enumerated_list(self, node):
        self._visit_list(node, '#')
    
    def _depart_list(self, node, bullet):
        next_node = node.next_node()
        self.list_depth -= 1
        if self.list_depth == 0:
            self.list_item_prefix = None
        else:
            self.list_item_prefix = ('  ' * self.list_depth) + bullet + ' '
        output_sep = True
        if isinstance(next_node, nodes.list_item):
            if self.list_depth > 0:
                output_sep = False
        if output_sep:
            self.output.append('\n\n')

    def depart_bullet_list(self, node):
        self._depart_list(node, '*')
    
    def depart_enumerated_list(self, node):
        self._depart_list(node, '#')
                           
    def visit_list_item(self, node):
        self.old_indent = self.indent
        self.indent = self.list_item_prefix

    def depart_list_item(self, node):
        self.indent = self.old_indent
        
    def visit_literal_block(self, node):
        self.output.extend(['{{{', '\n'])
        self.preformat = True

    def depart_literal_block(self, node):
        self.output.extend(['\n', '}}}', '\n\n'])
        self.preformat = False

    def visit_doctest_block(self, node):
        self.output.extend(['{{{', '\n'])
        self.preformat = True

    def depart_doctest_block(self, node):
        self.output.extend(['\n', '}}}', '\n\n'])
        self.preformat = False
        
    def visit_paragraph(self, node):
        self.output.append(self.indent)
        
    def depart_paragraph(self, node):
        self.output.append('\n')
        if not isinstance(node.parent, nodes.list_item):
            self.output.append('\n')
        if self.indent == self.list_item_prefix:
            # we're in a sub paragraph of a list item
            self.indent = ' ' * self.list_depth
        
    def visit_reference(self, node):
        if node.has_key('refuri'):
            href = node['refuri']
        elif node.has_key('refid'):
            href = '#' + node['refid']
        else:
            href = None
        if 'contents' in self.topic_classes:
            self.output.append('')
        elif not auto_url_re.search(node.astext()):
            self.output.append('[' + href + ' ')

    def depart_reference(self, node):
        if 'contents' in self.topic_classes:
            self.output.append('')
        elif not auto_url_re.search(node.astext()):
            self.output.append(']')
    
    def visit_substitution_definition(self, node):
        """Ignore these until there is some support in Google Code."""
        raise nodes.SkipNode
    
    def _find_header_level(self, node):
        if isinstance(node.parent, nodes.topic):
            h_level = 2 # ??
        elif isinstance(node.parent, nodes.document):
            h_level = 1
        else:
            assert isinstance(node.parent, nodes.section), (
                "unexpected parent: %s" % node.parent.__class__)
            h_level = self.section_level
        return h_level
    
    def _depart_header_node(self, node):
        h_level = self._find_header_level(node)
        self.output.append(' %s\n\n' % ('='*h_level))
        self.list_depth = 0
        self.indent = ''
    
    def _visit_header_node(self, node):
        h_level = self._find_header_level(node)
        self.output.append('%s ' % ('='*h_level))

    def visit_subtitle(self, node):
        self._visit_header_node(node)

    def depart_subtitle(self, node):
        self._depart_header_node(node)
        
    def visit_title(self, node):
        self._visit_header_node(node)

    def depart_title(self, node):
        self._depart_header_node(node)
        
    def visit_title_reference(self, node):
        self.output.append("`")

    def depart_title_reference(self, node):
        self.output.append("`")

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1
    
    def visit_topic(self, node):
        self.topic_classes = node['classes']
    
    def depart_topic(self, node):
        self.topic_classes = []

    def visit_emphasis(self, node):
        self.output.append('*')
    visit_strong = visit_emphasis

    def depart_emphasis(self, node):
        self.output.append('*')
    depart_strong = depart_emphasis
        
    def visit_literal(self, node):
        self.output.append('`')
        
    def depart_literal(self, node):
        self.output.append('`')
    
    def visit_note(self, node):
        self.output.append('*Note*: ')

settings_overrides = {
    'halt_level': 2,
    'report_level': 5
}

def publish_file(rstfile, **kw):
    """
    Set up & run a `Publisher` for programmatic use with file-like I/O.
    Return the encoded string output also.

    Parameters: see `publish_programmatically`.
    """
    kw.setdefault('writer', WikiWriter())
    kw.setdefault('settings_overrides', {})
    kw['settings_overrides'].update(settings_overrides)
    return docutils.core.publish_file(rstfile, **kw)
    
def publish_string(rstdoc, **kw):
    """
    Set up & run a `Publisher` for programmatic use with string I/O.  Return
    the encoded string or Unicode string output.

    For encoded string output, be sure to set the 'output_encoding' setting to
    the desired encoding.  Set it to 'unicode' for unencoded Unicode string
    output.  Here's one way::

        publish_string(..., settings_overrides={'output_encoding': 'unicode'})

    Similarly for Unicode string input (`source`)::

        publish_string(..., settings_overrides={'input_encoding': 'unicode'})

    Parameters: see `publish_programmatically`.
    """
    kw.setdefault('writer', WikiWriter())
    kw.setdefault('settings_overrides', {})
    kw['settings_overrides'].update(settings_overrides)
    return docutils.core.publish_string(rstdoc, **kw)
    