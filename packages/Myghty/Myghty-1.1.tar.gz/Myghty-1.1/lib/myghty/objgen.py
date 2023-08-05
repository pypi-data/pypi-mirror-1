# $Id: objgen.py 2133 2006-09-06 18:52:56Z dairiki $
# objgen.py - generates object files for Myghty
# Copyright (C) 2004, 2005 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of Myghty and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#
#

import re, string, types, time
from myghty.util import *
import myghty.exception as exception

class ObjectGenerator:
    """ generates myghty object files.
    
    uses the visitor pattern combined with the Compiler's flyweight pattern to 
    efficiently loop through a tokenized page object and produce appropriate code.
    
    an ObjectGenerator is stateful and is not threadsafe.  the clone() method can be used
    to create copies of this object for use in multiple threads.
    """
    
    def visit_code_block(self, block_obj, context):raise NotImplementedError()
    def visit_code_single_line(self, block_obj, context):raise NotImplementedError()
    def visit_text_line(self, block_obj, context):raise NotImplementedError()
    def visit_component_block(self, compiled):raise NotImplementedError()
    def visit_def_block(self, compiled):raise NotImplementedError()
    def visit_method_block(self, compiled):raise NotImplementedError()
    def visit_closure_block(self, compiled):raise NotImplementedError()
    def visit_substitution(self, block_obj, context):raise NotImplementedError()
    def visit_component_call(self, block_obj, context):raise NotImplementedError()
    def visit_component_content_call(self, block_obj, context):raise NotImplementedError()
    def visit_component_content_call_end(self, block_obj, context):raise NotImplementedError()
    
    def generate(self, compiler, compiled, stream):raise NotImplementedError()
    
    def clone(self, **params):
        """creates a clone of this ObjectGenerator.  allow the Prototype pattern
        to be used in creating generators for other threads."""
        raise NotImplementedError()


class PythonGenerator:


    def clone(self, **params):
        """creates a clone of this ObjectGenerator.  allow the Prototype pattern
        to be used in creating generators for use in other threads."""
        return PythonGenerator()

    def generate(self, compiler, compiled, stream):
        self.printer = PythonPrinter(stream)
        self.compiler = compiler
        self.compiled = compiled
        self.textbuffer = ''
        self.indentstack = []
        self.in_block = False
        self.last_asserted_line = -1
        
        self.uses_shared = (compiled.block_has_code("shared"))
        self.uses_threadonce = (compiled.block_has_code("threadonce"))
        
        # call the initial accept_visitor that will start the 
        # traversal of the whole compiled object
        compiled.accept_visitor(self)
        self.printer.close()

    def visit_code_block(self, block_obj, context):
        """handles a <%python> block, adjusting indent to match the
        current indent level."""
        
        self._flush_text()
        lines = block_obj.get_lines(context)

        self.printer.print_comment("BEGIN CODE BLOCK")
        self._assert_line_comment(block_obj, context)
        linenum = block_obj.get_line_number(context)
        
        for line in lines:
            line = self.compiler.post_process_python(line)
            #self.printer.add_normalized_block_line(self._line_comment(linenum))
            #linenum += 1
            self.printer.add_normalized_block_line(line)

        self.printer.print_comment("END CODE BLOCK")
    
    def visit_text_line(self, block_obj, context):
        """handles regular lines of text.
        
         Text line printing is buffered so that consecutive lines of text
         can be combined into a single print statement"""
         
        if not self.textbuffer: self._assert_line_comment(block_obj, context)
        self.textbuffer += self.compiler.post_process_text(block_obj.get_line(context))

    def visit_component_call(self, block_obj, context):
        self._generate_component_call(block_obj, context, content = False)
        
    def visit_component_content_call(self, block_obj, context):
        self._print_python("def %s():" % "component_content", block_obj, context)
        self._assert_line_comment(block_obj, context)
        self._cc_line = block_obj.get_line_number(context)
        
    def visit_component_content_call_end(self, block_obj, context):
        self._generate_component_call(block_obj, context, content = True)

    def _generate_component_call(self, block_obj, context, content = False):
        name = block_obj.get_component(context)

        self._assert_line_comment(block_obj, context)

        if self.closures.has_key(name):
            funcname = 'm.closure_with_content'
            args = [name]
        else:
            funcname = 'm.execute_component'
            args = ["'%s'" % name]
        if block_obj.get_args(context):
            args.append("args = argdict(%s)" % block_obj.get_args(context))
        if content is True:
            args.append("content = component_content")
            if block_obj.get_line_number(context) == self._cc_line:
                self._print_python("pass", block_obj, context)
            self._print_python(["", "%s(%s)" % (funcname, string.join(args, ", "))],
                        block_obj, context)
        else:
            self._print_python("%s(%s)" % (funcname, string.join(args, ", ")),
                        block_obj, context)
        
    def visit_code_single_line(self, block_obj, context):
        self._assert_line_comment(block_obj, context)
        self._print_python(block_obj.get_line(context), block_obj, context, normalize_indent = True)


    def visit_substitution(self, block_obj, context):
        escapes = block_obj.get_escapes(context)
        if escapes:
            code = "m.write(m.apply_escapes(%s, %s))" % (block_obj.get_line(context), repr(escapes))
        else:
            code = "m.write(%s)" % block_obj.get_line(context)
        
        self._assert_line_comment(block_obj, context)
        self._print_python(code, block_obj, context)
    
    
    def visit_component_block(self, compiled):
        self._generate_module_header(compiled)
        
        for block in compiled.get_named_blocks():
            block.accept_visitor(self)

        self._generate_component_class(compiled)
        

    def visit_def_block(self, compiled):
        self._generate_component_class(compiled, is_subcomponent = True, is_method = False)
            
    def visit_method_block(self, compiled):
        self._generate_component_class(compiled, is_subcomponent = True, is_method = True)


    def visit_closure_block(self, block_obj, context):
        compiled = block_obj.get_compiled(context)

        indent = self.printer.indentstring * self.printer.indent + " " * len(compiled.name)

        self.closures[compiled.name] = True
        
        def format_arg(arg):
            if not arg.required:
                return "\n%s%s = %s, " % (indent, arg.name, arg.default)
            else:
                return "\n%s%s, " % (indent, arg.name)

        args = []
        
        reqarg = [arg for arg in compiled.args.values() if arg.required]
        if len(reqarg):
            args.append(string.join(map(format_arg, reqarg)))

        nonreqarg = [arg for arg in compiled.args.values() if not arg.required]
        if len(nonreqarg):
            args.append(string.join(map(format_arg, nonreqarg)))

        args += ["\n" + indent + "**_comp_params"]

        code = "def %s(%s):" % (compiled.name, string.join(args))
        self._print_python(code, block_obj, context)
        self._generate_run_body(compiled)


    # generation methods.  each spits out various parts of the module 
    # file.  they are broken up to handle some freaky rearrangements that occur
    # based on if the component uses <%shared>, <%filter>, <%cleanup> etc.
    # <%shared> is the craziest one by far.
    
    def _generate_module_header(self, compiled):
        """generates the top header of the file, the <%once> section, and the dynamic subs if
        the module has a <%shared> block"""
        
        self.printer.print_comment("File: %s CompilerID: %s Timestamp: %s" % (compiled.fileid, self.compiler.get_object_id(), time.asctime()))

        if compiled.encoding is not None:
            self.printer.print_comment("-*- encoding: %s -*-"
                                       % compiled.encoding)
            

        self.printer.print_python_line("from myghty.component import Component, FileComponent, SubComponent")
        
        self.printer.print_python_line("import myghty.request as request")
        self.printer.print_python_line("import myghty.args")
        self.printer.print_python_line("from myghty.util import *")

        self.printer.print_python_line("_CREATION_TIME = %d" % time.time())
        
        self.printer.print_python_line("_MAGIC_NUMBER = %s"
                                       % repr(self.compiler.get_magic_number()))
        if compiled.block_has_code("once"):
            self._output_block(compiled, "once")

        if self.uses_threadonce:
            self._push_indent()
            self._generate_python_def(compiled, "thread_local_initializer", append_globals = True, append_component = False, args = ['self'])
            self._output_block(compiled, "threadonce")
            
            if self.uses_shared:
                self._push_indent()
                self._generate_python_def(compiled, "request_local_initializer", append_globals = True, append_component = False, args = ['self'])
                self._output_block(compiled, "shared")
                
            self._generate_dynamic_subs(compiled)
            
            if self.uses_shared:
                self._pop_indent()
                self.printer.print_raw_line("\n")
                self.printer.print_python_line("return request_local_initializer")
            
            self._pop_indent()
            
        elif self.uses_shared:
            self._push_indent()
            self._generate_python_def(compiled, "request_local_initializer", append_globals = True, append_component = False, args = ['self'])
            self._output_block(compiled, "shared")

            self._generate_dynamic_subs(compiled)
            
            self._pop_indent()  
    
    def _generate_dynamic_subs(self, compiled): 
        for block in compiled.get_named_blocks() + [compiled]:
            self._push_indent()
            self._generate_run_define(block, methodname = ("run_%s" % self._format_class_name(block.name)), is_dynamic_method = True)
            self._generate_run_body(block)
            self._pop_indent()
        self.printer.print_python_line("return {")
        for block in compiled.get_named_blocks() + [compiled]:
            self.printer.print_python_line("   '%s' : %s," % (self._format_class_name(block.name),("run_%s" % self._format_class_name(block.name)) ))
        self.printer.print_python_line("}")
    
    def _generate_component_class(self, compiled, **params):
        """generates the class definition of a component, all methods within the class,
        and a static accessor function if the component is the lead component"""
        
        self._push_indent()
        self._generate_init(compiled, **params)

        dynamic = (self.uses_shared or self.uses_threadonce)
        self._generate_run_define(compiled, add_dynamic_call = dynamic)
        if not dynamic:
            self._generate_run_body(compiled)

        self._pop_indent()
    
        if compiled.in_main:
            self.printer.print_raw_line("\n")
            self.printer.print_python_line("def get_component(interpreter, csource): return %s(interpreter, csource)" % self._format_class_name(compiled.name))

    def _generate_subcomponent_constructor(self, compiled, is_method):
        """generates a constructor call to create a subcomponent (def or method)"""
        
        return "'%s' : %s('%s', self, is_method = %s)" % (
            compiled.name,
            self._format_class_name(compiled.name),
            compiled.name,
            repr(is_method)
            )
        
    def _generate_init(self, compiled, is_subcomponent = False, is_method = False):
        """generates the __init__ method for a component """
        
        if is_subcomponent:
            superclass = "SubComponent"
        else:
            superclass = "FileComponent"

        self.printer.print_raw_line("\n")
        self.printer.print_python_line("class %s(%s):" % (self._format_class_name(compiled.name), superclass))

        self.printer.print_python_line("def do_component_init(self):")

        self.printer.print_python_line("self.defs = {%s}" % 
                string.join(map(lambda c: self._generate_subcomponent_constructor( c, False), 
                    compiled.get_named_blocks("def")), ",\n"))

        self.printer.print_python_line("self.methods = {%s}" % 
                string.join(map(lambda c: self._generate_subcomponent_constructor( c, True), 
                compiled.get_named_blocks("method")), ",\n"))

        self.printer.print_python_line("self.flags = %s" % self._repr_key_value(compiled.flags))
        self.printer.print_python_line("self.attr = %s" % self._repr_key_value(compiled.attr))
        self.printer.print_python_line("self.arguments = [%s]" % string.join(["myghty.args." + repr(arg) for arg in compiled.args.values()], ",\n"))
        self.printer.print_python_line("self.creationtime = _CREATION_TIME")
        
        if compiled.in_main:
            if self.uses_threadonce:
                    self.printer.print_python_line("self.thread_local_initializer = thread_local_initializer")
            elif self.uses_shared:
                self.printer.print_python_line("self.request_local_initializer = request_local_initializer")

        if compiled.block_has_code("filter"):
            self._generate_python_def(compiled, "filter", append_globals = True, append_component = False, args = ['f'])
            self._output_block(compiled, "filter")
            self.printer.print_python_line("")
            self.printer.print_python_line("self.filter = self._init_filter_func(filter)")
        elif compiled.flags.has_key('trim'):
            self.printer.print_python_line("self.filter = self._init_filter_func()")
            
        self.printer.print_python_line("")
        
        self.printer.print_python_line("def uses_request_local(self):return %s" % repr(self.uses_shared and compiled.in_main))
        self.printer.print_python_line("def uses_thread_local(self):return %s" % repr(self.uses_threadonce and compiled.in_main))
        

    def _repr_key_value(self, keyvalue):
        return ("{" +
            string.join(map(lambda k: "'%s' : %s" % (k, keyvalue[k]), keyvalue.keys()), ",\n")
        + "}")
            
    def _generate_run_define(self, compiled, methodname = "do_run_component", is_dynamic_method = False, add_dynamic_call = False):

        self.closures = {}

        (args, indent) = self._generate_method_args(compiled, methodname, append_globals = (is_dynamic_method or not add_dynamic_call), append_component = (is_dynamic_method or not add_dynamic_call))
        if not is_dynamic_method:
            defargs = ['self, '] + args
        else:
            defargs = args
        
        self.printer.print_comment("BEGIN BLOCK args")
        if compiled.start_blocks['args'] != -1: self.printer.print_comment(self._line_comment(compiled.start_blocks['args']))
        self.printer.print_python_line("def %s(%s\n%s):" % (methodname, string.join(defargs), indent))
        self.printer.print_comment("END BLOCK args")
    
        if add_dynamic_call:
            self.printer.print_python_line("return self._call_dynamic('%s', %s)" % 
                (
                    self._format_class_name(compiled.name),
                    string.join(args)
                )
            )

    def _generate_python_def(self, compiled, methodname, append_globals, append_component, args = None):
        (genargs, indent) = self._generate_method_args(compiled, methodname, append_globals = append_globals, append_component = append_component)
        if args is not None:
            genargs = [arg + ", " for arg in args] + genargs
        self.printer.print_python_line("def %s(%s\n%s):" % (methodname, string.join(genargs), indent))
        
    def _generate_method_args(self, compiled, methodname, append_globals, append_component):
        
        indent = self.printer.indentstring * self.printer.indent + " " * len(methodname)

        # we're trying to print the args with linebreaks, for an <%ARGS> section that was defined like
        # "g ='foo' #define g to be foo" , but this doesnt really work anyway since you need to get the commas 
        # in between where the comment starts....
        def format_arg(arg):
            if not arg.required:
                return "\n%s%s = %s, " % (indent, arg.name, arg.default)
            else:
                return "\n%s%s, " % (indent, arg.name)

        args = ['m, ', 'ARGS, ']

        if append_globals:
            # append global arguments to arg list.  the most ordinary is
            # "r" for the HTTP request.  "s" for session would be nice as well.
            args += map(lambda x: "%s, " % x, compiled.compiler.allow_globals)

        if append_component:
            reqarg = [arg for arg in compiled.args.values() if arg.required]
            if len(reqarg):
                args.append(string.join(map(format_arg, reqarg)))

            nonreqarg = [arg for arg in compiled.args.values() if not arg.required]
            if len(nonreqarg):
                args.append(string.join(map(format_arg, nonreqarg)))

            args += ["\n" + indent + "**_comp_params"]
        else:
            args += ['**_comp_params']

        return (args, indent)

        
    def _generate_run_body(self, compiled):
        
        has_blocks = False
        
        # generate blocks in order
        if compiled.block_has_code("cleanup"):
            # increments indent one more level
            self.printer.print_python_line("try:")
        
        for key in ('init', 'body', 'cleanup'):
            if not compiled.block_has_code(key):
                continue
                
            if key == 'cleanup':
                self.printer.print_python_line("finally:")
                self.printer.print_python_line("pass")
                
            self._output_block(compiled, key)
            has_blocks = True

        if not has_blocks:
            self.printer.print_python_line("pass")
            
        self.printer.print_python_line("")
        
        if compiled.block_has_code("cleanup"):
            # decrement indent one more level
            self.printer.print_python_line("")
        

    def _output_block(self, compiled, block_type):
        """traverses the lines of flyweight objects in a block 
        object (such as init, once, body) and outputs python code"""
        
        self._push_indent()
        iter = compiled.get_block_iterator(block_type)
        has_code = False
        
        outermost_block = False
        if not self.in_block:
            self.printer.print_comment("BEGIN BLOCK %s" % block_type)
            self.in_block = True
            outermost_block = True
        
        for code in iter:
            has_code = True
            code.accept_visitor(self, iter)

        if has_code:
            self._flush_text()

        if outermost_block:
            self.printer.print_comment("END BLOCK %s" % block_type)
            self.in_block = False
            
        self._pop_indent()
        self.printer.clear_whitespace_stack()
        return has_code


    def _print_python(self, code, block_obj, context, normalize_indent = False):
        """prints python code, performing the convenience steps of flushing
        the existing text buffer, printing line number tracking comments,
        and post processing of python code"""
        
        self._flush_text()
        self._assert_line_comment(block_obj, context)

        if type(code) == types.ListType:
            for c in code:
                self.compiler.post_process_python(c)
                self.printer.print_python_line(c, normalize_indent = normalize_indent)
        else:
            self.compiler.post_process_python(code)
            self.printer.print_python_line(code, normalize_indent = normalize_indent)
        
    def _assert_line_comment(self, block_obj, context):
        if block_obj.get_line_number(context) != self.last_asserted_line:
            self.printer.print_comment(self._line_comment(block_obj.get_line_number(context)))
            self.last_asserted_line = block_obj.get_line_number(context)

    def _line_comment(self, linenumber):
        return "SOURCE LINE %s" % (linenumber)

    def _flush_text(self):
        if not self.textbuffer: return
        buffer = self.compiler.post_process_text(self.textbuffer)
        # escape single quotes and backslashes
        buffer = re.sub(r"(['\\])", r"\\\1", buffer)
        if self.compiler.disable_unicode:
            self.printer.print_python_line("m.write('''%s''')" % buffer)
        else:
            self.printer.print_python_line("m.write(u'''%s''')" % buffer)
        self.textbuffer = ''

    def _format_class_name(self, name):
        name = re.sub(r"\.", "_", name)
        name = re.sub(r"[^\d\w_]", "", name)
        return "_" + name

    def _push_indent(self):
        """stores the current indentation level of the Python printer on a stack."""
        self.indentstack.append(self.printer.indent)
        
    def _pop_indent(self):
        """restores the indentation level of the Python printer to what we last
        stored."""
        indent = self.indentstack.pop()
        self.printer.indent = indent

        
class PythonPrinter:
    """prints Python code, keeping track of indentation level.  PythonPrinter has two
    basic modes, "print_python_line" mode which prints one line at a time and calculates
    whitespace on the fly, and "add_normalized_block_line" mode where you add lines to a 
    buffer, and then at the end print them all out as they were stored, 
    except relative to the current indent."""
    
    def __init__(self, stream):
        # the indentation counter
        self.indent = 0
        
        # a stack storing information about why we incremented 
        # the indentation counter, to help us determine if we
        # should decrement it
        self.indent_detail = []
        
        # the string of whitespace multiplied by the indent
        # counter to produce a line
        self.indentstring = "       "
        
        # a stack of whitespace we pulled from "normalized" 
        # Python lines to track when the indentation counter should
        # be incremented or decremented
        self.spacestack = []
        
        # the stream we are writing to
        self.stream = stream
        
        # a list of lines that represents a buffered "block" of code,
        # which can be later printed relative to an indent level 
        self.line_buffer = []
        
        # boolean indicating if we are in "print_python_line" mode or
        # "add_normalized_block_line" mode
        self.in_indent_lines = False
        
        self._reset_multi_line_flags()
        
    def print_python_line(self, line, normalize_indent = False, is_comment = False):
        """prints a line to the output buffer, preceded by a blank indentation
        string of proportional size to the current indent counter.  
        
        If the line ends with a colon, the indentation counter is incremented after
        printing.  If the line is blank, the indentation counter is decremented.
        
        if normalize_indent is set to true, the line is printed
        with its existing whitespace "normalized" to the current indentation 
        counter; additionally, its existing whitespace is measured and
        compared against a stack of whitespace strings grabbed from other
        normalize_indent calls, which is used to adjust the current indentation 
        counter.
        
        basically, "normalize_indent" is used with % lines in a template, 
        and non-normalize_indent is used by the objectgenerator's internally 
        generated lines of code.
        """

        if not self.in_indent_lines:
            self.flush_normalized_block()
            self.in_indent_lines = True

        decreased_indent = False
    
        if (
            re.match(r"^\s*#",line) or
            re.match(r"^\s*$", line)
            ):
            hastext = False
        else:
            hastext = True

        if normalize_indent:
            # determine the actual amount of whitespace preceding the
            # line of code.  check it against a stack of whitespace
            # and push it on if it is of greater indent and also
            # has some non-whitespace text, or pop 
            # the existing whitespace if it is of lesser indent
        
            line = string.expandtabs(line)
            space = re.match(r"^([ ]*)", line).group(1)

            # see if we have any whitespace already 
            if len(self.spacestack) == 0:
                if hastext:
                    self.spacestack.append(space)
            else:
                if len(space) > len(self.spacestack[-1]):
                    if hastext:
                        self.spacestack.append(space)

                elif len(space) < len(self.spacestack[-1]):
                    self.spacestack.pop()
                    if self.indent > 0: 
                        self.indent -=1
                        if len(self.indent_detail) == 0:  raise exception.Compiler("Too many whitespace closures")
                        self.indent_detail.pop()
                        decreased_indent = True

            line = string.lstrip(line)
        else:
            # not normalizing indentation.  no whitespace should be present.
            space = None
        
        # see if this line should decrease the indentation level
        if (not decreased_indent and 
            not is_comment and 
            (not hastext or self._is_unindentor(line, space))
            ):
            
            if self.indent > 0: 
                self.indent -=1
                # if the indent_detail stack is empty, the user
                # probably put extra closures - the resulting
                # module wont compile.  
                if len(self.indent_detail) == 0:  raise exception.Compiler("Too many whitespace closures")
                self.indent_detail.pop()
            
        # write the line    
        self.stream.write(self._indent_line(line) + "\n")
        
        # see if this line should increase the indentation level.
        # note that a line can both decrase (before printing) and 
        # then increase (after printing) the indentation level.

        if re.search(r":[ \t]*(?:#.*)?$", line):
            # increment indentation count, and also
            # keep track of what the keyword was that indented us,
            # if it is a python compound statement keyword
            # where we might have to look for an "unindent" keyword
            match = re.match(r"^\s*(if|try|elif|while|for)", line)
            if match:
                # its a "compound" keyword, so we will check for "unindentors"
                indentor = match.group(1)
                self.indent +=1
                self.indent_detail.append((space, indentor))
            else:
                indentor = None
                # its not a "compound" keyword.  but lets also
                # test for valid Python keywords that might be indenting us,
                # else assume its a non-indenting line
                m2 = re.match(r"^\s*(def|class|else|elif|except|finally)", line)
                if m2:
                    self.indent += 1
                    self.indent_detail.append((space, indentor))
        
    
    def _is_unindentor(self, line, space):
        """looks at the keyword and its whitespace that was most recently 
        responsible for incrementing the indent,
        and compares against the keyword (if any) and whitespace for the given line,
        to see if an unindent operation should occur"""
                
        # no indentation detail has been pushed on; return False
        if len(self.indent_detail) == 0: return False

        (indspace, indentor) = self.indent_detail[-1]
        
        # the last indent keyword we grabbed is not a 
        # compound statement keyword; return False
        if indentor is None: return False
        
        # the indentation from the last indent keyword we
        # grabbed does not match this current keword; return False
        if indspace != space: return False
        
        # if the current line doesnt have one of the "unindentor" keywords,
        # return False
        match = re.match(r"^\s*(else|elif|except|finally)", line)
        if not match: return False
        
        # whitespace matches up, we have a compound indentor,
        # and this line has an unindentor, this
        # is probably good enough
        return True
        
        # should we decide that its not good enough, heres
        # more stuff to check.
        #keyword = match.group(1)
        
        # match the original indent keyword 
        #for crit in [
        #   (r'if|elif', r'else|elif'),
        #   (r'try', r'except|finally|else'),
        #   (r'while|for', r'else'),
        #]:
        #   if re.match(crit[0], indentor) and re.match(crit[1], keyword): return True
        
        #return False
        
    def print_comment(self, comment):
        self.print_python_line("# " + comment, is_comment = True)
        
    def _indent_line(self, line, stripspace = ''):
        return re.sub(r"^%s" % stripspace, self.indentstring * self.indent, line)

    def _reset_multi_line_flags(self):
        (self.backslashed, 
        self.triplequoted) = (False, False) 
        
    def _in_multi_line(self, line):
        # we are only looking for explicitly joined lines here,
        # not implicit ones (i.e. brackets, braces etc.).  this is just
        # to guard against the possibility of modifying the space inside 
        # of a literal multiline string with unfortunately placed whitespace
         
        current_state = (self.backslashed or self.triplequoted) 
                        
        if re.search(r"\\$", line):
            self.backslashed = True
        else:
            self.backslashed = False
            
        triples = len(re.findall(r"\"\"\"|\'\'\'", line))
        if triples == 1 or triples % 2 != 0:
            self.triplequoted = not self.triplequoted

            
        return current_state


    def print_raw_line(self, line, indentlevel = 0):
        """adds a line to the deffered print buffer with the "multiline" flag set to true,
        so that this line will come out with its original indentation intact."""
        
        self.in_indent_lines = False
        self.line_buffer.append([True, line])


    def add_normalized_block_line(self, line):
        """adds a line to the deferred print buffer.
        
        When the deferred print buffer is flushed, its lines will be scanned for the
        initial whitespace amount.  lines with that much or greater whitespace
        will have their whitespace adjusted to line up with the whitespace that has
        been established by the last print_indent_line call.  Lines within continued 
        triplequotes and backslashes will remain unaffected.....if all goes well.
        
        This method is basically used for <%python> blocks.
        """
                
        self.in_indent_lines = False
        
        # append a record consisting of a multiline flag
        # as well as the line itself
        self.line_buffer.append([False, line])
        
    
    def flush_normalized_block(self):
        stripspace = None
        self._reset_multi_line_flags()
        
        for entry in self.line_buffer:
            if self._in_multi_line(entry[1]):
                self.stream.write(entry[1] + "\n")
            else:
                entry[1] = string.expandtabs(entry[1])
                if stripspace is None and re.search(r"[^ \t]", entry[1]):
                    stripspace = re.match(r"^([ \t]*)", entry[1]).group(1)
    
                self.stream.write(self._indent_line(entry[1], stripspace) + "\n")
            

            
        self.line_buffer = []
        self._reset_multi_line_flags()

    def clear_whitespace_stack(self):
        self.spacestack = []

    def close(self):
        self.flush_normalized_block()
