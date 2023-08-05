===============================================================================
freeform: natural interpretation of loosely structured user phrases
===============================================================================
:Download: `freeform-0.3.tar.gz`_, `freeform-0.2-1.tar.gz`_
:Authors: Robin Bryce

:Requires: python2.4, setuptools is optional

:Copyright: Copyright (c) 2006 Wiretooth Ltd. This program is dual-licensed 
    free software; you can redistribute it and/or modify it under the terms of 
    the `MIT License`_, or the  `Academic Free License v3.0`_

.. _MIT License: http://www.opensource.org/licenses/mit-license.php
.. _Academic Free License v3.0: http://www.opensource.org/licenses/afl-3.0.php
.. _freeform-0.3.tar.gz: ./freeform-0.3.tar.gz
.. _freeform-0.2-1.tar.gz: ./freeform-0.2-1.tar.gz

:Version: 0.3

:Abstract:  freeform makes it easy to correctly interpret loosely structured
    user text input without imposing any syntax requirements on the end user.
    This is particularly usefull for providing text based interfaces over
    mediums like SMS or instant messaging. 
 
highlights
----------
 * recognises user input without imposing any syntax requirements on the end 
   user.
 * Corrects finger trouble in a reliable way. (Levenstein edit distance).
 * Simple, intuitive, and OPTIONAL definition syntax and compiler tool. 
 * Multiple equivalent forms of a phrase can be resolved to a single `command` 
   identifier.
 * Refuses to guess if there are multiple interpretations. Instead it provides
   the remaining candidates and the current match data allowing you to chose
   based on the specifics of your application domain.
 * pure python implementation. (pyrex accelerations planned)
 * no complex external dependencies.
 * EFFICIENT matching algorithm.

.. contents::

overview
--------

freeform makes it easy to correctly interpret loosely structured user text
input without imposing any syntax requirements on the end user.  This is
particularly usefull for providing text based interfaces over mediums like SMS
or instant messaging. Where ambiguity can't be completely resolved it provides
you with as much help as possible to make the guess correctly in your
application. Typical use: Compile your phrase forms, associating them with a
collective `command` name; prepare the resulting `formtable`; Then use this
table to `match` user entered phrases to your commands. You can then access the
input fields you are interested in using the field names you supplied in your
phrase description. Matching considers the whole phrase for ambiguity
resolution. It uses levenshteins edit distance metric for individual words to
correct for finger trouble.  Backtracking is used to handle cases where the
content of user fields collides with the recognizable `features` of your phrase
forms. See tool.py for example usage & a tool to assist developing your form
descriptions.

examples
--------

The following illustrates simple use.

Given a text file, **example-1.forms**, containing::

    use_objects_with_set: 
        use {object(s)} on {set(list book,safe,fire,door. menu abcd)},
        {object(s)} on {set(list book,safe,fire,door. menu abcd)}, 
        {set(list book,safe,fire,door. menu abcd)} try {object(s)};
        
    put_objects_to: 
        put {object(s)} on {location(list shelf,box,floor. menu abc)}, 
        {object(s)} on {location(list shelf,box,floor. menu ijk)};


The following output is from 
**python freeform/tool.py -I data/example-1.forms**::

    Enter input corresponding to any of the following forms:
    use_objects_with_set: KE.use=use WW.object=? KE.on=on LM.set=?
    use_objects_with_set: WW.object=? KE.on=on LM.set=?
    use_objects_with_set: LM.set=? KE.try=try WW.object=?
    put_objects_to: KE.put=put WW.object=? KE.on=on LM.location=?
    put_objects_to: WW.object=? KE.on=on LM.location=?

    compiled from sources:
    use_objects_with_set:
        use {object(s)} on {set(list book,safe,fire,door. menu abcd)},
        {object(s)} on {set(list book,safe,fire,door. menu abcd)},
        {set(list book,safe,fire,door. menu abcd)} try {object(s)};

    put_objects_to:
        put {object(s)} on {location(list shelf,box,floor. menu abc)},
        {object(s)} on {location(list shelf,box,floor. menu ijk)};


    freeform:apple pear on book
    use_objects_with_set: WW.object=[['apple', 'pear']] KE.on=on LM.set=['book']
    freeform:use apple pear on book
    use_objects_with_set: KE.use=use WW.object=[['apple', 'pear']] KE.on=on LM.set=['book']
    freeform:book try apple pear
    use_objects_with_set: LM.set=['book'] KE.try=try WW.object=[['apple', 'pear']]
    freeform:apple pear on shelf
    put_objects_to: WW.object=[['apple', 'pear']] KE.on=on LM.location=['shelf']
    freeform:apple pear on shelf
    put_objects_to: WW.object=[['apple', 'pear']] KE.on=on LM.location=['shelf']
    freeform:apple pear on on shelf
    put_objects_to: WW.object=[['apple', 'pear', 'on']] KE.on=on LM.location=['shelf']
    freeform:apple pear on a
    use_objects_with_set: WW.object=[['apple', 'pear']] KE.on=on LM.set=['a']
    freeform:apple pear on i
    put_objects_to: WW.object=[['apple', 'pear']] KE.on=on LM.location=['i']
    freeform:apple pear on shelf
    put_objects_to: WW.object=[['apple', 'pear']] KE.on=on LM.location=['shelf']
    freeform: 

warts
-----

 * using setuptools, which will be excelent once its finished (imv)
   
This is alpha software, so is setuptools, which is used to extend pythons 
distutils behaviour. If setuptools gives you a problem feel free to ignore the 
setup.py file and run things in place.


freeformc
---------

A simple command line tool, with an optional interactive shell, for developing
and testing phrase sources. Instalation is optional this tool can be run in 
place::

  tar -zxvf freeform-$VER.tar.gz; cd freeform-$VER; python freeform/tool.py --help

If you are user of setuptools you can do this::

  tar -zxvf freeform-$VER.tar.gz; cd freeform-$VER; python setup.py develop; freeformc --help

freeform.match
--------------

The main entry point for the matching engine.

The matching algorithm is implemented by the `match` sub package. Its main entry
points are `freeform.match_sentence` and `freeform.match_command`.

freeform.formtable
------------------

Implements the compiler tool for constructing the data used by
the matching algorithm. The compiler is implemented by the functions: `compile`,
`compile_source`, `yield_forms`, `yield_fields`. These can be found in
`freeform.formtable`.

The compiler takes your form descriptions, collects them according to the
command name, that you provide for them, and produces output that should be
handed to `create_formtable`. Before performing matches you need to prepare
your formtable by calling `formtable_prepare`.

If you pass in a dictionary and list instance to either `compile` or
`compile_source` then you can accumulate the results from successive files into
the same `formtable`. Your form descriptions are collected under the command
name you give them. Multiple declarations sharing the same command name are
accumulated under the same command.

Strictly speaking you don't need this compiler if you are willing to put
together the input for `formtable.create_formtable` by hand (or using your own tools). 

syntax summary for the compiler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[ these notes are a work in progress, YMMV. ]

grammar for describing the input phrases that can be recognized::
    
    command => commandname: [ keyword | {paramword}] , [keyword|{paramword}* ;
    {paramword} => [
            {id} | 
            {id(s)} |
            {id(list one,two,three.)} | 
            {id(menu abc)} |
            {id(list one,two,three. menu abc)}]

[see the `MATCH_ xxx` regexes and `yield_ xxx` functions in `formtable.py` for more]

The command description: ``send_msg_to: send {msg(s)} to {name}, send {word(s)}
{choice(list fred,barny,flintstone.}``; Produces a formtable containing a
single command named ``send_msg_to`` that can invoked by one of two phrase
forms.

This one: ``send freeform is neat you should download it too to Mathew``; Would
match the first form. The field named **msg** will contain **freeform is neat you
should download it too**. The field named **name** will contain **Mathew**.

This one: ``send freeform has been downloaded by barney barney``; Would match
the second form. The field named **msg** will contain **freeform has been
downloaded by barney** and the field identified by **name** will contain
**barney**

In the following 'id' is the name you give a particular field such that you can grab
the user values out of the match result.

singular parameter identified by id: ``{id}`` 

a multi valued parameter, separated by whitespace and identified by id: ``{id(s)}``

a selection, one of which must match (levenshteins is applied to match each
item): ``{id(list apple,pear,bannana.)}``

a menu, a single character must match one of the characters in the menu:
``{id(menu abc4ef5)}``

a listmenu, a single character must match one of the characters in the menu OR
a single word must match one of the items in the list: 
``{id(list one,two,three. menu abc)}``

a keyword, which the phrase should contain at the appropriate `logical` position.
Any alphanumeric, additional the prefix characters .- are also allowed, eg
``1word`` ``word1`` ``.word`` ``-wo-&%@rd`` are all legal keywords. pretty much any
string that doesn't contain spaces, start with `{` or contain `;`

Note that all matches against keywords and list item entries are loosely 
matched using levenshteins word distance algorithm. Ambiguity is addressed
by considering the whole phrase.

Other field types, for example multiple select, are possible. They are still
TBD. The present set allows for a large number of simple user entry cases.

freeform_tests
--------------

The test suite, test_match.py, and test_freeform.py may be run inplace. At 
present they provide for reasonably comprehensive coverage of the features
offered by the matching algorithm and the guts of the compiler tool.

profile_match.py is where the shared bits of profiling & debug code live.

