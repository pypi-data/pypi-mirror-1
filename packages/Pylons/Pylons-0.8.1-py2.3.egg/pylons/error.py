"""Custom error middleware subclasses, used for error theme

These error middleware sub-classes are used mainly to provide skinning
for the Paste middleware. In the future this entire module will likely
be little more than a template, as Paste will get the skinning functionality.

The only additional thing besides skinning supplied, is the Myghty traceback
information.
"""
__all__ = []

import inspect, myghty.exception, sys

from paste.evalexception.middleware import *
from paste.exceptions.formatter import *

class Supplement(errormiddleware.Supplement):
    """This is a supplement used to display standard WSGI information in
    the traceback.
    """
    def extraData(self):
        data = {}
        cgi_vars = data[('extra', 'CGI Variables')] = {}
        wsgi_vars = data[('extra', 'WSGI Variables')] = {}
        hide_vars = ['paste.config', 'wsgi.errors', 'wsgi.input',
                     'wsgi.multithread', 'wsgi.multiprocess',
                     'wsgi.run_once', 'wsgi.version',
                     'wsgi.url_scheme']
        for name, value in self.environ.items():
            if name.upper() == name:
                if value:
                    cgi_vars[name] = value
            elif name not in hide_vars:
                wsgi_vars[name] = value
        if self.environ['wsgi.version'] != (1, 0):
            wsgi_vars['wsgi.version'] = self.environ['wsgi.version']
        proc_desc = tuple([int(bool(self.environ[key]))
                           for key in ('wsgi.multiprocess',
                                       'wsgi.multithread',
                                       'wsgi.run_once')])
        wsgi_vars['wsgi process'] = self.process_combos[proc_desc]
        wsgi_vars['application'] = self.middleware.application
        if 'paste.config' in self.environ:
            data[('extra', 'Configuration')] = dict(self.environ['paste.config'])
            
        # Add any extra sections here
       
        return data

class HTMLFormatter(formatter.HTMLFormatter):
    def format_collected_data(self, exc_data):
        general_data = {}
        if self.show_extra_data:
            for name, value_list in exc_data.extra_data.items():
                if isinstance(name, tuple):
                    importance, title = name
                else:
                    importance, title = 'normal', name
                for value in value_list:
                    general_data[(importance, name)] = self.format_extra_data(
                        importance, title, value)
        lines = []
        frames = self.filter_frames(exc_data.frames)
        for frame in frames:
            sup = frame.supplement
            if sup:
                if sup.object:
                    general_data[('important', 'object')] = self.format_sup_object(
                        sup.object)
                if sup.source_url:
                    general_data[('important', 'source_url')] = self.format_sup_url(
                        sup.source_url)
                if sup.line:
                    lines.append(self.format_sup_line_pos(sup.line, sup.column))
                if sup.expression:
                    lines.append(self.format_sup_expression(sup.expression))
                if sup.warnings:
                    for warning in sup.warnings:
                        lines.append(self.format_sup_warning(warning))
                if sup.info:
                    lines.extend(self.format_sup_info(sup.info))
            if frame.supplement_exception:
                lines.append('Exception in supplement:')
                lines.append(self.quote_long(frame.supplement_exception))
            if frame.traceback_info:
                lines.append(self.format_traceback_info(frame.traceback_info))
            filename = frame.filename
            if filename and self.trim_source_paths:
                for path, repl in self.trim_source_paths:
                    if filename.startswith(path):
                        filename = repl + filename[len(path):]
                        break
            lines.append(self.format_source_line(filename or '?', frame))
            source = frame.get_source_line()
            long_source = frame.get_source_line(2)
            if source:
                lines.append(self.format_long_source(
                    source, long_source))
        exc_info = self.format_exception_info(
            exc_data.exception_type,
            exc_data.exception_value)
        data_by_importance = {'important': [], 'normal': [],
                              'supplemental': [], 'extra': []}
        for (importance, name), value in general_data.items():
            data_by_importance[importance].append(
                (name, value))
        for value in data_by_importance.values():
            value.sort()
        return self.format_combine(data_by_importance, lines, exc_info)
        
    def format_extra_data(self, importance, title, value):
        if isinstance(value, str):
            s = self.pretty_string_repr(value)
            if '\n' in s:
                return '%s:<br><pre>%s</pre>' % (title, self.quote(s))
            else:
                return '%s: <tt>%s</tt>' % (title, self.quote(s))
        elif isinstance(value, dict):
            return self.zebra_table(title, value)
        elif (isinstance(value, (list, tuple))
              and self.long_item_list(value)):
            return '%s: <tt>[<br>\n&nbsp; &nbsp; %s]</tt>' % (
                title, ',<br>&nbsp; &nbsp; '.join(map(self.quote, map(repr, value))))
        else:
            return '%s: <tt>%s</tt>' % (title, self.quote(repr(value)))
            
    def zebra_table(self, title, rows, table_class="variables"):
        if isinstance(rows, dict):
            rows = rows.items()
            rows.sort()
        table = ['<table class="%s">' % table_class,
                 '<tr class="header"><th colspan="2">%s</th></tr>'
                 % self.quote(title)]
        odd = False
        for name, value in rows:
            try:
                value = repr(value)
            except Exception, e:
                value = 'Cannot print: %s' % e
            odd = not odd
            table.append(
                '<tr class="%s"><td>%s</td>'
                % (odd and 'odd' or 'even', self.quote(name)))
            table.append(
                '<td><tt>%s</tt></td></tr>'
                % make_wrappable(self.quote(value)))
        table.append('</table>')
        return '\n'.join(table)

    def format_combine(self, data_by_importance, lines, exc_info):
        
        lines[:0] = [value for n, value in data_by_importance['important']]
        lines.append(exc_info)
        for name in 'normal', 'supplemental':
            lines.extend([value for n, value in data_by_importance[name]])
            
        extra_data = []
        if data_by_importance['extra']:
            #extra_data.append(
            #    '<script type="text/javascript">\nshow_button(\'extra_data\', \'extra data\');\n</script>\n' +
            #    '<div id="extra_data" class="hidden-data">\n')
            extra_data.extend([value for n, value in data_by_importance['extra']])
            #extra_data.append('</div>')
        extra_data_text = self.format_combine_lines(extra_data)
        text = self.format_combine_lines(lines)
        if self.include_reusable:
            return str(error_css + hide_display_js + text), extra_data
        else:
            # Usually because another error is already on this page,
            # and so the js & CSS are unneeded
            return text, extra_data
            
def format_html(exc_data, include_hidden_frames=False, **ops):
    if not include_hidden_frames:
        return HTMLFormatter(**ops).format_collected_data(exc_data)
    short_er = format_html(exc_data, show_hidden_frames=False, **ops)
    # @@: This should have a way of seeing if the previous traceback
    # was actually trimmed at all
    ops['include_reusable'] = False
    ops['show_extra_data'] = False
    long_er = format_html(exc_data, show_hidden_frames=True, **ops)
    text_er = format_text(exc_data, show_hidden_frames=True, **ops)
    return """
    %s
    <br>
    <script type="text/javascript">
    show_button('full_traceback', 'full traceback')
    </script>
    <div id="full_traceback" class="hidden-data">
    %s
    </div>
    <br>
    <script type="text/javascript">
    show_button('text_version', 'text version')
    </script>
    <div id="text_version" class="hidden-data">
    <textarea style="width: 100%%" rows=10 cols=60>%s</textarea>
    </div>
    """ % (short_er, long_er, cgi.escape(text_er)), ''

error_template = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
 <title>Server Error</title>
 %(head)s

<!-- CSS Imports -->
<link rel="stylesheet" href="%(prefix)s/error/style/orange.css" type="text/css" media="screen" />

<!-- Favorite Icons -->
<link rel="icon" href="%(prefix)s/error/img/icon-16.png" type="image/png" />

</head>

<body id="documentation" onload="switch_display('%(set_tab)s')">
<!-- We are only using a table to ensure old browsers see the message correctly -->

<noscript>
<div style="border-bottom: 1px solid #808080">
<div style="border-bottom: 1px solid #404040">
<table width="100%%" border="0" cellpadding="0" bgcolor="#FFFFE1"><tr><td valign="middle"><img src="%(prefix)s/error/img/warning.gif" alt="Warning" /></td><td>&nbsp;</td><td><span style="padding: 0px; margin: 0px; font-family: Tahoma, sans-serif; font-size: 11px">Warning, your browser does not support JavaScript so you will not be able to use the interactive debugging on this page.</span></td></tr></table>
</div>
</div>
</noscript>
    
    <!-- Top anchor -->
    <a name="top"></a>
    
    <!-- Logo -->
    <h1 id="logo"><a class="no-underline" href="http://pylons.groovie.org"><img class="no-border" src="%(prefix)s/error/img/logo.gif" alt="Pylons" title="Pylons"/></a></h1>
    <p class="invisible"><a href="#content">Skip to content</a></p>

    <!-- Main Content -->
    <div id="nav-bar">

        <!-- Section Navigation -->
        <h4 class="invisible">Section Links</h4>

            <ul id="navlist">
               <!--  %%(links)s -->
                <li id='traceback_data_tab' class="active"><a href="javascript:switch_display('traceback_data')" id='traceback_data_link' class="active"  accesskey="1">Traceback</a></li>
                <li id='extra_data_tab' class="" ><a href="javascript:switch_display('extra_data')" id='extra_data_link' accesskey="2" >Extra Data</a></li>
                <li id='myghty_data_tab'><a href="javascript:switch_display('myghty_data')" accesskey="3" id='myghty_data_link'>Myghty</a></li>
            </ul>
    </div>
    <div id="main-content">
        <div class="hr"><hr class="hr" /></div>
        <div class="content-padding">
            <div id="extra_data" class="hidden-data">
                %(extra_data)s
            </div>
            <div id="myghty_data" class="hidden-data">
                %(myghty_data)s
            </div>
            <div id="traceback_data">
                %(traceback_data)s
            </div>
        </div>
        <br class="clear" />
        <div class="hr"><hr class="clear" /></div>
        <!-- Footer -->
    </div>
    <div style=" background: #FFFF99; padding: 10px 10px 10px 6%%">
        The Pylons Team | 
        <a href="#top" accesskey="9" title="Return to the top of the navigation links">Top</a>
    </div>
</body>
</html>
'''

class InvalidTemplate(Exception):
    pass
from pylons.util import get_prefix
class PylonsEvalException(EvalException):

    def __init__(self, application, global_conf=None, xmlhttp_key=None, error_template=error_template, **errorparams):
        self.application = application
        self.error_template=error_template
        self.debug_infos = {}
        if xmlhttp_key is None:
            xmlhttp_key = global_conf.get('xmlhttp_key', '_')
        self.xmlhttp_key = xmlhttp_key
        self.errorparams = errorparams
        self.errorparams['debug_mode'] = self.errorparams['debug']
        del self.errorparams['debug']
        
        for s in ['head','traceback_data','extra_data','myghty_data']:
            if "%("+s+")s" not in self.error_template:
                raise InvalidTemplate("Could not find %s in template"%("%("+s+")s"))
        try:
            error_template%{'head': '',
                'traceback_data': '',
                'extra_data':'',
                'myghty_data':'',
                'set_tab':'',
                'prefix':''}
        except:
            raise Exception('Invalid template. Please ensure all % signs are properly quoted as %% and no extra substitution strings are present.')
            
    def eval_javascript(self, base_path, counter):
        base_path = '/_debug' # Note the difference!
        return (
            '<script type="text/javascript" src="%s/mochikit/MochiKit.js">'
            '</script>\n'
            '<script type="text/javascript" src="%s/media/debug.js">'
            '</script>\n'
            '<script type="text/javascript">\n'
            'debug_base = %r;\n'
            'debug_count = %r;\n'
            '</script>\n'
            % (base_path, base_path, base_path, counter))
            
    #~ def pylons(self, environ, start_response):
        #~ app = urlparser.StaticURLParser(
            #~ os.path.join(os.path.dirname(__file__), 'media'))
        #~ return app(environ, start_response)
    #~ pylons.exposed = True
    
    def respond(self, environ, start_response):
        base_path = request.construct_url(environ, with_path_info=False,
                                          with_query_string=False)
        environ['paste.throw_errors'] = True
        started = []
        def detect_start_response(status, headers, exc_info=None):
            try:
                return start_response(status, headers, exc_info)
            except:
                raise
            else:
                started.append(True)
        try:
            __traceback_supplement__ = Supplement, self, environ
            app_iter = self.application(environ, detect_start_response)
            return self.catching_iter(app_iter, environ)
        except:
            exc_info = sys.exc_info()
            if inspect.isclass(exc_info[0]):
                for expected in environ.get('paste.expected_exceptions', []):
                    if issubclass(exc_info[0], expected):
                        raise
                    
            import paste.exceptions.errormiddleware
            paste.exceptions.errormiddleware.handle_exception(
                exc_info,
                environ['wsgi.errors'],
                **self.errorparams
            )

            if not started:
                start_response('500 Internal Server Error',
                               [('content-type', 'text/html')],
                               exc_info)
            if self.xmlhttp_key:
                get_vars = wsgilib.parse_querystring(environ)
                if dict(get_vars).get(self.xmlhttp_key):
                    exc_data = collector.collect_exception(*exc_info)
                    html = formatter.format_html(
                        exc_data, include_hidden_frames=False,
                        include_reusable=False, show_extra_data=False)
                    return [html]
            count = debug_counter.next()
            exc_data = collector.collect_exception(*exc_info)
            debug_info = DebugInfo(count, exc_info, exc_data, base_path,
                                   environ)
            assert count not in self.debug_infos
            self.debug_infos[count] = debug_info
            
            
            
            base_path = get_prefix(environ)
            #base_path = environ['SCRIPT_NAME']
            
            
            # @@: it would be nice to deal with bad content types here
            exc_data = collector.collect_exception(*exc_info)
            html, extra_data = format_eval_html(exc_data, base_path, count)
            #raise Exception(extra_data)
            head_html = (formatter.error_css + formatter.hide_display_js)
            head_html += self.eval_javascript(base_path, count)
            repost_button = make_repost_button(environ)
            myghty_data = '<p>No Myghty information available.</p>'
            tab = 'traceback_data'
            if hasattr(exc_info[1], 'htmlformat'):
                myghty_data = exc_info[1].htmlformat()[333:-14]
                tab = 'myghty_data'
            if hasattr(exc_info[1], 'mtrace'):
                myghty_data = exc_info[1].mtrace.htmlformat()[333:-14]
                tab = 'myghty_data'
            head_html = ("""
<!-- 
    This is the Pylons error handler.

    Adapted for inclusion in Pylons by James Gardner. 
    Uses code from Ian Bicking, Mike Bayer and others.
-->

<style type="text/css">
        .red {
            color:#FF0000;
        }
        .bold {
            font-weight: bold;
        }
</style>
<script type="text/javascript">

if (document.images)
{
  pic1= new Image(100,25); 
  pic1.src="%(prefix)s/error/img/tab-yellow.png"; 
}

function switch_display(id) {
    ids = ['extra_data', 'myghty_data', 'traceback_data']
    for (i in ids){
        part = ids[i] 
        var el = document.getElementById(part);
        el.className = "hidden-data";
        var el = document.getElementById(part+'_tab');
        el.className = "not-active";
        var el = document.getElementById(part+'_link');
        el.className = "not-active";
    }
    var el = document.getElementById(id);
    el.className = "active";
    var el = document.getElementById(id+'_link');
    el.className = "active";
    var el = document.getElementById(id+'_tab');
    el.className = "active";
}   
</script>
            """%{'prefix':base_path})+head_html

            traceback_data = """
            <div style="float: left; width: 100%%; padding-bottom: 20px;">
            <h1 class="first"><a name="content"></a>Error Traceback</h1>
            <div id="error-area" style="display: none; background-color: #600; color: #fff; border: 2px solid black">
            <button onclick="return clearError()">clear this</button>
            <div id="error-container"></div>
            <button onclick="return clearError()">clear this</button>
            </div>
            %(body)s
            <br />
            <div class="highlight" style="padding: 20px;">
            <b>Extra Features</b>
            <table border="0">
            <tr><td>&gt;&gt;</td><td>Display the lines of code near each part of the traceback</td></tr>
            <tr><td><img src="%(prefix)s/error/img/plus.jpg" /></td><td>Show a debug prompt to allow you to directly debug the code at the traceback</td></tr>
            </table>
            </div>%(repost_button)s"""%{
                'prefix':base_path,
                'body':html,
                'repost_button': repost_button or '',
            }
        
            page = self.error_template % {
                'head': head_html,
                'traceback_data': traceback_data,
                'extra_data':"""<h1 class="first"><a name="content"></a>Extra Data</h1>"""+'\n'.join(extra_data),
                'myghty_data':myghty_data.replace('<h2>','<h1 class="first">').replace('</h2>','</h1>'),
                'set_tab':tab,
                'prefix':base_path,
                }
            return [page]

class EvalHTMLFormatter(HTMLFormatter):

    def __init__(self, base_path, counter, **kw):
        super(EvalHTMLFormatter, self).__init__(**kw)
        self.base_path = base_path
        self.counter = counter
    
    def format_source_line(self, filename, frame):
        line = formatter.HTMLFormatter.format_source_line(
            self, filename, frame)
        return (line +
                '  <a href="#" class="switch_source" '
                'tbid="%s" onClick="return showFrame(this)">&nbsp; &nbsp; '
                '<img src="%s/error/img/plus.jpg" border=0 width=9 '
                'height=9> &nbsp; &nbsp;</a>'
                % (frame.tbid, self.base_path))

def format_eval_html(exc_data, base_path, counter):
    short_er, extra_data = EvalHTMLFormatter(
        base_path=base_path,
        counter=counter,
        include_reusable=False).format_collected_data(exc_data)
    #raise Exception(extra_data)
    long_er, extra_data_none = EvalHTMLFormatter(
        base_path=base_path,
        counter=counter,
        show_hidden_frames=True,
        show_extra_data=False,
        include_reusable=False).format_collected_data(exc_data)
    return """
    %s
    <br />
    <br />
    <script type="text/javascript">
    show_button('full_traceback', 'full traceback')
    </script>
    <div id="full_traceback" class="hidden-data">
    %s
    </div>
    """ % (short_er, long_er), extra_data
    
