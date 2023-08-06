#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
from bottle import redirect, request, route, send_file
from mako.exceptions import TopLevelLookupException
from mako.lookup import TemplateCollection
from mako.template import Template
import os.path
import subprocess

__version__ = 0.2
__license__ = 'MIT'

class Config:
    """
    Cuttlefish config from plist file.
    """
    filename = 'cuttlefish-config.plist'
    path_to_static = '.'
    plist = {}
    kleene_collection = ["."] # Have a usable default when no config is loaded
    
    @classmethod
    def loadFromVicinity(cls, path):
        from os.path import expanduser, expandvars, isdir, dirname, join
        from plistlib import readPlist
        path = expanduser(expandvars(path)) # Unix goodness
        if not isdir(path):
            path = dirname(path)
        file = join(path, cls.filename)
        cls.plist = readPlist(file)
        cls.path_to_static = join(path, 'static')
    
    @classmethod
    def collections(cls):
        return cls.plist['collections'].keys()
    
class SourceTemplateCollection (TemplateCollection):
    """
    Mako TemplateCollection embedded in the source.
    """
    def __init__(self):
        TemplateCollection.__init__(self)
        kwargs = {
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8',
            'encoding_errors': 'replace',
            'format_exceptions': True,
            #'imports': ["from cuttlefish import Config"],
            'lookup': self,
        }
        self.builtins = {}
        
        self.builtins['attribution'] = Template(ur"""# -*- coding: utf-8 -*-
            <center id="copyleft">
                <p>Copyright &copy; 2009 Kaelin Colclasure &bull; MIT License &bull; See <a href="/static/LICENSE.html">LICENSE</a> for details&hellip;<br/>
                Cuttlefish logo by Randall Munroe &bull; <a href="http://www.xkcd.com/520">www.xkcd.com</a></p>
            </center>
        """, **kwargs)

        self.builtins['formq'] = Template(ur"""# -*- coding: utf-8 -*-
            <%def name="mkoption(label,value,selected=None)">
                % if value == selected:
                    <option value="${value}" selected="True">\
                % else:
                    <option value="${value}">\
                % endif
                ${label | h}</option>
            </%def>
            <form action="/cuttlefish/search" accept-charset="utf-8" method="get">
            <table align="center">
            <tr>
                <td class="nobr">
                    <input name="q" value="${q | u}" type="search" placeholder="" autosave="net.colclasure.cuttlefish.q" results="20" maxLength="256" size="55" />
                    <input name="c" value="3" type="hidden" />
                    <input name="r" value="cooked" type="hidden" />
                    <input type="submit" value="Search" name="btnSearch" />
                </td>
            </tr>
            <tr>
                <td class="nobr" align="center">
                    Collection: <select id="collection" name="cn">
                                ${mkoption("All collections", "*", cn)}
                                <optgroup label="Select collection">
                                % for collection in Config.collections():
                                    ${mkoption(collection, collection, cn)}
                                % endfor
                                </optgroup>
                                </select>
                </td>
            </tr>
            </table>
            </form>
        """, **kwargs)

        self.builtins['root'] = Template(ur"""# -*- coding: utf-8 -*-
            <html>
            <head>
                <title>Cuttlefish Search: ${subtitle | h}</title>
                <link rel="stylesheet" type="text/css" href="/static/style.css" />
            </head>
            <body>
                <center id="logo">
                    <p><a href="/cuttlefish" class="logolink">
                    <img src="/static/cuttlefish.png" height="150" />[cuttlefish]
                    </a></p>
                </center>
                <%include file='formq' />
                <%include file='attribution' />
            </body>
            </html>
        """, **kwargs)

        self.builtins['cooked'] = Template(ur"""# -*- coding: utf-8 -*-
            <table width="100%">
            % for r in results:
                <tr><td>${r.filename | h}&nbsp;(${r.match_count | h})</td></tr>
                <tr><td><div class="context">
                % for l in r.lines:
                %   if l[0] == -1:
                </div><div class="context">
                %   else:
                %     if l[2]:
                <a href="txmt://open?url=file%3A%2F%2F${r.filename | u}&line=${l[0]}">
                %     endif
                <div class="${('contextline', 'matchline')[l[2]]}">${u"%5d %s" % (l[0], l[1]) | h}</div>
                %     if l[2]:
                </a>
                %     endif
                %   endif
                % endfor
                </div></td></tr>
            % endfor
            </table>
        """, **kwargs)

        self.builtins['raw'] = Template(ur"""# -*- coding: utf-8 -*-
            <pre>${results.raw_results | h}
            </pre>
        """, **kwargs)

        self.builtins['results'] = Template(ur"""# -*- coding: utf-8 -*-
            <html>
            <head>
                <title>Cuttlefish Search: &laquo;${subtitle | h}&raquo;</title>
                <link rel="stylesheet" type="text/css" href="/static/style.css" />
            </head>
            <body>
                <center id="logosmall">
                    <p><a href="/cuttlefish" class="logolink">
                    <img src="/static/cuttlefish.png" height="100" /><br/>[cuttlefish]
                    </a></p>
                </center>
                <%include file='formq' />
                % if render == 'cooked':
                  <%include file='cooked' />
                % elif render == 'raw':
                  <%include file='raw' />
                % else:
                  <%include file='nonesuch' />
                % endif
                <%include file='attribution' />
            </body>
            </html>
        """, **kwargs)

    def get_template(self, uri):
        try:
            return self.builtins[uri]
        except KeyError:
            raise TopLevelLookupException("Cant locate template for uri '%s'" % uri)

stc = SourceTemplateCollection()
results = None

@route('/cuttlefish')
def root():
    global results
    results = None
    return stc.get_template('root').render(subtitle=u"Python Source Code",
                                           q="",
                                           cn="*",
                                           Config=Config)

class MatchChunk:
    """
    Represent one or more matches with their surrounding context.
    """
    def __init__(self):
        self.filename = None
        self.lines = []
        self.match_count = 0
        self.is_last = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if exc_type is StopIteration:
                self.is_last = True
            else:
                return False
        return True
    
    def append(self, lnum, line, is_match=False):
        if is_match:
            self.match_count += 1
        self.lines.append((lnum, line, is_match))

class MatchParser:
    """
    Parse matches from `grep`.
    """
    def __init__(self, input):
        self.input = input
        self.chunk = None
        self.defer = None
        self.fin = False
    
    def _match(self, raw_result):
        try:
            parts = raw_result.split(u':', 2)
            lnum = int(parts[1])
            line = parts[2]
        except (IndexError, ValueError):
            return False
        if self.chunk.filename != None:
            if parts[0] != self.chunk.filename: # Bogus match
                return False
        else:
            if not os.path.isfile(parts[0]): # Bogus match
                return False
            self.chunk.filename = parts[0]
            [self._context(raw_defer) for raw_defer in self.defer]
        self.chunk.append(lnum, line, is_match=True)
        return True;
    
    def _context(self, raw_result):
        if self.chunk.filename == None:
            return False
        assert raw_result.startswith(self.chunk.filename), u"filename:'%s' raw_result:'%s'" % (self.chunk.filename, raw_result)
        raw_result = raw_result[len(self.chunk.filename):]
        parts = raw_result.split(u'-', 2)
        lnum = int(parts[1])
        line = parts[2]
        self.chunk.append(lnum, line, is_match=False)
        return True;
    
    def next(self): # Raise StopIteration when no more results
        if self.fin:
            raise StopIteration
        with MatchChunk() as self.chunk:
            self.defer = []
            raw_result = unicode(self.input.next(), 'utf-8', 'replace').rstrip()
            while raw_result != u"--":
                if self._match(raw_result) or self._context(raw_result):
                    pass
                else:
                    self.defer.append(raw_result)
                raw_result = unicode(self.input.next(), 'utf-8', 'replace').rstrip()
        if self.chunk.is_last:
            self.fin = True
            if len(self.chunk.lines) == 0: # Happens when there are no results…
                raise StopIteration
        return self.chunk

class MatchChunkRunParser:
    """
    Collect runs of chunks from a MatchParser.
    """
    def __init__(self, input):
        self.parser = MatchParser(input)
        self.next_chunk = None
    
    def next(self): # Raise StopIteration when no more results
        if self.next_chunk == None:
            self.next_chunk = self.parser.next()
        chunk = self.next_chunk
        while not chunk.is_last:
            chunk = self.parser.next()
            if chunk.filename != self.next_chunk.filename:
                (self.next_chunk, chunk) = (chunk, self.next_chunk)
                return chunk
            self.next_chunk.append(-1, None) # Marker b/w original chunks
            [self.next_chunk.append(*line) for line in chunk.lines]
        (self.next_chunk, chunk) = (None, self.next_chunk)
        return chunk

class SearchSubprocess:
    """
    Search using `grep` in a subprocess.
    """
    def __init__(self, query, c=3, cn="*", parser=MatchChunkRunParser):
        self.query = query
        self.parser = parser
        cmd = ["/usr/bin/grep",
               "--recursive",
               "--binary-files=without-match",
               "--line-number",
               "--context=%d" % (c),
               "--fixed-strings", query]
        if cn == "*":
            cmd.extend([os.path.abspath(path) for path in Config.kleene_collection])
        else:
            cmd.extend([os.path.abspath(path) for path in Config.plist['collections'][cn]])
        self.proc = subprocess.Popen(cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        self._raw_results = None
    
    def __iter__(self): # Return a parser with a next() method…
        return self.parser(self.proc.stdout)
    
    @property
    def raw_results(self):
        if self._raw_results == None:
            self._raw_results = unicode(self.proc.communicate()[0], 'utf-8', 'replace')
        return self._raw_results

def quicklook(q):
    from pprint import pprint
    results = SearchSubprocess(q)
    for chunk in results:
        pprint((chunk.filename, chunk.match_count, chunk.lines))

@route('/cuttlefish/search')
def search():
    try:
        q = unicode(request.GET['q'], 'utf-8', 'replace')
        c = unicode(request.GET['c'], 'utf-8', 'replace')
        r = unicode(request.GET['r'], 'utf-8', 'replace')
        cn = unicode(request.GET['cn'], 'utf-8', 'replace')
        global results
        if results != None and results.query == q:
            print "Using cached results… NOT!" # Disabled for now
        #else:
        results = SearchSubprocess(query=q, c=int(c), cn=cn)
        return stc.get_template('results').render(subtitle=q,
                                                  q=q,
                                                  render=r,
                                                  cn=cn,
                                                  results=results,
                                                  Config=Config)
    except KeyError:
        redirect('/cuttlefish')

@route('/static/:filename')
def static(filename):
    send_file(filename, root=Config.path_to_static)

def see_bottle_run():
    import bottle
    Config.loadFromVicinity(__file__)
    kwargs = Config.plist['bottle-run-kwargs']
    bottle.run(**kwargs)

if __name__ == "__main__":
    see_bottle_run()
