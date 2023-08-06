
from textwrap import dedent
from wikir import *
from wikir.tests import *
from nose.tools import eq_

@attr(syntax=1)
def test_option_list():
    ## see commented out test below which is failing. This is a compromise
    match(publish_string(dedent("""
    -h, --help            display this help and exit
    --version             output version information and exit
    -p, --ping=VERBOSITY  use the machine that goes PING
    """)),
    """\
`-h` `--help` 
  display this help and exit

`--version` 
  output version information and exit

`-p` `--ping=VERBOSITY` 
  use the machine that goes PING

""")

### hmm, this is how it should look with commas but isn't working:
### http://code.google.com/p/wikir/issues/detail?id=2
#     """\
# `-h`, `--help`
#   display this help and exit
# `--version`
#   output version information and exit
# `-p`, `--ping=`_VERBOSITY_
#   use the machine that goes PING
# 
# """

@attr(syntax=1)
def test_new_lines_to_spaces():
    # http://code.google.com/p/wikir/issues/detail?id=4
    match(
        publish_string("foo *bar*\nquux"),
        "foo *bar* quux\n\n")

@attr(syntax=1)
def test_headers():
    match(publish_string(dedent("""
    =====
    Title
    =====
    
    Some Headline
    =============
    
    More Headlines
    --------------
    
    Even More
    ~~~~~~~~~
    
    Another Big One
    ===============
    
    Descending
    ----------
    
    Deeper
    ~~~~~~
    
    And More
    ++++++++
    """)),
    dedent("""\
    = Title =
    
    = Some Headline =
    
    == More Headlines ==
    
    === Even More ===
    
    = Another Big One =
    
    == Descending ==
    
    === Deeper ===
    
    ==== And More ====
    
    """))

@attr(syntax=1)
def test_link():
    match(publish_string(dedent("""
    `Google Code`_
    
    .. _Google Code: http://code.google.com/
    
    """)),
    dedent("""\
    [http://code.google.com/ Google Code]
    
    """))

@attr(syntax=1)
def test_bullet_list():
    match(publish_string(dedent("""
    - toast
    - eggs
    
      - pancakes
      - omelettes
      
        - goat cheese
    
    - tomatoes
    """)),
    """\
  * toast
  * eggs
    * pancakes
    * omelettes
      * goat cheese
  * tomatoes
    
    
""")

@attr(syntax=1)
def test_definition_list():
    match(publish_string(dedent("""
    Brontosaurus
        All brontosauruses are thin at one end,
        much much thicker in the middle
        and then thin again at the far end.
    """)),
    """\
Brontosaurus
  All brontosauruses are thin at one end, much much thicker in the middle and then thin again at the far end.


    """)

@attr(syntax=1)
def test_definition_list_with_classifier():
    match(publish_string(dedent("""
    Brontosaurus : herbivore
        All brontosauruses are thin at one end,
        much much thicker in the middle
        and then thin again at the far end.
    """)),
    """\
Brontosaurus : _herbivore_
  All brontosauruses are thin at one end, much much thicker in the middle and then thin again at the far end.


    """)

@attr(syntax=1)
@attr(deferred=1)
def test_num_list():
    match(publish_string(dedent("""
    1. toast
    2. eggs
    
      - pancakes
      - omelettes
      
        - goat cheese
    
    3. tomatoes
    """)),
    """\
  # toast
  # eggs
    * pancakes
    * omelettes
      * goat cheese
  # tomatoes
    
    
""")
    
@attr(syntax=1)
def test_bullet_list_then_section():
    match(publish_string(dedent("""
    - toast
    - eggs
    
      - pancakes
      - omelettes
      
        - goat cheese
    
    - tomatoes
    
    This Is A Title
    ---------------
    """)),
    dedent("""\
      * toast
      * eggs
        * pancakes
        * omelettes
          * goat cheese
      * tomatoes
    
    
    = This Is A Title =
    
    """))

@attr(syntax=1)
def test_literal_block():
    match(publish_string(dedent("""
    ::
    
        some pseudo (code {
            'doing',
            'crazy'
            }).acrobatics(
            
        1,2,3)
    
    """)),
    dedent("""\
    {{{
    some pseudo (code {
        'doing',
        'crazy'
        }).acrobatics(
        
    1,2,3)
    }}}
    
    """))

@attr(syntax=1)
def test_paragraphs():
    match(publish_string(dedent("""
    This is a paragraph.

    Paragraphs line up at their left
    edges, and are normally separated
    by blank lines. 
    """)),
    dedent("""\
    This is a paragraph.

    Paragraphs line up at their left edges, and are normally separated by blank lines.
    
    """))

@attr(syntax=1)
def test_doctest():
    match(publish_string(dedent("""
    ::
        
        >>> 1 + 1
        2
        >>> 3 + 4
        7
        
    """)),
    dedent("""\
    {{{
    >>> 1 + 1
    2
    >>> 3 + 4
    7
    }}}
    
    """))

@attr(syntax=1)
def test_auto_urls():
    match(publish_string(dedent("""\
    Plain URLs such as http://www.google.com/ or ftp://ftp.kernel.org/ or https://secret/ are
    automatically made into links.
    """)),
    dedent("""\
    Plain URLs such as http://www.google.com/ or ftp://ftp.kernel.org/ or https://secret/ are automatically made into links.
    
    """))

@attr(syntax=1)
def test_inline_literal():
    match(publish_string("``inline literal``"), 
        dedent("""\
        `inline literal`
        
        """))

@attr(syntax=1)
def test_interpretted_text():
    match(publish_string("`interpretted text`"), 
        dedent("""\
        `interpretted text`
        
        """))

@attr(syntax=1)
def test_emphasis():
    match(publish_string("*emphasis*"), 
        dedent("""\
        *emphasis*
        
        """))

@attr(syntax=1)
def test_strong_emphasis():
    match(publish_string("**emphasis**"), 
        dedent("""\
        *emphasis*
        
        """))

@attr(syntax=1)
def test_crossreferences():
    match(publish_string(dedent("""
    Internal crossreferences, like example_.

    .. _example:

    This is an example crossreference target. """)),
    ## this could be more useful :
    dedent("""\
    Internal crossreferences, like [#example example].

    This is an example crossreference target.
    
    """))

@attr(syntax=1)
def test_table_of_contents():
    match(publish_string(dedent("""
    
    .. contents::
    
    The Beginning
    =============
    
    The Middle
    ----------
    
    The Almost End
    ~~~~~~~~~~~~~~
    
    A New Section
    =============
    """)),
    dedent("""\
    == Contents ==

      * The Beginning
        * The Middle
          * The Almost End
      * A New Section


    = The Beginning =

    == The Middle ==

    === The Almost End ===

    = A New Section =

    """))

@attr(syntax=1)
def test_comment():
    match(publish_string(dedent("""
    .. This text will not be shown
       (but, for instance, in HTML might be
       rendered as an HTML comment)
       
    """)),
    '')

@attr(syntax=1)
def test_empty_comment():
    match(publish_string(dedent("""
    An "empty comment" does not
    consume following blocks.

    ..

            So this block is not "lost",
            despite its indentation.
            
    """)),
    dedent("""\
    An "empty comment" does not consume following blocks.
    
    So this block is not "lost", despite its indentation.
    
    """))

@attr(syntax=1)
def test_substitutions():
    match(publish_string(dedent("""
    Systematic Dysfunctioner (tm)
    (c) Gemma Ryan
    
    .. Substitutions for reST:

    .. |(tm)| unicode:: U+2122
       :ltrim:
    .. |(c)| unicode:: 0xA9
    """)),
    dedent("""\
    Systematic Dysfunctioner (tm) (c) Gemma Ryan
    
    """))

@attr(syntax=1)
@attr(deferred=1)
def test_grid_table():
    match(publish_string(dedent("""
    +-----+---------+-------+
    | you | are     | sick  |
    +=====+=========+=======+
    | for | writing | grids |
    +-----+---------+-------+
    """)),
    dedent("""\
    || *you* || *are* || *sick* ||
    || for || writing || grids ||
    
    """))

@attr(syntax=1)
def test_note():
    match(publish_string(dedent("""
    .. note::
        something really important
    """)),
    dedent("""\
    *Note*: something really important
    
    """))