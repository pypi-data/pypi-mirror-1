
__all__ = ['find_shell_sessions', 'fix_trailing_space', 'validate_session']
import re, os, subprocess, textwrap
from wikir.tests import match
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
shell_sess_re = re.compile(r'(?P<indent>[\s]+)(?P<token>(\$|\|)\s?)(?P<line>.*)')

class ShellSession(object):
    def __init__(self, lines):
        self.lines = [line for line in lines]
        if len(self.lines) is 0:
            raise ValueError("cannot create an empty session")
    
    def __iter__(self):
        for line in self.lines:
            yield line
    
    def __len__(self):
        return len(self.lines)
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    __repr__ = __str__
    
    def __unicode__(self):
        cmd = self.lines[0][2] # just the first command
        if isinstance(cmd, str):
            cmd = cmd.decode('utf-8')
        desc = u"<%s($ %s ... and %s more)>" % (self.__class__.__name__, cmd, len(self))
        return desc

def find_shell_sessions(filelike):
    if isinstance(filelike, basestring):
        filelike = StringIO(filelike)
    session = []
    last_indent_len = None
    for line in filelike:
        clean_line = line.strip()
        if clean_line == '':
            continue
        match = shell_sess_re.match(line)
        if match:
            indent_len = len(match.group('indent'))
            if not last_indent_len:
                last_indent_len = indent_len
            cline = match.group('line')
            if not isinstance(cline, unicode):
                cline = unicode(cline, 'utf-8')
            if not cline.endswith("\n"):
                cline = cline + "\n"
            token = match.group('token')
            token = token[0] # force it into a single char
            session.append(
                (match.group('indent'), token, cline))
        else:
            if len(session):
                yield ShellSession(session)
            session[:] = []
            last_indent_len = None
    if len(session):
        yield ShellSession(session)

def as_output(filelike):
    if isinstance(filelike, basestring):
        filelike = StringIO(filelike)
    buf = []
    for line in filelike:
        buf.append("| %s" % line)
    return "".join(buf)

def fix_trailing_space(s):
    if s == '':
        return s
    if s[-1] == "\n":
        return s
    chop_at = len(s)-1
    while chop_at > 0:
        if s[chop_at] in (" ", "\t"):
            chop_at -= 1
        else:
            break
    return s[:chop_at+1]

def validate_command(cmd, expected_output=''):
    if cmd.startswith('cd'):
        # special case (hmm)
        os.chdir(cmd.split(' ')[1].strip())
        return
    # print "**run", cmd
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, close_fds=True, shell=True)
    returncode = p.wait()
    stdout, stderr = p.stdout, p.stderr    
    if returncode != 0:
        raise RuntimeError("\n\n$ %s%s\n(exit: %s)" % (
                            cmd, as_output(stderr), returncode))
    output = []
    while 1:
        line = stdout.readline()
        if not line:
            break
        output.append(line)
    output = fix_trailing_space("".join(output))
    
    context = textwrap.dedent("""\
        COMMAND: %s
        WORKING DIR: %s
        """ % (
            cmd.rstrip(), os.getcwd()))
    match(output, expected_output, show=False, context=context)

def validate_session(session):
    stack = []
    cmd = None
    expected_output = []
    saved_wd = os.getcwd()
    try:
        for indent, token, line in session:
            # print token, line,
            if token == '$':
                if cmd:
                    stack.append((cmd, "".join(expected_output)))
                    cmd = None
                    expected_output[:] = []
                cmd = line
            elif token == '|':
                expected_output.append(line)
            else:
                raise ValueError("unexpected token: %s (with line: '%s')" % (token, repr(line)))
        if cmd:
            stack.append((cmd, "".join(expected_output)))
        for cmd, expected_output in stack:
            validate_command(cmd, expected_output)            
    finally:
        os.chdir(saved_wd)