from textwrap import fill

from docutils import nodes, writers
from sphinx.addnodes import desc_name

HEADER="#########################\n# ldaptool configuration\n#########################\n"

class ConfigWriter(writers.Writer):

    supported = ('ldaptoolconfig',)
    settings_spec = ('No options here,', '', ())
    settings_defaults = {}

    output = None

    def __init__(self, builder):
        writers.Writer.__init__(self)
        self.builder = builder

    def translate(self):
        visitor = ConfigTranslator(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
        self.document.has_config = visitor.has_config


class ConfigTranslator(nodes.NodeVisitor):

    def __init__(self, document, builder):
        nodes.NodeVisitor.__init__(self, document)
        self.builder = builder
        self.body = []
        self.has_config = False

    def reset_desc(self):
        self.examples = []
        self.paragraphs = []

    def astext(self):
        return '\n'.join(self.body) + '\n'

    def unknown_visit(self, node):
        pass

    def unknown_departure(self, node):
        pass

    def visit_document(self, node):
        self.reset_desc()
        self.body.append(HEADER)

    def visit_desc(self, node):
        self.reset_desc()

    def depart_desc(self, node):
        if node['desctype'] != 'config':
            return
        self.has_config = True
        res = u""
        for paragraph in self.paragraphs:
            res += fill(
                paragraph.astext(),
                initial_indent="# ",
                subsequent_indent="# ",
                replace_whitespace=True
            )
            res += '\n'
        if not self.examples:
            pass
            #res += self.format("%s = None" % node.first_child_matching_class(desc_name).astext(), comment="#")
        for example in self.examples:
            if example.get('comment', False):
                comment = "#"
            else:
                comment = ""
            res += '\n'.join([comment+x for x in example.astext().split('\n') ])
            res += '\n'
        self.body.append(res)

    def visit_literal_block(self, node):
        self.examples.append(node)

    def visit_paragraph(self, node):
        self.paragraphs.append(node)

