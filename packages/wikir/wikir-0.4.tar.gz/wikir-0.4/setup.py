from setuptools import setup, find_packages
import tokenize, pydoc
from StringIO import StringIO

def get_module_meta(modfile):
    docstring = None
    version = [(tokenize.NAME, '__version__'), (tokenize.OP, '=')]
    f = open(modfile,'r')
    for toknum, tokval, _, _, _ in tokenize.generate_tokens(lambda: f.readline()):
        # this will fail in interesting ways if tehre is no docstring nor __version__
        if not docstring:
            if toknum == tokenize.STRING:
                docstring = tokval
                continue
        if len(version):
            if (toknum, tokval) == version[0]:
                version.pop(0)
        else:
            version = tokval
            break
    if docstring is None:
        raise ValueError("could not find docstring in %s" % modfile)
    if not isinstance(version, basestring):
        raise ValueError("could not find __version__ in %s" % modfile)
    # unquote :
    docstring = docstring[3:]
    docstring = docstring[:-3]
    version = version[1:]
    version = version[:-1]
    return (version,) + pydoc.splitdoc(docstring)

version, description, long_description = get_module_meta("./wikir/__init__.py")

setup(
    name = 'wikir',
    install_requires = ['docutils'],
    tests_require = ['nose'],
    entry_points = {
        'distutils.commands': [
            'publish_wiki = wikir.commands:publish_wiki',
            ],
        'console_scripts': [ 
            'wikir = wikir:main' 
            ],
        },
    version = version,
    author = 'Kumar McMillan',
    author_email = 'kumar.mcmillan@gmail.com',
    description = description,
    url="http://code.google.com/p/wikir/",
    long_description = long_description,
    license = 'MIT License',
    packages = find_packages(),
    test_suite = "nose.collector"
    )