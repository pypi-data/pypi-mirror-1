import operator
from pprint import pprint
from freeform.match import *
from freeform.match import _fieldtype_reprtab_compact

from freeform.formtable import compile, create_formtable
from time import clock

try:
    import hotshot, hotshot.stats
    PROFILE=1
except ImportError:
    PROFILE=0

def profile_match_scentence(compiler, profilefile, sourcenames, sources, test_inputs,
    numruns=4,
    xmatch_scentence=match_scentence,
    xformtable_prepare=formtable_prepare):
    global PROFILE
    compiler = compiler or Compiler()
    errors = []
    productions = []
    results=[]
    clocks=[]
    
    # 'disambiguate_on_singular_param_position'
    #  'plural_params_at_arbitrary_positions'
    profilefile = numruns > 1 and profilefile or profilefile
    PROFILE=profilefile and PROFILE or 0
    if PROFILE:
        prof = hotshot.Profile(profilefile, 1)
    numinputs=0

    formtables={}
    for name in sourcenames:
        #outs,e = compile([sources[name]], compiler)
        #cs=outs[0]        
        cs,e = compiler([sources[name]])
        errors.append(e)        
        formtable = create_formtable(*cs)        
        formtable=xformtable_prepare(formtable)
        formtables[name] = formtable
        
    
    allsuccess=True
    allmsgs=[]
    for name in sourcenames:
        formtable=formtables[name]
        inputs = test_inputs[name]
        tick = 0
        for i in range(0,numruns):
            tick=clock()-tick
            for input,expect in inputs:
                numinputs+=1
                words = input.split()
                if i == 0:
                    match,productions = xmatch_scentence(formtable, words)
                    results.append((words,expect,match,productions))
                elif PROFILE:
                    prof.runcall(xmatch_scentence, formtable, words)
                else:
                    xmatch_scentence(formtable, words)
            tick=clock()-tick
        clocks.append(tick)
        success=True
        verbose=not PROFILE and True or False
        #verbose=True
        success, msg = format_results(formtable, results, verbose)
        results[:]=[]
        if not success:
            allmsgs.append(sources[name])
        allsuccess = allsuccess and success
        allmsgs.append('[%s]\n%s' % (name,msg))
        allmsgs.append('-' * 40)

    if PROFILE:
        prof.close()
        stats = hotshot.stats.load(profilefile)
        stats.strip_dirs()
        stats.sort_stats('time')
        stats.print_stats(40)
    minclocks = min(clocks)
    
    allmsgs.append("clock(match_scentence):\n\ttot=%s\n\tpercal=%s\n\t#calls=%s" % (
        minclocks, minclocks / numinputs,numinputs))
    allmsgs.append("tests:%s" % (allsuccess and "OK" or "FAILED"))
    return allsuccess, allmsgs
            
def profile_levenshtein(profilefile, sourcenames, sources, test_inputs):
    raise Exception("Needs porting") 
    compiler = Compiler()
    PROFILE = profilefile and 1 or 0
    allsuccess
    for name in sourcenames:
        verbose=True
        name = 'plural_params_at_arbitrary_positions'
        name = 'disambiguate_on_singular_param_position'
        outs,e = compile([sources[name]], compiler)
        cs=outs[0]
        formtable = formtable_prepare(create_formtable(*cs))
        errors.append(e)
        allmatchwords = formtable['allmatchwords']
        asequence=allmatchwords.keys()
        maxlen=reduce(max,map(len, asequence))
        counter=0
        inputs = [(input.split(), expect) for input,expect in test_inputs[name]]
        for words,expect in inputs:
            counter += len(words)
        clocks1=[]
        clocks2=[]
        tick1=clock()
        tick2=clock()
        for i in range(0,50):
            tick2=clock()-tick2
            for words,expect in inputs:
                for word in words:
                    for a in asequence:
                        if levenshtein_distance(a, word)==0:
                            break
                #match,productions = match_scentence_plurals(formtable, words)
                #results.append((words,expect,match,productions))   
            #success, msg = format_results(formtable, results, verbose)
            tick2=clock()-tick2
            tick1=clock()-tick1
            for words,expect in inputs:
                for word in words:
                    #levenshtein_selectone(asequence, word)
                    _levenshtein_select(asequence, word, None, maxlen)
                #match,productions = match_scentence_plurals(formtable, words)
                #results.append((words,expect,match,productions))
            tick1=clock()-tick1   
        counter *= 50
        msg = "levenshtien_selectone: %s,%s, levenshtein_distance: %s,%s" % (tick1,tick1/counter,tick2,tick2/counter)
        print msg
        print "tests:%s" % (tick1 < tick2 and "OK" or "FAILED")
        raise SystemExit

def format_results(formtable, results, verbose=True):
    allsuccess=True
    msgs=[]
    formfieldnames=formtable['form2fieldnames']
    formfieldtypes = formtable['form2fieldtypes']
    fieldtypeforms = formtable['field2fieldtypes']
    formfieldselectvalues = formtable['form2fieldselectvalues']
    for input, expect, match, productions in results:
        success,msg=True,'ok'
        if productions:
            productions = [
                (formtable['form2command'][formid],
                 [formfieldnames[formid], 
                    map(_fieldtype_reprtab_compact.get, 
                        formfieldtypes[formid]), match])
                    for formid in productions]
            if False and verbose:
                msg='\n'.join([
                    'Words: "%s"' % ' '.join(input),
                    'Matched: "%s"' % ' '.join(map(str,match))])
            if isinstance(expect, tuple):
                expect, expect_match = expect
            else:
                expect, expect_match = expect, None
            if len(productions)==1 and productions[0][0] == expect:
                if expect_match:
                    if not reduce(operator.and_, 
                        map(operator.eq, expect_match, productions[0][1][2])):
                        success,msg=(False, 
                                'Failed, matched [%s] as expected, but the '
                                'parameters were not recognised in the expected manner.'
                                '\n\tgot %s'
                                '\n\texp %s' % (
                            expect, repr(productions[0][1][2]), repr(expect_match)))
                if verbose and success:
                    msg='Success, %s' % (
                        '%s <= %s' % (productions[0][0], ' '.join(
                            ['%s:%s=%s' % (t,n,m) 
                            for n,t,m in zip(*productions[0][1])])))
            else:
                if len(productions) == 1:
                    success,msg = (False, 
                        'Matched [%s], expected [%s]' % (
                            productions[0][0], repr(expect)))
                elif isinstance(expect, str) or (
                        len(productions) != len(expect)):
                    success,msg = (False,
                        'Unexpected ambiguous match.'
                        '%s vs %s' % (repr(expect), repr(productions)))
                else:
                    matched_cmds=[]
                    for i,((cmd,_),ex) in enumerate(zip(productions,expect)):
                        if isinstance(ex, tuple):
                            ex, ex_match = ex
                        else:
                            ex, ex_match = ex, None
                        if cmd != ex:
                            success,msg=(False,
                                'Got an expected ambiguous match but '
                                'for the wrong forms. %s not in %s. [%s]' % (
                                    cmd, ','.join(map(operator.getitem(0), expect))),
                                    str(i))
                        elif ex_match and not reduce(operator.and_, 
                                map(operator.eq, ex_match, productions[0][1][2])):
                                success,msg=(False, 
                                        'Failed, ambiguous match [%s] vs [%s] as '
                                        'expected, but the parameters were not '
                                        'recognised in the expected manner. [%s]'
                                        '\n\tgot %s'
                                        '\n\texp %s' % (
                                    ex, ','.join(map(operator.getitem(0), expect)),
                                    str(i),
                                    repr(productions[0][1][2]), repr(ex_match)))
                        else:
                            matched_cmds.append(cmd)
                    if verbose and success:
                        msg=('Success, got the expected ambiguous match: '
                             '%s <= [%s]') % (','.join(matched_cmds), ' '.join(input))
        else:
            if expect:
                success,msg=(False,'Failed to produce expected match.\n\t'
                        '%s <!= "%s", productions:%s' % (
                        expect, ' '.join(input), repr(productions)))
            else:
                if verbose:
                    msg = ('Success, bad scentence [%s] did not match '
                           'anything.') % ' '.join(input)
        if msg is 'ok' and verbose:
            msgs.append(msg)
        else:
            msg is not 'ok' and msgs.append(msg)
        allsuccess = allsuccess and success
    if allsuccess:
        msgs.append('OK')
    return allsuccess, '\n'.join(msgs)
