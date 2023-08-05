###############################################################################
###
### Python DBAPI 2.0 Paramstyle Conversions
###
### Peter L. Buschman <plb@iotk.com>
###
### 2004-08-30
###
###############################################################################

import string
import re


##
## Categorization of paramstyles into different categories.  Different types of conversions
## will have different optimal algorithms.
##
PARAMSTYLES    = {
    'all'      : [ 'qmark', 'numeric', 'named', 'format', 'pyformat' ],
    'sequence' : [ 'qmark', 'numeric', 'format' ],
    'dict'     : [ 'named', 'pyformat' ],
    'token'    : [ 'qmark', 'format' ],
}


##
## Valid quote characters.
##
QUOTE_CHARS = [ '"', "'" ]  # " or '


##
## Valid escape characters.
##
ESCAPE_CHARS = [ '\\' ]


##
## This dictionary is used to lookup the placeholder strings for paramstyles whose
## placeholders are always the same.  This is currently just qmark and format.
##
PLACEHOLDER_TOKENS = {
    'qmark'    : '?',
    'format'   : '%s',
}


##
## This dictionary is used to look-up regular expressions for matching placeholders
## in a query string for a given paramstyle.
##
PLACEHOLDER_EXPS = {
    'qmark'    : re.compile(r'(\?)'),
    'numeric'  : re.compile(r'(:\d+)'),
    'named'    : re.compile(r'(:\w+)'),
    'format'   : re.compile(r'(%s)'),
    'pyformat' : re.compile(r'(%\(\w+\)s)'),
}


##
## This dictionary is used to get the correct datastructure to return params in when converting
## from one paramstyle to another.
##
PARAM_TYPES = {
    'qmark'    : lambda : [],
    'numeric'  : lambda : [],
    'named'    : lambda : {},
    'format'   : lambda : [],
    'pyformat' : lambda : {},
}


##
## Add a parameter to a sequence or dictionary of parameters.
##
def param_add( param_num, param_name, param, params ):
    try:
        params.append(param)
    except AttributeError:
        params[param_name] = param
    return params


##
## This dictionary is used to lookup regular expressions for matching the parameter
## name contained within the placeholder of a named paramstyle.  This is currently
## just named and pyformat.
##
PARAMNAME_EXPS = {
    'named'    : re.compile(':(\w+)'),
    'pyformat' : re.compile('%\((\w+)\)s'),
}


##
## Parameter name generators.
##
PARAMNAME_GENS = {
    'qmark'    : lambda param_num, placeholder : 'param%d' % (param_num),
    'numeric'  : lambda param_num, placeholder : 'param%d' % (param_num),
    'named'    : lambda param_num, placeholder : PARAMNAME_EXPS['named'].findall(placeholder)[0],
    'format'   : lambda param_num, placeholder : 'param%d' % (param_num),
    'pyformat' : lambda param_num, placeholder : PARAMNAME_EXPS['pyformat'].findall(placeholder)[0],
}


##
## Parameter value generators.
##
PARAMVALUE_GENS = {
    'qmark'    : lambda param_num, param_name, params : params[param_num - 1],
    'numeric'  : lambda param_num, param_name, params : params[param_num - 1],
    'named'    : lambda param_num, param_name, params : params[param_name],
    'format'   : lambda param_num, param_name, params : params[param_num - 1],
    'pyformat' : lambda param_num, param_name, params : params[param_name],
}


##
## This dictionary contains lambda functions that return the appropriate replacement
## string given the parameter's sequence number.
##
PLACEHOLDER_SUBS = {
    'qmark'     : lambda param_num, param_name : '?',
    'numeric'   : lambda param_num, param_name : ':%d' % (param_num),
    'named'     : lambda param_num, param_name : ':%s' % (param_name),
    'format'    : lambda param_num, param_name : '%s',
    'pyformat'  : lambda param_num, param_name : '%%(%s)s' % (param_name),
}


##
## The following conversion matrix was inspired by similar code in Wichert Akkerman's dhm
## module at http://www.wiggy.net/code/python-dhm.
##
## The primary reason for listing conversion algorithms in a lookup table like this is that
## it allows for individual conversions to be overridden as additional, possibly experimental,
## algorithms are developed without breaking the functionality of the entire module.
##
CONVERSION_MATRIX = {
    'qmark' : {
        'qmark'    : lambda query, params : (query, params),
        'numeric'  : lambda query, params : paramstyle_to_paramstyle( 'qmark', 'numeric', query, params ),
        'named'    : lambda query, params : paramstyle_to_paramstyle( 'qmark', 'named', query, params ),
        'format'   : lambda query, params : paramstyle_to_paramstyle( 'qmark', 'format', query, params ),
        'pyformat' : lambda query, params : paramstyle_to_paramstyle( 'qmark', 'pyformat', query, params ),
    },
    'numeric' : {
        'qmark'    : lambda query, params : paramstyle_to_paramstyle( 'numeric', 'qmark', query, params ),
        'numeric'  : lambda query, params : (query, params),
        'named'    : lambda query, params : paramstyle_to_paramstyle( 'numeric', 'named', query, params ),
        'format'   : lambda query, params : paramstyle_to_paramstyle( 'numeric', 'format', query, params ),
        'pyformat' : lambda query, params : paramstyle_to_paramstyle( 'numeric', 'pyformat', query, params ),
    },
    'named' : {
        'qmark'    : lambda query, params : paramstyle_to_paramstyle( 'named', 'qmark', query, params ),
        'numeric'  : lambda query, params : paramstyle_to_paramstyle( 'named', 'numeric', query, params ),
        'named'    : lambda query, params : (query, params),
        'format'   : lambda query, params : paramstyle_to_paramstyle( 'named', 'format', query, params ),
        'pyformat' : lambda query, params : paramstyle_to_paramstyle( 'named', 'pyformat', query, params ),
    },
    'format' : {
        'qmark'    : lambda query, params : paramstyle_to_paramstyle( 'format', 'qmark', query, params ),
        'numeric'  : lambda query, params : paramstyle_to_paramstyle( 'format', 'numeric', query, params ),
        'named'    : lambda query, params : paramstyle_to_paramstyle( 'format', 'named', query, params ),
        'format'   : lambda query, params : (query, params),
        'pyformat' : lambda query, params : paramstyle_to_paramstyle( 'format', 'pyformat', query, params ),
    },
    'pyformat' : {
        'qmark'    : lambda query, params : paramstyle_to_paramstyle( 'pyformat', 'qmark', query, params ),
        'numeric'  : lambda query, params : paramstyle_to_paramstyle( 'pyformat', 'numeric', query, params ),
        'named'    : lambda query, params : paramstyle_to_paramstyle( 'pyformat', 'named', query, params ),
        'format'   : lambda query, params : paramstyle_to_paramstyle( 'pyformat', 'format', query, params ),
        'pyformat' : lambda query, params : (query, params),
    },
}

##
## Return True if the character at pos in string is escaped.
##
def escaped( string, pos ):
    escape_chars = ESCAPE_CHARS
    count = 0
    if pos > 0:
        pos -= 1
        if string[pos] in escape_chars:
            escape_char = string[pos]
            while string[pos] == escape_char and pos >= 0:
                count += 1
                pos -= 1
    if count % 2 == 1:
        return True
    else:
        return False

##
## Return True if the string is quoted.
##
def quoted( string ):
    if string[0] in QUOTE_CHARS and string[-1] == string[0]:
        return True
    else:
        return False

##
##
##
class SegmentizeError(Exception):
    """
    Error associated with string segmentization.
    """
    pass


##
## Parse a string into quoted and non-quoted segments.  We do this so that it is easy to tell
## which segments of a string to look for placeholders in and which to ignore.
##
def segmentize( string ):
    """
    Split a string into quoted and non-quoted segments.
    """
    quote_chars     = QUOTE_CHARS
    segments        = []
    current_segment = ''
    previous_char   = None
    quote_char      = None
    quoted          = False
    pos             = 0
    for char in string:
        if quoted:
            if char == quote_char and not escaped( string, pos ):
                current_segment += char
                segments.append(current_segment)
                current_segment = ''
                previous_char = char
                quoted = False
            else:
                current_segment += char
                previous_char = char
        elif not quoted:
            if char in quote_chars and not escaped( string, pos ):
                if current_segment != '':
                    segments.append(current_segment)
                    current_segment = ''
                quoted = True
                quote_char = char
                current_segment += char
                previous_char = char
            else:
                current_segment += char
                previous_char = char
        pos += 1
    if current_segment != '':
        segments.append(current_segment)
    if quoted:
        raise SegmentizeError, 'Unmatched quotes in string'

    return segments


##
## Universal paramstyle converter.  This is the initial conversion algorithm supplied with PyDAL.
## It is intended to complete, but may not offer optimal performance in all cases.
##
## --PLB 2004-09-08
##
def paramstyle_to_paramstyle( from_paramstyle, to_paramstyle, query, params ):
    placeholder_exp = PLACEHOLDER_EXPS[from_paramstyle]
    placeholder_sub = PLACEHOLDER_SUBS[to_paramstyle]
    paramname_gen   = PARAMNAME_GENS[from_paramstyle]
    paramvalue_gen  = PARAMVALUE_GENS[from_paramstyle]
    new_query = ''
    segments = segmentize(query)
    new_params = PARAM_TYPES[to_paramstyle]()
    param_num = 0
    for segment in segments:
        #
        # If the segment is a quoted string, do not check for placeholders.
        #
        if quoted(segment):
            new_query += segment
        else:
            #
            # ...otherwise, check for any placeholder matches.
            #
            pos = 0
            match = placeholder_exp.search(segment, pos)
            if match != None:
                #
                # If there are placeholders...
                #
                while match != None:
                    new_query += segment[pos:match.start()]
                    placeholder = segment[match.start():match.end()]
                    #
                    # Ignore the placeholder if it is escaped...
                    #
                    if escaped( segment, match.start() ):
                        new_query += placeholder
                    else:
                        #
                        # ...otherwise replace it.
                        #
                        param_num += 1
                        param_name  = paramname_gen( param_num, placeholder )
                        param_value = paramvalue_gen( param_num, param_name, params )
                        new_placeholder = placeholder_sub( param_num, param_name )
                        new_query += new_placeholder
                        new_params = param_add( param_num, param_name, param_value, new_params )
                    pos = match.end()
                    match = placeholder_exp.search(segment, pos)
                #
                # Tack on the end of the string segment when there are no more matches.
                #
                if pos < len(segment):
                    new_query += segment[pos:]
            #
            # If there were no placeholders, just add the segment to our query.
            #
            else:
                new_query += segment

    return new_query, new_params


##
## Convert from any paramstyle to any other paramstyle.
##
def convert( from_paramstyle, to_paramstyle, query, params ):

    try:
        convert_function = CONVERSION_MATRIX[from_paramstyle][to_paramstyle]
    except KeyError:
        raise NotImplementedError, 'Unsupported paramstyle conversion: %s to %s' % (from_paramstyle, to_paramstyle)

    new_query, new_params = convert_function(query, params)

    return new_query, new_params

##
## Unit Tests
##
## Need to move these to the python unit testing framework...
##
if __name__ == '__main__':
    sequence_params = ['a', 'b', 'c', 'd']
    dict_params = {
        'foo'  : 'a',
        'bar'  : 'b',
        'baz'  : 'c',
        'quux' : 'd',
    }
    tests = {
        'qmark'    : [ 'SELECT * FROM ? WHERE ? > ? OR ? IS NOT NULL', sequence_params ],
        'numeric'  : [ 'SELECT * FROM :1 WHERE :2 > :3 OR :4 IS NOT NULL', sequence_params ],
        'named'    : [ 'SELECT * FROM :foo WHERE :bar > :baz OR :quux IS NOT NULL', dict_params ],
        'format'   : [ 'SELECT * FROM %s WHERE %s > %s OR %s IS NOT NULL', sequence_params ],
        'pyformat' : [ 'SELECT * FROM %(foo)s WHERE %(bar)s > %(baz)s OR %(quux)s IS NOT NULL', dict_params ],
    }
    indent = 4
    width = 16
    print ''
    print '[ PARAMSTYLE TRANSLATIONS ]'
    print ''
    for from_paramstyle in PARAMSTYLES['all']:
        query  = tests[from_paramstyle][0]
        params = tests[from_paramstyle][1]
        print ''
        print '%s[ %s ]' % (' ' * indent, from_paramstyle.upper())
        print ''
        label = 'query'
        print '%s%s%s: %s' % (' ' * indent, label, '.' * (width + indent - len(label)), query)
        label = 'paramstyle'
        print '%s%s%s: %s' % (' ' * indent, label, '.' * (width + indent - len(label)), from_paramstyle)
        print ''
        for to_paramstyle in PARAMSTYLES['all']:
            converted_query, converted_params = convert(from_paramstyle, to_paramstyle, query, params)
            label = '%s_query' % (to_paramstyle)
            print '%s%s%s: %s' % (' ' * indent * 2, label, '.' * (width - len(label)), converted_query)
            label = '%s_params' % (to_paramstyle)
            print '%s%s%s: %s' % (' ' * indent * 2, label, '.' * (width - len(label)), converted_params)
        print ''

