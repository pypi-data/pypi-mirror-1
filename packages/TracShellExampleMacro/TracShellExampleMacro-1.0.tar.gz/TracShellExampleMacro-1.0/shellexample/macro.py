# Created by  on 2008-06-30.
# Copyright (c) 2008 Noah Kantrowitz. All rights reserved.
import re

from trac.core import *
from trac.wiki.macros import WikiMacroBase
from trac.web.chrome import ITemplateProvider, add_stylesheet
from genshi.core import Markup, escape
from genshi.builder import tag
from pkg_resources import resource_filename

class ShellExampleMacro(WikiMacroBase):
    """Preprocessor Highlight ShellExample"""

    implements(ITemplateProvider)

    regex_crlf = re.compile("(\\r\\n|\\r|\\n)")
    regexp_db_qstr = '"[^"\\\\]*(?:\\\\.[^"\\\\]*){0,250}"';
    regexp_si_qstr = '\'[^\'\\\\]*(?:\\\\.[^\'\\\\]*){0,250}\'';
    regexp = re.compile(
            ('^(?P<path>~ |~?/[^ ]+ |.:.*?\\\\|[a-zA-Z]+@[a-zA-Z]+ )?(?P<cli>[#$] |&gt;)(?P<input>(?:[^\\\\\n\'"]+|\\\\\n|%s|%s|[\\\\\'"]){0,255})$' % (regexp_db_qstr, regexp_si_qstr)) +
            '|^(?P<option_space>\s+)(?P<option>-[a-zA-Z0-9]\\b|--[^ \t\n]+)(?P<option_desc>.*)$'
            '|^(?P<note>\(.*\))$'
            , re.M)
    regexp_string = re.compile('(?:%s|%s)' % (regexp_db_qstr, regexp_si_qstr))
    
    def expand_macro(self, formatter, name, txt):
        add_stylesheet(formatter.req, 'shellexample/shell.css')
        # args will be null if the macro is called without parenthesis.
        txt = txt and self.regex_crlf.sub("\n", escape(txt).replace('&#34;', '"')) or ''
        def stringcallback(match):
            return '<span class="code-string">' + match.group(0) + '</span>'

        def callback(match):
            m = match.group('cli')
            if m:
                path = match.group('path')
                if path:
                    line = '<span class="code-path">' + path + '</span>'
                else:
                    line = ''

                input = self.regexp_string.sub(stringcallback, match.group('input'))
                input = '<span class="code-input">' + input + '</span>'
                if m == '# ':
                    line = line + '<span class="code-root">' + m + input + '</span>'
                else:
                    line = line + '<span class="code-user">' + m + input + '</span>'
                return line
            m = match.group('option')
            if m:
                space = match.group('option_space')
                desc  = match.group('option_desc')
                return space + '<span class="code-func">' + m + '</span>' + desc
            m = match.group('note')
            if m:
                return '<span class="code-note">' + m + '</span>'
            return match.group(0)
        return tag.div(tag.pre(Markup(self.regexp.sub(callback, txt))), class_='code')

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        yield 'shellexample', resource_filename(__name__, 'htdocs')
            
    def get_templates_dirs(self):
        return ()