#!/usr/bin/env python
"""Distutils setup file"""
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages


def get_descriptors(
    filename,
    short=':Abstract:', 
    long='',
    version='',
    other=[],
    includeprefix=[],
    excludeprefix=[]):
    f = file(filename)
    seeksections=other[:] # last entry is terminator.
    if long: seeksections.insert(0,long)
    if short: seeksections.insert(0,short)
    if version: seeksections.insert(0,version)
    lines,section,sectionlines,sections = [],None,[],{}
    try:
        for line in f:
            #line = line.strip()
            for candidate in seeksections:
                if line.startswith(candidate):
                    if section:
                        sections[section]=sectionlines
                        sectionlines=[]
                    if candidate == seeksections[-1]:
                        for section, lines in sections.items():
                            sections[section]=''.join(lines)
                        short=sections.pop(short,'')
                        long=sections.pop(long,'')
                        #version=float(sections.pop(version,'0.0').split()[-1])
                        version=sections.pop(version,'0.0'
                            ).strip().split()[-1].strip()
                        return dict(short=short, long=long, version=version,
                            other='\n'.join(sections.values()))
                    section=candidate
                    break
            for include,exclude in zip(includeprefix,excludeprefix):
                if line.startswith(include):
                    sectionlines.append(line)
                    break
                elif line.startswith(exclude):
                    line=None
                    break
            line and sectionlines.append(line)
    finally:
        f.close()
    return sections

desc=get_descriptors(
    'freeform.rst',
    short='freeform:',
    long=':Abstract:',
    version=':Version:',
    other=[
        ':Authors:', ':Requires:', ':Copyright:', ':Version:', 'highlights', 
        '.. contents::'],
    includeprefix=['.. _'],
    excludeprefix=['========'])

setup(
    name = desc.get('short').split(' ',1)[0].replace(':',''),
    version = desc.get('version').split()[-1],
    description = desc.get('short').split(' ',1)[-1].strip(),
    long_description = desc.get('long').split(' ',1)[-1],
    license = 'Choose either AFL v3.0 or MIT',
    author = "Robin Bryce",
    author_email = "robin@wiretooth.com",
    url = "http://svn.wiretooth.com/downloads/freeform.html",
    download_url = "http://svn.wiretooth.com/downloads/freeform.html",
    entry_points = {
        'console_scripts': [
        'freeformc = freeform.tool:compile_tool',
        ]},    
        packages = find_packages('.', exclude=['ez_setup']),
    test_suite = 'freeform_tests.test_all',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Academic Free License (AFL)',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        ],
    include_package_data=True
)
