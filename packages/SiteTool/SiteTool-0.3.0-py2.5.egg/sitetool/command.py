"""Command line interface to the sitetool API

You can being using it like this:

::

    python -m sitetool.command --help

"""

import os.path
import logging
import sys
import getopt
import subprocess
import math

from commandtool import parse_html_config
from commandtool import strip_docstring
from commandtool import option_names_from_option_list
from commandtool import set_error_on
from commandtool import parse_command_line
from commandtool import handle_program
from commandtool import makeHandler
from sitetool.exception import TemplateError
from sitetool.template.dreamweaver import relpath
from sitetool import help

from bn import uniform_path

log = logging.getLogger(__name__)

# Bit of a hack but will do for now
from gallery import handle_command_thumb, handle_command_metadata, handle_command_gallery


#
# Command Handlers
#

def path_from_config(filename, path):
    abs = uniform_path(path)
    if abs != path:
        # Relative path
        return os.path.abspath(os.path.normpath(os.path.join(os.path.split(filename)[0], path)))
    return abs

def handle_command_create(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s create [OPTION]... TEMPLATE PAGE``

    create (cr): Create a new page

    Arguments:

      :``PAGE``: path of page to create
      :``TEMPLATE``: the full path of the template to use

    Options:

      All program options... (see \`%(program)s --help')

    Typical use:

      ``%(program)s create Templates/jimmyg.dwt new.html``
    """
    set_error_on(
        command_options, 
        allowed=[]
    )
    if len(args) < 1:
        raise getopt.GetoptError('No TEMPLATE specified')
    elif len(args) < 2:
        raise getopt.GetoptError('No PAGE specified')
    elif len(args) > 2:
        raise getopt.GetoptError('Unexpected argument %r'%args[2])
    # Note, the Python API has page as the first argument, not template
    page = uniform_path(args[1])
    template = uniform_path(args[0])
    from sitetool.api import create
    try:
        create(page=page, template=template)
    except TemplateError, e:
        print "FAILED: %s" % e
    else:
        print "Page created successfully."

def handle_command_list(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s list [OPTIONS]... [PAGE|TEMPLATE]``

    list (ls): List the regions and properties contained in a page or template

    Arguments:

      :``PAGE``: the path of the page
      :``TEMPLATE``: the path of the template

    Options:

      All program options... (see \`%(program)s --help')
    
    Typical use:

      ``%(program)s list page.html``
    """
    set_error_on(
        command_options, 
        allowed=[]
    )
    if len(args) < 1:
        raise getopt.GetoptError('No PAGE or TEMPLATE specified')
    elif len(args) > 1:
        raise getopt.GetoptError('Unexpected argument %r'%args[1])
    page_or_template = uniform_path(args[0])
    from sitetool.api import list_areas
    try:
        properties, regions = list_areas(page_or_template)
    except TemplateError, e:
        print "FAILED: %s" % e
    else:
        print "Properties:"
        for property in properties:
            print " "+property
        print
        print "Regions:"
        for region in regions:
            print " "+region

def handle_command_get(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s get [OPTIONS]... [PAGE|TEMPLATE]``

    get: Display the contents of a page or template region or property

    Arguments:

      :``PAGE``: the path of the page
      :``TEMPLATE``: the path of the template

    Options:

      -a, --area=AREA  name of the page region or property to fetch

      Plus all program options... (see \`%(program)s --help')
    
    Typical use:

      ``%(program)s get -a doctitle page.html``
    """
    set_error_on(
        command_options, 
        allowed=['area']
    )
    if len(args) < 1:
        raise getopt.GetoptError('No PAGE or TEMPLATE specified')
    elif len(args) > 1:
        raise getopt.GetoptError('Unexpected argument %r'%args[1])
    page_or_template = uniform_path(args[0])
    if not command_options.has_key('area'):
        raise getopt.GetoptError(
            'No AREA to get specified. Use the -a option.'
        )
    else:
        area_options = command_options['area']
        if len(area_options) > 1:
            raise getopt.GetoptError('Only one --area or -a option is allowed')
        area = area_options[0]['value'] 
    from sitetool.api import get
    try:
        result = get(page_or_template, area)
    except TemplateError, e:
        print "FAILED: %s" % e
    else:
        print result

def handle_command_set(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s set [OPTIONS]... [PAGE|TEMPLATE]``

    set: Set a page region or property

    If neither the -i nor -n options are used the value to update the page with
    is read from STDIN.

    Arguments:

      :``PAGE``: the path of the page to update
      :``TEMPLATE``: the path of the template

    Options:

      -a, --area=AREA              name of the page region or property to fetch
      -e, --new-content=CONTENT    the value to update the content with
      -i, --interactive            load the current value of the region in the 
                                   editor specified by the EDITOR environment 
                                   variable and update the saved contents of the
                                   page when the editor exits

      Plus all program options... (see \`%(program)s --help')
    
    Typical use for interactive editing:

      ``%(program)s set -i -a doctitle page.html``
    """
    set_error_on(
        command_options, 
        allowed=['area', 'content', 'interactive']
    )
    if len(args) < 1:
        raise getopt.GetoptError('No PAGE or TEMPLATE specified')
    elif len(args) > 1:
        raise getopt.GetoptError('Unexpected argument %r'%args[1])
    page_or_template = uniform_path(args[0])
    if not command_options.has_key('area'):
        raise getopt.GetoptError(
            'No AREA to get specified. Use the -a option.'
        )
    else:
        area_options = command_options['area']
        if len(area_options) > 1:
            raise getopt.GetoptError(
                'Only one --area or -a option is allowed'
            )
        area = area_options[0]['value'] 
    if command_options.has_key('content') and \
       command_options.has_key('interactive'):
        raise getopt.GetoptError(
            'The %s and %s options cannot be used together' % (
                command_options['content'][0]['name'],
                command_options['interactive'][0]['name'],
            )
        )
    if not command_options.has_key('content') and not \
       command_options.has_key('interactive'):
        log.info(
            "Reading from STDIN "
            "(press Ctrl+C to abort, Press Ctrl+D twice to save)"
        )
        try:
            content = sys.stdin.read()
        except KeyboardInterrupt:
            print "Aborted"
            sys.exit(1)
    elif command_options.has_key('content'):
        if len(command_options['content'])>1:
            raise getopt.GetoptError(
                'Only one --content or -e option is allowed'
            )
        content = command_options['content'][0]['value']
    else:
        # Interactive mode

        import os
        import re
        from tempfile import mkstemp
        from sitetool.api import get

        EDITOR = os.environ.get('EDITOR', 'vim')
        fd, tmpfl = mkstemp()
        try:
            buf = get(page_or_template, area)
        except TemplateError, e:
            print "FAILED: %s" % e
            sys.exit(1)
        else:
            os.write(fd, buf.encode('utf8'))
            os.close(fd)
            os.system('%s %s' % (EDITOR, tmpfl))
            content = open(tmpfl).read()
            os.unlink(tmpfl)
            tmpfl = ''
    from sitetool.api import set
    try:
        result = set(page_or_template, area, content)
    except TemplateError, e:
        print "FAILED: %s" % e
    else:
        print "Successfully updated"

def handle_command_convert(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s convert [OPTIONS]... [PLUGIN_OPTIONS]...``

    convert (cv): Convert a source file to HTML using all available plugins

    If -S is specified only the files under that directory are scanned, in which
    case the -s option is not required. If START_PATH is a file, only that
    file is converted, if it is a directory all files in that directory are
    converted.  If -r is specified, or -S is not specified the search is recursive
    and all child directories are converted. If -f is specified, files are
    re-created even if they appear up to date.

    The -c option is always required because it contains information about which
    plugins should be used to convert which sections and the templates to use.
    See http://jimmyg.org/blog/2009/site-tool for more information.

    Caution: 
 
      You shouldn't usually try to convert a sub-directoy of a blog 
      directory if you want the indexes to be re-generated, instead
      convert the whole directory. 

    Options:

      -c, --config=CONFIG           path to the config file
      -s, --site-root=SITE_ROOT     path to the site root directory
      -S, --start-path=START_PATH   the path to start the search at
      -g, --generated-files         create generated files and index pages
      -u, --user-files              convert user-created files
      -r, --recursive               recursivley convert all files under that directory
      -f, --force                   force convertion of all files, even if HTML versions
                                    already exist
      -C, --context-items           reapply context library items to newly converted and
                                    existing pages

      Plus all program options... (see \`%(program)s --help')

    Plugin options:

      -t, --template=TEMPLATE       the template to use for the plain rst plugin 

    Typical use to re-convert an entire section and then reapply context items to
    both newly convert and existing items:

      ``%(program)s convert -c about.html -ugrfC -S blog``
    """
    set_error_on(
        command_options, 
        allowed=[
            'config', 
            'site_root', 
            'start_path', 
            'generated_files', 
            'user_files', 
            'recursive', 
            'force',
            'template',
            'update_context_items',
        ]
    )
    if args:
        raise getopt.GetoptError('Unexpected argument %r'%args[0])
    internal_vars = {}
    # Set up config
    if command_options.has_key('config'):
        internal_vars['config'] = parse_html_config(
            command_options['config'][0]['value']
        )
    if not internal_vars.has_key('config'):
        internal_vars['config'] = {}
    # Set up template
    if command_options.has_key('template'):
        print command_options['template'][0]
        internal_vars['config']['DEFAULT_TEMPLATE'] = uniform_path(
            command_options['template'][0]['value']
        )
    elif not internal_vars['config'].has_key('DEFAULT_TEMPLATE'):
        raise getopt.GetoptError('No DEFAULT_TEMPLATE specified')
        # XXX Need a relative path
        if not command_options.has_key('template'):
            raise getopt.GetoptError('No DEFAULT_TEMPLATE specified')
        internal_vars['config']['DEFAULT_TEMPLATE'] = uniform_path(
            command_options['template'][0]['value']
        )
    # Set up site_root
    if command_options.has_key('site_root'):
        site_root = uniform_path(command_options['site_root'][0]['value'])
    elif internal_vars.has_key('config') and internal_vars['config'].has_key('SITE_ROOT'):
        site_root = path_from_config(
            command_options['config'][0]['value'],
            internal_vars['config']['SITE_ROOT'],
        )
    else:
        raise getopt.GetoptError('No SITE_ROOT specified')
    # Set up start_path
    if command_options.has_key('start_path'):
        internal_vars['start_path'] = uniform_path(
            command_options['start_path'][0]['value']
        )
    # Set up generated_files
    if command_options.has_key('generated_files'):
        internal_vars['generated_files'] = True
    # Set up user_files
    if command_options.has_key('user_files'):
        internal_vars['user_files'] = True
    # Set up recursive
    if command_options.has_key('recursive'):
        internal_vars['recursive'] = True
    # Set up force
    if command_options.has_key('force'):
        internal_vars['force'] = True
    # Set up update_context_items
    if command_options.has_key('update_context_items'):
        internal_vars['update_context_items'] = True
    # Set up plugin_classes
    import sitetool.convert.rst
    import sitetool.convert.blog
    import gallery.plugin
    import sitetool.convert.suunto
    plugin_classes = [
        ('name',  sitetool.convert.blog.BlogPlugin), 
        ('default', sitetool.convert.rst.PlainRstPlugin),
        ('gallery', gallery.plugin.GalleryPlugin),
        ('suunto', sitetool.convert.suunto.SuuntoPlugin),
    ]
    # Now run the command
    from sitetool.api import convert
    try:
        convert(site_root, plugin_classes, **internal_vars)
    except TemplateError, e:
        print "FAILED: %s" % e

def handle_command_update(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s update [OPTIONS]...``

    update (ud): Convert a source file to HTML using all available plugins

    If -S is specified only the files under that directory are scanned. If
    START_PATH is a file, only that file is updated, if it is a directory all 
    files in that directory are converted.  If -r is specified, or -S is not 
    specified the search is recursive and all child directories are updated.

    The -T, -C, -D and -L options specify what to update in any pages which are 
    found.

    Options:

      -c, --config=CONFIG           path to the config file
      -s, --site-root=SITE_ROOT     path to the site root directory
      -S, --start-path=START_PATH   the path to start the search at
      -r, --recursive               recursivley convert all files under directory
      -T, --templates               reapply the templates
      -C, --context-items           reapply context library items
      -D, --dynamic-items           reapply dynamic library items
      -L, --static-items            reapply static library items

      Plus all program options... (see \`%(program)s --help')

    Typical use to udpdate an entire section:
      %(program)s update -c about.html -rTCDL -S blog/
    """
    set_error_on(
        command_options, 
        allowed=[
            'config', 
            'site_root', 
            'start_path', 
            'recursive', 
            'update_templates',
            'update_context_items', 
            'update_dynamic_items', 
            'update_static_items', 
        ]
    )
    if args:
        raise getopt.GetoptError('Unexpected argument %r'%args[0])
    internal_vars = {}
    config = {}
    if command_options.has_key('config'):
        config = parse_html_config(command_options['config'][0]['value'])
    # Set up site_root
    # It doesn't matter if site_root is missing
    if command_options.has_key('site_root'):
        internal_vars['site_root'] = uniform_path(
            command_options['site_root'][0]['value']
        )
    elif config.has_key('SITE_ROOT'):
        internal_vars['site_root'] = path_from_config(
            command_options['config'][0]['value'],
            config['SITE_ROOT'],
        )
    # Set up start_path
    if command_options.has_key('start_path'):
        internal_vars['start_path'] = uniform_path(
            command_options['start_path'][0]['value']
        )
    if not internal_vars.has_key('start_path') and \
       not internal_vars.has_key('site_root'):
        raise getopt.GetoptError('No START_PATH specified, use the -S option')
    # Set up recursive
    if command_options.has_key('recursive'):
        internal_vars['recursive'] = True
    # Set up update_templates
    if command_options.has_key('update_templates'):
        internal_vars['update_templates'] = True
    # Set up update_context_items
    if command_options.has_key('update_context_items'):
        internal_vars['update_context_items'] = True
    # Set up update_dynamic_items
    if command_options.has_key('update_dynamic_items'):
        internal_vars['update_dynamic_items'] = True
    # Set up update_static_items
    if command_options.has_key('update_static_items'):
        internal_vars['update_static_items'] = True
    if not internal_vars.has_key('update_templates') and not \
       internal_vars.has_key('update_context_items') and not \
       internal_vars.has_key('update_dynamic_items') and not \
       internal_vars.has_key('update_static_items'):
        raise getopt.GetoptError("Nothing to update. Please specify at least one of -T, -C, -D or -L.")
    # Now run the command
    from sitetool.api import update
    try:
        update(**internal_vars)
    except TemplateError, e:
        print "FAILED: %s" % e

def handle_command_move(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s move [OPTIONS]... SOURCE DEST``

    move (mv): Move a page or section

    Arguments:

      :``SOURCE``: path of the page or directory to move
      :``DEST``: path of directory to move to

    Options:

      -c, --config=CONFIG          path to the config file
      -s, --site-root=SITE_ROOT    path to the site root directory
      -l, --links                  update links sitewide to the moved page(s)
      -C, --context-items          update context items in the moved page(s)

      Plus all program options... (see \`%(program)s --help')

    Typical use:

      ``%(program)s move -Clc about.html src/page.html dst``
    """
    set_error_on(
        command_options, 
        allowed=[
            'config', 
            'site_root', 
            'update_other_links', 
            'update_context_items',
        ]
    )
    if len(args) < 1:
        raise getopt.GetoptError('No SOURCE specified')
    elif len(args) < 2:
        raise getopt.GetoptError('No DEST specified')
    elif len(args) > 2:
        raise getopt.GetoptError('Unexpected argument %r'%args[2])
    src = uniform_path(args[0])
    dst = uniform_path(args[1])
    internal_vars = {}
    # Set config
    config = {}
    if command_options.has_key('config'):
        config = parse_html_config(command_options['config'][0]['value'])
    # Set up site_root
    if command_options.has_key('site_root'):
        internal_vars['site_root'] = uniform_path(
            command_options['site_root'][0]['value']
        )
    elif config.has_key('SITE_ROOT'):
        internal_vars['site_root'] = path_from_config(
            command_options['config'][0]['value'],
            config['SITE_ROOT'],
        )
    else:
        getopt.GetoptError('No SITE_ROOT specified')
    # Set up update_context_items
    if command_options.has_key('update_context_items'):
        internal_vars['update_context_items'] = True
    # Set up update_other_links
    if command_options.has_key('update_other_links'):
        internal_vars['update_other_links'] = True
    # Now run the command
    from sitetool.api import move
    try:
        files = move(src, dst, **internal_vars)
    except TemplateError, e:
        print "FAILED: %s" % e
    else:
        if files:
            print "Successfully moved %s files"%len(files)

def handle_command_deploy(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s deploy [OPTIONS]...``

    deploy (dp): Upload any local changes to the remote site

    Either a config file containing SITE_ROOT and REMOTE_SCP must be specified or
    the -s and -d options must be used. Internally the command uses \`rsync' but
    does not delete files on the remote server unless --delete is specified.

    Options:

      -c, --config=CONFIG           path to the config file
      -s, --site-root=SITE_ROOT     path to the site root directory
      -d, --remote-scp=REMOTE_SCP   remote directory in the format expected by
                                    the \`scp' program
      --delete                      delete files on the remote server which aren't
                                    present on the local server
      -n, --dry-run                 show the changes to be made but don't make
                                    them
      --exclude-from=EXCLUDE_FROM   a file listing all the files not to deploy

      Plus all program options... (see \`%(program)s --help')

    Typical use:

      ``%(program)s deploy -s ./ -d user@server.example.com:path/to/site``
    """
    set_error_on(
        command_options, 
        allowed=['config', 'exclude_from', 'site_root', 'remote_scp', 'delete', 'dry_run']
    )
    if args:
        raise getopt.GetoptError('Unexpected argument %r'%args[0])
    internal_vars = {}
    config = {}
    if command_options.has_key('config'):
        config = parse_html_config(command_options['config'][0]['value'])
    # Set up remote_scp
    if command_options.has_key('remote_scp'):
        internal_vars['remote_scp'] = command_options['remote_scp'][0]['value']
    elif config.has_key('REMOTE_SCP'):
        internal_vars['remote_scp'] = config['REMOTE_SCP']
    else:
        raise getopt.GetoptError('No REMOTE_SCP specified')
    # Set up site_root
    if command_options.has_key('site_root'):
        internal_vars['site_root'] = uniform_path(
            command_options['site_root'][0]['value']
        )
    elif config.has_key('SITE_ROOT'):
        internal_vars['site_root'] = path_from_config(
            command_options['config'][0]['value'],
            config['SITE_ROOT'],
        )
    else:
        raise getopt.GetoptError('No SITE_ROOT specified')
    if command_options.has_key('exclude_from'):
        internal_vars['exclude_from'] = command_options['exclude_from'][0]['value']
    # Set up delete
    if command_options.has_key('delete'):
        internal_vars['delete'] = True
    # Set up dry_run
    if command_options.has_key('dry_run'):
        internal_vars['dry_run'] = True
    # Now run the command
    from sitetool.api import deploy
    try:
        files = deploy(**internal_vars)
    except TemplateError, e:
        print "FAILED: %s" % e

def handle_command_sitemap(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s sitemap [OPTIONS]... SITEMAP``

    sitemap (sm): Scan the site and rebuild a sitemap

    Arguments:

      :``SITEMAP``: path of the file to create

    Options:

      -c, --config=CONFIG          path to the config file
      -s, --site-root=SITE_ROOT    path to the site root directory
      -F, --format=FORMAT          format for the sitemap, can be \`html' for a
                                   human readable sitemap or \`xml' for a search
                                   engine comaptible sitemap (see
                                   http://sitemaps.org)
      -t, --template=TEMPLATE      the template to use for the sitemap

      Plus all program options... (see \`%(program)s --help')

    Typical use:

      ``%(program)s sitemap -c about.html sitemap.html``
    """
    set_error_on(
        command_options, 
        allowed=['config', 'site_root', 'format', 'template']
    )
    if len(args)<1:
        raise getopt.GetoptError('No SITEMAP filename specified')
    if len(args)>1:
        raise getopt.GetoptError('Unexpected argument %r'%args[1])
    sitemap_path = uniform_path(args[0])
    internal_vars = {}
    config = {}
    if command_options.has_key('config'):
        config = parse_html_config(command_options['config'][0]['value'])
    # Set up site_root
    if command_options.has_key('site_root'):
        internal_vars['site_root'] = uniform_path(
            command_options['site_root'][0]['value']
        )
    elif config.has_key('SITE_ROOT'):
        internal_vars['site_root'] = path_from_config(
            command_options['config'][0]['value'],
            config['SITE_ROOT'],
        )
    else:
        raise getopt.GetoptError('No SITE_ROOT specified')
    # Set up template
    if command_options.has_key('template'):
        internal_vars['template'] = uniform_path(
            command_options['template'][0]['value']
        )
    elif config.has_key('DEFAULT_TEMPLATE'):
        internal_vars['template'] = path_from_config(
            command_options['config'][0]['value'],
            config['DEFAULT_TEMPLATE'],
        )
    else:
        raise getopt.GetoptError('No TEMPLATE specified')
    # Format
    if command_options.has_key('format'):
        getopt.GetoptionError('-f not supported yet')
    # Now run the command
    from sitetool.api import sitemap
    try:
        files = sitemap(sitemap_path, **internal_vars)
    except TemplateError, e:
        print "FAILED: %s" % e

def handle_command_broken(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s broken [OPTIONS]...`` 

    broken (br): Find broken links

    Scans the entire site for broken links. If -S is specified only
    the files under that directory are scanned, in which case the -c and -s
    options are not required. If START_PATH is a file, only that file is 
    converted, if it is a directory all files in that directory are converted.
    If -r is specified, or -S is not specified the search is recursive and
    all child directories are scanned.

    Options:

      -c, --config=CONFIG          path to the config file
      -s, --site-root=SITE_ROOT    path to the site root directory

      Plus all program options... (see \`%(program)s --help')

    Typical use:

      ``%(program)s broken -S blog/`` 
    """
    set_error_on(
        command_options, 
        allowed=['config', 'site_root', 'start_path']
    )
    if len(args):
        raise getopt.GetoptError('Unexpected argument %r'%args[0])
    internal_vars = {}
    config = {}
    if command_options.has_key('config'):
        config = parse_html_config(command_options['config'][0]['value'])
    # Set up site_root
    if command_options.has_key('site_root'):
        internal_vars['site_root'] = uniform_path(
            command_options['site_root'][0]['value']
        )
    elif config.has_key('SITE_ROOT'):
        internal_vars['site_root'] = path_from_config(
            command_options['config'][0]['value'],
            config['SITE_ROOT'],
        )
    else:
        raise getopt.GetoptError('No SITE_ROOT specified')
    # Now run the command
    from sitetool.api import broken
    try:
        files = broken(**internal_vars)
    except TemplateError, e:
        print "FAILED: %s" % e
    else:
        strip = len(internal_vars['site_root'])+1
        if not files:
            print "No broken links found"
        else:
            for filename, broken in files.items():
                print filename[strip:]
                for link in broken:
                    print '  ' + link[strip:] 
                print

def handle_command_orphan(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s orphan [OPTIONS]...``

    orphan (or): Find ophaned files

    Scans the entire site for files which are not linked from other files
    in the site.

    Options:

      -c, --config=CONFIG           path to the config file
      -s, --site-root=SITE_ROOT     path to the site root directory
      --relative                    make paths relative to the current dir

      Plus all program options... (see \`%(program)s --help')

    Typical use:

      ``%(program)s orphan -s static | grep "\.html"``
    """
    set_error_on(
        command_options, 
        allowed=['config', 'relative', 'site_root', 'start_path']
    )
    if len(args):
        raise getopt.GetoptError('Unexpected argument %r'%args[0])
    internal_vars = {}
    config = {}
    if command_options.has_key('config'):
        config = parse_html_config(command_options['config'][0]['value'])
    if command_options.has_key('relative'):
        internal_vars['relative'] = True
    # Set up site_root
    if command_options.has_key('site_root'):
        internal_vars['site_root'] = uniform_path(
            command_options['site_root'][0]['value']
        )
    elif config.has_key('SITE_ROOT'):
        internal_vars['site_root'] = path_from_config(
            command_options['config'][0]['value'],
            config['SITE_ROOT'],
        )
    else:
        raise getopt.GetoptError('No SITE_ROOT specified')
    # Now run the command
    from sitetool.api import orphan
    try:
        orphans = orphan(**internal_vars)
    except TemplateError, e:
        print "FAILED: %s" % e
    else:
        if not orphans:
            print "No orphaned files found"
        else:
            #strip = len(internal_vars['site_root'])+1
            for filename in orphans:
                print filename

def handle_command_export(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s export [OPTIONS]... [MYSQL_OPTIONS] DEST``

    update (ex): Export from another system to static files

    Specify the export mode with -m. Currently only \`wordpress-rst' is supported.

    Arguments:

      :``DEST``: directory to export the files to

    Options:

      -c, --config=CONFIG          path to the config file
      -s, --site-root=SITE_ROOT    path to the site root directory
      -m, --mode=MODE              export mode (only \`wordpress-rst' supported)

      Plus all program options... (see \`%(program)s --help')

    MySQL Options:

      -B, --database=DATABASE      MySQL database to export
      -h, --host=HOST              host or IP address of the server
      -p, --port=PORT              the port of the MySQL server
      -U, --username=USERNAME      the username to use to connect
      -w, --password=PASSWORD      specify password on the command line. 
                                   Hint: more secure to use -i
      -i, --interactive            prompt for a password

    Typical use to export wordpress to reStructuredText:

      ``%(program)s export -m wordpress-rst -h db.example.com -B wp -U user -i blog/``
    """
    set_error_on(
        command_options, 
        allowed=[
            'config', 
            'site_root',
            'mode',
            'database', 
            'host',
            'port', 
            'username', 
            'password', 
            'interactive', 
        ]
    )
    if len(args)<1:
        raise getopt.GetoptError('No DEST specified')
    if len(args)>1:
        raise getopt.GetoptError('Unexpected argument %r'%args[1])
    dest = uniform_path(args[0])
    internal_vars = {}
    config = {}
    if command_options.has_key('config'):
        config = parse_html_config(command_options['config'][0]['value'])
    # Set up the mode:
    if command_options.has_key('mode'):
        internal_vars['mode'] = command_options['mode'][0]['value']
        if not internal_vars['mode'] == 'wordpress-rst':
            raise getopt.GetoptError(
                'Unsupported mode %r'%internal_vars['mode']
            )
    # Set up site_root
    if command_options.has_key('site_root'):
        internal_vars['site_root'] = uniform_path(
            command_options['site_root'][0]['value']
        )
    elif config.has_key('SITE_ROOT'):
        internal_vars['site_root'] = path_from_config(
            command_options['config'][0]['value'],
            config['SITE_ROOT'],
        )
    else:
        raise getopt.GetoptError('No SITE_ROOT specified')  
    connect = {} 
    if command_options.has_key('password') and \
       command_options.has_key('interactive'):
        raise getopt.GetoptError(
            'You cannot specify both %s and %s'%(
                command_options['password']['name'], 
                command_options['interactive']['name'], 
            )
        )
    password = None
    if command_options.has_key('password'):
        password = command_options['password'][0]['value']
    elif command_options.has_key('interactive'):
        import getpass
        try:
            password = getpass.getpass('Password: ')
        except KeyboardInterrupt:
            print "Aborted"
            sys.exit(1)
    if password is not None:
        connect['passwd'] = password
    if command_options.has_key('host'):
        connect['host'] = command_options['host'][0]['value']
    if command_options.has_key('username'):
        connect['user'] = command_options['username'][0]['value']
    if command_options.has_key('port'):
        connect['port'] = int(command_options['port'][0]['value'])
    if command_options.has_key('database'):
        connect['db'] = command_options['database'][0]['value']
    # Now run the command
    from sitetool.export import wordpress
    try:
        posts, tags = wordpress.export(connect)
        internal_vars['posts'] = posts
        internal_vars['dest'] = dest
        del internal_vars['mode']
        log.info('Building pages...')
        wordpress.save_posts(**internal_vars)
    except TemplateError, e:
        print "FAILED: %s" % e

def handle_command_redirect(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s redirect [OPTIONS]...``

    update (ex): Generate Apache .htaccess with required redirects

    Scan for files which may have come from elsewhere and require redirects to
    their current positions. If -S is specified only the files under that directory
    are scanned, otherwise all files in the site are scanned.

    Caution:

      Currently adds the redirects even if files at that location already exist.

    Options:
      -b, --base-url=BASE_URL       path to the site root directory
      -S, --start-path=START_PATH   the path to start the search at

      Plus all program options... (see \`%(program)s --help')

    Typical use to export wordpress to reStructuredText:

      ``%(program)s redirect -c about.html -b http://jimmyg.org -S blog``
    """
    set_error_on(
        command_options, 
        allowed=[
            'config', 
            'site_root',
            'start_path',
            'base_url',
        ]
    )
    if args:
        raise getopt.GetoptError('Unexpected argument %r'%args[0])
    internal_vars = {}
    config = {}
    if command_options.has_key('config'):
        config = parse_html_config(command_options['config'][0]['value'])
    # Set up start_path
    if command_options.has_key('start_path'):
        internal_vars['start_path'] = uniform_path(
            command_options['start_path'][0]['value']
        )
    else:
        raise getopt.GetoptError('No START_PATH specified, use the -S option')
    # Set up base_url
    if command_options.has_key('base_url'):
        internal_vars['base_url'] = command_options['base_url'][0]['value']
    else:
        raise getopt.GetoptError('No BASE_URL specified, use the -b option')
    # Now run the command
    from sitetool.convert import blog
    try:
        years, tags, tag_paths = blog.build_index(internal_vars['start_path'])
        if internal_vars['base_url'].endswith('/'):
            internal_vars['base_url'] = internal_vars['base_url'][:-1]
        print '\n'.join(blog.build_redirects(years, tag_paths, internal_vars['base_url']))
    except TemplateError, e:
        print "FAILED: %s" % e

def handle_command_resize(
    option_sets, 
    command_options, 
    args,
):
    """\
    usage: ``%(program)s resize [OPTIONS]... -z 800x600 -F png -o test.rst FILES...``

    resize (rz): Create thumbnails for images and pre-popualte a .rst file

    Arguments:

      :FILES:  A list of files to convert

    WARNING: If the output format is the same as the input format your input
    files will be overwritten.

    Options:

      -z, --size=SIZE               the size for the thumbnails
      -F, --format=FORMAT           the output format for the thumbnails
      -o, --output=OUTPUT           the filename to contain the optional rst source

      Plus all program options... (see \`%(program)s --help')

    Typical use to export wordpress to reStructuredText:

      ``%(program)s resize -z 800x600 -F png -o holiday.rst holiday/*.JPG``
    """
    internal_vars = set_error_on(
        command_options, 
        allowed=[
            'output',
            'format',
            'size',
        ]
    )
    if not args:
        raise getopt.GetoptError('No FILES specified')
    files = args[:]
    output = None
    if internal_vars.has_key('output'):
        output = internal_vars['output']
        del internal_vars['output']
    if not output and not internal_vars:
        raise getopt.GetoptError('No actions to perform. Please specify -z -F -o etc')
    if output:
        result = []
        for path in files:
            
            filename = relpath(path, os.path.split(output)[0])
            new_website = ('.'.join(filename.split('.')[:-1]))+'.'+internal_vars.get('format', filename.split('.')[-1])

            file = os.path.split(filename)[1] 
            link = '.'.join(file.replace('-', ' ').replace('_', ' ').split('.')[:-1]).capitalize()
            rst = '.. image :: %s\n   :alt: %s\n   :target: %s'%(
                new_website,
                link,
                filename,
            )
            result.append(rst)
            fp = open(output, 'w')
            fp.write('New File\n++++++++\n\n'+'\n\n'.join(result))
            fp.close()
    if internal_vars:
        # Now run the command
        try:
            result = resize(files, **internal_vars)
        except TemplateError, e:
            print "FAILED: %s" % e
        else:
            if result:
                print "FAILED: Command exited with value %s" % result

def resize(files, size=None, format=None, output=None):
    jpgs = []
    for filename in files:
        for ext in ['.JPG', '.JPEG', '.jpg', '.jpeg']:
            if filename.endswith(ext):
                jpgs.append(filename)
    if jpgs:
        cmd = ['exiftran', '-ia'] + jpgs
        log.info('Running command %r', ' '.join(cmd))
        process = subprocess.Popen(cmd, shell=False)
    process = subprocess.Popen(cmd, shell=False)
    process.wait()
    cmd = 'mogrify -monitor '
    if size:
        cmd += '-geometry %s ' % size
    if format:
        cmd += '-format %s ' % format
    cmd_parts = cmd.strip().split(' ')
    cmd = cmd_parts + files
    log.info('Running command %r', ' '.join(cmd))
    process = subprocess.Popen(cmd, shell=False)
    return process.wait()

command_handler_factories = {

    'create'   : makeHandler(handle_command_create),
    'list'     : makeHandler(handle_command_list), 
    'get'      : makeHandler(handle_command_get), 
    'set'      : makeHandler(handle_command_set), 
    'convert'  : makeHandler(handle_command_convert), 
    'move'     : makeHandler(handle_command_move), 
    'update'   : makeHandler(handle_command_update), 
    'deploy'   : makeHandler(handle_command_deploy), 
    'sitemap'  : makeHandler(handle_command_sitemap), 
    'broken'   : makeHandler(handle_command_broken), 
    'orphan'   : makeHandler(handle_command_orphan), 
    'export'   : makeHandler(handle_command_export), 
    'redirect' : makeHandler(handle_command_redirect), 
    'resize'   : makeHandler(handle_command_resize), 
    'thumb'    : makeHandler(handle_command_thumb),
    'metadata' : makeHandler(handle_command_metadata),
    'gallery'  : makeHandler(handle_command_gallery),
}

#
# Option Sets
#

option_sets = {
    'relative': [
        dict(
            type = 'command',
            long = ['--relative'],
            short = [],
        ),
    ],
    'exclude_from': [
        dict(
            type = 'command',
            long = ['--exclude-from'],
            short = [],
            metavar = 'EXCLUDE_FROM',
        ),
    ],
    'video_overlay_file': [
        dict(
            type = 'command',
            long = ['--video-overlay-file'],
            short = ['-y'],
            metavar = 'OVERLAY_FILE',
        ),
    ],
    'gallery_thumb': [
        dict(
            type = 'command',
            long = ['--gallery-thumb'],
            short = [],
        ),
    ],
    'gallery_reduced': [
        dict(
            type = 'command',
            long = ['--gallery-reduced'],
            short = [],
        ),
    ],
    'gallery_exif': [
        dict(
            type = 'command',
            long = ['--gallery-exif'],
            short = [],
        ),
    ],
    'gallery_h264': [
        dict(
            type = 'command',
            long = ['--gallery-h264'],
            short = [],
        ),
    ],
    'gallery_meta': [
        dict(
            type = 'command',
            long = ['--gallery-meta'],
            short = [],
        ),
    ],
    'gallery_still': [
        dict(
            type = 'command',
            long = ['--gallery-still'],
            short = [],
        ),
    ],
    'mode': [
        dict(
            type = 'command',
            long = ['--mode'],
            short = ['-m'],
            metavar = 'MODE',
        ),
    ],
    'database': [
        dict(
            type = 'command',
            long = ['--database'],
            short = ['-B'],
            metavar = 'DATABASE',
        ),
    ],
    'port': [
        dict(
            type = 'command',
            long = ['--port'],
            short = ['-p'],
            metavar = 'PORT',
        ),
    ],
    'host': [
        dict(
            type = 'command',
            long = ['--host'],
            short = ['-h'],
            metavar = 'HOST',
        ),
    ],
    'username': [
        dict(
            type = 'command',
            long = ['--username, --user'],
            short = ['-U'],
            metavar = 'USERNAME',
        ),
    ],
    'password': [
        dict(
            type = 'command',
            long = ['--password'],
            short = ['-w'],
            metavar = 'PASSWORD',
        ),
    ],
    'base_url': [
        dict(
            type = 'command',
            long = ['--base-url'],
            short = ['-b'],
            metavar = 'BASE_URL',
        ),
    ],
    'update_templates': [
        dict(
            type = 'command',
            long = ['--templates'],
            short = ['-T'],
        ),
    ],
    'update_context_items': [
        dict(
            type = 'command',
            long = ['--context-items'],
            short = ['-C'],
        ),
    ],
    'update_dynamic_items': [
        dict(
            type = 'command',
            long = ['--dynamic-items'],
            short = ['-D'],
        ),
    ],
    'update_static_items': [
        dict(
            type = 'command',
            long = ['--library-items'],
            short = ['-L'],
        ),
    ],
    'force': [
        dict(
            type = 'command',
            long = ['--force'],
            short = ['-f'],
        ),
    ],
    'recursive': [
        dict(
            type = 'command',
            long = ['--recursive'],
            short = ['-r'],
        ),
    ],
    'generated_files': [
        dict(
            type = 'command',
            long = ['--generated-files'],
            short = ['-g'],
        ),
    ],
    'user_files': [
        dict(
            type = 'command',
            long = ['--user-files'],
            short = ['-u'],
        ),
    ],
    'start_path': [
        dict(
            type = 'command',
            long = ['--start-path'],
            short = ['-S'],
            metavar = 'START_PATH',
        ),
    ],
    'delete': [
        dict(
            type = 'command',
            long = ['--delete'],
            short = [],
        ),
    ],
    'dry_run': [
        dict(
            type = 'command',
            long = ['--dry-run'],
            short = ['-n'],
        ),
    ],
    'remote_scp': [
        dict(
            type = 'command',
            long = ['--remote-scp'],
            short = ['-d'],
            metavar = 'REMOTE_SCP',
        ),
    ],
    'format': [
        dict(
            type = 'command',
            long = ['--format'],
            short = ['-F'],
            metavar = 'FORMAT',
        ),
    ],
    'output': [
        dict(
            type = 'command',
            long = ['--output'],
            short = ['-o'],
            metavar = 'OUTPUT',
        ),
    ],
    'size': [
        dict(
            type = 'command',
            long = ['--size'],
            short = ['-z'],
            metavar = 'SIZE',
        ),
    ],
    'content': [
        dict(
            type = 'command',
            long = ['--new-content'],
            short = ['-e'],
            metavar = 'CONTENT',
        ),
    ],
    'interactive': [
        dict(
            type = 'command',
            long = ['--interactive'],
            short = ['-i'],
        ),
    ],
    'area': [
        dict(
            type = 'command',
            long = ['--area'],
            short = ['-a'],
            metavar = 'AREA',
        ),
    ],
    'template': [
        dict(
            type = 'command',
            long = ['--template'],
            short = ['-t'],
            metavar = 'TEMPLATE',
        ),
    ],
    'update_other_links': [
        dict(
            type = 'command',
            long = ['--links'],
            short = ['-l'],
        ),
    ],
    'site_root': [
        dict(
            type = 'command',
            long = ['--site-root'],
            short = ['-s'],
            metavar = 'SITE_ROOT',
        ),
    ],
    'config': [
        dict(
            type = 'command',
            long = ['--config'],
            short = ['-c'],
            metavar = 'CONFIG',
        ),
    ],
    'help': [
        dict(
            type = 'shared',
            long = ['--help'],
            short = [],
        ),
    ],
    'version': [
        dict(
            type = 'program',
            long = ['--version'],
            short = [],
        ),
    ],
    'verbose': [
        dict(
            type = 'program',
            long = ['--verbose'],
            short = ['-v'],
        ),
        dict(
            type = 'program',
            long = ['--quiet'],
            short = ['-q'],
        ),
    ]
}

#
# Aliases
#

aliases = {
    'create'   : ('cr',), 
    'list'     : ('ls',), 
    'get'      : []     , 
    'set'      : []     , 
    'convert'  : ('cv',), 
    'move'     : ('mv',), 
    'update'   : ('ud',), 
    'deploy'   : ('dp',), 
    'sitemap'  : ('sm',), 
    'broken'   : ('br',), 
    'orphan'   : ('or',), 
    'export'   : ('ex',), 
    'redirect' : ('rd',), 
    'resize'   : ('rz',), 
    'thumb'    : ('gt',),
    'metadata' : ('gm',),
    'gallery'  : ('gc',),
}


program_help = """\
    usage: ``%(program)s [PROGRAM_OPTS] COMMAND [OPTIONS] ARGS``

    PROGRAM_OPTS (available to all commands):

      -q, --quiet           don't show info messages
      -v, --verbose         show debug messages as well as usual output
      --help                show this help message and exit
      --version             show program's version number and exit

    COMMAND (alias):
 
    Pages:
      :create   (cr):  create page from a template
      :list     (ls):  list page or template regions and properties
      :get:            display contents of page or template region or property
      :set:            set page or template region or property
      :update   (ud):  update template, context, dynamic and static library items

    Site:
      :convert  (cv):  convert source file(s) to HTML using available plugins
      :deploy   (dp):  upload local changes to remote site
      :move     (mv):  move or rename page or section
      :sitemap  (sm):  scan site and build sitemap
      :broken   (br):  find broken links
      :orphans  (or):  find orphaned files
      :resize:         resize thumbnails and create a .rst file

    Wordpress:
      :export   (ex):  export from another system to a static file
      :redirect (rd):  generate Apache .htaccess with required redirects

    Gallery:
      :resize   (rz): Create thumbnails for images and pre-popualte a .rst file
      :thumb    (gt):  convert pictures and videos to web format
      :metadata (gm):  extract metadata from CSV files
      :gallery  (gc):  create galleries automatically from folders of thumbs

    Config Options (can be specifed in an HTML file):

      :``SITE_ROOT``:  the local path of the site root directory
      :``REMOTE_SCP``: the remote directory path in the format understood by ``scp``

    Try \`%(program)s COMMAND --help' for help on a specific command.
"""

if __name__ == '__main__':
    program_options, command_options, command, args = parse_command_line(
        option_sets,
        aliases,
    )
    try:
        program_name = os.path.split(sys.argv[0])[1]
        handle_program(
            command_handler_factories=command_handler_factories,
            option_sets=option_sets,
            aliases=aliases,
            program_options=program_options,
            command_options=command_options,
            command=command,
            args=args,
            program_name=program_name,
            help=help,
        )
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        if command:
            print "Try `%(program)s %(command)s --help' for more information." % {
                'program': os.path.split(sys.argv[0])[1],
                'command': command,
            }
        else:
            print "Try `%(program)s --help' for more information." % {
                'program': os.path.split(sys.argv[0])[1],
            }
        sys.exit(2)

#def handle_program(
#    command_handlers, 
#    option_sets, 
#    aliases, 
#    program_options, 
#    command_options, 
#    command, 
#    args
#):
#
#    # First, are they asking for program help?
#    if program_options.has_key('help'):
#        # if so provide it no matter what other options are given
#        print strip_docstring(
#            getattr(help, '__program__') % {
#                'program': os.path.split(sys.argv[0])[1],
#            }
#        )
#        sys.exit(0)
#    else:
#        if not command:
#            raise getopt.GetoptError("No command specified.")
#        # Are they asking for command help:
#        if command_options.has_key('help'):
#            # if so provide it no matter what other options are given
#            if not command_handlers.has_key(command):
#                raise getopt.GetoptError('No such command %r'%command)
#            print strip_docstring(
#                getattr(help, command) % {
#                    'program': os.path.split(sys.argv[0])[1],
#                }
#            )
#            sys.exit(0)
#        format="%(levelname)s: %(message)s"
#        if program_options.has_key('verbose'):
#            verbose_options = []
#            for option in program_options['verbose']:
#                verbose_options.append(option['name'])
#            verbose_option_names = option_names_from_option_list(
#                [option_sets['verbose'][0]]
#            )
#            quiet_option_names = option_names_from_option_list(
#                [option_sets['verbose'][1]]
#            )
#            if len(verbose_options) > 1:
#                raise getopt.GetoptError(
#                    "Only specify one of %s"%(
#                        ', '.join(verbose_options)
#                    )
#                )
#            elif verbose_options[0] in quiet_option_names:
#                logging.basicConfig(level=logging.ERROR, format=format)
#            elif verbose_options[0] in verbose_option_names:
#                logging.basicConfig(level=logging.DEBUG, format=format)
#        else:
#            logging.basicConfig(level=logging.INFO, format=format)
#        # Now handle the command options and arguments
#        command_handlers[command](
#            option_sets, 
#            command_options, 
#            args,
#        )
#
#if __name__ == '__main__':
#    try:
#        command = None
#        prog_opts, command_opts, command, args = parse_command_line(
#            option_sets, 
#            aliases, 
#        )
#        handle_program(
#            command_handlers, 
#            option_sets, 
#            aliases, 
#            prog_opts, 
#            command_opts, 
#            command, 
#            args
#        )
#    except getopt.GetoptError, err:
#        # print help information and exit:
#        print str(err) 
#        if command:
#            print "Try `%(program)s %(command)s --help' for more information." % {
#                'program': os.path.split(sys.argv[0])[1],
#                'command': command,
#            }
#        else:
#            print "Try `%(program)s --help' for more information." % {
#                'program': os.path.split(sys.argv[0])[1],
#            }
#        sys.exit(2)
#
