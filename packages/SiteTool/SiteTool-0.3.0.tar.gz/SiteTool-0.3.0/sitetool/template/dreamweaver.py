"""\
Module desinged to provide an easy interface to allow python programs to output
HTML pages based on Dreamweaver MX Templates *.dwt files.

:author: James Gardner <james@pythonweb.org>
:date: 2009-04-13 (updated 2005-02-11, 2003-02-02)
:version: 0.3

This module provides support for Dreamweaver-style templates. In addition there
are a number of extra features including:

* Dynamic library items
* Context library items
* Auto regions
* Layout regions

Compound Library Items
======================

Compound library items with associated CSS, JS, head, body top and body bottom
parts. They can be used in combination with other compound regions, for example
to specify the top and bottom of a box. Any context or library region can be
used as a component library item if components are present.

Auto Library Items
==================

The HTML component of component library items is always included in the file
where it is embedded but to embed the other parts you either have to add them
as library items individually or use an auto library. 

There are 5 auto libraries, one for each of the types of component librries
(apart from HTML which is already embedded). An auto library is just an empty
library item which automatically gets updated with all the component library
items of each type for the HTML components in its page.

For example the ``auto_css.lbi`` will contain the CSS for any component library
items in the page.

Using Compound and Auto Libraries for Layout
============================================

Compound and auto libraries are handy for layouts. 

"""

import os.path 
import logging
import os
import re
import shutil
import posixpath

from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator

log = logging.getLogger('due')

from sitetool.exception import TemplateError, PluginError

# Tidy import 

try:
    import tidy as tidylib
except ImportError:
    tidy_available = False
else:
    tidy_available = True

# relpath import (available in Python 2.6 and above)

try:
    relpath = posixpath.relpath
except AttributeError:

    from posixpath import curdir, sep, pardir, join

    def relpath(path, start=curdir):
        """Return a relative version of a path"""
    
        if not path:
            raise ValueError("no path specified")
    
        start_list = posixpath.abspath(start).split(sep)
        path_list = posixpath.abspath(path).split(sep)
    
        # Work out how much of the filepath is shared by start and path.
        i = len(posixpath.commonprefix([start_list, path_list]))
    
        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)

class DreamweaverTemplateInstance(object):
    """\
    Class to parse Macromedia Dreamweaver MX Template files and handle 
    the assignment of content to regions
    """

    def __init__(self, filename=None, template=None, version=4):
        """\
        Parse the Template and place the content of the editable regions of
        the template in a dictionary with the namesof the ediatable regions
        as the keys.
        """
        if filename and template:
            raise TemplateError(
                'You cannot specify both a file and template text to be used.'
            )
        self.page_regions = {}
        self.template_regions = []
        self.template = ''
        self.filename = filename
        self.updated_regions = []
        self.version = version
        if filename:
            fp=open(filename, "r")
            self.template = fp.read().decode('utf-8')
            fp.close()
        else:
            self.template = template
        # Check the template has <html> and </html> tags so that if it is
        # saved as a page, the BeginInstance comment can be added
        end_of_start_html_tag(self.template)
        start_of_end_html_tag(self.template)
        self.instance_type, template_path = determine_instance_type(
            self.template,
            self.version
        )
        if template_path is not None:
            self.template_path = os.path.abspath(
                os.path.join(os.path.dirname(filename), template_path)
            )
        else:
            if self.filename:
                self.template_path = os.path.abspath(self.filename)
            else:
                self.template_path = None
        # Now extract the regions
        if self.version == 4:
            name_regex=re.compile(
                r"<!--\s*?" + \
                self.instance_type.capitalize() + \
                r"BeginEditable\s*?name=\"(\W*\s*.*\w*)?\"\s*?-->"
            )
            content_regex=re.compile(
                r"<!--\s*?" + \
                self.instance_type.capitalize() + \
                r"EndEditable\s*?-->"
            )
        else:
            name_regex = re.compile(r"""<!--(\s*?)#BeginEditable(\s*?)"(\W*\s*.*\w*)?\"(\s*?)-->""")
            content_regex=re.compile(
                r"<!--\s*?" + \
                #self.instance_type.capitalize() + \
                r"#EndEditable\s*?-->"
            )
        pos = 0
        prev_match = ''
        while 1:
            name_match = name_regex.search(self.template, pos)
            if not name_match:
                break
            begin = name_match.end(0)
            if version == 4:
                region_name = name_match.group(1)
            else:
                region_name = name_match.group(3)
            content_match = content_regex.search(
                self.template,
                begin
            )
            end = content_match.start(0)
            next_start = content_match.end(0)
            if self.page_regions.has_key(region_name):
                raise TemplateError('Bad template: Duplicate regions named %r found.'%(region_name))
            self.template_regions.append(
                [
                    region_name,
                    prev_match,
                    self.template[pos:name_match.start(0)],
                    self.template[name_match.start(0):begin],
                ]
            )
            self.page_regions[region_name] = self.template[begin:end]
            # start next search where this one ended
            pos = next_start
            prev_match = content_match.group(0)
        self.template_regions.append(
            [
                None, 
                prev_match, 
                self.template[pos:],
                '',
            ]
        )

    def get(self, key):
        """\
        Return the current value of the editable region ``key``.
        """
        # Should this return a copy?
        if self.page_regions.has_key(key):
            return self.page_regions[key]
        else:
            raise TemplateError(
                "Error, %r is not an editable region the template." % key
            )
    
    def set(self, key, value):
        """\
        Set the editable region specified by ``key`` to ``value``.
        """
        if not isinstance(value, unicode):
            value = value.decode('utf=8')
        if not isinstance(key, unicode):
            key = key.decode('utf-8')
        if self.page_regions.has_key(key):
            self.page_regions[key] = value
            if key not in self.updated_regions:
                self.updated_regions.append(key)
        else:
            raise TemplateError(
                "Error, '%s' is not an editable region of the template." % key
            )
        
    def append(self, key, value):
        """\
        Append ``value`` to the end of the editable region specified by 
        ``key``.
        """
        value = unicode(value)
        key = unicode(key)
        self.set(key, self.get(key)+value)
        
    def save_as_page(
        self, 
        filename=None, 
        template_path=None, 
        old_path=None, 
        new_path=None, 
        tidy=False
    ):
        """\
        Merge the Editable Regions with the information in the Template to 
        create the HTML page to be output. Returns the HTML.

        Each of the regions use InstanceBegin instead of TemplateBegin and 
        the whole document is wrapped in an 
        ``<!-- InstanceBegin template="..." -->`` comment

        Regions which have changed do not have there links updated as it is
        assumed you have updated them with the correct links already.
        """
        if self.instance_type == 'instance':
            if not old_path:
                # If it was loaded from a file, use that filename
                old_path = self.filename
                if not old_path:
                    raise TemplateError(
                        "Please specify 'old_path', the full path and "
                        "filename the page was loaded from."
                    )
            if not new_path:
                # Assume we want to save it to the filename specified or back
                # to where it came from as a last resort
                new_path = filename or self.filename
                if not new_path:
                    raise TemplateError(
                        "Please specify 'new_path', the full path and "
                        "filename the page should be saved to."
                    )
            if not template_path:
                # Assume the template path hasn't changed
                template_path = self.template_path
                if not template_path:
                    raise TemplateError(
                        "Please specify 'template_path', the full path and "
                        "filename of the template the page uses."
                    )
        else:
            # Assume it is a template being saved as a page for the first time
            if old_path:
                raise TemplateError( 
                    "You shouldn't specify 'old_path' when the template "
                    "instance was derived from a template because the "
                    "'template_path' is used instead"
                )
            if not template_path:
                template_path = self.template_path
                if not template_path:
                    raise TemplateError(
                        "Please specify 'template_path', the full path and "
                        "filename of the original template"
                    )
            old_path = template_path
            if not new_path:
                new_path = filename
                if not filename:
                    raise TemplateError(
                        "Please specify 'new_path', the full path and "
                        "filename of the new page to be created"
                    )
        output = []
        first = True
        site_root = os.path.sep.join(
            os.path.split(
                os.path.dirname(template_path)
            )[:-1]
        )
        for k, end, template_region, start in self.template_regions:
            template_region = update_links(
                site_root = site_root,
                old_path = old_path,
                new_path = new_path,
                content = template_region,
            )
            if self.instance_type == 'template':
                if first:
                    first = False
                    # Need to add the comment specifying the template the page 
                    # is using
                    pos = end_of_start_html_tag(template_region)
                    rel = relpath(
                        self.template_path, 
                        posixpath.dirname(new_path)
                    )
                    template_region = '%s%s%s' % (
                        template_region[:pos],
                        '<!-- InstanceBegin template="' + rel +\
                           '" codeOutsideHTMLIsLocked="false" -->',
                        template_region[pos:],
                    )
                    output.append(template_region)
                    output.append(
                        start.replace(
                            'TemplateBeginEditable',
                            'InstanceBeginEditable'
                        )
                    )
                    if k in self.updated_regions:
                        output.append(self.page_regions[k])
                    else:
                        output.append(
                            update_links(
                                site_root = site_root,
                                old_path = old_path,
                                new_path = new_path,
                                content = self.page_regions[k],
                            )
                        )
                elif k is not None:
                    # middle part
                    output.append(
                        end.replace(
                            'TemplateEndEditable', 
                            'InstanceEndEditable'
                        )
                    )
                    output.append(template_region)
                    output.append( 
                        start.replace(
                            'TemplateBeginEditable', 
                            'InstanceBeginEditable'
                        )
                    )
                    if k in self.updated_regions:
                        output.append(self.page_regions[k])
                    else:
                        output.append(
                            update_links(
                                site_root = site_root,
                                old_path = old_path,
                                new_path = new_path,
                                content = self.page_regions[k],
                            )
                        )
                else:
                    # The last part
                    pos = start_of_end_html_tag(template_region)
                    template_region = '%s%s%s' % (
                        template_region[:pos],
                        '<!-- InstanceEnd -->',
                        template_region[pos:],
                    )
                    output.append(
                        end.replace(
                            'TemplateEndEditable', 
                            'InstanceEndEditable'
                        )
                    )
                    output.append(template_region)
            else:
                # Its a page region, not a template region
                page_region = template_region
                if first:
                    first = False
                    # Need to update the comment specifying the template the page 
                    # is using
                    pos = end_of_start_html_tag(page_region)
                    end_pos = page_region[pos:].find('-->')+pos+3
                    if not end_pos:
                        raise TemplateError('Could not find the end of the BeginInstance comment specifying the template location')
                    rel = relpath(
                        self.template_path, 
                        posixpath.dirname(new_path)
                    )
                    page_region = '%s%s%s' % (
                        page_region[:pos],
                        '<!-- InstanceBegin template="' + rel +\
                           '" codeOutsideHTMLIsLocked="false" -->',
                        page_region[end_pos:],
                    )
                    output.append(page_region)
                    output.append(start)
                    if k in self.updated_regions:
                        output.append(self.page_regions[k])
                    else:
                        output.append(
                            update_links(
                                site_root = site_root,
                                old_path = old_path,
                                new_path = new_path,
                                content = self.page_regions[k],
                            )
                        )
                elif k is not None:
                    # middle part
                    output.append(end)
                    output.append(page_region)
                    output.append(start)
                    if k in self.updated_regions:
                        output.append(self.page_regions[k])
                    else:
                        output.append(
                            update_links(
                                site_root = site_root,
                                old_path = old_path,
                                new_path = new_path,
                                content = self.page_regions[k],
                            )
                        )
                else:
                    # The last part
                    pos = start_of_end_html_tag(page_region)
                    output.append(end)
                    output.append(page_region)
        output = ''.join(output)
        if tidy:
            output = tidy_output(output)
        if filename is not None:
            f=open(filename, 'w')
            f.write(output.encode('utf-8'))
            f.close()
        else:
            return output
    
    def save_as_template(self, filename=None, tidy=False):
        """\
        Merge the Editable Regions with the information in the Template to 
        create the HTML page to be output. Returns the HTML.
        """
        if self.instance_type == 'page':
            raise NotImplementedError('Not implemented yet')
        output = []
        for k, end, template_region, start in self.template_regions:
            output.append(end)
            output.append(template_region)
            output.append(start)
            if k is not None:
                output.append(self.page_regions[k])
        output = ''.join(output)
        if tidy:
            output = tidy_output(output)
        if filename is not None:
            f=open(filename, 'w')
            f.write(output.encode('utf-8'))
            f.close()
        else:
            return output
    
    def __repr__(self):
        return '<%s (%s), %s>' % (
            self.__class__.__name__, 
            self.instance_type,
            self.filename,
        )

    __str__ = __repr__
    
    def __getitem__(self, key):
        """\
        Simulate mapping-style access.
        """
        return self.get(key)
    
    def __setitem__(self, key, value):
        """\
        Simulate mapping-style access.
        """
        self.set(key, value)
    
    # Simulated methods
    
    def keys(self):
        "Simulate mapping's methods"
        return self.page_regions.keys()
    
    def has_key(self, key):
        "Simulate mapping's methods"
        return key in self.page_regions.keys()
    
    def items(self):
        "Simulate mapping's methods"
        return self.page_regions.items()
    
    # Conversion Methods
    
    def to_dict(self):
        """\
        Return a dictionary containing a copy of the text in editable regions 
        of the page as it stands with the names of theeditable regions as the 
        keys.
        """
        return self.page_regions.copy()
DWT = DreamweaverTemplateInstance

# Helpers

def determine_instance_type(template, version):
    """\
    Check for the presence of an ``InstanceBegin`` comment with a 
    ``template`` attribute and if it exists, assume the instance is a
    page, otherwise assume it is a template.
    """
    if version == 4:
        regex=re.compile(
            r'''<!--\s*?InstanceBegin\s*?template\s*?=\s*?("|')'''
            r'''(.*?)("|').*?-->'''
        )
    else:
        regex=re.compile(
            r'''<!--\s*?#BeginTemplate\s*?("|')'''
            r'''(.*?)("|').*?-->'''
        )
    match = regex.search(template)
    if not match:
        return 'template', None
    else:
        return 'instance', match.group(2)

def end_of_start_html_tag(template):
    # We need to use [^<]*? to match any character except <
    start_html_regex=re.compile(
        r"<\s*?html [^<]*?>",
        re.IGNORECASE,
    )
    start_html_match = start_html_regex.search(
        template, 
    )
    if not start_html_match:
        raise TemplateError(
            'No <html> tag could be found in the template.'
        )
    return start_html_match.end(0)

def start_of_end_html_tag(template):
    end_html_regex=re.compile(
        r"</\s*?html\s*?>",
        re.IGNORECASE,
    )
    end_html_match = end_html_regex.search(
        template, 
    )
    if not end_html_match:
        raise TemplateError(
            'No </html> tag could be found in the template.'
        )
    return end_html_match.start(0)
 
def tidy_output(output):
    if not tidy_available:
        raise TemplateError(
            "The 'tidy' module from uTidyLib is not available"
        )
    options = dict(
        output_xhtml=1, 
        add_xml_decl=1, 
        indent=1, 
        tidy_mark=0,
        wrap=78,
    )
    output = tidylib.parseString(output.encode('utf-8'), **options)
    return output

# Link functions

href_and_src_pattern = r'''<([^>]*?)(href|src)(\s*?)=(\s*?)("|')(.*?)("|')(\s*?.*?)>'''
def update_links(site_root, old_path, new_path, content):
    site_root = posixpath.abspath(site_root)
    old_path = posixpath.abspath(old_path)
    new_path = posixpath.abspath(new_path)
    # First check old_path and new_path are under site root
    if not old_path.startswith(site_root):
        raise TemplateError(
            "The old_path (%r) is not under site_root (%r)."%(
                old_path, 
                site_root,
            )
        )
    elif not new_path.startswith(site_root):
        raise TemplateError(
            "The new_path (%r) is not under site_root (%r)."%(
                new_path, 
                site_root,
            )
        )

    def get_new_link(old_path, old_link, new_path):
        # Calculate the absolute path of each link from the link and the
        # old_path
        link_path = posixpath.abspath(
            posixpath.join(posixpath.dirname(old_path), old_link)
        )
        # Calculate the new relative path from the new_path to the absolute 
        # path of the link
        new_link = relpath(link_path, posixpath.dirname(new_path))
        # If the link is a directory ensure there is a trailing slash
        if (old_link == '.' or old_link.endswith('/')) and \
           not new_link.endswith('/'):
            new_link += '/'
        return new_link

    # Handle src and html tags first
    def href_and_src_replace(match):
        found = match.group(0)
        old_link = match.group(6)
        if old_link.startswith('/') or old_link.startswith('http://') or old_link.startswith('https://'):
            return found
        new_link = get_new_link(old_path, old_link, new_path)
        # Keep the old HTML spacing
        result = '<%s%s%s=%s%s%s%s%s>'%(
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
            match.group(5),
            new_link,
            match.group(7),
            match.group(8),
            #match.group(9),
        )
        return result
    content, replaced_links = re.subn(
        href_and_src_pattern, 
        href_and_src_replace, 
        content
    )

    # Now handle library item paths
    library_item_pattern = r"""<!--(\s*?)#Begin(ContextItem|LibraryItem|DynamicItem)(\s*?)"(\W*\s*.*\w*)?\"(\s*?)-->"""
    def library_item_replace(match):
        found = match.group(0)
        old_link = match.group(4)
        new_link = get_new_link(old_path, old_link, new_path)
        # Keep the old HTML spacing
        result = '<!--%s#Begin%s%s"%s"%s-->'%(
            match.group(1),
            match.group(2),
            match.group(3),
            new_link,
            match.group(5),
        )
        return result
    content, replaced_links = re.subn(
        library_item_pattern, 
        library_item_replace,
        content
    )
    return content

def reapply_template_to_pages(template_path, pages, delete_missing_sections=[]):
    if not isinstance(pages, (list, tuple)):
        pages = pages
    for page_filename in pages:
        log.debug("Applying template %r to page %r", template_path, page_filename)
        template = DreamweaverTemplateInstance(filename=template_path)
        page = DreamweaverTemplateInstance(filename=page_filename)
        # Check we've got the right template
        if not page.template_path == template.template_path:
            raise TemplateError( 
                'The page %r uses the template %r not %r'%(
                    page_filename,
                    page.template_path,
                    template.template_path
                )
            )
        # Apply the page regions to the template
        for k, v in page.items():
            if template.has_key(k):
                template[k] = v
            elif k in delete_missing_sections:
                # Log, but continue, the section will be removed
                log.warning('Deleting section %r from page, not in template', k)
            else:
                raise TemplateError('Could not reapply template, the section %r does not exist'%k)
        template.save_as_page(filename=page_filename, new_path=page_filename)

def update_library_item_links_for_path(
    library_item_filename, 
    destination_filename,
):
  
    fp = open(library_item_filename, 'r')
    content = fp.read().decode('utf-8')
    fp.close()
    site_root = os.path.abspath(os.path.split(os.path.split(library_item_filename)[0])[0])
    old_path = os.path.abspath(library_item_filename)
    new_path = os.path.abspath(destination_filename)
    result = update_links(
        site_root = site_root,
        old_path = old_path,
        new_path = new_path,
        content = content
    )
    return result

def extract_title(filename, full=False):
    fp = open(filename, 'r')
    data = fp.read().decode('utf-8')
    fp.close()
    section_property_regex=re.compile(
        r"""<!--\s*?InstanceBeginEditable\s*?name="section_property"\s*?--><!--\s*?(.*?)\s*?--><!--\s*?InstanceEndEditable\s*?-->"""
    )
    section_property_match = section_property_regex.search(data)
    if section_property_match:
        title = section_property_match.group(1)
    else:
        title_regex=re.compile(
            r"<\s*?title\s*?>(.*?)</\s*?title\s*?>"
        )
        title_match = title_regex.search(data)
        if not title_match:
            # Just use the filename instead
            title = '.'.join(
                filename.split(os.sep)[-1].split('.')[:-1]
            ).replace('-', ' ').capitalize()
        else:
            title = title_match.group(1)
    if full is False and len(title) > 40:
        short_title = ''
        parts = title.split(' ')
        counter = 0
        while(len(short_title+parts[counter])<35):
            short_title += parts[counter]+' '
            counter += 1
        if not short_title:
            short_title = title[:35]+' '
        title = short_title[:-1]+'...'
    return title

def update_context_item_links_for_path(
    context_item_filename, 
    destination_filename,
    site_root=None,
):
    dir = os.path.dirname(destination_filename)
    if not os.path.exists(context_item_filename):
        raise TemplateError('No such context item %r, path: %s'%(context_item_filename, destination_filename))
    type = os.path.split(context_item_filename)[-1]
    if type == 'section_navigation.cti':
        to_parse = []
        if not dir:
            dir = '.'
        files = os.listdir(dir)
        for file_ in files:
            if file_.endswith('.html'):
                to_parse.append(file_)
            elif os.path.isdir(os.path.join(dir, file_)):# and file_ not in ['Templates', 'Context', 'Dynamic', 'Library']:
                # Ignore directories without an index.html file
                if os.path.exists(os.path.join(dir, file_, 'index.html')):
                    to_parse.append(os.path.join(file_, 'index.html'))
        if not to_parse:
            return ''
        else:
            links = []
            for file_ in to_parse:
                links.append(
                    [
                        file_, 
                        extract_title(os.path.join(dir, file_))
                    ]
                )
            output = []
            for file_, title in links:
                output.append('\n<a href="'+file_+'">'+title+'</a> ')
                #output.append(file_.split(os.sep)[-1])
            return ''.join(output)+'\n'
    elif type == 'breadcrumbs.cti':
        if site_root is None:
            site_root = os.path.split(os.path.split(context_item_filename)[0])[0]
            log.warning('No SITE_ROOT specified so inferring it from the location of the context item to be %r', site_root)
        # Assume the file has an index page
        site_index = os.path.join(
            site_root, 
            'index.html',
        )
        if os.path.abspath(site_index) == os.path.abspath(destination_filename):
            return ''
        breadcrumbs = []
        if not (destination_filename == 'index.html' or destination_filename.endswith(os.sep+'index.html')):
            breadcrumbs.append(
                [
                    '.',
                    extract_title(destination_filename),
                ]
            )
        depth = 0
        paths = []
        base = ''
        parts = dir[len(site_root):].split(os.sep)
        for part in parts:
            if part:
                paths.append(os.path.join(base, part, 'index.html'))
                base = os.path.join(base, part)
        paths.reverse()
        for filename in paths:
            path = os.path.join(site_root, filename)
            if os.path.abspath(path) == os.path.abspath(site_index):
                break
            if not os.path.exists(path):
                log.warning("No index.html exists at %s", path)
                breadcrumbs.append(
                    [
                        None,
                        '..'
                    ]
                )
            else:
                breadcrumbs.append(
                    [
                        '../'*depth + 'index.html',
                        extract_title(path),
                    ]
                )
            depth += 1
        breadcrumbs.reverse()
        output = ['\n'] 
        counter = 0
        for link, title in breadcrumbs:
            counter += 1
            if counter == len(breadcrumbs):
                output.append(title)
            elif link:
                output.append('<a href="')
                output.append(link)
                output.append('">')
                output.append(title)
                output.append('</a> &gt;\n')
            else:
                output.append(title)
                output.append(' &gt;\n')
        output.append('\n')
        return ''.join(output)
    else:
        raise TemplateError('Unrecognised Context Item type %r'%type)

#def reapply_library_item(filename, old_filename=None):
#    print "DEPRECATED--reapply_library_item()------------------"
#    return reapply_library_items_to_page(filename, None, True, True, True)

def reapply_library_items_to_page(
    page,
    site_root = None,
    update_context_items=False, 
    update_dynamic_items=False, 
    update_static_items=False, 
):
    """\
    Takes a file (template or page) and updates the library items
    it contains.

    By default, none of the types of library items are updated. You must
    therefore specify at least one of ``update_context_items``,
    ``update_dynamic_items`` or ``update_static_items`` before this function 
    will perform any action.

    ``filename``
        The full, absolute, normalised path to the page to update
 
    ``update_context_items``
        Update any context library items the page contains

    ``update_dynamic_items``
        Update any dynamic library items the page contains
     
    ``update_static_items`` 
        Update any static library items the page contains
    """
    library_types = []
    if update_context_items:
        library_types.append('ContextItem')
    if update_dynamic_items:
        library_types.append('DynamicItem')
    if update_static_items:
        library_types.append('LibraryItem')
    if not library_types:
        raise TemplateError(
            'You have not chosen which types of library item in %r to '
            'update' % page
        )
    regex_string = '|'.join(library_types)
    
    filename = page
    fp = open(filename, 'r')
    data = fp.read()
    fp.close()
    try:
        data = data.decode('utf-8')
    except UnicodeDecodeError, e:
        log.warning('%s in %r. Continuing without UTF-8' , e, filename)
    output = []
    updated_library_items = {}
    start_regex=re.compile(
        r"""<!--\s*?#Begin(%s)\s*?"(\W*\s*.*\w*)?\"\s*?-->"""%regex_string
    )
    end_regex=re.compile(
        r"<!--\s*?#End(%s)\s*?-->"%regex_string
    )
    pos = 0
    while 1:
        start_match = start_regex.search(data, pos)
        if not start_match:
            # No more items
            break
        library_item_type = start_match.group(1)
        start_of_start = start_match.end(0)
        end_of_start = start_match.end(0)
        path = start_match.group(2)
        end_match = end_regex.search(
            data,
            end_of_start,
        )
        start_of_end = end_match.start(0)
        end_of_end = end_match.end(0)
        # Output all the information up to here
        output.append(data[pos:start_of_start])
        if not updated_library_items.has_key(path):
            # If we haven't seen this item before in this template, calculate and cache it
            realpath = os.path.normpath(
                os.path.join(
                    os.path.dirname(filename),
                    path,
                )
            )
            if library_item_type in ['DynamicItem', 'LibraryItem']:
                updated_library_items[path] = update_library_item_links_for_path(
                    library_item_filename = realpath,
                    destination_filename = filename,
                )
            elif library_item_type in ['ContextItem']:
                updated_library_items[path] = update_context_item_links_for_path(
                    context_item_filename = realpath, 
                    destination_filename = filename,
                    site_root = site_root,
                )
            else:
                raise TemplateError('Unknown library item type %r'%library_item_type)
        # Now apply the item
        output.append(data[start_of_start:end_of_start])
        output.append(updated_library_items[path])
        output.append(data[start_of_end:end_of_end])
        pos = end_of_end
    # Output to the end
    output.append(data[pos:])
    fp = open(filename, 'w')
    fp.write(''.join(output).encode('utf-8'))
    fp.close()

def replace_link(filename, src, dst):
    """\
    The approach is to re-calculate what the changed link should be like in
    this file as a relative path then to do a simple regex replace on any 
    ``src`` or ``href`` attributes using that value.
    """
    path = os.path.abspath(filename)
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    cur_link = relpath(src, os.path.dirname(filename))
    new_link = relpath(dst, os.path.dirname(filename))
    fp = open(filename, 'r')
    data = fp.read().decode('utf-8')
    fp.close()
   
    # Handle src and html tags first
    href_and_src_pattern = r'''<([^>]*?)(href|src)(\s*)=(\s*)("|')%s("|')(\s*.*?)>'''%(re.escape(cur_link))
    def href_and_src_replace(match):
        # Keep the old HTML spacing
        result = '<%s%s%s=%s%s%s%s%s>'%(
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
            match.group(5),
            new_link,
            match.group(6),
            match.group(7),
        )
        return result
    data, replaced_links = re.subn(
        href_and_src_pattern, 
        href_and_src_replace, 
        data
    )
    if replaced_links:
        fp = open(filename, 'w')
        fp.write(data.encode('utf-8'))
        fp.close()

def reapply_template_to_page(page, delete_missing_sections=[]):
    fp = open(page, 'r')
    data = fp.read().decode('utf-8')
    fp.close()
    template_regex = re.compile(r"""<!--\s*?InstanceBegin\s*?template\s*?=\s*?"(.*?)\"[^>]*?-->""")
    template_match = re.search(template_regex, data)
    if not template_match:
        raise TemplateError('Could not determine the template used by %r'%page)
    template = os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(page), template_match.group(1))))
    log.debug("Found template %r", template)
    reapply_template_to_pages(template, [os.path.abspath(page)], delete_missing_sections)

def move_file(src, dst, site_root, update_other_links=False):
    if not os.path.exists(src):
        raise TemplateError("No such file %r."%src)
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.split(src)[-1])
    # Update the file
    fp = open(src, 'rb')
    data = fp.read()
    fp.close()
    if src.endswith('.html'):
        data = update_links(
            site_root = site_root,
            old_path = src,
            new_path = dst,
            content = data,
        )
    log.info("Creating new file %r...", dst)
    fp = open(dst, 'wb')
    fp.write(data)
    fp.close()
    log.info("Removing %r...", src)
    if os.path.normpath(os.path.abspath(src)) != os.path.normpath(os.path.abspath(dst)):
        os.remove(src)
    if src.endswith('.html'):
        # Update the page's internal links
        if update_other_links:
            page = DreamweaverTemplateInstance(filename=dst)
            log.info("Scanning for links that need updating...")
            #site_root = os.sep.join(os.path.dirname(page.template_path).split(os.sep)[:-1])
            for dirpath, dirnames, filenames in os.walk(site_root):
                for filename in filenames:
                    if filename.endswith('.html'):
                        path = os.path.join(dirpath, filename)
                        if path == dst:
                            # Don't update the file we've just moved
                            continue
                        log.debug("Inspecting %r in site %s to replace %r with %r", path, site_root, src, dst)
                        # Update the links
                        replace_link(
                            filename=path,
                            src=src,
                            dst=dst,
                        )
    return [dst]

def handle_sitemap_entry(site_root, content, dirpath, filename, current_path):
    path = os.path.join(dirpath, filename)
    #site_path = path
    #if site_path.endswith('/index.html'):
    #    site_path = site_path[:-len('/index.html')]
    #if current_path is None:
    #    content.append('<div class="indent">')
    #else:
    #    change = site_path.count(os.sep) - current_path.count(os.sep) 
    #    # content.append('<!-- %s -->'%change)
    #    if change > 0:
    #        content.append('<div class="indent">'*change)
    #    elif change < 0:
    #        print '</ul>'
    #        content.append('</div>'*change)
    #    #elif dirpath != os.path.dirname(current_path):
    #    #    print '---</ul>'
    #    #    content.append('</div><div class="indent">')
    #        
    #current_path = site_path
    log.info("Inspecting %r", path)
    content.append('<div><a href="%s">%s</a></div>'%(relpath(path, site_root), extract_title(path, full=True)))
    return current_path

def links(site_root):
    if not os.path.exists(os.path.join(site_root, 'Templates')):
        raise TemplateError("Path %r does not appear to be a vaild site root, it has no 'Templates' directory"%site_root)
    files = {}
    passed = []
    failed = []
    all = []
    log.debug("Extracting internal links in %r", site_root)
    for dirpath, dirnames, filenames in os.walk(site_root):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            all.append(os.path.join(dirpath, filename))
            if filename.endswith('.html'):
                fp = open(os.path.join(dirpath, filename), 'r')
                data = fp.read()
                fp.close()
                links = []
                while data:
                    link_match = re.search(href_and_src_pattern, data)
                    if not link_match:
                        break
                    else:
                        link = link_match.group(6)
                        if link.startswith('/') or link.startswith('http://') or link.startswith('ftp://') or link.startswith('smb://') or link.startswith('mailto:') or link.startswith('javascript:') or link.startswith('https://') or link.startswith('#'):
                            # XXX actually need to handle anchors properly too and external links.
                            pass
                        else:
                            path = os.path.normpath(os.path.join(dirpath, link))
                            links.append(path)
                        data = data[link_match.end(0):]
                broken = []
                for link in links:
                    if link in passed:
                        # the link exists
                        pass
                    elif link in failed:
                        broken.append(link)
                    else:
                        # We need to see if it exists
                        if os.path.exists(link):
                            passed.append(link)
                        else:
                            failed.append(link)
                            broken.append(link)
                if broken:
                    files[os.path.join(dirpath, filename)] = broken
    return passed, files, all

