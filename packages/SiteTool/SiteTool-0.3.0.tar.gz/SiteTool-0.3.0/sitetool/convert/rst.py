"""A simple reStructuredText convert plugin"""

import logging
import re
import os
import sys
import StringIO

from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator
from sitetool.template.dreamweaver import DreamweaverTemplateInstance

from sitetool.exception import PluginError
from sitetool.convert.plugin import Plugin

log = logging.getLogger(__name__)

class CustomHTMLTranslator(HTMLTranslator):
    def __init__(self, *k, **p):
        HTMLTranslator.__init__(self, *k, **p)
        # Allow long field names more than 14 characters in reStructuredText
        # field lists
        self.settings.field_name_limit = 0
        self.initial_header_level = 2

def rstify(string, path='no path'):
    """
    Turn a reSturcturedText string into HTML, capturing any errors or warnings
    and re-emitting them with this programs logging system.
    """
    
    # Temporarily capture stderr and stdout
    err = sys.stderr
    out = sys.stdout
    error = '' 
    out_msg = ''
    try:
        sys.stderr = StringIO.StringIO() 
        sys.stdout = StringIO.StringIO() 
        w = Writer()
        w.translator_class = CustomHTMLTranslator
        result = core.publish_parts(string, writer=w)['html_body']
        # Strip the first and last lines
        result = '\n'.join(result.split('\n')[1:-2])
        error = sys.stderr.getvalue()
        out_msg = sys.stdout.getvalue()
    finally:
        sys.stderr = err
        sys.stdout = out
    if error:
        log.warning('%s - %s', path, error.replace('\n', ' '))
    if out_msg:
        log.warning('%s - %s', path, out_msg.replace('\n', ' '))
    return result                      




def save(path, data):
    fp = open(path, 'w')
    fp.write(data)
    fp.close()

class PlainRstPlugin(Plugin):

    def parse_config(self, config):
        if not config:
            return None
        result = {}
        
        if config.has_key('DEFAULT_TEMPLATE'):
            template = config['DEFAULT_TEMPLATE'].strip()
            if template.startswith(self.site_root):
                result['template'] = template
            else:
                if '..' in template:
                    raise PluginError('Template paths cannot contain .. characters')
                if template.startswith('/'):
                    raise PluginError('Template paths cannot start with /')
                result['template'] = os.path.join(self.site_root, template)
        else:
            raise PluginError('No default template could be parsed from the config file')
        return result

    def on_file(self, path):
        if not self.user_files:
            log.debug('DefaultPlugin: Skipping %r, --ignore-user-files set', path)
            return False
        filename = path
        if not filename.endswith('.rst'):
            log.debug("Don't know how to convert %r files"%(filename.split('.')[-1]))
            return False
        html_version = filename[:-4]+'.html'
        if os.path.exists(html_version):
            if (not os.stat(filename).st_mtime > os.stat(html_version).st_mtime) and not self.force:
                log.debug('Skipping %s since an HTML file of the same name already exists', filename)
                # In this case we have handled the file by doing nothing to it.
                return True
        # It needs converting:
        log.info("DefaultPlugin: Converting %r", path)
        fp = open(filename, 'r')
        rst = fp.read().decode('utf-8')
        fp.close()
        parts = rstify(rst).split('\n')
        title = parts[0][18:-5]
        content = '\n'.join(parts[1:])
        page = DreamweaverTemplateInstance(self.config['template'])
        page['doctitle'] = '<title>'+title+'</title>'
        # Leave section navigation as the default
        page['heading'] = title
        page['content'] = content + '<p class="text-right">(<a href="%s">view source</a>)</p>'%os.path.split(path)[1]
        page.save_as_page(filename[:-4]+'.html')
        return True

