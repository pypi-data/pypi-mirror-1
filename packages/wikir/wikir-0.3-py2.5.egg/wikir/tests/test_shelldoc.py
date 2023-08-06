
from textwrap import dedent
from cStringIO import StringIO
from nose.tools import eq_
from wikir.tests import *
from wikir.tests.shelldoc import *

def rebuild_sess(session, include_indent=False):
    lines = []
    for indent, token, line in session:
        full = ''
        if include_indent:
            full = indent
        full += (token + ' ' + line)
        lines.append(full)
    return "".join(lines)

def test_find_single_valid_shell_session():
    text = """
        $ cd ../somewhere
        $ echo "pet me"
        | pet me
    """
    sess = [rebuild_sess(c) for c in find_shell_sessions(StringIO(text))]
    match(
        sess[0],
        dedent("""\
        $ cd ../somewhere
        $ echo "pet me"
        | pet me
        """))

def test_allow_empty_command():
    text = dedent("""
    this is a valid shell test::
    
        $
        
    """)
    sess = [rebuild_sess(c) for c in find_shell_sessions(StringIO(text))]
    match(
        sess[0],
        dedent("""\
        $ 
        """))

def test_sessions_must_be_indented():
    text = dedent("""
    $ cd ../somewhere
    $ echo "pet me"
    | pet me
    """)
    sess = [rebuild_sess(c) for c in find_shell_sessions(StringIO(text))]
    eq_(len(sess), 0)
        
def test_allow_unicode_output():
    text = dedent(u"""
    this is a shell test with unicode output:
    
        $ systematic_dysfunctioner
        | you will earn many \u20ac Euros
        
    """.encode('utf-8'))
    sess = [rebuild_sess(c) for c in find_shell_sessions(StringIO(text))]
    # print repr( u"""\
    #     $ systematic_dysfunctioner
    #     | you will earn many \u20ac Euros
    #     """.encode('utf-8'))
    match(
        sess[0],
        dedent(u"""\
        $ systematic_dysfunctioner
        | you will earn many \u20ac Euros
        """))
        
def test_single_command():
    text = dedent("""
    this is a valid shell test::
    
        $ cd ../elsewhere
        
    """)
    sess = [rebuild_sess(c) for c in find_shell_sessions(StringIO(text))]
    match(
        sess[0],
        dedent("""\
        $ cd ../elsewhere
        """))

def test_allow_session_with_invalid_indent():
    text = dedent("""
    this is an invalid shell test::
    
        $ cd ../somewhere
          $ echo "pet me"
        | pet me
        
    """)
    sess = [rebuild_sess(c) for c in find_shell_sessions(StringIO(text))]
    match(
        sess[0],
        dedent("""\
        $ cd ../somewhere
        $ echo "pet me"
        | pet me
        """))

def test_find_multiple_shell_sessions():
    text = dedent("""
    This is A Document
    ==================
    
    this is a shell test::
    
        $ cd ../somewhere
        $ echo "pet me"
        | pet me
    
    this is another shell test::
        
        $ cd /nowhere
        $ cat bah.txt
        | pretend
        | this is bah.txt
        $ echo produce_multi_lines
        | This is line one
        | 
        | Notice the blank line above
        | - - - 
        | THE END
        
    """)
    sess = [rebuild_sess(c) for c in find_shell_sessions(StringIO(text))]
    eq_(len(sess), 2)
    match(
        sess[0],
        dedent("""\
        $ cd ../somewhere
        $ echo "pet me"
        | pet me
        """))
        
    match(
        sess[1],
        dedent("""\
        $ cd /nowhere
        $ cat bah.txt
        | pretend
        | this is bah.txt
        $ echo produce_multi_lines
        | This is line one
        | 
        | Notice the blank line above
        | - - - 
        | THE END
        """))

def test_fix_trailing_space_empty_string():
    eq_(fix_trailing_space(""), "")
    
def test_fix_trailing_space_new_line():
    eq_(fix_trailing_space("\n"), "\n")
    
def test_fix_trailing_space_two_new_lines():
    eq_(fix_trailing_space("\n\n"), "\n\n")
    
def test_fix_trailing_space_ignore_space():
    eq_(fix_trailing_space(" "), " ")
    
def test_fix_trailing_space_when_trailing():
    eq_(fix_trailing_space("\n "), "\n")
    
def test_fix_trailing_space_when_multi_trailing():
    eq_(fix_trailing_space("\n \n"), "\n \n")
    
def test_fix_trailing_space_with_tab():
    eq_(fix_trailing_space("\n   \t  "), "\n")
    
def test_fix_trailing_space_with_word_and_tab():
    eq_(fix_trailing_space("barbed \n   \t  "), "barbed \n")
    