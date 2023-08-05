"""formtable: compiles form descriptions  for use by `freeform.match`

"""

import operator, re
from match import *
from match import _fieldtype_reprtab

__all__=[
    'DefinitionErrors', 
    'compile', 'compile_source', 'yield_forms', 'yield_fields',
    'create_formtable',
    ]

class DefinitionErrors(Exception): pass

def create_formtable(commands, forms):
    """Create a formtable.

    create_formtable will take input of the format returned by `compile` and
    produce a formtable. This can then be used to match the described phrases 
    in a reasonably efficient manner and, importantly, compensate reliably for
    user finger trouble.
    
    Note: it should be possible to dynamicaly patch list and menu entries by
    pokeing the formtable directly, (ie dynamicaly filled menus). However 
    support for easily doing this is incomplete.
    """ 
    
    maxfieldtypes = len([k for k in _fieldtype_reprtab.keys() if k >=0])
    longestformlen=0
    form2command=[form[0] for form in forms]
    form2fieldtypes=[]
    form2fieldnames=[]
    form2fieldselectvalues=[]
    formtable=[
        form2fieldtypes, form2fieldnames, 
        form2fieldselectvalues]
    for formid, (cmd, form) in enumerate(forms):
        fieldtypes = map(operator.itemgetter(0), form)
        fieldnames = map(operator.itemgetter(1), form)
        fieldselectvalues = map(operator.itemgetter(2), form)
        formproperties=[
            fieldtypes, fieldnames, fieldselectvalues]
        for iproperty, property in enumerate(formproperties):                
            formtable[iproperty].append(property)

        if longestformlen < len(form):
            longestformlen = len(form)
            
    for propertytable in formtable:
        for formproperties in propertytable:
            formproperties.extend([None] * (longestformlen - len(formproperties)))

    formcount = len(forms)
    
    # compute the transpose
    tformtable = [[[] for ifield in range(0,longestformlen)] 
                    for propertytable in formtable]
    for iproperty in range(0, len(formtable)):
        for ifield in range(0, longestformlen):
            for formid in range(0, formcount):
                tformtable[iproperty][ifield].append(
                    formtable[iproperty][formid][ifield])
    field2fieldtypes = tformtable[0]
    field2fieldnames = tformtable[1]
    field2selectvalues = tformtable[2]
    return dict([
        ('formcount', formcount),
        ('maxfieldcount', longestformlen),
        ('maxfieldtypes',maxfieldtypes),
        ('form2command',form2command),
        ('form2fieldtypes',form2fieldtypes),
        ('form2fieldnames', form2fieldnames),
        ('form2fieldselectvalues', form2fieldselectvalues),
        ('field2fieldtypes', field2fieldtypes),
        ('field2fieldnames', field2fieldnames),
        ('field2selectvalues',field2selectvalues)])

MATCH_CMD_START=re.compile(r'(?P<NAME>[a-zA-Z_]\w*)\s*:\s*').match
MATCH_CMD_END=re.compile(r';\s*').match
MATCH_CEND_OR_FSEP=re.compile(r'(?P<CEND>;\s*)|(?P<FSEP>,\s*)').match
_CENDCHAR=';'

# there is nothing critical about the leagal start characters for keywords.
# freeform doesn't care. the only hard restriction, due to the form compiler,
# rather than the match algorithim, is that a keyword may not
# contain any of '{', ';'. Note that it _can_ contain any punctuation 
# character, including '.','@', etc.. If you _realy_ need every last drop
# of flexibility you could  hand code your form definition.

MATCH_KW=re.compile(r'(?P<NAME>[-\.]?\w+[^\s;\{]*\w)\s*').match

MATCH_WW=re.compile(r'\{\s*(?P<NAME>\w*?)\s*\(\s*s\s*\)\s*\}\s*').match
MATCH_WO=re.compile(r'\{\s*(?P<NAME>\w*?)\s*\}\s*').match
MATCH_ME=re.compile(
        r'\{\s*(?P<NAME>\w*?)\s*\(\s*menu\s+'
        r'(?P<variants>\w*?)\s*\)\s*\}\s*').match
MATCH_LI_START=re.compile(r'\{\s*(?P<NAME>\w*?)\s*\(\s*list\s+').match
MATCH_LM_menu=re.compile(r'\s*menu\s*(?P<variants>\w+)\s*').match
MATCH_paramlist=re.compile(r'((\s*\w+\s*))(,(\s*\w+\s*))*[.]').match
MATCH_LILM_END=re.compile(r'\s*\)\s*\}\s*').match

def compile(sources, commands=None, forms=None):
    if commands is None: commands = {}
    if forms is None: forms = []
    brokenforms=[]
    
    for i, source in enumerate(sources):
        source = source.strip()
        (pos, c, f, e) = compile_source(
            source, commands, forms)
        e and brokenforms.extend(e)
    if brokenforms:
        raise DefinitionErrors(commands, forms, brokenforms)
    return (commands,forms),brokenforms 

def compile_source(source, commands=None, forms=None, pos=0):
    if commands is None: commands={}
    if forms is None: forms = []
    brokenforms=[]
    # easier to strip the coment lines in one pass
    source = '\n'.join((line for line in source.split('\n') 
        if not line.startswith('#')))
    while 1:
        match=MATCH_CMD_START(source[pos:])
        if not match:
            return pos, commands, forms, brokenforms
        pos += match.span()[-1]
        command=match.group('NAME')
        commandforms=commands.setdefault(command, [])
        for pos, form, error in yield_forms(source, pos):
            # error may be informative warning. if the error was
            # unrecoverable the last field considered will be marked
            # invalid
            if form and form[-1][0] is not FIELDTYPE_INVALID:
                commandforms.append(len(forms))
                forms.append((command, form))
            else:
                brokenforms.append((command, form))

def yield_forms(source, pos=0):
    CENDCHAR=_CENDCHAR
    while 1:
        form=[]
        for pos, fieldtype, name, details in yield_fields(source, pos):
            form.append((fieldtype, name, details))
            if fieldtype is FIELDTYPE_INVALID:        
                yield pos, form, details[0]
                return
        match = MATCH_CEND_OR_FSEP(source[pos:])
        if not match:
            yield pos, form, 'ERR_GRAMATICAL1:unterminated form definition list'
            return
        group = match.group('FSEP') or match.group('CEND')
        pos += match.span()[-1]
        yield pos, form, None
        if group[0] == CENDCHAR:
            return
        
def yield_fields(source, pos=0):
    produced = None
    while 1:
        for (matcher,fieldtype) in [
            (MATCH_WW, FIELDTYPE_WORDS), 
            (MATCH_WO, FIELDTYPE_WORD), 
            (MATCH_ME, FIELDTYPE_MENU), 
            (MATCH_LI_START, FIELDTYPE_UNKNOWN),
            (MATCH_KW, FIELDTYPE_KEYWORD)]:
            match=matcher(source[pos:])
            if not match:
                continue
            pos += match.span()[-1]
            name=match.group('NAME')
            if matcher is not MATCH_LI_START:
                produced = (fieldtype, name, 
                    (fieldtype is FIELDTYPE_MENU 
                        and [c for c in match.group('variants')])
                    or 
                    (fieldtype is FIELDTYPE_KEYWORD and [name])
                    or [])
                break
            listmatch=MATCH_paramlist(source[pos:])
            if not listmatch:
                produced = (FIELDTYPE_INVALID, name, 
                    ['TOKENERROR1:bad list or listmenu field', source[pos:], 
                        [match]])
                break
            listparams = [variant.strip() for variant in 
                    listmatch.group(0).split('.')[0].split(',')]
            
            pos += listmatch.span()[-1]
            menumatch=MATCH_LM_menu(source[pos:])
            if not menumatch:
                menuend=MATCH_LILM_END(source[pos:])
                if not menuend:
                    produced = (FIELDTYPE_INVALID, name,
                            ['TOKENERROR2:badly terminated list parameters', 
                                source[:pos],
                            [match, listmatch, listparams]])
                    break
                pos += menuend.span()[-1]
                produced = (FIELDTYPE_LIST, name, listparams)
                break
            pos += menumatch.span()[-1]
            listmenuend=MATCH_LILM_END(source[pos:])
            if not listmenuend:
                produced = (FIELDTYPE_INVALID, name,
                    ['TOKENERROR4:badly terminated menu parameters in listmenu field',
                    source[pos:], 
                        [match,listmatch,menumatch]])
                break
            pos+=listmenuend.span()[-1]
            produced =  (FIELDTYPE_LISTMENU, name, 
                [listparams, [c for c in menumatch.group('variants')]])
            break
                
        if produced:
            yield (pos,)+produced
            produced = None
        else:
            return
