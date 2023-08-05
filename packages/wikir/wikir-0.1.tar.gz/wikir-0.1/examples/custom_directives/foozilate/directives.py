
from docutils import statemachine

def foozilate(  
        name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine):
    """insert a foozilate command's raw output in a pre block, like::
        
        | .. foozilate:: 
        |     some text here
    
    """
    output = ['--foozilated-- ']
    for line in block_text.split("\n")[1:]:
        line = line.strip()
        if line == '':
            continue
        output.append(line)
    output.append(" --foozilated--")
    output.append("\n")
    output = "".join(output)
    include_lines = statemachine.string2lines(output)
    state_machine.insert_input(include_lines, None)
    return []
    
foozilate.arguments = (1, 0, 1)
foozilate.options = {}
foozilate.content = 1