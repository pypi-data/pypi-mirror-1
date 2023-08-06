from setuptools import setup
setup(
    name = 'Foozilate',
    entry_points = {
        'wikir.rst_directives': [
            'foozilate = foozilate.directives:foozilate'
        ]
    },
    description = "A mysterious package that aids in foozilation")
