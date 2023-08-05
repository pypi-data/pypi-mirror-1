# $Id: compiler.py 2133 2006-09-06 18:52:56Z dairiki $
# compiler.py - compiles parsed files into a parse tree for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
# Original Perl code and documentation copyright (c) 1998-2003 by Jonathan Swartz.
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#


"""
 Middle tier between a Lexer and an ObjectGenerator.  receives parse events from Lexer
and constructs a parse tree, then calls an ObjectGenerator to generate an object file from 
the parse tree.  the parse tree structure is language-neutral and contains no python code.

Compiler is currently stateful and is not thread-safe. the clone() method can be used
to create copies of this object for use in multiple threads.
"""


from myghty.util import *
from myghty import exception
import myghty.lexer
import myghty.objgen as objgen
import myghty.args as args
import string, re, sys, warnings



# blocks that can only be in the top level
top_level_only_block = dict(map (lambda x:[x ,True], ['once', 'shared', 'threadonce']))

# valid flags in use
valid_comp_flag = dict(map (lambda x:[x ,True], ['inherit']))

# map of block names pointing to compile method names
BLOCKS = {
    'python'    : 'python_block',
    }


argscopes = {
    'request' : args.RequestArg,
    'subrequest' : args.SubRequestArg,
    'dynamic' : args.DynamicArg,
    'component' : args.LocalArg
}

class Compiler:

    # compiled component modules must have this defined as their
    # _MAGIC_NUMBER or an IncompatibleCompiler exception will be raised
    MAGIC_NUMBER = 5
    
    class BlockFlyweight:
        """an object that represents
         a construct in the original source file.  maintains a reference to a list
         of source file items and uses a context to act upon the list entry
         in question, so that very few objects need to be created """
        def __init__(self):pass

        def get_line(self, context):
            return context.entry[2]
            
        def get_line_number(self, context):
            return context.entry[1]
            
        def append(self, list, line, linenumber):
            list.append([self, linenumber, line])
            
        def accept_visitor(self, visitor, context):raise NotImplementedError

    class CodeBlock(BlockFlyweight):
        """represents a <%python> section"""
        def get_lines(self, context):
            block = context.entry[2]
            lines = re.split(r"\n", block)
            return lines
            
        def accept_visitor(self, visitor, context):
            visitor.visit_code_block(self, context)

    class Substitution(BlockFlyweight):
        """represents a <% %> line """
        def accept_visitor(self, visitor, context):
            visitor.visit_substitution(self, context)

        def append(self, list, line, escape, linenumber):
            list.append([self, linenumber, line, escape])
            
        def get_escapes(self, context):
            return context.entry[3]
    
    class TextLine(BlockFlyweight):
        """ represents a line of plain text"""
        def accept_visitor(self, visitor, context):
            visitor.visit_text_line(self, context)

    class CodeSingleLine(BlockFlyweight):
        """ represents a % line """
        def accept_visitor(self, visitor, context):
            visitor.visit_code_single_line(self, context)

    class ComponentCall(BlockFlyweight):
        """ represents a component call without content <& &>"""
        def append(self, list, component, args, linenumber):
            list.append([self, linenumber, component, args])
        
        def get_component(self, context):
            return context.entry[2]
        
        def get_args(self, context):
            return context.entry[3]
            
        def accept_visitor(self, visitor, context):
            visitor.visit_component_call(self, context)

    class ComponentContentCall(ComponentCall):
        """ represents a component call with content <&| &>"""
        def accept_visitor(self, visitor, context):
            visitor.visit_component_content_call(self, context)

    class ComponentContentCallEnd(ComponentCall):
        """ represents a component call with content end tag </&>"""
        def accept_visitor(self, visitor, context):
            visitor.visit_component_content_call_end(self, context)

    class Closure(BlockFlyweight):
        def append(self, list, compiled, linenumber):
            list.append([self, linenumber, compiled])

        def get_compiled(self, context):
            return context.entry[2]
            
        def accept_visitor(self, visitor, context):
            visitor.visit_closure_block(self, context)
            
    class BlockFlyweightIterator:
        """an iterator that loops through an array of BlockFlyweight references and
        their associated data,
        and acts as the context to send to their get() methods"""
        def __init__(self, list):
            self.list = list
            self.index = -1
            self.entry = None
            
        def __iter__(self):
            return self
            
        def next(self):
            self.index += 1
            if self.index >= len(self.list): raise StopIteration()
            self.entry = self.list[self.index]
            return self.entry[0]

    # singleton instances of BlockFlyweights
    codeblock = CodeBlock()
    textline = TextLine()
    codesingleline = CodeSingleLine()
    substituteline = Substitution()
    componentcall = ComponentCall()
    componentcontentcall = ComponentContentCall()
    componentcontentcallend = ComponentContentCallEnd()
    closure = Closure()
    
    def __init__(self, 
            python_pre_processor = None, 
            python_post_processor = None, 
            text_post_processor = None, 
            lexer = None, 
            generator = None,
            default_escape_flags = [],
            use_source_line_numbers = True,
            allow_globals = [],
            disable_unicode = False,
            **params):
            
        self.current_compile = None
        if lexer:
            self.lexer = lexer
        else:
            self.lexer = myghty.lexer.Lexer(**params)
            
        if generator:
            self.generator = generator
        else:
            self.generator = objgen.PythonGenerator()
            
        self.default_escape_flags = default_escape_flags
        self.python_pre_processor = python_pre_processor
        self.python_post_processor = python_post_processor
        self.text_post_processor = text_post_processor
        self.use_source_line_numbers = use_source_line_numbers
        self.allow_globals = allow_globals
        self.disable_unicode = bool(disable_unicode)
        
    def get_object_id(self):
        """identification string placed at the top of compiled files"""
        return "%s|%s|%s" % (self.lexer.get_object_id(),
                             "Myghty.Compiler",
                             repr(self.get_magic_number()))

    def get_magic_number(self):
        return Compiler.MAGIC_NUMBER, {'disable_unicode': self.disable_unicode}

    def clone(self, **params):
        """creates a clone of this Compiler.  allow the Prototype pattern
        to be used in creating compilers for use in other threads."""

        params['lexer'] = self.lexer.clone()
        params['generator'] = self.generator.clone()
        clone = ConstructorClone(self, **params)
        return clone.clone()



    
    class Compiled:
        "Stores information about the currently compiling block"
        def __init__(self, compiler, fileid, name, in_main = True, parent = None, block_type = None, flags = None):
            self.compiler = compiler
            self.lexer = compiler.lexer
            self.parent = parent
            self.in_main = in_main
            self.block_type = block_type
            
            self.fileid = fileid
            self.name = name    
                
            self.component_content_call_stack = []
            
            self.in_block = None

            self.args = OrderedDict()
            
            if flags is not None:
                self.flags = OrderedDict([flags])
            else:
                self.flags = OrderedDict()
            
            self.attr = OrderedDict()
            
            self.named_blocks = {'def': {}, 'method': {}}
            
            self.blocks = {
                    'cleanup' : [],
                    'filter' : [],
                    'init' : [],
                    'once' : [],
                    'threadonce' : [],
                    'shared' : [],
                    'body' : []
                }

            self.start_blocks = {
                'args' : -1,
                'flags' : -1,
                'attr': - 1,
            }

            self.encoding = None
            

        def accept_visitor(self, visitor):
            if self.in_main:
                visitor.visit_component_block(self)
            elif self.block_type == 'def':
                visitor.visit_def_block(self)
            elif self.block_type == 'method':
                visitor.visit_method_block(self)
                
        def add_argument(self, name, default, linenumber, scope):
            if self.args.has_key(name):
                self.lexer.raise_syntax_error("component argument %s already defined" % name)

            try:
                self.args[name] = argscopes[scope or 'component'](name, default = default, linenumber = linenumber)
            except KeyError:
                self.lexer.raise_syntax_error("Unknown %%args scope '%s'" % scope)


        def has_named_block(self, block_type, name):
            if block_type is None:
                for value in self.named_blocks.values():
                    if value.has_key(name):
                        return True
                else:
                    return False
            else:
                return self.named_blocks.has_key(block_type) and self.named_blocks[block_type].has_key(name)
            
        def get_named_block(self, block_type, name):
            if block_type is None:
                for value in self.named_blocks.values():
                    if value.has_key(name):
                        return value[name]
                else:
                    raise KeyError(name)
            else:
                return self.named_blocks[block_type][name]
            
        def add_named_block(self, block_type, name, block):
            self.named_blocks[block_type][name] = block

        def get_named_blocks(self, block_type = None):
            if block_type is not None:
                return self.named_blocks[block_type].values()
            else:
                list = []
                for d in self.named_blocks.values():
                    list += d.values()
                return list

        def get_body(self):
            return self.blocks['body']
            
        def get_block_list(self, block_type):
            return self.blocks[block_type]

        def block_has_code(self, block_type):
            return len(self.blocks[block_type]) > 0
            
        def get_block_iterator(self, block_type):
            block = self.get_block_list(block_type)
            return Compiler.BlockFlyweightIterator(block)

        def set_encoding(self, encoding):
            if self.parent is not None:
                self.parent.set_encoding(encoding, ignore_if_already_set)
            elif self.encoding:
                self.lexer.raise_syntax_error(
                    'multiple file encoding specifiers')
            else:
                self.encoding = encoding

        def get_encoding(self):
            if self.parent is not None:
                return self.parent.get_encoding()
            return self.encoding
        
        def __str__(self):
            return self._to_string()
            
        def _to_string(self, indent = ''):
            """dumps out the structure attempting to recreate the original source file,
            more or less."""
            
            list = []
            if self.encoding is not None:
                list.append("# -*- encoding: %s -*-" % self.encoding)

            list.append("<%args>")
            for arg in self.args.keys():
                list.append(arg + " = " + repr(self.args[arg]))
            list.append("</%args>")
            
            for key in ('once', 'init', 'shared', 'body', 'cleanup'):
                block = self.get_block_list(key)
                
                if key != 'body':
                    list.append("<%%%s>" % key)
                else:
                    list.append("# body code begin")
                    
                iter = Compiler.BlockFlyweightIterator(block)
                for code in iter:
                    list.append(code.get_line(iter))

                if key != 'body':
                    list.append("</%%%s>\n" % key)
                else:
                    list.append("# body code end\n")

            
            for blockname, blocks in self.named_blocks.iteritems():
                for key, value in self.def_blocks.iteritems():
                    ind = indent + "\t"
                    list.append(ind + "<%%%s %s>" % (blockname, key))
                    list.append(value._to_string(ind + "\t"))
                    list.append(ind + "</%%%s %s>" % (blockname, key))

            
            return indent + string.join(list, "\n" + indent)
    
        
    
    def compile(self, source, name, file, input_file = None):
        """compiles a source file.
        
        source - a string representing the source of the file
        name - a name to give to the compiled object
        file - a file object that the compiled output will be streamed to."""
        
        self.current_compile = Compiler.Compiled(compiler = self, fileid = name, name = 'top_level')

        # Preprocess the source.  The preprocessor routine is handed a
        # reference to the entire source.
        if self.python_pre_processor:
            try:
                source = self.python_pre_processor(source)
            except Exception, e:
                raise exception.Compiler(e.args)
    
        self.lexer.lex(source, name, self, input_file)
        self.compiled_component(file)
        


    def start_block(self, block_type, attributes = None):
        """called by Lexer to indicate a <%block> tag """
                
        compile = self.current_compile

        if top_level_only_block.has_key(block_type) and not compile.in_main:
            self.lexer.raise_syntax_error("Cannot define a %s section inside a method or subcomponent" % block_type)

        if compile.start_blocks.has_key(block_type):
            compile.start_blocks[block_type] = self.lexer.line_number()
        
        if compile.in_block:
            self.lexer.raise_syntax_error("Cannot nest a %s inside a %s block" % (block_type, c.in_block))

        compile.in_block = block_type


    def end_block(self, block_type):
        """called by Lexer to indicate a </%block> tag"""
        compile = self.current_compile
        
        if compile.in_block != block_type:
            self.lexer.raise_syntax_error("End of %s encountered while in %s block" % (block_type, compile.in_block))
        
        compile.in_block = None

    
    def text_block(self, block, **params):
        Compiler.textline.append(self.current_compile.get_block_list('body'), block, self.lexer.line_number())

        
    # comment - discard
    def doc_block(self, **params):pass

    def magic_encoding_comment(self, encoding, **params):
        """A magic -*- encoding: foo -*- style comment."""
        assert encoding and type(encoding) is str
        self.current_compile.set_encoding(encoding)
        
    def post_process_text(self, code):
        if self.text_post_processor:
            try:
                return self.text_post_processor(code)
            except Exception, e:
                raise exception.Compiler(e.args)
        else:
            return code
        
    
    def post_process_python(self, code):
        if self.python_post_processor:
            try:
                return self.python_post_processor(code)
            except Exception, e:
                raise exception.Compiler(e.args)
        else:
            return code 
    
    def raw_block(self, **params):
        # see if we have a method corresponding to this block and call it if so

        if BLOCKS.has_key(params['block_type']):
            method = BLOCKS[params['block_type']]
            
            # call method dynamically
            return getattr(self, method)(**params)

        else:
            Compiler.codeblock.append(self.current_compile.get_block_list(params['block_type']), params['block'], self.lexer.line_number())

        
    def variable_declaration(self, block_type, name, default, scope):
        
        """Inserts a variable declaration from the C<< <%args> >> section into
        the component."""

        if block_type != 'args':
            self.lexer.raise_syntax_error("Variable Declaration called inside a %s block" % block_type)
        
        self.current_compile.add_argument(name, default, self.lexer.line_number(), scope)
        
    def key_value_pair(self, block_type, key, value):
        try :
            dict = {"flags": self.current_compile.flags, "attr": self.current_compile.attr}[block_type]
            if dict.has_key(key):
                self.lexer.raise_syntax_error("%s %s already defined" % (key, block_type))
                
            dict[key] = value

            if block_type == "flags" and key == "encoding":
                #warnings.warn(
                #    "The 'encoding' flag has been deprecated, "
                #    "use an encoding magic comment instead.",
                #    category=DeprecationWarning)
                self.current_compile.set_encoding(eval(value, {}))

        except KeyError:
            exception.Compiler("key_value_pair called inside a %s block" % block_type)
        

    def python_line(self, line):
        Compiler.codesingleline.append(self.current_compile.get_body(), line, self.lexer.line_number())
        
    def python_block(self, block, **params):
        Compiler.codeblock.append(self.current_compile.get_body(), block, self.lexer.line_number())

    def substitution(self, line, escape):
        if escape or len(self.default_escape_flags):
            dict = OrderedDict()

            if escape:
                escapes = re.split(r"\s*,\s*", escape)
                for esc in escapes:
                    dict[esc] = 1

            if self.default_escape_flags and not dict.has_key('n'):
                for esc in self.default_escape_flags:
                    dict[esc] = 1

            if dict.has_key('n'): del dict['n']

            escapes = dict.keys()
        else:
            escapes = None
                
        Compiler.substituteline.append(self.current_compile.get_body(), line, escapes, self.lexer.line_number())

    def start_component(self):
        pass

    def end_component(self):
        compile = self.current_compile
        if len(compile.component_content_call_stack) > 0:
            self.lexer.raise_syntax_error("Not enough component-with-content ending tags found")
    


    def compiled_component(self, file):
        self.generator.generate(self, self.current_compile, file)
        

    def start_named_block(self, block_type, name, attributes):
        compile = self.current_compile
        
        # Error if defining one def or method inside another
        if block_type != 'closure' and not compile.in_main:
            self.lexer.raise_syntax_error("Cannot define a %s block inside a method or subcomponent" % block_type)

        if re.search(r"[^.\w-]", name):
            self.lexer.raise_syntax_error("Invalid %s name: %s" % (block_type, name))


        # error if we have a named block with this name already
        if block_type != 'closure' and compile.has_named_block(None, name):
            block = compile.get_named_block(None, name)
            self.lexer.raise_syntax_error("%s block %s already exists" % (block.block_type, name))
                
        # make a new compile object, set it to be our current
        newcompile = Compiler.Compiled(compiler = self, parent = self.current_compile, in_main = False, fileid = self.current_compile.fileid, name = name, block_type = block_type, flags = attributes)
        if block_type != 'closure':
            compile.add_named_block(block_type, name, newcompile)
        else:
            Compiler.closure.append(self.current_compile.get_body(), newcompile, self.lexer.line_number())
        
        self.current_compile = newcompile


    def end_named_block(self, block_type):
        # reset current compile object to be its parent
        if self.current_compile.parent:
            self.current_compile = self.current_compile.parent
        else:
            raise exception.Compiler("end_named_block found no parent block")


    def _generic_component_call(self, call, iscontent = False, isclose = False):
    
        if isclose:
            try:
                call = self.current_compile.component_content_call_stack.pop()
            except IndexError:
                self.lexer.raise_syntax_error("found component with content ending tag but no beginning tag")
        else:
            call = string.strip(call)

        (component, args) = (re.split(r",", call, 1) + [''])[0:2]
        component = string.strip(component)
        args = string.strip(args)

        if not iscontent:       
            Compiler.componentcall.append(self.current_compile.get_body(), component, args, self.lexer.line_number())
        else:
            if not isclose:
                self.current_compile.component_content_call_stack.append(call)
                Compiler.componentcontentcall.append(self.current_compile.get_body(), component, args, self.lexer.line_number())
            else:
                Compiler.componentcontentcallend.append(self.current_compile.get_body(), component, args, self.lexer.line_number())

    def component_call(self, call):
        self._generic_component_call(call, False, False)
        
    def component_content_call(self, call):
        self._generic_component_call(call, True, False)
    
    def component_content_call_end(self):
        self._generic_component_call(None, True, True)


    def get_encoding(self):
        return self.current_compile.get_encoding()
        
