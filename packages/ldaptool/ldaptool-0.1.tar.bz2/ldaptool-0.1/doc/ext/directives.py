from docutils import nodes
from docutils.parsers.rst import directives


def example_directive(name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine):
    code = u'\n'.join(content)
    literal = nodes.literal_block(code, code)
    if 'language' in options:
        literal['language'] = options['language']
    literal['comment'] = 'comment' in options
    return [literal]


def setup(app):

    app.add_description_unit('config', 'conf', 'pair: %s; config')
    app.add_directive('example', example_directive, 1, (0, 0, 1), **{
        'comment': directives.flag,
        'language': str,
    })


