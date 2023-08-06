"""\
Tools to write command line interfaces with sub-commands
See the blog post at http://jimmyg.org/blog/2009/XXX for information
Public domian, no warranty, use responsibly.
"""

import logging
import types
import os.path
import posixpath
import getopt
import sys
import datetime

#
# Logging
#

log = logging.getLogger(__name__)

#
# Exceptions
#

class ManError(Exception):
    pass

class OptionConfigurationError(Exception):
    pass

#
# Helpers
#

#def get_docstrings(module_name):
#    """\
#    Extract docstrings for functions in the module given by ``module_name``
#    """
#    doc_strings = {}
#    module = __import__(module_name)
#    for name, item in module.__module__.items():
#        if type(item) == types.function_type and name.startswith('handle_command_'):
#            doc_strings[name] = item.__doc__
#        elif name == 'program_help':
#            doc_strings['__program__'] = item
#    return doc_strings

def make_man_page(
    program_name, 
    program_description=None, 
    email=None, 
    organization=None, 
    address=None, 
    date=None, 
    copyright=None,
    version=None,
    section=1,
    group='text processing',
    synopsis=None,
    description=None,
    options=None,
    rest=None,
):
    """\
    Build a reStructuredText page in a format capable of being converted to 
    man format by rst2man.py
    """
    if program_description is None:
        program_description = program_name
    if email is not None:
        email = ":Author: "+email+'\n'
    else:
        email = ''
    if organization is not None:
        organization = ':organization: '+organization+'\n'
    else:
        organization = ''
    if address is not None:
        a = [':Address: ']
        parts = address.split('\n')
        a.append(parts[0])
        for part in parts[1:]:
            a.append('          '+part)
        address = '\n'.join(a)+'\n'
    else:
        address = ''
    if date == '':
        # Autogenerate it
        date = datetime.datetime.now()
        date = ':Date: %s\n' % datetime.date(date.year, date.month, date.day)
    elif date is not None:
        date = ':Date: '+str(date)+'\n'
    else:
        date = ''
    if copyright is not None:
        copyright = ':copyright: '+copyright+'\n'
    else:
        copyright = ''
    if version is not None:
        version = ':Version: '+version+'\n'
    else:
        version = ''
    if synopsis is not None:
        synopsis = '''\
SYNOPSIS
========

%s

''' % synopsis
    else:
        synopsis = ''
    if description is not None:
        description = '''\
DESCRIPTION
===========

%s

''' % description
    else:
        description = ''
    if options is not None:
        options = '''\
OPTIONS
=======

%s

''' % options
    else:
        options = ''
    if not section:
        raise ManError('You must specify a manual section')
    if not group:
        raise ManError('You must specify a manual group')
    if rest is None:
        rest = ''
    man_page = """\
%(program_name_underline)s
%(program_name)s
%(program_name_underline)s

%(program_description_underline)s
%(program_description)s
%(program_description_underline)s

%(email)s%(organization)s%(address)s%(date)s%(copyright)s%(version)s:Manual section: %(section)s
:Manual group: %(group)s

%(synopsis)s%(description)s%(options)s%(rest)s


""" % {
    'program_name': program_name,
    'program_name_underline': '='*len(program_name),
    'program_description': program_description,
    'program_description_underline': '-----------------------------',
    'group': group,
    'section': section,
    'synopsis': synopsis,
    'options': options,
    'description': description,
    'rest': rest,
    'email': email,
    'organization': organization,
    'address': address,
    'date': date,
    'copyright': copyright,
    'version': version,
}
    return man_page

#def format_result(program_opts, command_opts, command, args):
#    output = ['program options: ']
#    for k, vs in program_opts.items():
#        for v in vs:
#            if v['value']:
#                output.append('%s %s, '%(k, v['value']))
#            else:
#                output.append('%s, '%(k))
#    output[-1] = output[-1][:-1]
#    if command:
#        output.append('\ncommand options: ')
#        for k, vs in command_opts.items():
#            for v in vs:
#                if v['value']:
#                    output.append('%s %s, '%(k, v['value']))
#                else:
#                    output.append('%s, '%(k))
#        output[-1] = output[-1][:-1]
#        output.append('\ncommand:         %s'%command)
#        output.append('\nargs:            %s'%(', '.join(args)))
#    return ''.join(output) 

def build_help(options, aliases, program, usage):
    output = []
    output.append('Commands:')
    for name, aliases, help in aliases:
        output.append(' %-10s %s'%(name, help))
    output.append('')
    output.append('Options:')
    for option in options:
        output.append(
            ' %-2s %-15s %s'%(
                option['short'][0].strip(':'), 
                option['long'][0].strip('='), 
                option['help'],
            )
        )
    output.append('')
    output.append(usage%{'program': program})
    return '\n'.join(output)

def uniform_path(path):
    return os.path.normpath(os.path.abspath(path))

def extract_metavars(list_of_option_sets):
    metavars = {}
    for option_set in list_of_option_sets:
        for internal_name, option_list in option_set.items():
            for option in option_list:
                if option.has_key('metavar'):
                    metavar = option['metavar']
                    if metavars.has_key(metavar):
                        if metavars[metavar][1] != option['value']:
                            raise getopt.GetoptError(
                                'The options %r and %r must have the same '
                                'value if specified together' % (
                                    metavars[metavar][1],
                                    option['name'],
                                )
                            )
                        else:
                            metavars[metavar] = (option['name'], option['value'])
    return metavars

def strip_docstring(docstring, tabstop=4):
    docstring = docstring.replace('\r', '\n')
    min = len(docstring)
    lines = docstring.split('\n')
    for line in lines:
        if line:
            chars = 0
            i = 0
            while line[i:]:
                if line[i] == ' ':
                    i += 1
                    chars += 1
                elif line[i] == '\t':
                    i += 1
                    chars += tabstop
                else:
                    break
            if chars < min:
               min = chars
    # Now we know the amount of whitespace for the line with the least 
    # we can regenerate the final docstring whitespace
    final = []
    for line in lines:
        if not line:
            final.append('')
        else:
            final.append(line[min:])
    return '\n'.join(final)
strip_docsting = strip_docstring

def option_names_from_option_list(option_list):
    names = []
    for option in option_list:
        for name in option['short']:
            names.append(name)
        for name in option['long']:
            names.append(name)
    return names

def set_error_on(command_options, allowed):
    # Since position numbers are unique we simply scan the tree for allowed
    # positions, then scan the tree again to see if the keys which aren't
    # allowed have options which aren't in the allowed positions.
    valid_positions = []
    for k, vs in command_options.items():
        for v in vs:
            if k in allowed:
                valid_positions.append(v['pos'])
    internal_vars = {}
    for k, vs in command_options.items():
        for v in vs:
            if v['pos'] not in valid_positions:
                raise getopt.GetoptError(
                    "The option %r was not expected"%v['name']
                )
            if v.has_key('metavar'):
                internal_vars[k] = v['value']
            else:
                internal_vars[k] = True
    return internal_vars

from xml.dom.minidom import parseString

def get_text(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
        else:
            rc += get_text(node.childNodes)
    return rc

def handle_html_config_row(row):
    result = []
    for node in row.childNodes:
        if node.nodeType == node.TEXT_NODE:
            continue
        else:
            # Assume it is a <td>
            result.append(get_text(node.childNodes))
    if not len(result) == 3:
        raise getopt.GetoptError("Couldn't parse the config file, one of the rows didn't have 3 <td> elements")
    return result[0], result[2]

def parse_html_config(filename):
    """\

    Looks for a config file in the form of an HTML table where the first column
    specifies the metavars, the second column gives a descritption and the third
    column contains the values.

    Returns a dictionary of metavars and their corresponding values, the
    descriptions are ignored.

    The HTML file must contain a table strictly with three columns and no 
    colspans. The table must be started with precisely these characters:
    ``<table class="commandtool-config" `` and ended with precisely these characters:
    ``</table>``. Between these two tags the content must also be valid XML.

    eg:
    
    ::
    
        <table class="commandtool-config" border="0">
        <tr>
            <td class="metavar"><tt>START_DIRECTORY</tt></td>
            <td>The directory to begin the search</td>
            <td>/home/james</td>
        </tr>
        </table>

    Any HTML tags within the table cells are stripped.
    """
    if not os.path.exists(filename):
        raise getopt.GetoptError("No such config file %r."%filename)
    fp = open(filename, 'r')
    data = fp.read()
    fp.close()
    start_table = '<table class="commandtool-config"'
    end_table = '</table>'
    start = data.find(start_table)
    if start == -1:
        raise getopt.GetoptError("Could not find start table tag in config file %r."%filename)
    end_start = data[start+len(start_table):].find('>')
    if end_start == -1:
        raise getopt.GetoptError("Could not find start table tag in config file %r."%filename)
    end = data[start+end_start+1:].find(end_table)
    if end == -1:
        raise getopt.GetoptError("Could not find end table tag in config file %r."%filename)
    table = data[start+end_start+len(start_table)+1:start+end_start+1+end]
    log.debug('Found table rows: %r', table)
    dom = parseString('<table>'+table+'</table>')
    rows = dom.documentElement.childNodes
    result = {}
    for node in rows:
        if node.nodeType == node.TEXT_NODE:
            continue
        else:
            k, v = handle_html_config_row(node)
            result[k] = v
    log.debug('Parsed config file to: %r', result)
    return result

#
# Main
#

def parse_command_line(option_sets, aliases=None):
    program_opts, command_opts, command, args = _parse_command_line(
        option_sets, 
        aliases, 
    )
    # Now check that the results haven't ended up with conflicting metavars
    # but ignore the extracted value
    metavars = extract_metavars([program_opts, command_opts])
    return program_opts, command_opts, command, args

def _parse_command_line(option_sets, aliases=None):
    if aliases is None:
        aliases = []
    short_options = ''
    long_options = []
    by_option = {}
    used_internal = []
    # Check the options are valid and generate the get_opt options
    for internal_name, option_list in option_sets.items():
        if internal_name in used_internal:
            raise OptionConfigurationError(
                'The internal option %r has already been configured'% (
                    internal_name,
                )
            )
        else:
            used_internal.append(internal_name)
        for option in option_list: 
            option['internal'] = internal_name
            if option['type'] not in ['shared', 'program', 'command']:
                raise OptionConfigurationError(
                    'Unknown type %r for option %r' % (
                         option['type'], 
                         option['internal']
                    )
                )
            # Now set up the long and short options
            for short in option['short']:
                if option.has_key('metavar'):
                    short_options += short.strip(':-')+':'
                else:
                    short_options += short.strip(':-')
                if by_option.has_key(short.strip(':')):
                    raise OptionConfigurationError(
                        'The short option %r is already being used'%short
                    )
                else:
                    new = option.copy()
                    new['name'] = short.strip(':')
                    by_option[short.strip(':')] = new 
            for long in option['long']:
                if option.has_key('metavar'):
                    long_options.append(long.strip('-=')+'=')
                else:
                    long_options.append(long.strip('-='))
                if by_option.has_key(long.strip('=')):
                    raise OptionConfigurationError(
                        'The long option %r is already being used'%long
                    )
                else:
                    new = option.copy()
                    new['name'] = long.strip('=')
                    by_option[long.strip('=')] = new

    # Now we know the options are valid, parse them
    log.debug('Short options: %r', short_options)
    log.debug('Long options: %r', long_options)
    log.debug('by_option: %r', by_option.keys())
    opts, args = getopt.gnu_getopt(sys.argv[1:], short_options, long_options)
    if not args:
        # If we have only use shared or program options then that's fine
        program_options = {}
        counter = 0
        for opt in opts:
            if by_option[opt[0]]['type'] == 'command':
                raise getopt.GetoptError("No command specified.")
            else:
                internal = by_option[opt[0]]['internal']
                new = by_option[opt[0]].copy()
                new['value'] = opt[1]
                new['pos'] = counter
                counter += 1
                if program_options.has_key(internal):
                    program_options[internal].append(new)
                else:
                    program_options[internal] = [new]
        log.debug('No command, returning')
        return (
            program_options,
            {},
            None,
            None,
        )
    else:
        orig_command = args[0]
        command = None
        for name, alias_ in aliases.items():
            if orig_command == name:
                command = name
                break
            else:
                for alias in alias_:
                    if orig_command == alias: 
                        command = name
                        break
        if not command:
            raise getopt.GetoptError('No such command %r'%orig_command)
        log.debug('command: %r' % command)
        log.debug('orig_command: %r' % orig_command)
        args = args[1:] 
        log.debug('args: %r' % args)
        # Get the extra data about the options used this time:
        option_types = {
            'program': {},
            'command': {},
            'shared': {},
        }
        # Start a new counter
        counter = 0
        for opt in opts:
            all_options = option_types[by_option[opt[0]]['type']]
            internal = by_option[opt[0]]['internal']
            new = by_option[opt[0]].copy()
            new['value'] = opt[1]
            new['pos'] = counter
            counter += 1
            if all_options.has_key(internal):
                all_options[internal].append(new)
            else:
                all_options[internal] = [new]
        log.debug('option_types: %s' % option_types)
        if option_types['shared']:
            log.debug('shared: %s' % option_types['shared'])
            # Work out which of the shared options are program options and
            # which are command options. We need to find out which 
            # arguments came before COMMAND on the command line, being
            # careful not to confuse the command with an option value
            # find the command then see if it was an option value
            for i, term in enumerate(sys.argv[1:]):
                if term.strip() == orig_command:
                    if i == 0:
                        # Must be the command, all shared options are 
                        # command options 
                        for k, vs in option_types['shared'].items():
                            for v in vs:
                                if option_types['command'].has_key(k):
                                    option_types['command'][k].append(v)
                                else:
                                    option_types['command'][k] = [v]
                            del option_types['shared']
                        break
                    elif i == len(sys.argv):
                        # Must be the command, all shared options are
                        # program options
                        for k, vs in option_types['shared'].items():
                            for v in vs:
                                if option_types['program'].has_key(k):
                                    option_types['program'][k].append(v)
                                else:
                                    option_types['program'][k] = [v]
                            del option_types['program']
                        break
                    else:
                        # previous term
                        if by_option.has_key(sys.argv[i]) and \
                           by_option[sys.argv[i]].has_key('metavalue'):
                            # The term before is an option which takes
                            # a value, ignore this one
                            continue
                        else:
                            # This is the command, terms up to here are
                            # program options, those after are command
                            # options
                            prog_opts, no_args = getopt.gnu_getopt(
                                sys.argv[1:i+1], 
                                short_options, 
                                long_options
                            )
                            if no_args:
                                raise Exception(
                                    'Extra args were found in the program '
                                    'options postion. This is a bug.'
                                )
                            prog_opts = option_types['program']
                            command_opts = option_types['command']
                            for k, vs in option_types['shared'].items():
                                for v in vs:
                                    if v['pos'] < i:
                                        if prog_opts.has_key(k):
                                            prog_opts[k].append(v)
                                        else:
                                            prog_opts[k] = [v]
                                    else:
                                        if command_opts.has_key(k):
                                            command_opts[k].append(v)
                                        else:
                                            command_opts[k] = [v]
                            del option_types['shared']
                            break
        return (
            option_types['program'],
            option_types['command'],
            command,
            args,
        )

def handle_program(
    command_handlers, 
    option_sets, 
    aliases, 
    program_options, 
    command_options, 
    command, 
    args,
    program_name,
    help = None,
):
    """\
    usage: ``%(program)s [PROGRAM_OPTIONS] COMMAND [OPTIONS] ARGS``

    Try \`%(program)s COMMAND --help' for help on a specific command."""
    # First, are they asking for program help?
    if program_options.has_key('help'):
        # if so provide it no matter what other options are given
        if help and hasattr(help, '__program__'):
            print strip_docstring(
                help.__program__ % {
                    'program': program_name,
                }
            )
        else:
            raise Exception('ada')
            print strip_docstring(
                handle_program.__doc__ % {
                    'program': program_name,
                }
            )
        sys.exit(0)
    else:
        if not command:
            raise getopt.GetoptError("No command specified.")
        # Are they asking for command help:
        if command_options.has_key('help'):
            # if so provide it no matter what other options are given
            if not command_handlers.has_key(command):
                raise getopt.GetoptError('No such command %r'%command)
            if hasattr(help, command):
                print strip_docstring(
                    getattr(help, command) % {
                        'program': program_name,
                    }
                )
            else:
                print strip_docstring(
                    command_handlers[command].__doc__ % {
                        'program': program_name,
                    }
                )
            sys.exit(0)
        format="%(levelname)s: %(message)s"
        if program_options.has_key('verbose'):
            verbose_options = []
            for option in program_options['verbose']:
                verbose_options.append(option['name'])
            verbose_option_names = option_names_from_option_list(
                [option_sets['verbose'][0]]
            )
            quiet_option_names = option_names_from_option_list(
                [option_sets['verbose'][1]]
            )
            if len(verbose_options) > 1:
                raise getopt.GetoptError(
                    "Only specify one of %s"%(
                        ', '.join(verbose_options)
                    )
                )
            elif verbose_options[0] in quiet_option_names:
                logging.basicConfig(level=logging.ERROR, format=format)
            elif verbose_options[0] in verbose_option_names:
                logging.basicConfig(level=logging.DEBUG, format=format)
        else:
            logging.basicConfig(level=logging.INFO, format=format)
        # Now handle the command options and arguments
        command_handlers[command](option_sets, command_options, args)


