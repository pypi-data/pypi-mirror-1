
import wikir, inspect, pydoc
from wikir.tests.shelldoc import find_shell_sessions, validate_session

def test_docs():
    doc = pydoc.splitdoc(inspect.getdoc(wikir))[1]
    for session in find_shell_sessions(doc):
        yield validate_session, session