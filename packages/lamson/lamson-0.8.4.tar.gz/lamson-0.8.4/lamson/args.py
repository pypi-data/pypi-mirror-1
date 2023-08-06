import re
import sys

def s_ip_address(scanner, token): return ['ip_address', token]
def s_word(scanner, token): return ['word', token]
def s_email_addr(scanner, token): return ['email', token]
def s_option(scanner, token): return ['option', token.split("-")[-1]]
def s_int(scanner, token): return ['int', int(token) ]
def s_bool(scanner, token): return ['bool', bool(token) ]
def s_empty(scanner, token): return ['empty', '']
def s_string(scanner, token): return ['string', token]
def s_trailing(scanner, token): return ['trailing', None]


scanner = re.Scanner([
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", s_email_addr),
    (r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]", s_ip_address),
    (r"-+[a-zA-Z0-9]+", s_option),
    (r"True", s_bool),
    (r"[0-9]+", s_int),
    (r"--", s_trailing),
    (r"[a-z\-]+", s_word),
    (r"\s", s_empty),
    (r".+", s_string),
])


def match(tokens, of_type = None):
    """Responsible for taking a token off and processing it, ensuring it is 
    of the correct type.  If of_type is None (the default) then you are
    asking for anything."""
    # check the type (first element)
    if of_type:
        if not peek(tokens, of_type):
            raise RuntimeError("Expecting '%s' type of argument not %s in tokens: %r." % 
                               (of_type, tokens[0][0], tokens))

    # take the token off the front
    tok = tokens[0] ; del tokens[0]

    # return the value (second element)
    return tok[1]


def peek(tokens, of_type):
    """Returns true if the next token is of the type, false if not.  It does not
    modify the token stream the way match does."""
    if len(tokens) == 0:
        raise RuntimeError("No more tokens available.")

    return tokens[0][0] == of_type


def Trailing(data, tokens):
    data['TRAILING'] = [x[1] for x in tokens]
    del tokens[:]

def Option(data, tokens):
    """The Option production, used for -- or - options.  The number of - aren't 
    important.  It will handle either individual options, or paired options."""
    if peek(tokens, 'trailing'):
        # this means the rest are trailing arguments, collect them up
        match(tokens, 'trailing')
        Trailing(data, tokens)
    else:
        opt = match(tokens, 'option')
        if not tokens:
            # last one, it's just true
            data[opt] = True
        elif peek(tokens, 'option'):
            # the next one is an option so just set this to true
            data[opt] = True
        else:
            # this option is set to something else, so we'll grab that
            data[opt] = match(tokens)


def Options(tokens):
    """List of options, optionally after the command has already been taken off."""
    data = {}
    while tokens:
        Option(data, tokens)
    return data


def Command(tokens):
    """The command production, just pulls off a word really."""
    return match(tokens, 'word')


def tokenize(argv):
    """Goes through the command line args and tokenizes each one, trying to match
    something in the scanner.  If any argument doesn't completely parse then it
    is considered a 'string' and returned raw."""

    tokens = []
    for arg in argv:
        toks, remainder = scanner.scan(arg)
        if remainder or len(toks) > 1:
            # if we got a remainder then this is too complex so it's a generic
            # string and they deal with it
            tokens.append(['string', arg])
        else:
            tokens += toks
    return tokens


def parse(argv):
    """
    Tokenizes and then parses the command line as wither a command style or
    plain options style argument list.  It determines this by simply if the
    first argument is a 'word' then it's a command.  If not then it still
    returns the first element of the tuple as None.  This means you can do:

        command, options = args.parse(sys.argv[1:])

    and if command==None then it was an option style, if not then it's a command 
    to deal with.
    """
    tokens = tokenize(argv)
    if not tokens:
        return None, {}
    elif peek(tokens, "word"):
        # this is a command style argument
        return Command(tokens), Options(tokens)
    else:
        # options only style
        return None, Options(tokens)


def defaults(options, **reqs):
    """
    Given a set of kw requirements, it will make sure that the options map given
    has any required settings, and any that have default values get these set.
    
    If you want an argument be required, then set it to None in reqs:

        args.defaults(options, cheese=None)

    Then the user will be required to set chees to something.

    If you want an argument to get a default, then give it a value that's not
    None.

        args.defaults(options, meat=1)

    Then if they don't set meat, it gets set to 1.

    Anything you don't specify is just ignored.
    """

    for key in reqs:
        if reqs[key] == None:
            # explicitly set to required
            if not options.has_key(key):
                raise RuntimeError("Option '%s' is required." % key)
        else:
            # given a default, so set that up
            if not options.has_key(key):
                options[key] = reqs[key]

def command_module(mod, command, options, ending="_command"):
    """Takes a module, uses the command to run that function."""
    return mod.__dict__[command+ending](options)


def available_help(mod, ending="_command"):
    """Returns the dochelp from all functions in this module that have _command
    at the end."""
    help = []
    for key in mod.__dict__:
        if key.endswith(ending):
            name = key.split(ending)[0]
            help.append(name + ":\n" + mod.__dict__[key].__doc__)

    return help


def help_for_command(mod, command, ending="_command"):
    """
    Returns the help string for just this one command in the module.
    If that command doesn't exist then it will return None so you can
    print an error message.
    """

    if command in available_commands(mod):
        return mod.__dict__[command + ending].__doc__
    else:
        return None


def available_commands(mod, ending="_command"):
    """Just returns the available commands, rather than the whole long list."""
    commands = []
    for key in mod.__dict__:
        if key.endswith(ending):
            commands.append(key.split(ending)[0])

    return commands


def invalid_command_message(mod, exit_on_error):
    print "You must specify a valid command.  Try these: "
    print ", ".join(available_commands(mod))

    if exit_on_error: 
        sys.exit(1)
    else:
        return False


def parse_and_run_command(argv, mod, default_command=None, exit_on_error=True):
    """
    A one-shot function that parses the args, and then runs the command
    that the user specifies.  If you set a default_command, and they don't
    give one then it runs that command.  If you don't specify a command,
    and they fail to give one then it prints an error.

    On this error (failure to give a command) it will call sys.exit(1).
    Set exit_on_error=False if you don't want this behavior, like if
    you're doing a unit test.
    """
    command, options = parse(argv)

    if not command and default_command:
        command = default_command
    elif not command and not default_command:
        return invalid_command_message(mod, exit_on_error)

    if command not in available_commands(mod):
        return invalid_command_message(mod, exit_on_error)

    command_module(mod, command, options)

    return True

