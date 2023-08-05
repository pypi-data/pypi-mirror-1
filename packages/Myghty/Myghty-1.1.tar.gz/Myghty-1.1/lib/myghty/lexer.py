# $Id: lexer.py 2133 2006-09-06 18:52:56Z dairiki $
# lexer.py - template parsing routines for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
# Original Perl code and documentation copyright (c) 1998-2003 by Jonathan Swartz. 
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#


import string, re, sys, codecs
from myghty import exception
from myghty.util import *

"""initial parser for a Myghty file, locates tokens and fires events in a Compiler object.

Lexer is currently stateful and is not thread safe.  the clone() method can be used
to create copies of this object for use in multiple threads.
"""

# map of block names pointing to parse method names
BLOCKS = {
    'args'    : 'variable_list_block',
    'attr'    : 'key_value_block',
    'flags'   : 'key_value_block',
    'cleanup' : 'raw_block',
    'doc'     : 'doc_block',
    'filter'  : 'raw_block',
    'init'    : 'raw_block',
    'once'    : 'raw_block',
    'global'  : 'synonym:once',
    'threadonce' : 'raw_block',
    'threadlocal': 'synonym:threadonce',
    'python'  : 'raw_block',
    'shared'  : 'raw_block',
    'requestlocal' : 'synonym:shared',
    'requestonce' : 'synonym:shared',
    'text'    : 'text_block',
    }

PYTHON_SCOPES = {
        'component': 'python',
        'request': 'shared',
        'thread': 'threadonce',
        'global': 'once',
        'init' : 'init',
        'cleanup': 'cleanup'
    }



class Lexer:
        
    def __init__(self, **params):
        self.current = None
        
    def get_object_id(self):
        """returns an ID that can identify this lexer"""
    
        return "Myghty.Lexer"
    
    def clone(self, **params):
        """creates a clone of this Lexer.  allow the Prototype pattern
        to be used in creating lexers for use in other threads."""
        return Lexer(**params)

    class LexContext:
        """an object tracking the lexer's progress through a component block."""
        def __init__(self, source, name, compiler):
            self.source = source
            self.name = name
            self.compiler = compiler
            
            # a regular expression to match the "end" of whatever construct
            # the parser located
            # different methods override this to locate different kinds of
            # endings
            # This will be overridden if entering a def or method section.
            self.ending = re.compile(r'\Z', re.S)

            # place to begin regular expression matching
            # since I cannot find an equivalent of perl's \G in python
            self.match_position = 0

            self.in_def = False
            self.in_method = False
            self.block_name = None
            self.block_type = None
            self.lines = 0

        def set_in_named_block(self, block_type, name):
            if block_type == 'def':
                self.in_def = True
            elif block_type == 'method':
                self.in_method = True
            elif block_type == 'closure':
                pass
            else:
                raise "invalid block type %s" % block_type
            
            self.block_name = name
            self.block_type = block_type
                
        def reset_in_named_block(self):
            self.in_def = False
            self.in_method = False
            self.block_name = None

            
        def match_pos(self, regstring = None, flags = None, regexp = None):
            if regexp == None:
                if flags:
                    regexp = re.compile(regstring, flags)
                else:
                    regexp = re.compile(regstring)

            match = regexp.match(self.source, self.match_position )
            if match:
                (start, end) = match.span()

                # attempt to simulate perl's \G operator.  usually works, except 
                # it behaves differently with zero-length matches.  
                # well actually perl's operator behaves more strangely. 
                # see def variable_list_block for further \G angst
                
                if end == start:
                    self.match_position = end + 1
                else:
                    self.match_position = end
                

            return match
            

            
    def lex(self, source, name, compiler, input_file = None):
        
        # Holds information about the current lex.  
        current = Lexer.LexContext(source, name, compiler)

        # set current lex to this one
        self.current = current
        
        # optional full path of the file the source came from; passed through
        # to SyntaxErrors for exception reporting
        self.input_file = input_file

        # Clean up Mac and DOS line endings
        current.source = re.sub(r'\r\n?', "\n", current.source)

        # Detect and remove leading UTF-8 byte-order-marker
        # Some windows editors add these at the beginning of a file to
        # mark their content as UTF-8.
        if current.source.startswith(codecs.BOM_UTF8):
            current.source = current.source[len(codecs.BOM_UTF8):]
            self.current.compiler.magic_encoding_comment('utf_8')

        try:
            try:
                current.compiler.start_component()
                self.start()
            except Exception, e:
                raise
        finally:
            current.compiler.end_component()
    



    def start(self):
        end = None

        length = len(self.current.source)
        
        while (True):
            if self.current.match_position > length: break
        
            end = self.match_end()
            
            if end: break
            
            if self.match_block(): continue

            if self.match_named_block():continue
            
            if self.match_substitute(): continue
    
            if self.match_comp_call(): continue
            
            if self.match_python_line(): continue
            
            if self.match_comp_content_call(): continue
            
            if self.match_comp_content_call_end(): continue

            if self.match_text(): continue
            
            isend = (self.current.match_position > len(self.current.source))
            
            if (self.current.in_def or self.current.in_method) and isend:
                self.raise_syntax_error("Missing closing </%%%s> tag" % self.current.block_type)

            if isend: break
        
            raise exception.Compiler("Infinite parsing loop encountered - Lexer bug?")
            

        if self.current.in_def or self.current.in_method:
            type = self.current.block_type
            if not isinstance(end, str) or not self.current.ending.match(end):
                block_name = self.current.block_name
                self.raise_syntax_error("no closing </%%%s> tag for <%%%s %s> block" % (type, type, block_name))


    def match_block(self):
        match = self.current.match_pos(regexp = re.compile(r'\<%(' + string.join(BLOCKS.keys(), '|') + r')(\s+[^>]*)?\s*>', re.I | re.S ))
        if match:
            (type, attr) = (match.group(1).lower(), match.group(2))
            self.current.block_type = type

            attributes = {}
            if attr:
                attrmatch = re.findall(r"\s*((\w+)\s*=\s*('[^']*'|\"[^\"]*\"|\w+))\s*", attr)
                for att in attrmatch:       
                    (full, key, val) = att
                    try:
                        attributes[key] = eval(val)
                    except:
                        (e, msg) = sys.exc_info()[0:2]
                        
                        self.raise_syntax_error("Non-evaluable attribute value: '%s' (%s: %s)" % (val, e, msg))
            
            syntype = None
            
            # get method name for this block
            try:
                method = BLOCKS[type]
                if string.find(method, ':') != -1:
                    syntype = method.split(':', 1)[-1]
                    method = BLOCKS[syntype]
            except KeyError:
                self.raise_syntax_error("no such block type '%s'" % type)
            
            if attributes.has_key('scope') and type == 'python' or syntype == 'python':
                try:
                    syntype = PYTHON_SCOPES[attributes['scope']]
                except KeyError:
                    self.raise_syntax_error("unknown python scope '%s'" % attributes['scope'])
                
            if syntype:
                self.current.compiler.start_block(block_type = syntype, attributes = attributes)
            else:
                self.current.compiler.start_block(block_type = type, attributes = attributes)
            
            
            # call method dynamically
            getattr(self, method)(block_type = type, synonym_for = syntype, attributes = attributes)
            
            self.current.block_type = None
            
            return True
            
        else: return False


    def match_named_block(self):
        match = self.current.match_pos(regexp = re.compile(r"<%(def|method|closure)(?:\s+([^\n]+?))?(\s+[^>]*)?\s*>", re.I | re.S))
        if match:
            (type, name, attr) = (match.group(1).lower(), match.group(2), match.group(3))

            attributes = {}
            if attr:
                attrmatch = re.findall(r"\s*((\w+)\s*=\s*('[^']*'|\"[^\"]*\"|\w+))\s*", attr)
                for att in attrmatch:       
                    (full, key, val) = att
                    attributes[key] = val
    
            if not type or not name:
                self.raise_syntax_error("%s block without a name" % type)
            
            self.current.compiler.start_named_block(block_type = type, name = name, attributes = attributes)
            
            # preserve a little state
            existingending = self.current.ending
            
            # screw with the current compile context
            self.current.ending = re.compile(r"<\/%%%s>(\n?)" % type, re.I)
            self.current.set_in_named_block(block_type = type, name = name)
            
            # recursively call the start() stuff
            self.start()
            
            # tell compiler to close up the block
            self.current.compiler.end_named_block(block_type = type)
            
            # restore the state of the current compile
            self.current.ending = existingending
            self.current.reset_in_named_block()
            
            # give our caller the good news         
            return True
        else:
            return False

        

    def match_text(self):
        current = self.current
        
        match = current.match_pos(regexp = re.compile(r"""
                (.*?)         # anything, followed by:
                (
                 (?<=\n)(?=[%#]) # an eval or comment line, preceded by a consumed \n 
                 |
                 (?=</?[%&])  # a substitution or block or call start or end
                                              # - don't consume
                 |
                 (\\\n)         # an escaped newline  - throw away
                 |
                 \Z           # end of string
                )""", re.X | re.S))
        
        
        if match:
            text = match.group(1)
            current.compiler.text_block(block = text)
            current.lines += self._count_lines(text)
            if match.group(3):
                current.lines += 1
            return True
        else:
            return False




    def match_substitute(self):
        # This routine relies on there *not* to be an opening <%foo> tag
        # present, so match_block() must happen first.
        
        
        if not self.current.match_pos(r"<%"):
            return False
        
        match = self.current.match_pos(
            regexp = re.compile("""
               (.+?)                # Substitution body ($1)
               (
                \s*
                (?<!\|)             # Not preceded by a '|'
                \|                  # A '|'
                \s*
                (                   # (Start $3)
                 [^\W\d]\w*              # A flag
                 (?:\s*,\s*[^\W\d]\w*)*  # More flags, with comma separators
                )
                \s*
               )?
               %>                   # Closing tag

            """, re.X | re.I | re.S)) 
            
        if match:
            (body, extra, escape) = match.group(1, 2, 3)
            self.current.lines += self._count_lines(body)
            if extra: 
                self.current.lines += self._count_lines(extra)
            self.current.compiler.substitution(body, escape)
            return True
        else:
            self.raise_syntax_error("'<%' without matching '%>'")
            
            
            
    def match_comp_call(self):
        match = self.current.match_pos(regexp = re.compile(r"<&(?!\|)", re.S))
        if match:
            match = self.current.match_pos(regexp = re.compile(r"(.*?)&>", re.S))
            if match:
                call = match.group(1)
                self.current.compiler.component_call(call)
                self.current.lines += self._count_lines(call)
                return True
            else:
                self.raise_syntax_error("'<&' without matching '&>'")
        else:
            return False


    def match_comp_content_call(self):
        match = self.current.match_pos(regexp = re.compile(r"<&\|", re.S))
        if match:
            match = self.current.match_pos(regexp = re.compile(r"(.*?)&>", re.S))
            if match:
                call = match.group(1)
                self.current.compiler.component_content_call(call)
                self.current.lines += self._count_lines(call)
                return True
            else:
                self.raise_syntax_error("'<&|' without matching '&>'")
        else:
            return False


    def match_comp_content_call_end(self):
        match = self.current.match_pos(r"</&>")
        if match:
            self.current.compiler.component_content_call_end()
            return True
        else:
            return False


    def match_block_end(self, block_type, allow_text = True, **params):
        
        if allow_text:
            regex = re.compile(r"(.*?)</%%%s>(\n?)" % block_type, re.I | re.S)
        else:
            regex = re.compile(r"\s*</%%%s>(\n?)" % block_type, re.I | re.S)
        
        match = self.current.match_pos(regex)
        if match:
            if allow_text:
                return tuple(match.group(1,2))
            else:
                return match.group(1)
        else:
            self.raise_syntax_error("Invalid <%%%s> section line" % block_type)

    def match_python_line(self):
        match = self.current.match_pos(r"(?<=^)([%#])([^\n]*)(?:\n|\Z)", re.M)
        if match:
            # comment
            if match.group(1) == '#':
                if self.current.lines < 2:
                    # Magic -*- encoding: foo -*- comment
                    m = re.search(r'coding[=:]\s*([-\w.]+)', match.group(2))
                    if m:
                        self.current.compiler.magic_encoding_comment(m.group(1))
                self.current.lines += 1
                return True
            
            self.current.compiler.python_line(line = match.group(2))
            self.current.lines += 1
            return True
        else:
            return False


    def match_end(self):
        match = self.current.match_pos(regexp = self.current.ending)
        if match:
            
            string = match.group()
            self.current.lines += self._count_lines(string)
            if string:
                return string
            else:
                return True
        else:
            return False


    def variable_list_block(self, block_type, attributes = None, **params):

        # python doesnt quite do the regexp here the same way as perl (which seems to
        # do it, incorrectly ??? somehow perl magically knows to stop global matching beyond
        # the </%args> line based on the (?= </%args> ) match at the end. python doesnt.
        # or maybe i just goofed.).
        # anyway, just to get this to work, get the whole ARG block out of the source first, 
        # then operate upon that.  if theres some all-in-one way
        # to do it in python, or i goofed, be my guest.
        
        match = self.current.match_pos(regexp = re.compile(r""".*?(?= <\/%%%s> )""" % block_type, re.M | re.S | re.X))

        if match:
            source = match.group()
        else:
            source = ''
    
        # operate upon the stuff inside of <%block></%block>
        
        regexp = re.compile(r"""
            (?:

                (?:
    
                    [ \t]*
                    ( [^\W\d]\w* )  #only allows valid Python variable names
                    [ \t]*
    
                    (?:
                        (?:         # begin optional part of arg
                            =
                            ( [^\n]+ )  # default value, also consumes an inline comment, if any
                        )
                        |
                        (?:         # an optional comment after an arg without a default
                            [ \t]*
                            \#
                            [^\n]*
                        )
                    )?
    
                )

                |
    
                    [ \t]*      # a comment line
                    \#
                    [^\n]*
                |
                    [ \t]*      # just space
            )
    
            (\n?)       # optional newline.  the ? makes finditer() go into an endless loop.
                """ , re.VERBOSE | re.I | re.M)

        # finditer has a bug here.  goes into an endless loop.
        # but findall works.  if i take the ? off the last newline there, then 
        # finditer works, but we lose the args if it looks like <%args>foo</%args>
        # with no newline.  *shrug*             
        matches = regexp.findall(source)    
        #matches = regexp.finditer(source)

        scope = None
        if attributes is not None and attributes.has_key('scope'):
            scope = attributes['scope']
            
        for match in matches:       
            (name, default, linebr) = match
            #(name, default, linebr) = match.group(1, 2, 3)
            if name:
                self.current.compiler.variable_declaration(block_type=block_type,
                    name=name,
                    default=default,
                    scope = scope)
            if linebr:
                self.current.lines += 1
        

        params['allow_text'] = False
        nl = self.match_block_end(block_type = block_type, **params)
        if nl:
            self.current.lines +=1
        
        self.current.compiler.end_block(block_type = block_type)


    def key_value_block(self, block_type, **params):
        # do this like the variable_list_block
        # see that method for regexp quirks

        match = self.current.match_pos(regexp = re.compile(r""".*?(?= <\/%%%s> )""" % block_type, re.M | re.S | re.X))

        if match:
            source = match.group()
        else:
            source = ''

        regexp = re.compile(r"""
                (?:
                    [ \t]*
                    ([\w_]+)        # identifier
                    [ \t]*[=:][ \t]*    # separator
                    (\S[^\n]*)      # value ( must start with a non-space char)
                    |
                    [ \t]*          # an optional comment
                    \#
                    [^\n]*
                    |
                    [ \t]*          # just space
                )
                (\n?) 
                """ , re.VERBOSE | re.I)
                    
        matches = regexp.findall(source)    
        #matches = regexp.finditer(source)
        for match in matches:
            (key, value, newline) = match
            #(key, value) = match.group(1, 2)
            if key:
                self.current.compiler.key_value_pair(block_type = block_type,
                    key = key, value = value)
            if newline: 
                self.current.lines += 1

        params['allow_text'] = False
        nl = self.match_block_end(block_type = block_type, **params)
        if nl:
            self.current.lines +=1
        
        self.current.compiler.end_block(block_type = block_type)


    def generic_block(self, method, **params):
        params['allow_text'] = True
        (block, n1) = self.match_block_end(**params)
        
        if params.has_key('synonym_for') and params['synonym_for'] is not None:
            compiler_block_type = params['synonym_for']
        else:
            compiler_block_type = params['block_type']

        getattr(self.current.compiler, method)(block_type = compiler_block_type, block = block)
        self.current.lines += self._count_lines(block)
        
        if n1:
            self.current.lines +=1
        
        self.current.compiler.end_block(block_type = compiler_block_type)
        

    def text_block(self, **params):
        self.generic_block('text_block', **params)

    def raw_block(self, **params):
        self.generic_block('raw_block', **params)

    def doc_block(self, **params):
        self.generic_block('doc_block', **params)
        
    
    def line_number(self):
        return self.current.lines + 1

    def get_name(self):
        return self.current.name


    def _count_lines(self, text):
        return len(re.findall(r"\n", text))


    def _current_line(self):
        lines = re.split(r"\n",self.current.source[0:self.current.match_position])
        if len(lines) <= self.current.lines:
            return ''
        else:
            return lines[self.current.lines]


            
    def raise_syntax_error(self, error):
        raise exception.Syntax(
            error = error,
            comp_name = self.get_name(),
            source_line = self._current_line(),
            line_number = self.line_number(),
            source = self.current.source,
            file = self.input_file,
            source_encoding = self.current.compiler.get_encoding())
        
        
