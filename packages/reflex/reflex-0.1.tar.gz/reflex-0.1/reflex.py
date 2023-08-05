# reflex - a small lexical analyser that uses regular expressions

"""Reflex: A lightweight lexical scanner library.

Reflex supports regular expressions, rule actions, multiple scanner states,
tracking of line/column numbers, and customizable token classes.

Reflex is not a "scanner generator" in the sense of generating source code.
Instead, it generates a scanner object dynamically based on the set of
input rules sepecified. The rules themselves are ordinary python regular
expressions, combined with rule actions which are simply python functions.

Example use:

    # Create a scanner. The "start" parameter specifies the name of the
    # starting state. Note: The state argument can be any hashable python
    # type.
    scanner = reflex.scanner( "start" )
    
    # Add some rules.
    # The whitespace rule has no actions, so whitespace will be skipped
    scanner.rule( "\s+" )
    
    # Rules for identifiers and numbers.
    TOKEN_IDENT = 1
    TOKEN_NUMBER = 2
    scanner.rule( "[a-zA-Z_][\w_]*", token=TOKEN_IDENT )
    scanner.rule( "0x[\da-fA-F]+|\d+", token=TOKEN_NUMBER )
    
    # The "string" rule kicks us into the string state
    TOKEN_STRING = 3
    scanner.rule( "\"", tostate="string" )

    # Define the string state. "string_escape" and "string_chars" are
    # action functions which handle the parsed charaxcters and escape
    # sequences and append them to a buffer. Once a quotation mark
    # is encountered, we set the token type to be TOKEN_STRING
    # and return to the start state.
    scanner.state( "string" )
    scanner.rule( "\"", tostate="start", token=TOKEN_STRING )
    scanner.rule( "\\\\.", string_escape )
    scanner.rule( "[^\"\\\\]+", string_text )

Invoking the scanner: The scanner can be called as a function which
takes a reference to a stream (such as a file object) which iterates
over input lines. The "context" argument is for application use,
The result is an iterator which produces a series of tokens.
The same scanner can be used to parse multiple input files, by
creating a new stream for each file.

    # Return an instance of the scanner.
    token_iter = scanner( istream, context )

Getting the tokens. Here is a simple example of looping through the
input tokens. A real-world use would most likely involve comparing
vs. the type of the current token.

    # token.id is the token type (the same as the token= argument in the rule)
    # token.value is the actual characters that make up the token.
    # token.line is the line number on which the token was encountered.
    # token.pos is the column number of the first character of the token.
    for token in token_iter:
        print token.id, token.value, token.line, token.pos
     
Action functions are python functions which take a single argument, which
is the token stream instance.

    # Action function to handle striing text.
    # Appends the value of the current token to the string data
    def string_text( token_stream ):
        string_data += scanner.token.value
        
The token_stream object has a number of interesting and usable attributes:

    states:  dictionary of scanner states
    state:   the current state
    stream:  the input line stream
    context: the context pointer that was passed to the scanner
    token:   the current token
    line:    the line number of the current parse position
    pos:     the column number of the current parse position
    
Note - reflex currently has a limit of 99 rules for each state. (That is
the maximum number of capturing groups allowed in a python regular expression.)

"""
__author__ = "Talin"
__version__ = "0.1"

class token( object ):
    """Class representing a token
    
    Attributes:
       id    -- the type of the token.
       value -- the characters that make up the text of the token.
       line  -- the line number where the token occurred.
       pos   -- the column number of the start of the token.
    """
    
    __slots__ = [ 'id', 'value', 'line', 'pos' ]
  
    def __init__( self, id, value, line, pos ):
        self.id = id
        self.value = value
        self.line = line
        self.pos = pos
        
    def __str__( self ):
        return "%s,%s:%s:%s" % ( self.line, self.pos, self.id, self.value )

def set_token( token_id ):
    """Returns a callback function that sets the current scanner token type to 'token_id'."""
    def set_token_func( scanner ):
        scanner.token.id  = token_id
    return set_token_func

def set_state( state_id ):
    """Returns a callback function that sets the current scanner state type to 'state_id'."""
    def set_state_func( scanner ):
        scanner.state = scanner.states[ state_id ]
    return set_state_func

# A scanner definition
class scanner( object ):
    """Class that defines the rules for a scanner."""

    # A scanner state
    class st( object ):
        __slots__ = [ 'name', 'rules', 're' ]
        
        def __init__( self, name ):
            self.name = name
            self.rules = []
            self.re = None
            
        def compile( self ):
            import string
            import re
            if len( self.rules ) > 99:
                raise ArgumentException( "Too many rules for this state" )
            pattern = string.join( [ "(" + x[ 0 ] + ")" for x in self.rules ], "|" )
            self.re = re.compile( pattern )
            
    class token_iter( object ):
        """An iterator class that returns a series of token objects parsed from the input stream."""
    
        def __init__( self, scanner, stream, context ):
            self.states = scanner.states
            self.state = scanner.start_state
            self.token_class = scanner.token_class
            self.stream = stream
            self.context = context
            self.linebuf = ""
            self.pos = 0
            self.line = 0
            self.token = None
            
        def __iter__( self ):
            return self
            
        def next( self ):
            """Returns the next token from the input stream."""
        
            self.token = self.token_class( None, 0, 0, 0 )
            while 1:
                if self.pos >= len( self.linebuf ):
                    try:
                        # Bump the line number first, because underlying reader might reset it
                        self.line += 1
                        self.pos = 0
                        self.linebuf = self.stream.next()
                        continue
                    except StopIteration:
                        raise StopIteration()
                    
                match = self.state.re.match( self.linebuf, self.pos )
                if match:
                    self.token.pos = self.pos
                    self.token.line = self.line
                    self.token.value = match.group()
                    actions = self.state.rules[ match.lastindex-1 ][ 1 ]
                    self.pos = match.end()
                    for action in actions:
                        action( self )
                    if self.token.id:
                        return self.token
                else:
                    raise SyntaxError( "No match: " + self.linebuf[ self.pos:-1 ] )
    
    def __init__( self, start_state = None, token_class = token ):
        """Initialize a new scanner type.
        The 'start_state' parameter is the name of the default starting state.
        The 'token_class' parameter is used to specify the type of tokens that should be created."""
        self.states = {}
        self.refresh = True
        self.build_state = None
        self.start_state = None
        self.token_class = token_class
        if start_state != None:
            self.start_state = self.state( start_state )
            
    def __call__( self, istream, context=None ):
        """Function call operator. Returns a token stream."""
        if self.refresh:
            self.refresh = False
            for st in self.states.values():
                st.compile()
        return scanner.token_iter( self, istream, context )
    
    def state( self, state_name ):
        """Changes the current scanner state to state_name. If the specified
        state does not exist, then it will be created automatically. Any rules
        subsequently defined will be appended to the current state."""
        if state_name in self.states:
            self.build_state = self.states[ state_name ]
        else:
            self.build_state = scanner.st( state_name )
            self.states[ state_name ] = self.build_state
            self.refresh = True
        return self.build_state
        
    def start( self, state_name ):
        """Sets the starting state."""
        self.start_state = self.states[ state_name ]
        
    def rule( self, pattern, *actions, **kwargs ):
        """Defines a rule. The 'pattern' argument is a regular expression to match.
        The 'actions' argument is a list of actions to be run when this rule
        is matched.
        
        Two keyword arguments are recognized:
        
        - 'token' is the type of token to be returned. If this value is missing,
           then the token will be skipped (although actions will still be run).
           
        - 'tostate' is the state to transition to after parsing this token.
        """
        if self.build_state == None:
            self.state( "start" )

        token = kwargs.get( "token" )
        if token:
            actions = actions + ( set_token( token ), )

        tostate = kwargs.get( "tostate" )
        if tostate:
            actions = actions + ( set_state( tostate ), )

        self.build_state.rules.append( ( pattern, actions ) )
        self.refresh = True
