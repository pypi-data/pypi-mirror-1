"""usage: %prog [-Rr][-d][-I] files or pkg_resouces

compiler front end. Use this to test & develop your command sets or as example
code, see formtable.tool.py` to develop your own tools.

`pgk_resources` should be listed as `requirement:resource` or just `resource`. 
If you use the later you must specify the requirement, used for all, using `-R`.

`files` are just filesystem paths.

`-I` will drop you into a very limited interactive shell. The banner will 
indicate the results, and hence the recognisable forms, gleaned from your 
argument sources.

If `-I` is not specified the tool attempts to read from the standard input.


non interactive use::
    
    cat sample_input | freeformc .freeform/data/session.ffb

interactive use::

    freeformc -I ./freeform/data/session.ffb

or substitute your own sources for `session.ffb`. The extention is not magic
in any way.
"""

__all__=[
    'compile_tool',  
    'compile_aggregate_resources', 'compile_aggregate_files',

    'add_options_compile_tool'
    ]
import sys, optparse
try:
    import pkg_resources
except ImportError:
    pkg_resources = None
from pprint import pprint
from freeform.match import *
from freeform.formtable import *

def add_options_compile_tool(parser):
    if pkg_resources:
        parser.add_option('-R', '--requirement',
            help='Specify the default pkg_resources requirement for the '
                 'argument freeform resources. This option MUST be specified '
                 'if -r is set AND ANY of your arguments are not of the form '
                 '"requirement:resource".',
            default=None)
        parser.add_option('-r', '--resource-sources', action='store_true',
            help='Set to indicate the command line arguments are setuptools '
                 'pkg_resources resources. Default [false]',
            default=False)
            
    parser.add_option('-d','--input-data-file',
            default=None,
            help='Read input from file rather than stdin')
    parser.add_option('-I', '--interpreter-shell', 
            action='store_true',
            default=False,
            help='a very basic shell')
    parser.add_option('-V','--verbose', action="store_true",
            default=False)
    
def compile_tool():
    parser = optparse.OptionParser(
        usage=sys.modules[__name__].__doc__)
    add_options_compile_tool(parser)    
    options, names = parser.parse_args()
    input = sys.stdin
    if options.input_data_file:
        input = open(options.input_data_file)
    if pkg_resources and options.resource_sources:
        for n in names:
            n=n.split(':',1)
            if len(n)==2:
                requirement,resource = pkg_resources.Requirement(n[0]),n[1]
            else:
                if not options.requirement:
                    print ('[ERROR] using pkg_resources arguments requires '
                           'you either specify -R defaultrequirement, OR '
                           'you format each of the arguments as '
                           '"requirement:resource".')
                    raise SystemExit
                requirement,resource=pkg_resources.Requirement(
                    options.requirement),n[0]
            resources.append((requirement, resource))
        ft, e, s = compile_aggregate_resources(resources)
    else:
        ft, e, s = compile_aggregate_files(names) 
    if e:
        pprint(e)
    
    formtable_prepare(ft)
    if options.verbose:
        pprint(ft)

    # prepare a banner decribing the forms we can match based on the supplied
    # sources.
    banner = (
        "\nEnter input corresponding to any of the following forms:\n%s"
        "\n\ncompiled from sources:\n%s"
            % (' \n'.join(['%s: %s' % describe_form(ft, formid)
        for formid in range(0, len(ft['form2command']))]),s))
            
    if options.interpreter_shell:
        run_shell(ft, banner, input)
    else: 
        # read user input from file or stdin and print the match results. 
        for line in input.readlines():
            line=line.strip()
            match,details = match_command(ft,line.split())
            print match_input(ft, line)

def match_input(formtable, line):
    match,details = match_command(formtable,line.split())
    if type(details)==type({}):
        _,form=match
        return '%s: %s' % tuple(describe_form(formtable, form, **details))   
    if match is None and not len(details):
        return "<*** no match ***> for:'%s'" % line
    return '\n'.join(
        ["<*** ambiguouse match ***> for:'%s'" % line]+
            ['%s: ?= %s' % describe_form(formtable,formid) 
             for formid in details])

def describe_form(formtable, formid, **valuemap):
    try:
        command = formtable['form2command'][formid]
    except IndexError:
        return 'unknown',''
    ftypes=formtable['form2fieldtypes'][formid]
    fnames=formtable['form2fieldnames'][formid]
    matchdesc = ' '.join(['%s.%s=%s' % (
            repr_fieldtype_compact(t), n, 
            (t == FIELDTYPE_KEYWORD and n or valuemap.get(n,'?'))
        )
        for t,n in zip(ftypes,fnames) if n])
    return command, matchdesc
    
def compile_aggregate_resources(resources, compiler=None):
    compiler = compiler or compile
    sources = [pkg_resources.resource_string(*resource) 
        for resource in [
            ((not isinstance(req, pkg_resources.Requirement) and
              pkg_resources.Requirement.parse(req)) or req,res)
            for req,res in resources]]
    (c,f), e = compile(sources)
    ft = create_formtable(c,f)
    return ft, e, ''.join(sources)

def compile_aggregate_files(files, compiler=None):
    compiler = compiler or compile
    errors, sources = [],[]
    for f in files:
        try:
            sources.append(file(f,'r').read())
        except IOError, e:
            errors.append(e)
    (c,f), e = compile(sources)
    ft=create_formtable(c,f)
    return ft, e, ''.join(sources)

def run_shell(formtable, banner, input, fshell=None):
    if not fshell:
        from cmd import Cmd
        class FreeformShell(Cmd):
            prompt='freeform:'
            def default(self, x):
                print x
            def precmd(self, line):
                matched = match_input(formtable, line)
                return matched
        fshell = FreeformShell(None, input)
    try:
        fshell.cmdloop(banner)
    except KeyboardInterrupt, e:
        raise SystemExit


if __name__ == '__main__':
    from os import environ
    if environ.get('FREEFORM_DEBUG',None):
        import wingdbstub   
    compile_tool()
