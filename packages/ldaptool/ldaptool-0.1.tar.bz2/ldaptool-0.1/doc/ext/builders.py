from os import path

from docutils.io import StringOutput
from sphinx.builder import Builder
from sphinx.util.console import bold, darkgreen

from configwriter import ConfigWriter


class ConfigBuilder(Builder):
    """Builds example config files from the documentation."""

    name = 'config'

    def init(self):
        pass

    def prepare_writing(self, docnames):
        pass

    def get_outdated_docs(self):
        return self.env.found_docs

    def get_target_uri(self, docname, typ=None):
        return ''

    def write(self, *ignored):

        docwriter = ConfigWriter(self)

        self.info(bold("writing... "), nonl=1)

        for docname in set(self.env.found_docs):


            doctree = self.env.get_and_resolve_doctree(docname, self)
            destination = StringOutput(
                destination_path=path.join(self.outdir, docname),
                encoding='utf-8'
            )
            res = docwriter.write(doctree, destination)

            if not doctree.has_config:
                continue

            self.info(darkgreen(docname) + " ", nonl=1)
            f = file(path.join(self.outdir, docname), 'w')
            f.write(res)
            f.close

        self.info()

    def finish(self):
        pass

def setup(app):
    app.add_builder(ConfigBuilder)

