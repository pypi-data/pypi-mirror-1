"""
Shows any variables that were put in
``environ['paste.testing_variables']`` at the bottom of each page.
"""

from wsgifilter import Filter
from webhelpers.util import html_escape
import re
import pprint

def smart_quote(s):
    s = html_escape(s)
    def space_repl(match):
        return match.group(0).replace('  ', ' &nbsp;')
    s = s.replace('\t', '    ')
    s = re.sub(r' +', space_repl, s)
    s = s.replace('\n', '<br>\n')
    return s

def safe_repr(value):
    try:
        return pprint.pformat(value)
    except Exception, e:
        return 'Error in pprint: %s' % e

class TestingVars(Filter):

    standard_css = '''
    <style type="text/css">
    table.testing-vars-table {
      width: 100%;
      color: #000;
      background-color: #ff9;
      border: 2px solid #000;
    }
    table.testing-vars-table th {
      background-color: #9dd;
    }
    table.testing-vars-table td {
      border-top: 1px solid #dd8;
    }
    td.testing-vars-label {
      padding-right: 1em;
    }
    </style>
    '''

    def __call__(self, environ, start_response):
        environ.setdefault('paste.testing_variables', {})
        return super(TestingVars, self).__call__(environ, start_response)

    def filter(self, environ, headers, data):
        testing_vars = environ.get('paste.testing_variables')
        if not testing_vars:
            return data
        var_block = self.format_vars(testing_vars)
        new_body = self.add_to_end_of_body(data, var_block)
        return new_body

    def format_vars(self, vars):
        vars = vars.items()
        vars.sort()
        rows = []
        for name, value in vars:
            name = smart_quote(name)
            value = smart_quote(safe_repr(value))
            rows.append('''
            <tr>
              <td class="testing-vars-label"><code>%s</code></td>
              <td class="testing-vars-value"><code>%s</code></td>
            </tr>
            ''' % (name, value))
        table = '''
        <table class="testing-vars-table">
          <tr class="testing-vars-header">
            <th colspan="2">Testing Variables</th>
          </tr>
        %s
        </table>
        ''' % (''.join(rows))
        return self.standard_css + table

    end_body_re = re.compile(r'</body\s*>', re.I)
            
    def add_to_end_of_body(self, html, block):
        match = self.end_body_re.search(html)
        if match:
            return html[:match.start()] + block + html[match.end():]
        else:
            return html + block
