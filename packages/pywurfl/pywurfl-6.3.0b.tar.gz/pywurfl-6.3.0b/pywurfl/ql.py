# pywurfl QL - Wireless Universal Resource File Query Language in Python
# Copyright (C) 2006 Armand Lynch
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Armand Lynch <lyncha@users.sourceforge.net>

__doc__ = \
"""
pywurfl Query Language

pywurfl QL is a WURFL query language that looks very similar to SQL.

Language Definition
===================

Select statement
================

    select (device|id|ua)
    ---------------------

    The select statement consists of the keyword 'select' followed by the
    select type which can be one of these keywords: 'device', 'ua', 'id'.
    The select statement is the first statement in all queries.

    device
    ------
    When 'select' is followed by the keyword 'device', a device object will
    be returned for each device that matches the 'where' expression
    (see below).

    ua
    --
    When 'select' is followed by the keyword 'ua', an user-agent string
    will be returned for each device that matches the 'where' expression
    (see below).

    id
    --
    When 'select' is followed by the keyword 'id', a WURFL id string will be
    returned for each device that matches the 'where' expression (see below).


Where statement
===============

    where condition
    ---------------
    where condition and/or condition
    --------------------------------
    where any/all and/or condition
    ------------------------------

    The where statement follows a select statement and can consist of the
    following elements: 'where condition', 'any statement', 'all statement'.

    Where condition
    ---------------
    A where condition consists of a capability name followed by a test
    operator followed by a value. For example, "ringtone = true".

    Any statement
    -------------
    An any statement consists of the keyword 'any' followed by a
    parenthesized, comma delimited list of capability names, followed by
    a test operator and then followed by a value. All capabilities
    listed in an any statement will be 'ored' together. There must be a
    minimum of two capabilities listed.

    For example: "any(ringtone_mp3, ringtone_wav) = true".

    All statement
    -------------
    An all statement consists of the keyword 'all' followed by a
    parenthesized, comma delimited list of capability names, followed by
    a test operator and then followed by a value. All capabilities
    listed in an all statement will be 'anded' together. There must be a
    minimum of two capabilities listed.

    For example: "all(ringtone_mp3, ringtone_wav) = true".

    Test operators
    --------------
    The following are the test operators that the query language can
    recognize::

        = != < > >= <=

    Comparing strings follow Python's rules.

    Values
    ------
    Test values can be integers, strings in quotes and the tokens
    "true" or "false" for boolean tests.


Binary operators
================

    There are two binary operators defined in the language "and" and "or".
    They can be used between any where statement tests and follow
    conventional precedence rules::

      ringtone=true or ringtone_mp3=false and preferred_markup="wml_1_1"
                                -- becomes --
      (ringtone=true or (ringtone_mp3=false and preferred_markup="wml_1_1"))


Example Queries
===============

    select id where ringtone=true

    select id where ringtone=false and ringtone_mp3=true

    select id where rows > 3

    select id where all(ringtone_mp3, ringtone_aac, ringtone_qcelp)=true

    select ua where preferred_markup = "wml_1_1"


EBNF
====

query := select_statement where_statement

select_statement := 'select' ('device' | 'id' | 'ua')

where_statement := 'where where_test (boolop where_test)*

where_test := (any_test | all_test | capability_test)

any_test := 'any' capability_list operator value

all_test := 'all' capability_list operator value

capability := alphanums ('_' alphanums)*

capability_list := '(' capability, capability (',' capability)* ')'

capability_test := capability operator value

operator := ('='|'!='|'<'|'>'|'>='|'<=')

value := (<quote> string <quote> | integer | boolean)

boolean := ('true' | 'false')

boolop := ('and' | 'or')
"""

import operator
from pyparsing import (CaselessKeyword, Forward, Group, ParseException,
                       QuotedString, StringEnd, Suppress, Word, ZeroOrMore,
                       alphanums, alphas, nums, oneOf)
from exceptions import BaseException


__author__ = "Armand Lynch <lyncha@users.sourceforge.net>"
__copyright__ = "Copyright 2006, Armand Lynch"
__license__ = "LGPL"
__url__ = "http://wurfl.sourceforge.net/python/"
__version__ = "1.0.0a"


class QueryLanguageError(BaseException):
    """Base exception class for pywurfl.ql"""
    pass


def define_language():
    """
    Defines the pywurfl query language.

    @rtype: pyparsing.ParserElement
    @return: The definition of the pywurfl query language.
    """

    # Select statement
    select_token = CaselessKeyword("select")
    ua_token = CaselessKeyword("ua")
    id_token = CaselessKeyword("id")
    device_token = CaselessKeyword("device")
    select_type = (device_token | ua_token | id_token).setResultsName("type")
    select_clause = select_token + select_type
    select_statement = Group(select_clause).setResultsName("select")

    capability = Word(alphas, alphanums + '_').setResultsName("capability")
    integer = Word(nums)
    boolean = CaselessKeyword("true") | CaselessKeyword("false")
    string = QuotedString("'") | QuotedString('"')
    value = (integer | boolean | string).setResultsName("value")
    binop = oneOf("= != < > >= <=", caseless=True).setResultsName("operator")
    and_ = CaselessKeyword("and")
    or_ = CaselessKeyword("or")

    # Any test
    capabilities = (capability + Suppress(',') + capability +
                    ZeroOrMore(Suppress(',') + capability))
    any_token = CaselessKeyword("any")
    any_list = capabilities.setResultsName("any_caps")
    any_test = (any_token + Suppress('(') + any_list + Suppress(')') +
                     binop + value)
    # All test
    all_token = CaselessKeyword("all")
    all_list = capabilities.setResultsName("all_caps")
    all_test = (all_token + Suppress('(') + all_list + Suppress(')') +
                     binop + value)
    # Capability test
    cap_test = capability + binop + value

    # WHERE statement
    boolop = (and_ | or_).setResultsName('boolop')
    where_token = CaselessKeyword("where")

    where_test = all_test | any_test | cap_test
    where_expression = Forward()
    where_expression << (Group(where_test + ZeroOrMore(boolop +
                                                       where_expression)
                               ).setResultsName('where'))

    #where_expression << (Group(where_test + ZeroOrMore(boolop +
    #                                                   where_expression) +
    #                           StringEnd()).setResultsName('where'))
    #where_expression = (Group(where_test + ZeroOrMore(boolop + where_test) +
    #                    StringEnd()).setResultsName('where'))

    where_statement = where_token + where_expression

    # Mon Jan  1 12:35:56 EST 2007
    # If there isn't a concrete end to the string pyparsing will not parse
    # query correctly

    return select_statement + where_statement + '*' + StringEnd()


def get_operators():
    """
    Returns a dictionary of operator mappings for the query language.

    @rtype: dict
    """

    def and_(func1, func2):
        """
        Return an 'anding' function that is a closure over func1 and func2.
        """
        def and_tester(value):
            """Tests a device by 'anding' the two following functions:"""
            return func1(value) and func2(value)
        and_tester.__doc__ = '\n'.join([and_tester.__doc__, func1.__doc__,
                                        func2.__doc__])
        return and_tester

    def or_(func1, func2):
        """
        Return an 'oring' function that is a closure over func1 and func2.
        """
        def or_tester(value):
            """Tests a device by 'oring' the two following functions:"""
            return func1(value) or func2(value)
        or_tester.__doc__ = '\n'.join([or_tester.__doc__, func1.__doc__,
                                       func2.__doc__])
        return or_tester

    return {'=':operator.eq, '!=':operator.ne, '<':operator.lt,
            '>':operator.gt, '>=':operator.ge, '<=':operator.le,
            'and':and_, 'or':or_}


ops = get_operators()


def capability_test(cap, op, val):
    """
    Returns a capability test function.

    @param cap: A WURFL capability
    @type cap: string
    @param op: A binary test operator
    @type op: string
    @param val: The value to test for
    @type val: string

    @rtype: function
    """

    try:
        val = int(val)
    except ValueError:
        if val == 'true':
            val = True
        elif val == 'false':
            val = False
    def capability_tester(devobj):
        return ops[op](getattr(devobj, cap), val)
    capability_tester.__doc__ = "Test a device for %s %s %s" % (cap, op, val)
    return capability_tester


def combine_funcs(funcs):
    """
    Combines a list of functions with binary operators.

    @param funcs: A python list of function objects with descriptions of
                  binary operators interspersed.

                  For example [func1, 'and', func2, 'or', func3]
    @type funcs: list
    @rtype: function
    """

    while len(funcs) > 1:
        try:
            f_index = funcs.index('and')
            op = ops['and']
        except ValueError:
            try:
                f_index = funcs.index('or')
                op = ops['or']
            except ValueError:
                break
        combined = op(funcs[f_index - 1], funcs[f_index + 1])
        funcs = funcs[:f_index-1] + [combined] + funcs[f_index + 2:]
    return funcs[0]


def reduce_funcs(func, seq):
    """
    Reduces a sequence of function objects to one function object by applying
    a binary function recursively to the sequence::

        In:
            func = and
            seq = [func1, func2, func3, func4]
        Out:
            and(func1, and(func2, and(func3, func4)))

    @param func: A function that acts as a binary operator.
    @type func: function
    @param seq: An ordered sequence of function objects
    @type seq: list
    @rtype: function
    """

    if seq[1:]:
        return func(seq[0], reduce_funcs(func, seq[1:]))
    else:
        return seq[0]


def reduce_statement(exp):
    """
    Produces a function that represents the "any" or "all" expression passed
    in by exp::

        In:
            any(ringtone_mp3, ringtone_awb) = true
        Out:
            ((ringtone_mp3 = true) or (ringtone_awb = true))

    @param exp: The result from parsing an 'any' or 'all' statement.
    @type exp: pyparsing.ParseResults
    @rtype: function
    """

    funcs = []
    if exp.any_caps:
        for cap in exp.any_caps:
            funcs.append(capability_test(cap, exp.operator, exp.value))
        return reduce_funcs(ops['or'], funcs)
    elif exp.all_caps:
        for cap in exp.all_caps:
            funcs.append(capability_test(cap, exp.operator, exp.value))
        return reduce_funcs(ops['and'], funcs)


def test_generator(ql_result):
    """
    Produces a function that encapsulates all the tests from a where
    statement that takes a Device class or object as a parameter::

        In (a result object from the following query):
          select id where ringtone=true and any(ringtone_mp3, ringtone_awb)=true

        Out:
          def func(devobj):
              if (devobj.ringtone == true and
                  (devobj.ringtone_mp3 == true or
                   devobj.ringtone_awb == true)):
                  return True
              else:
                  return False
          return func

    @param ql_result: The result from calling pyparsing.parseString()
    @rtype: function
    """

    funcs = []
    exp = ql_result.where
    while exp:
        if exp.any_caps or exp.all_caps:
            func = reduce_statement(exp)
        else:
            func = capability_test(exp.capability, exp.operator, exp.value)

        boolop = exp.boolop
        if boolop:
            funcs.extend([func, boolop])
        else:
            funcs.append(func)
        exp = exp.where
    return combine_funcs(funcs)


def QL(devices):
    """
    Return a function that can run queries against the WURFL.

    @param devices: The device class hierarchy from pywurfl
    @type devices: pywurfl.Devices
    @rtype: function
    """

    language = define_language()

    def query(qstr, instance=True):
        """
        Return a generator that filters the pywurfl.Devices instance by the
        query string provided in qstr.

        @param qstr: A query string that follows the pywurfl.ql language
                     syntax.
        @type qstr: string
        @param instance: Used to select that you want an instance instead of a
                         class.
        @type instance: boolean
        @rtype: generator
        """
        qstr = qstr.replace('\n', ' ')
        qstr = qstr + '*'
        try:
            qres = language.parseString(qstr)
            tester = test_generator(qres)
            if qres.select.type == 'ua':
                return (x.devua for x in devices.devids.itervalues()
                        if tester(x))
            elif qres.select.type == 'id':
                return (x.devid for x in devices.devids.itervalues()
                        if tester(x))
            else:
                if instance:
                    return (x() for x in devices.devids.itervalues()
                            if tester(x))
                else:
                    return (x for x in devices.devids.itervalues()
                            if tester(x))
        except ParseException, exception:
            raise QueryLanguageError(str(exception))
    setattr(devices, 'query', query)
    return query
