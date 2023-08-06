"""Manage a blog based on reStructuredText files"""

import datetime
import logging
import os.path
import re

from docutils import core

from sitetool.template.dreamweaver import DreamweaverTemplateInstance
from sitetool.api import update
from sitetool.convert.plugin import Plugin
from sitetool.convert.rst import rstify
from sitetool.exception import PluginError

log = logging.getLogger(__name__)

def build_rst_post(post):              
    tag_links = []
    for tag in post['tags']:
        #tag_links.append('`%s <../tag/%s.html>`_'%(tag['name'], tag['path']))
        tag_links.append('%s'%(tag['name']))
    rst = """\
%s
%s

:Posted: %s%s
"""%(
        post['title'],
        '+'*len(repr(post['title'])),
        post['posted'].year,#'`%s <../%s/index.html>`' % (post['posted'].year, post['posted'].year),
        post['posted'].strftime('-%m-%d %H:%M'),
    )
    if tag_links:
        rst += ':Tags: %s\n\n'%(', '.join(tag_links))
    rst+=post['source']
    if post.get('comments'):
        comments = []
        for comment in post['comments']:
            author = comment['author']
            if not author:
                author = 'Anonymous Coward'
            text = """\
%s
%s

:Posted: %s

%s
"""             %(
                    author,
                    '-'*len(repr(comment['author'])),
                    comment['created'].strftime('%Y-%m-%d %H:%M'),
                    comment['content']
                )
            if comment.get('url'):
                text += ':URL: %s'%comment.get('url')
            comments.append(text)
        rst += """\


Comments
========

%s"""%(
    '\n\n'.join(comments)
)
    try:
        return rst
    except Exception, e:
        log.error('Could not encode to UTF-8: %s', e)
        return ''

class BlogPlugin(Plugin):
    changed = False

    def parse_config(self, config):
        if not config:
            return None
        result = {}
       
        result['dirs'] = []
        if config.has_key('BLOG_DIRECTORIES'):
            for directory in config['BLOG_DIRECTORIES'].split(','):
                if '..' in directory:
                    raise PluginError('Blog directories cannot contain .. characters')
                if directory.startswith('/'):
                    raise PluginError('Blog directories cannot start with /')
                result['dirs'].append(os.path.abspath(os.path.join(self.site_root, directory.strip())))
        if config.has_key('BLOG_TITLE'):
            result['title'] = config['BLOG_TITLE']
        if config.has_key('BLOG_HEADING'):
            result['heading'] = config['BLOG_HEADING']
        if config.has_key('BLOG_TEMPLATE'):
            template = config['BLOG_TEMPLATE']
            if '..' in template:
                raise PluginError('Blog template paths cannot contain .. characters')
            if template.startswith('/'):
                raise PluginError('Blog template paths cannot start with /')
            result['template'] = os.path.join(self.site_root, template)
        if not result['dirs']:
            log.warning('Configuration: No blog directories defined')
        if not result.has_key('template'):
            log.warning('Configuration: No blog template')
        if not result:
            return None
        return result

    def on_file(self, path, page=None, template=None):
        if not self.user_files:
            log.debug('Skipping %r, --ignore-user-files set', path)
            return False
        if not self.config:
            log.debug('No blog configuration, skipping %s', path)
            return False
        dir, filename = os.path.split(path)
        matched = False
        for blog_dir in self.config['dirs']:
            if os.path.abspath(os.path.normpath(path)).startswith(blog_dir):
                matched = True
        if not matched:
            log.debug('Not in a blog directory: %s. (%s)', path, self.config['dirs'])
            return False
        if not path.endswith('.rst'):
            log.debug('Not a .rst file: %s', filename)
            return False
        html_version = path[:-4]+'.html'
        if os.path.exists(html_version):
            if (not os.stat(path).st_mtime > os.stat(html_version).st_mtime) and not self.force:
                log.debug('Skipping %s since an HTML file of the same name already exists', filename)
                # In this case we have handled the file by doing nothing to it.
                return True
        # This is a file we should handle
        log.info('Converting blog post %s...', path[len(self.site_root)+1:])
        fp = open(path, 'r')
        rst = fp.read().decode('utf-8')
        fp.close()
        parts = rstify(rst, path).split('\n')
        title = parts[0][18:-5]
        content = []
        content = '\n'.join(parts[1:])
        tags = []
        tag_r, start, end = extract_tags(content)
        if not tag_r:
            log.warning("No tags found for %s"%path)
        else:
            for name, tag_path in tag_r:
                tags.append('<a href="../tag/%s.html">%s</a>'%(tag_path, name))
            content = content[:start] + ', '.join(tags) + content[end:]
        page = DreamweaverTemplateInstance(self.config['template'])
        page['doctitle'] = '<title>'+title+'</title>'
        page['section_navigation'] = '''
      <div class="nav">
      <!-- #BeginLibraryItem "../../Library/blog_main_nav.lbi" --><!-- #EndLibraryItem -->
      </div>
    '''
        if page.has_key('section_navigation_bottom'):
            page['section_navigation_bottom'] = page['section_navigation'] 
        page['heading'] = title
        page['content'] = content + '<p class="text-right">(<a href="%s">view source</a>)</p>'%os.path.split(path)[1]
        page.save_as_page(path[:-4]+'.html')
        self.changed = True
        update(start_path=path[:-4]+'.html', site_root=self.site_root, update_static_items=True)
        return True

    def on_leave_directory(self, directory):
        if directory in self.config['dirs']:
            if not self.generated_files:
                log.info('Skipping indexes on %r, (--auto-files not set)', directory)
                return True
            # At this point generate the indexes
            elif not self.changed and not self.force:
                log.info('Skipping indexes, no changes made to %r', directory)
                return True
            else:
                log.info('Regenerating indexes for %r', directory)
                years, tags, tag_paths = build_index(directory)
                build_index_pages(years, tags, tag_paths, directory, self.config['template'], self.site_root, self.config)
                return True
        return False

tags_regex=re.compile(
    r"""<th class="docinfo-name">Tags:</th><td class="field-body">(.*?)</td>"""
)
def extract_tags(content):
    tags_match = tags_regex.search(content)
    result = []
    if tags_match:
        tags_ = tags_match.group(1)
        for tag in tags_.split(', '):
            # <a class="reference external" href="../tag/web/index.html">Web</a>
            if '>' in tag:
                tag_parts = tag.split('>')
                try:
                    name = tag_parts[1][:-3]
                    tag_path = tag_parts[0].split(' ')[1][len('href="../tag/'):-len('.html"')]
                except IndexError, e:
                    log.error("Failed to extract tags: %s, %s", e, tag_parts)
                else:
                    result.append((name, tag_path))
            else:
                result.append((tag, tag.lower().replace(' ','-')))
        return result, tags_match.start(1), tags_match.end(1)
    else:
        return [], None, None

def build_index(base):
    years = {}
    tags = {}
    tag_paths = {}
    posted_regex=re.compile(
        r"""<th class="docinfo-name">Posted:</th><td class="field-body">([0-9: \-]*?)</td>"""
    )
    title_regex=re.compile(
        r"""<title>(.*?)</title>"""
    )
    for dirpath, dirnames, filenames in os.walk(base):
        if dirpath.endswith('/tag'):
            continue
        for filename in filenames:
            if filename.endswith('.html') and not filename == 'index.html':
                path = os.path.join(dirpath, filename)
                log.debug("Extracting data from %r", path)
                fp = open(path, 'r')
                html = fp.read().decode('utf-8')
                fp.close()
                title = title_regex.search(html).group(1)
                # Get the bit of the page likely to contain the characters we need
                start_tag = '<!-- InstanceBeginEditable name="content" -->'
                pos = html.find(start_tag)
                content = html[pos+len(start_tag):]
                posted_match = posted_regex.search(content)
                if not posted_match:
                    log.warning("No posted date found for %s, not adding to index", path)
                else:
                    date = datetime.datetime.strptime(posted_match.group(1), '%Y-%m-%d %H:%M')
                    index_data = (date, {'filename': filename, 'title': title, 'posted': date})
                    if not years.has_key(date.year):
                        years[date.year] = [index_data]
                    else:
                        years[date.year].append(index_data)
                        tag_r, start, end = extract_tags(content)
                        if not tag_r:
                            log.warning("WARNING: No tags found for %s", path)
                        for name, tag_path in tag_r:
                            if not tag_paths.has_key(name):
                                tag_paths[name] = tag_path
                            index_data[1]['tag_path'] = tag_path
                            index_data[1]['tag_name'] = name
                            if not tags.has_key(name):
                                tags[name] = [index_data]
                            else:
                                tags[name].append(index_data)
    return years, tags, tag_paths

def build_index_pages(years, tags, tag_paths, base, template, site_root, config):
    blog_dir = base[len(site_root)+1:]
    # Add the navigation library item
    lbi = os.path.normpath(os.path.join(os.path.dirname(template), '..', 'Library', 'blog_main_nav.lbi'))
    content = []
    content.append('<a href="../%s/index.html">Blog</a> '%blog_dir)
    content.append('<a href="../%s/tag/index.html">Categories</a> '%blog_dir)
    years_=years.keys()
    years_.sort()
    years_.reverse()
    for year in years_:
        content.append('<a href="../%s/%s/index.html">%s</a> '%(blog_dir, year, year))
    fp = open(lbi, 'w')
    fp.write(''.join(content).encode('utf-8'))
    fp.close()
     
    # Build the tag index pages
    for tag, v in tags.items():
        page = DreamweaverTemplateInstance(template)
        page['doctitle'] = '<title>%s</title>'%tag
        page['section_navigation'] = '''
              <div class="nav">
              <!-- #BeginLibraryItem "../../Library/blog_main_nav.lbi" --><!-- #EndLibraryItem -->
              </div>
'''
        if page.has_key('section_navigation_bottom'):
            page['section_navigation_bottom'] = page['section_navigation'] 
        #page['section_navigation'] = ''
        page['heading'] = 'Blog Category: %s'%tag
        content = ['<ul>']
        v.sort()
        v.reverse()
        for date, item in v:
            content.append(
                '<li><a href="../%s/%s">%s</a> (posted %s)</li>'%(
                    date.year,
                    item['filename'][:-5]+'.html', 
                    item['title'], 
                    date.strftime('%Y-%m-%d %H:%M')
                )
            )
        if tag_paths.has_key(tag):
            path = tag_paths[tag]
            content.append('</ul>')
            page['content'] = '\n'.join(content)
            if not os.path.exists(os.path.join(base, 'tag')):
                os.mkdir(os.path.join(base, 'tag'))
            path = os.path.join(base, 'tag', str(path)+'.html')
            page.save_as_page(path)
            update(start_path=path, site_root=site_root, update_static_items=True)
        else:
            log.warning("Tag %r not used", tag)
    
    # Build the year index pages
    for year, v in years.items():
        page = DreamweaverTemplateInstance(template)
        page['doctitle'] = '<title>%s</title>'%year
        page['heading'] = 'Blog Archives %s'%year
        page['section_navigation'] = '''
              <div class="nav">
              <!-- #BeginLibraryItem "../../Library/blog_main_nav.lbi" --><!-- #EndLibraryItem -->
              </div>
'''
        if page.has_key('section_navigation_bottom'):
            page['section_navigation_bottom'] = page['section_navigation'] 
        content = ['<ul>']
        v.sort()
        v.reverse()
        for date, item in v:
            content.append(
                '<li><a href="%s">%s</a> (posted %s)</li>'%(
                    item['filename'][:-5]+'.html', 
                    item['title'], 
                    date.strftime('%Y-%m-%d %H:%M')
                )
            )
        content.append('</ul>')
        page['content'] = '\n'.join(content)
        path = os.path.join(base, str(year), 'index.html')
        page.save_as_page(path)
        update(start_path=path, site_root=site_root, update_static_items=True)

 
    # Build the index page listing the different categories
    page = DreamweaverTemplateInstance(template)
    page['doctitle'] = "<title>Categories</title>"
    page['section_navigation'] = '''
              <div class="nav">
              <!-- #BeginLibraryItem "../../Library/blog_main_nav.lbi" --><!-- #EndLibraryItem -->
              </div>
'''
    if page.has_key('section_navigation_bottom'):
        page['section_navigation_bottom'] = page['section_navigation'] 
    page['heading'] = "Categories"
    content = []
    tags_ = tag_paths.keys()
    tags_.sort()
    for name in tags_:
        path = tag_paths[name]
        content.append(
            '<li><a href="%s.html">%s</a></li>'%(
                path, name
            )
        )
    content.append('</ul>')
    page['content'] = '\n'.join(content)
    page.save_as_page(os.path.join(base, 'tag', 'index.html'))

    # Build the blog section homepage
    all = []
    for year, v in years.items():
        for page in v:
            all.append(page)
    all.sort()
    all.reverse()
    page = DreamweaverTemplateInstance(template)
    if config.has_key('title'):
        page['doctitle'] = "<title>%s</title>"%config['title']
    if config.has_key('heading'):
        page['heading'] = config['heading']
    page['section_navigation'] = '''
              <div class="nav">
              <!-- #BeginLibraryItem "../Library/blog_main_nav.lbi" --><!-- #EndLibraryItem -->
              </div>
'''
    content = ['<h2>20 Latest Posts</h2><ul>']
    for date, item in all[:20]:
        content.append(
            '<li><a href="%s/%s">%s</a> (posted %s)</li>'%(
                date.year,
                item['filename'][:-5]+'.html', 
                item['title'], 
                date.strftime('%Y-%m-%d %H:%M')
            )
        )
    if page.has_key('section_navigation_bottom'):
        page['section_navigation_bottom'] = page['section_navigation'] 
    archives = []
    for year in years.keys():
        archives.append('<a href="%s/index.html">%s</a> '%(year, year))
    archives.sort()
    archives.reverse()
    content.append('</ul><p>See the archives for more: %s'%(''.join(archives)))
    page['content'] = '\n'.join(content)
    path = os.path.join(base, 'index.html')
    page.save_as_page(path)
    update(start_path=path, site_root=site_root, update_static_items=True)
    log.info("Finished: %s posts in all", len(all))

def build_redirects(years, tag_paths, blog_url):
    # Build a set of redirects that can be used from the old site
    # http://jimmyg.org/2009/04/06/my-experience-of-using-restructuredtext-to-write-the-definitive-guide-to-pylons/
    all = []
    for year, v in years.items():
        for page in v:
            all.append(page)
    all.sort()
    all.reverse()
    redirects = []
    for date, item in all:
        redirects.append('Redirect permanent /%04d/%02d/%02d/%s/ %s/%4d/%s'%(date.year, date.month, date.day, item['filename'][:-5], blog_url, date.year, item['filename']))
        redirects.append('Redirect permanent /%04d/%02d/%02d/%s  %s/%4d/%s'%(date.year, date.month, date.day, item['filename'][:-5], blog_url, date.year, item['filename']))
    for tag in tag_paths.values():
        redirects.append('Redirect permanent /category/%s/  %s/tag/%s.html'%(tag, blog_url, tag))
        redirects.append('Redirect permanent /category/%s  %s/tag/%s.html'%(tag, blog_url, tag))
    return redirects 

