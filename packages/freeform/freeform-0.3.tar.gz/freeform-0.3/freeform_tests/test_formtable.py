import re
import unittest

from freeform.match import *
from freeform.formtable import *
from freeform.formtable import MATCH_KW, MATCH_WO, MATCH_WW, MATCH_ME
from freeform.formtable import MATCH_CMD_START, MATCH_CMD_END, MATCH_CEND_OR_FSEP
from freeform.formtable import MATCH_LI_START, MATCH_LM_menu, MATCH_paramlist
from freeform.formtable import MATCH_LILM_END
 
class TestPythonRECompiler(unittest.TestCase):
    
    def test_symbol_regexs(self):
        for input, expect in [
            ('wo.&@rd ', 'wo.&@rd '),
            ('keyword nextword', 'keyword '),
            ('keyword {param}', 'keyword '),
            ('_word ', '_word '),
            ('-word ', '-word '),
            ('word', 'word'),
            ('5word ', '5word '),
            ('@magic', None),
            ('who le', 'who '),
            ('who;le ', 'who'),
            ('who{le ', 'who'),
            ('who}le ', 'who}le '),
            ('doesntendwith;', 'doesntendwith')]:
            match = MATCH_KW(input)
            self.assertEqual(match and match.group(0) or match, expect)
            if match:
                self.assert_(expect.find(match.group('NAME')) >= 0)
        for input, expect, cend, fsep in [
            (';', ';', ';', None),
            (',', ',', None, ','),
            (';,', ';', ';', None),
            (',;', ',', None, ',') 
            ]:
            match=MATCH_CEND_OR_FSEP(input)
            self.assertEqual(match and match.group(0) or match, expect)
            self.assertEqual(cend or fsep, 
                cend and match.group('CEND') or
                fsep and match.group('FSEP') or match)
        for input, expect, name in [ 
            ('cmd_1 : ', 'cmd_1 : ', 'cmd_1'),
            ('1cmd_ : ', None, None),
            ('cmd:\n', 'cmd:\n', 'cmd')]:
            match = MATCH_CMD_START(input)
            self.assertEqual(match and match.group(0) or match, expect)
            if match:
                self.assertEqual(match.group('NAME'), name)
        self.assertEqual(
            MATCH_WW('{ foo (s )} bar').group(0), '{ foo (s )} ')
        self.assertEqual(
            MATCH_WW('{ foo (s )}bar').group(0), '{ foo (s )}')
        self.assertEqual(
            MATCH_WW('{ foo (s )} bar').group('NAME'), 'foo')
        self.assertEqual(
            MATCH_WW('{ foo (s )}bar').group('NAME'), 'foo')       
        self.assertEqual(
            MATCH_WW(' { foo (s )}bar'), None)
        self.assertEqual(
            MATCH_WW('bar{ foo (s )}'), None)
        self.assertEqual(
            MATCH_WO('{ foo } bar').group(0), '{ foo } ')
        self.assertEqual(
            MATCH_WO('{ foo }bar').group(0), '{ foo }')
        self.assertEqual(
            MATCH_WO('{ foo } bar').group('NAME'), 'foo')
        self.assertEqual(
            MATCH_WO('{ foo }bar').group('NAME'), 'foo')       
        self.assertEqual(
            MATCH_WO(' { foo }bar'), None)
        self.assertEqual(
            MATCH_WO('bar{ foo }'), None)
        self.assertEqual(
            MATCH_ME('{ foo (menu abc)} bar').group(0), '{ foo (menu abc)} ')
        self.assertEqual(
            MATCH_ME('{ foo ( menu abc )}bar').group(0), '{ foo ( menu abc )}')
        self.assertEqual(
            MATCH_ME('{ foo ( menu abc)} bar').group('NAME'), 'foo')
        self.assertEqual(
            MATCH_ME('{ foo ( menu abc )}bar').group('NAME'), 'foo')       
        self.assertEqual(
            MATCH_ME(' { foo (menu abc)} bar'), None)
        self.assertEqual(
            MATCH_ME('bar{ foo (menu abc)} bar'), None)
        self.assertEqual(
            MATCH_WO('{foo}{bar(s)}').group('NAME'), 'foo')
        self.assertEqual(
            MATCH_WW('{bar(s)} {foo}').group('NAME'), 'bar')
        for input, expect, name in [
            ('{foo(list)',None,None), 
            ('{foo(list )', '{foo(list ','foo'), 
            ('{foo(list x)', '{foo(list ','foo'),
            ('{ foo( list x{', '{ foo( list ','foo')]:
            match=MATCH_LI_START(input)
            self.assertEqual(match and match.group(0) or match, expect)
            if match:
                self.assertEqual(match.group('NAME'), name)
        for input, expect in [
            ('foo', None), ('foo ', None), ('foo bar.', None),
            ('foo.','foo.'), ('foo .', 'foo .'),
            ('foo,bar.', 'foo,bar.'),
            ('foo,bar,baz.', 'foo,bar,baz.'),
            ('foo, bar,baz , aba,1yx9.', 'foo, bar,baz , aba,1yx9.'),
            ('foo,   bar,baz  ,   aba,  1xy9...','foo,   bar,baz  ,   aba,  1xy9.')]:
            match = MATCH_paramlist(input)
            self.assertEqual(match and match.group(0) or match, expect)
        for input,expect in [
            (' )}', ' )}'), (')}', ')}'), (' ) }{', ' ) }'),
            ('.)}', None), ('foo', None), ('))}', None),
            (')}foo', ')}')]:
            match=MATCH_LILM_END(input)
            self.assertEqual(match and match.group(0) or match, expect)


    def test_fieldtype_tokenizer(self):
        WO=FIELDTYPE_WORD
        WW=FIELDTYPE_WORDS
        ME=FIELDTYPE_MENU
        LI=FIELDTYPE_LIST
        LM=FIELDTYPE_LISTMENU
        for formdef,expect in [
            ("{bar} {foo(s)} {baz(list aaa, bbb,ccc.)} {baz(menu xyz)}"
             " {pear(list foo,bar , baz. menu 123)} {apple}",
             [WO, WW, LI, ME, LM, WO]),
             ("{bar}{foo(s)}{baz(list aaa, bbb,ccc.)}{baz(menu xyz)}"
              "{pear(list foo,bar , baz. menu 123)}{apple}",
             [WO, WW, LI, ME, LM, WO])
            ]:
            for i, (pos,fieldtype, name, details) in enumerate(yield_fields(formdef)):
                self.assertEqual(fieldtype,expect[i])

    def test_compile_accumulates_results(self):
        commands,forms={},[]
        sources = [
            "cmd1:{aaa}{bbb},{ccc};cmd2:{aaa}{bbb};",
            "cmd2:{foo(list a,b,c.)};",
            "cmd_c: apple {param_a} pear {param_b} {param_c} bannana;"]
        (c,f),e = compile(sources,commands,forms)
        self.assertEqual(len(commands['cmd1']),2)
        self.assertEqual(len(commands['cmd2']),2)
        self.assertEqual(len(commands['cmd_c']),1)
        self.assert_(c is commands)
       
            
    def test_compile_commands(self):
        KW=FIELDTYPE_KEYWORD
        WO=FIELDTYPE_WORD
        WW=FIELDTYPE_WORDS
        ME=FIELDTYPE_MENU
        LI=FIELDTYPE_LIST
        LM=FIELDTYPE_LISTMENU
        KE=FIELDTYPE_KEYWORD
        for source,expect in [
             ("""
                cmd_c: apple {param_a} pear {param_b} {param_c} bannana;
                cmd_1: {apple} {pear(s)} {fruit(menu abc)},
                {apple} {pear(s)} {fruit(list bannana,apple,pear. menu abc)};
                cmd_2: {salt(s)}{pepper(list aa,bb,cc.)};
                cmd_2: {pepper(menu abc)}{choice(list aaa,bbb,333. menu 123)},
                {foo(s)},{bar};
                cmd_1: {baz}{bar(list aaa,bbb,ccc. menu abc)};""", 
                dict(
                    cmd_1=[(WO,WW,ME),(WO,WW,LM),(WO, LM)],
                    cmd_2=[(WW,LI),(ME,LM),(WW,),(WO,)],
                    cmd_c=[(KW,WO,KW,WO,WO,KW)]))
            ]:
            pos, commands, forms, brokenforms = compile_source(source.strip())
            self.assert_(commands.has_key('cmd_c'))
            self.assertEqual(forms[commands['cmd_c'][0]][-1][-1][-1][0],'bannana')
            #form=forms[commands['cmd_c'][0]]
            #print ' '.join([','.join([repr_fieldtype_compact(ft),name,repr(det)])
            #    for ft,name,det in form[-1]])
            for command, commandforms in commands.iteritems():
                self.assert_(expect.has_key(command))
                print 'command [%s]' % command
                expectedform=expect[command]
                for i,form in enumerate(commandforms):
                    print ' '.join([repr_fieldtype_compact(ft) 
                            for ft,n,det in forms[form][-1]])
                    #print repr(forms[form])
                    self.assertEqual(forms[form][0], command)
                    for j,(ft,n,det) in enumerate(forms[form][-1]):
                        self.assertEqual(ft, expectedform[i][j])


    def test_form_parse(self):
        WO=FIELDTYPE_WORD
        WW=FIELDTYPE_WORDS
        ME=FIELDTYPE_MENU
        LI=FIELDTYPE_LIST
        LM=FIELDTYPE_LISTMENU       
        for formdefs, expect in [

            ("{bar}{foo(s)},{baz(list aaa,bb,ccc.)},"
             "{apple} {pear(list foo,bar,baz. menu 123)}",
             [(WO,WW,None),(LI,None),(WO,LM, 'ERR_GRAMATICAL1:')]),

             ("{bar}{foo(s)},{baz(list aaa,bb,ccc.)},"
             "{apple} {pear(list foo,bar,baz. menu 123)};",
             [(WO,WW,None),(LI,None),(WO,LM,None)])
           
            ]:
            for i, (pos, form, error) in enumerate(yield_forms(formdefs)):
                log = '%s [%s]' % (
                        ' '.join([repr_fieldtype_compact(ft) for ft,n,d in form]),
                        (error and
                         error.find(expect[i][-1]) == 0 and 
                         'OK:got the expected error' or error)
                        or 'OK')
                #print log
                self.assertEqual(len(expect[i])-1, len(form))
                for j, (ft,n,d) in enumerate(form):
                    self.assertEqual(ft,expect[i][j])
                self.assert_(not error or error.find(expect[i][-1]) == 0)

def debug():
    print 'freeform.test_formtable'

    class Dummy: pass
    self=Dummy()
    def assertEqual(a,b):
        print "'%s'='%s' ?" % (a,b)
    def assert_(expr):
        print "is truth ? [%s]" % str(expr)
    self.assertEqual=assertEqual
    self.assert_=assert_

if __name__ == '__main__':
    from os import environ
    if environ.get('FREEFORM_DEBUG',None):
        import wingdbstub
        debug()
    else:
        unittest.main()
