from heapq import *
from freeform.levenshtein import *
from freeform.match import *
from freeform.formtable import *
from freeform.match import _fieldtype_reprtab
from freeform.levenshtein import _levenshtein_firstcol, _levenshtein_firstrow
from profile_match import profile_match_scentence, format_results

from freeform import levenshtein
import unittest

def _xxx_match_scentence_noplurals(formtable, words):
    """Match a scentence.

    Assumes there are no forms in formtable that use plurals"""

    wordcount = len(words)
    maxfieldcount = formtable['maxfieldcount']
    tymatch = formtable['tymatch']
    tyflags = formtable['tyflags']
    tyformids = formtable['tystartformids']
    tyselects = formtable['tyselects']
    matchfieldforms = formtable['matchfieldforms']
    fieldcount = min(maxfieldcount, wordcount)
    ilastfield = fieldcount - 1
    match=[]
    TYEND=-2 #assumes typrecedence is such that WO,WW are the last two elments.
    for ifield in range(0, fieldcount):
        candidatenextformids = None
        for matchfn,selects,formids in zip(
                tymatch[:TYEND], tyselects[:TYEND], tyformids[:TYEND]):
            matched = matchfn(selects, words[ifield], ifield, formids)
            if matched:
                match.append(matched)
                # optimisation
                if len(matched) > 1: # not a menu item match
                    ffs=matchfieldforms.get(matched,[0,[],[],{}])[-1].get(ifield, [])
                    formids = [formid for formid in formids if formid in ffs]
                candidatenextformids = formids
                if ifield < ilastfield:
                    tyformids = _nextforms(formids, ifield, tyflags)
                break               
        if not candidatenextformids:
            # assume a word match, candidates are then all the remaining
            # forms that have a WORD at this position.
            match.append(words[ifield])
            candidatenextformids = tyformids[TYEND]
            if ifield < ilastfield:
                tyformids = _nextforms(tyformids[TYEND], ifield, tyflags)
        if not candidatenextformids:
            break
    return match, candidatenextformids

def debug():
    # 'disambiguate_on_singular_param_position'
    #  'plural_params_at_arbitrary_positions'
    sources = dict(TestDisambiguation.sources)    
    test_inputs = dict(TestDisambiguation.source_tests)
    verbose = False
    while 1 and not verbose:
        for (verbose,numruns,profilefile,xmatch_scentence,xformtable_prepare) in [
                (True, 1, None and 'profile.log', match_scentence, formtable_prepare)
                ]:
            allsucces,allmsgs=profile_match_scentence(
                compile,
                profilefile,
                    [
                     'menu_vs_listmenu',
                     'disambiguate_on_singular_param_position',
                     'plural_params_at_arbitrary_positions',
                     'pylon_session_commands'
                     ],
                    sources, test_inputs, numruns, 
                    xmatch_scentence, xformtable_prepare)
            print '\n'.join(verbose and allmsgs or allmsgs[-2:])
            if verbose:
                break

class TestCompiler(unittest.TestCase):
    def test_commandset_construction(self):
        for (sourcename, source) in TestDisambiguation.sources:
            (commands,forms),brokenforms = compile([source])
            for cmd,formids in commands.items():
                for formid in formids:
                    self.assertEqual(forms[formid][0], cmd)


class TestLevenshtein(unittest.TestCase):

    def reset_levenshtein(self):
        global _levenshtein_maxwordrange, _levenshtein_firstcol, _levenshtein_firstrow
        levenshtein._levenshtein_maxwordrange = 0
        _levenshtein_firstcol[:]=[]
        _levenshtein_firstrow[:]=[]
        pass

    def setUp(self):
        self.reset_levenshtein()

    def test_firstinit(self):
        # this test fails if bindconst is used
        global _levenshtein_maxwordrange, _levenshtein_firstcol, _levenshtein_firstrow
        fcolcache = _levenshtein_firstcol
        frowcache = _levenshtein_firstrow
        def maxwordlen():
            return max(len(fcolcache), len(frowcache))
        self.assertEqual(levenshtein_distance('foobar','foobar'), 0, 
                'warmup: LD(foobar,foobar) == 0')
        self.assertEqual(maxwordlen(), len('foobar') + 1)
        self.assertNotEqual(levenshtein_distance('foobarfoobar', 'foobar'), 0)
        self.assertEqual(maxwordlen(), len('foobarfoobar') + 1)
        idoffirstelement = id(_levenshtein_firstrow[0])
        self.assertNotEqual(levenshtein_distance('foobar', 'foobarfoobar'), 0)
        self.assertEqual(maxwordlen(), len('foobarfoobar') + 1)
        self.assertEqual(idoffirstelement, id(_levenshtein_firstrow[0]),
            "[issue:optimization] initial row data is being rebuilt un-necessarily")
        
    def test_levenshtein_selectfrom(self):
        
        # a very pathological case
        i,d = levenshtein_selectone(['apple', 'apple', 'apple'], 'param')
        self.assertEqual((-1,LEVENSHTEIN_DEFAULT_MAXDIST), (i,d))


        # this is a somewhat pathological case
        i,d = levenshtein_selectone(['aabaa', 'aacaa', 'aadaa'], 'aaaaa')
        self.assertEqual((i,d),(0,1))
        
        # this matches after a single test on 'apple','orange' and 'pear', 'orange'
        # and a full consideration of 'orange','orange'
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'orange')
        self.assertEqual((i,d), (2,0))
        # this matches on first pass as 'aaaaa' is first and the duplicate is
        # redundant.
        i,d = levenshtein_selectone(['aaaaa', 'aabaa', 'aaaaa'], 'aaaaa')
        self.assertEqual((i,d), (0,0))
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'apple')
        self.assertEqual(i,0)
        self.assertEqual(d,0)
        self.assertEqual(d, levenshtein_distance('apple', 'apple'))
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'orange')
        self.assertEqual(i,2)
        self.assertEqual(d,0)
        self.assertEqual(d, levenshtein_distance('orange', 'orange'))

        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'pear')
        self.assertEqual(i,1)
        self.assertEqual(d,0)
        self.assertEqual(
            d, levenshtein_distance('pear', 'pear'))
        for x, (from_, match) in enumerate([
            (['aaaaa', 'baaaa', 'caaaa'], 'aaaaa'),
            (['aaaaa', 'baaaa', 'caaaa'], 'baaaa'),
            (['aaaaa', 'baaaa', 'caaaa'], 'caaaa'),
            (['aaaaa', 'aaaab', 'aaaac'], 'aaaaa'),
            (['aaaaa', 'aaaab', 'aaaac'], 'aaaab'),
            (['aaaaa', 'aaaab', 'aaaac'], 'aaaac')]):
            i,d = levenshtein_selectone(from_, match)
            self.assertEqual(i, x % 3)
            self.assertEqual(d, levenshtein_distance(from_[x % 3], match))
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'paple')
        self.assertEqual(i,0)
        self.assertEqual(d,2)
        self.assertEqual(
            d, levenshtein_distance('apple', 'paple'))
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'roange')
        self.assertEqual(i,2); self.assertEqual(d,2); self.assertEqual(
            d, levenshtein_distance('orange', 'roange'))
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'epar')
        self.assertEqual(i,1); self.assertEqual(d,2); self.assertEqual(
            d, levenshtein_distance('pear', 'epar'))
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'appel')
        self.assertEqual(i,0); self.assertEqual(d,2); self.assertEqual(
            d, levenshtein_distance('apple', 'appel'))
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'oraneg')
        self.assertEqual(i,2); self.assertEqual(d,2); self.assertEqual(
            d, levenshtein_distance('orange', 'oraneg'))
        i,d = levenshtein_selectone(['apple', 'pear', 'orange'], 'pera')
        self.assertEqual(i,1); self.assertEqual(d,2); self.assertEqual(
            d, levenshtein_distance('pear', 'pera'))
        
    def test_levenshtein_selectfrom_reentry(self):
        asequence = ['apple', 'apple', 'apple']
        state = _levenshtein_select(asequence, 'appel')
        htop = heappop(state[1])
        i,d = htop[-1], htop[0]
        self.assertEqual((0,2), (i,d))
        #asequence[htop[-1], htop[-1]+1]=[]
        state = _levenshtein_select(asequence, 'appel', None, 0, 0, state)
        htop = heappop(state[1])
        i,d = htop[-1],htop[0]
        self.assertEqual((1,2), (i,d))
        #print repr(state[1])
        #self.assert_(not state[1])
        # Re-entering _levenshtein_select with a single item heap should raise IndexError
        # If there is only one entry left you don't need to call again.
        self.assertRaises(
            IndexError, _levenshtein_select, asequence, 'appel', None, 0, 0, state)

class TestDisambiguation(unittest.TestCase):
    def _generic_source_tests(self, name, compiler = None):
        compiler = compiler or self.compiler
        msgs=[]
        results=[]
        commandforms,e = compiler([self.sources[name]])
        formtable = create_formtable(*commandforms)
        self.assert_(not e, '\n'.join(e))
        formtable=formtable_prepare(formtable)
        results=[]
        for input,expect in self.source_tests[name]:
            words = input.split()
            match,productions = match_scentence(formtable, words)
            results.append((words,expect,match,productions))
        success,msg = self._process_match_results(formtable, results)
        return success, msg
    
    def setUp(self):
        self.compiler = compile
        self.sources = dict(self.sources)
        self.source_tests = dict(self.source_tests)
    def test_token_const_assumptions(self):        
        for i in range(0, max(_fieldtype_reprtab.keys()) + 1):
            self.assertEqual(_fieldtype_reprtab.has_key(i), True)

    def _process_match_results(self, formtable, results):
        return format_results(formtable, results)
    def test_menu_precedence_trumps_listmenu(self):
        success, msg = self._generic_source_tests('menu_vs_listmenu')
        self.assert_(success, msg)        
    def test_singular_param_disambiguation(self):
        success, msg = self._generic_source_tests(
            'disambiguate_on_singular_param_position')
        self.assert_(success, msg)
    def test_plural_params_at_arbitrary_positions(self):
        success, msg = self._generic_source_tests(
            'plural_params_at_arbitrary_positions')
        self.assert_(success, msg)

    source_tests = [
        ('menu_vs_listmenu',
            [('apple pear a bannana e', 
                [('cmd_m',['apple', 'pear', 'a', 'bannana', 'e']),
                 ('cmd_lm',['apple', 'pear', 'a', 'bannana', 'e'])]
                ),
             ('apple pear carrot bannana e', 
                 ('cmd_lm',['apple', 'pear', 'carrot', 'bannana', 'e'])),
             ('apple pear carrot bannana pepper', ['cmd_lm','cmd_lm2']),
             ('apple pear a bannana pepper', 'cmd_lm'),
             ('apple pear y bannana pepper', 'cmd_lm2')
            ]),
        ('disambiguate_on_singular_param_position',
            [
             ('apple pear a bannana e', 
                [('cmd_e',['apple', 'pear', 'a', 'bannana', 'e']),
                 ('cmd_g',['apple', 'pear', 'a', 'bannana', 'e'])]),
             ('parsnip apple pear e bannana', 'cmd_h'),
             ('apple pear param_a param_b bannana param_c', 
                 ('cmd_a',
                  ['apple', 'pear', 'param_a', 'param_b', 'bannana', 'param_c'])),
             ('apple param_a pear param_b bannana param_c', ''),
             ('apple param_a pear param_b param_c bannana', 
                 ('cmd_c',
                     ['apple', 'param_a', 'pear', 'param_b', 'param_c', 'bannana'])),
             ('apple pear param_a bannana param_b param_c', 
                 ('cmd_d',
                     ['apple', 'pear', 'param_a', 'bannana', 'param_b', 'param_c'])),
             ('param_a apple pear param_b param_c bannana', 
                 ('cmd_b',
                     ['param_a', 'apple', 'pear', 'param_b', 'param_c', 'bannana'])),
             ('param_a apple pear carrot param_c bannana', 
                 ('cmd_i',
                     ['param_a', 'apple', 'pear', 'carrot', 'param_c', 'bannana'])),
            ('parsnip apple pear x bannana', '')

             ]),
        ('plural_params_at_arbitrary_positions',
            [('apple pear param_a param_b bannana foo bar bannana bannana', 
                ('cmd_a',['apple', 'pear', 'param_a', 'param_b', 'bannana', 
                            ['foo', 'bar', 'bannana', 'bannana']])),
             ('apple pear param_a param_b foo bar bannana', 
                 ('cmd_b',['apple', 'pear', 'param_a', 'param_b', 
                            ['foo', 'bar'], 'bannana'])),
             ('param_a apple pear param_b foo bar bannana bannana', 
                 ('cmd_c',['param_a', 'apple', 'pear', 'param_b', 
                            ['foo', 'bar', 'bannana'], 'bannana'])),
             ('param_a apple pear param_b foo bar bannana bannana', 
                 ('cmd_c',['param_a', 'apple', 'pear', 'param_b', 
                            ['foo', 'bar', 'bannana'], 'bannana'])),
             ('param_a apple pear param_b foo bar bannana baz bannana', 
                 ('cmd_c',['param_a', 'apple', 'pear', 'param_b', 
                            ['foo', 'bar', 'bannana', 'baz'], 'bannana'])),
             ('param_a bannana pear param_b foo bar apple param_d orrange', 
                ('cmd_e', ['param_a', 'bannana', 'pear', 'param_b', ['foo', 'bar'], 
                    'apple', 'param_d', 'orrange'])),
             ('param_a bannana pear param_b foo bar apple baz apple param_d orrange', 
                ('cmd_e',['param_a', 'bannana', 'pear', 'param_b', 
                            ['foo', 'bar', 'apple', 'baz'], 
                            'apple', 'param_d', 'orrange']))
            ]),
         ('pylon_session_commands', [
            ('create account bakdog bakdog password',(
                'create_named_account', ['create', 'account', 'bakdog', 'bakdog', 'password']))
                ]),
       
        ]

    sources = [
        # menu_vs_listmenu
        #
        # forms that have menu and listmenu's in equivelent fields are ambiguous
        # if the menu part of the listmenu is equivelent, or a superset, of the
        # menu. however, menu's match with greater precedence than listmenus.
        # if the end user uses the short menu options for all fields that
        # have both menu and listmenu forms the menu form will match and the
        # listmenu form will be discarded. the result is un-ambiguous but
        # can cause surprise. however, if both forms are different forms
        # of the same logical command its what you'd expect. having both 
        # forms is a little redundant but will accelerate the match. menu
        # forms are faster to match than listmenu forms.
        ('menu_vs_listmenu',
             'cmd_m: apple pear {menu_a(menu abcd)} bannana {menu_b(menu efgh)};'
             'cmd_lm: apple pear {listmenu_a(list potatoe,carrot,turnip,parsnip. menu abcd)} bannana {listmenu_b(list salt,sugar,thyme,pepper. menu efgh)};'
             'cmd_lm2: apple pear {listmenu_a(list potator,carrot,turnip,parsnip. menu xyzw)} bannana {listmenu_b(list salt,sugar,thyme,pepper. menu lmno)};'),
   
        ('disambiguate_on_singular_param_position',
            'cmd_a: apple pear {param_a} {param_b} bannana {param_c};'
            'cmd_b: {param_a} apple pear {param_b} {param_c} bannana;'
            'cmd_c: apple {param_a} pear {param_b} {param_c} bannana;'
            'cmd_d: apple pear {param_a} bannana {param_b} {param_c};'
            'cmd_e: apple pear {menu_a(menu abcd)} bannana {menu_b(menu efgh)};'
            'cmd_f: {menu_a(menu abcd)} apple pear {menu_b(menu efgh)} bannana;'
            'cmd_g: apple pear {listmenu_a(list potatoe,carrot,turnip,parsnip. menu abcd)} bannana {listmenu_b(list salt,sugar,thyme,pepper. menu efgh)};'
            'cmd_h: {listmenu_a(list potatoe,carrot,turnip,parsnip. menu abcd)} apple pear {listmenu_b(list salt,sugar,thyme,pepper. menu efgh)} bannana;\n'
            'cmd_i: {param_a} apple pear {list_a(list potatoe,carrot,turnip,parsnip.)} {param_c} bannana;'),
        ('pylon_session_commands',
            'login: login {displayname} {password};\n'
            'create_named_account: create account {displayname} {password} {password_confirm};\n'
            'create_acccount_default_name: create account {password} {password_confirm};'),

    # cmd_a can be handled by disalowing plural params in any position other 
    # than the end of the phrase. in practice this covers most cases but 
    # results in un-natural, and hence harder to remember, commands.
    # cmd_b, can be handled by detecting the last instance of the last keyword
    # - bannana - and terminating the plural just before it. ie needs one fields
    # worth of lookahead.
    # cmd_c requires at two fields worth of lookahead, both param_b and param_c
    # are ambiguous until the last instance of bannana is encounterd.
    # cmd_d, cmd_e are the same as cmd_b, cmd_c but verify we are not dependent
    # on end of phrase for disambiguation. ie when considering both cmd_d, and 
    # cmd_e ambiguity in the plural param should be resolved before param_d is
    # considered.
    # cmd_f, cmd_g can not be disambiguated because the only differ in relative
    # order of two consecutive params, one of which is plural.
        ('plural_params_at_arbitrary_positions', 
            'cmd_a: apple pear {param_a} {param_b} bannana {param_c(s)};\n'
            'cmd_b: apple pear {param_a} {param_b} {param_c(s)} bannana;\n'
            'cmd_c: {param_a} apple pear {param_b} {param_c(s)} bannana;\n'
            'cmd_d: {param_a} pear apple {param_b(s)} {param_c} bannana;\n'
            'cmd_e: {param_a} bannana pear {param_b} {param_c(s)} apple {param_d} orrange;\n'
            'cmd_f: {param_a} bannana apple {param_b(s)} {param_c} pear {param_d} orrange;\n'
            'cmd_g: {param_a} pear bannana {param_b} {param_c(s)} apple {param_d} orrange;\n'
            'cmd_h: {param_a} pear bannana {param_b(s)} {param_c} apple {param_d} orrange;')]

    """

    plural params `{word(s)}`
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    the problem we are solving with plural params is to not require the user to
    escape or other wise use special syntax when they are entering free text
    that may contain command key words. command disambiguation is only achieved
    by order, possition and presence of keyword params and singular params.

    * can we support {param_a(s)} {param_b} ?
    
      termination of plural param with subsequent singular param. this is right
      recursive and requires backtracking. it is not possible to disambiguate two
      commands if the only distinction is the order of two consecutive
      parameters, on of which is plural and the other is not. eg.,
      
       foo {param_a} {param_b(s)} bar
       foo {param_a(s)} {param_b} bar 
       
      can _not_ be distinguished. 
      
    * can we support foo {param_a(s)} bar ?
    
      plural param may contain a keyword that should be interpreted as a param
      word. we want to terminate the plural param on the last word before the
      last instance of keyword 'bar'. this is right recursive and requires
      backtracking.
      
    """

if __name__=='__main__':
    from os import environ
    if environ.get('FREEFORM_DEBUG',None):
        import wingdbstub
        debug()   
    else:
        unittest.main()

