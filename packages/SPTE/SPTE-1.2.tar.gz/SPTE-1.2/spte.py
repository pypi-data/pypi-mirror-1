# -*- coding: utf-8 -*-
# Author: Daniel Garcia <dani@danigm.net>
# license: gplv3

'''
A Simple Python Template Engine
'''

import re
import os
IF = re.compile('(?P<if>[ \t]*#if(?P<n>\d+) (?P<cond>.*?):\s?(?P<body>.*?)\s?([ \t]*#else:\s?(?P<else>.*?)\s?)?#fi(?P=n))', re.DOTALL)
FOR = re.compile('(?P<for>[ \t]*#for(?P<n>\d+) (?P<var>.*?) in (?P<list>.*?):\s?(?P<body>.*?)\s?#rof(?P=n))', re.DOTALL)
CODE = re.compile('\${(.*?)}', re.DOTALL)
INCLUDE = re.compile('(?P<include>[ \t]*#include (?P<template>.*))')

def render(template, vars):
    template = open(template).read()
    return render_str(template, vars, preproc=True)

def preprocess(template):
    '''
    Change if to ifn and for to forn to make avaliable nested ifs
    and nested for
    '''
    if_index, for_index = 0, 0
    newline = []
    for line in template.split(os.linesep):
        new = []
        for word in line.split(' '):
            fword = word.strip()
            if fword == '#if':
                new.append(fword+'%d' % if_index)
                if_index += 1
            elif fword == '#fi':
                if_index -= 1
                new.append(fword+'%d' % if_index)
            elif fword == '#for':
                new.append(fword+'%d' % for_index)
                for_index += 1
            elif fword == '#rof':
                for_index -= 1
                new.append(fword+'%d' % for_index)
            else:
                new.append(word)

        aline = ' '.join(new)
        reserved_words = ['#if', '#for', '#else', '#fi', '#rof', '#include']
        res_line = map(aline.strip().startswith, reserved_words)
        if res_line.count(True):
            aline = aline.strip()
        newline.append(aline)

    new_template = os.linesep.join(newline)
    return new_template
    

def check_include_statement(template, vars):
    '''
    Parse only include statements

    example:

    #include template.spte
    '''
    include_result = INCLUDE.search(template)
    while include_result:
        include_template = ''
        sentence = include_result.group('include')
        templ = include_result.group('template')

        include_template = render(eval(templ, vars), vars)

        template = template.replace(sentence, include_template)
        include_result = INCLUDE.search(template)

    return template

def check_for_statement(template, vars):
    '''
    Parse only for statements

    example:

    #for var in list:
    something with ${var} or not
    #rof
    '''

    for_result = FOR.search(template)
    while for_result:
        for_template = ''
        sentence = for_result.group('for')
        var = for_result.group('var')
        var_list = map(str.strip, var.split(','))
        new_list = for_result.group('list')
        body = for_result.group('body')

        # making the for
        for new_var in eval(new_list, vars):
            extendeds_vars = dict(vars)
            # support for i in l1
            if len(var_list) == 1:
                extendeds_vars[var] = new_var
            # support for i, j, k in zip(l1, l2, l3)
            else:
                for i, j in zip(var_list, new_var):
                    extendeds_vars[i] = j
            for_template += render_str(body, extendeds_vars)
        
        template = template.replace(sentence, for_template)
        for_result = FOR.search(template)

    return template

def check_if_statement(template, vars):
    '''
    Parse only if statements

    example: 

    #if cond:
      body
    #else:
      body_else
    #fi
    '''

    if_result = IF.search(template)
    while if_result:
        sentence = if_result.group('if')
        cond = if_result.group('cond')
        body = if_result.group('body')
        body_else = if_result.group('else')

        if eval(cond, vars):
            new_vars = dict(vars)
            result = render_str(body, new_vars)
        elif body_else:
            result = render_str(body_else, vars)
        else:
            result = ''
        template = template.replace(sentence, result)
        if_result = IF.search(template)

    return template

def render_str(template, vars, preproc=False):
    '''Return a string with vars changed in template'''

    if preproc:
        template = preprocess(template)

    # for statement
    template = check_for_statement(template, vars)
    
    # if statement
    template = check_if_statement(template, vars)

    template = check_include_statement(template, vars)
    
    # vars replacing ${var}
    all_vars = CODE.findall(template)
    for change in all_vars:
        template = template.replace('${%s}' % change, str(eval(change, vars)))

    return template
        

class template:
    ''' Decorator to apply a template to a function that return a dict
    with values '''

    def __init__(self, file='template.spte'):
        self.file = file
    def __call__(self, f):
        def templated(*args, **kwargs):
            vars = f(*args, **kwargs)
            tmp_file = self.file
            try:
                tmp_file = vars['template']
            except:
                pass

            return render(tmp_file, vars)
        return templated
