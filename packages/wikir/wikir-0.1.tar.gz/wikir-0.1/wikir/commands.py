import os, sys
from setuptools import Command
import pkg_resources
from distutils import log
# turn off logging temporarily so stdout can work:
log.set_threshold(6)
import pydoc, tokenize
from docutils.parsers.rst import directives
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def split_doc_from_module(modfile):
    docstring = None
    f = open(modfile,'r')
    for toknum, tokval, _, _, _ in tokenize.generate_tokens(lambda: f.readline()):
        if toknum == tokenize.STRING:
            docstring = tokval
            break
        if toknum not in (tokenize.NL, tokenize.COMMENT):
            # we went too far
            break
    if docstring is None:
        raise ValueError("could not find docstring in %s" % modfile)
    docstring = docstring[3:]
    docstring = docstring[:-3]
    return pydoc.splitdoc(docstring)

class publish_wiki(Command):
    description = "Publish RST to wiki"
    user_options = [
        ("source=", 's', "path to RST source.  if a python module, the top-most docstring will be used as the source"),
        ]
    
    def initialize_options(self):
        self.source = None
        self.input = None
        
    def finalize_options(self):        
        if self.source is None:
            raise NotImplementedError("empty --source, need to iter entry_point")
        if self.source.endswith('.py'):
            short_desc, long_desc = split_doc_from_module(self.source)
            self.input = StringIO(long_desc)
        else:
            self.input = open(self.source, 'r')
        # # todo: check for output option
        # # otherwise:
        # log.set_threshold(log.INFO)

    def run(self):
        from wikir import publish_file
        for ep in pkg_resources.iter_entry_points('wikir.rst_directives'):
            log.info("registering RST directive: %s", str(ep))
            directives.register_directive(ep.name, ep.load())
        # from docutils.core import publish_file
        publish_file(self.input)