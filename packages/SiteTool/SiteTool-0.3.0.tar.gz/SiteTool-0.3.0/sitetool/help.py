redirect="""usage: %(program)s redirect [OPTIONS]...

update (ex): Generate Apache .htaccess with required redirects

Scan for files which may have come from elsewhere and require redirects to
their current positions. If -S is specified only the files under that
directory are scanned, otherwise all files in the site are scanned.

Caution:

  Currently adds the redirects even if files at that location already
  exist.

Options:

         -b, --base-url=BASE_URL
               path to the site root directory
         -S, --start-path=START_PATH
               the path to start the search at

        Plus all program options... (see `%(program)s --help')

Typical use to export wordpress to reStructuredText:

  %(program)s redirect -c about.html -b http://jimmyg.org -S blog
"""

convert="""     usage: %(program)s convert [OPTIONS]... [PLUGIN_OPTIONS]...

     convert (cv): Convert a source file to HTML using all available plugins

     If -S is specified only the files under that directory are scanned, in
     which case the -s option is not required. If START_PATH is a file, only
     that file is converted, if it is a directory all files in that directory
     are converted. If -r is specified, or -S is not specified the search is
     recursive and all child directories are converted. If -f is specified,
     files are re-created even if they appear up to date.

     The -c option is always required because it contains information about
     which plugins should be used to convert which sections and the templates
     to use. See [1]http://jimmyg.org/blog/2009/site-tool for more
     information.

     Caution:

       You shouldn't usually try to convert a sub-directoy of a blog
       directory if you want the indexes to be re-generated, instead convert
       the whole directory.

     Options:

        -c, --config=CONFIG
                     path to the config file
        -s, --site-root=SITE_ROOT
                     path to the site root directory
        -S, --start-path=START_PATH
                     the path to start the search at
        -g, --generated-files
                     create generated files and index pages
        -u, --user-files
                     convert user-created files
        -r, --recursive
                     recursivley convert all files under that directory
        -f, --force  force convertion of all files, even if HTML versions
                     already exist
        -C, --context-items
                     reapply context library items to newly converted and
                     existing pages

       Plus all program options... (see `%(program)s --help')

     Plugin options:

        -t, --template=TEMPLATE
             the template to use for the plain rst plugin

     Typical use to re-convert an entire section and then reapply context
     items to both newly convert and existing items:

       %(program)s convert -c about.html -ugrfC -S blog

References

   Visible links
   1. http://jimmyg.org/blog/2009/site-tool
"""

set="""usage: %(program)s set [OPTIONS]... [PAGE|TEMPLATE]

set: Set a page region or property

If neither the -i nor -n options are used the value to update the page
with is read from STDIN.

Arguments:

   PAGE:      the path of the page to update
   TEMPLATE:  the path of the template

Options:

   -a, --area=AREA
      name of the page region or property to fetch
   -e, --new-content=CONTENT
      the value to update the content with
   -i, --interactive
      load the current value of the region in the editor specified by the
      EDITOR environment variable and update the saved contents of the
      page when the editor exits

  Plus all program options... (see `%(program)s --help')

Typical use for interactive editing:

  %(program)s set -i -a doctitle page.html
"""

thumb="""usage: %(program)s [PROGRAM_OPTIONS] thumb SOURCE DEST

Recursively convert all the pictures and videos in SOURCE into a directory
structure in DEST

Arguments:

   SOURCE:  The source directory for the images and videos
   DEST:    An empty directory which will be populated with a converted
            data structure

Options:

         -t, --thumbnail-size=THUMBNAIL_SIZE
            The width in pixels of the thumbnails
         -o, --video-overlay-file=OVERLAY_FILE
            A transparent PNG file the same size as the thumbnails to
            overlay on video thumbnails to distinguish them from picture
            thumbnails

        All PROGRAM_OPTIONS (see `%(program)s --help')
"""

get="""usage: %(program)s get [OPTIONS]... [PAGE|TEMPLATE]

get: Display the contents of a page or template region or property

Arguments:

   PAGE:      the path of the page
   TEMPLATE:  the path of the template

Options:

   -a, --area=AREA
      name of the page region or property to fetch

  Plus all program options... (see `%(program)s --help')

Typical use:

  %(program)s get -a doctitle page.html
"""

orphan="""usage: %(program)s orphan [OPTIONS]...

orphan (or): Find ophaned files

Scans the entire site for files which are not linked from other files in
the site.

Options:

   -c, --config=CONFIG
               path to the config file
   -s, --site-root=SITE_ROOT
               path to the site root directory
   --relative  make paths relative to the current dir

  Plus all program options... (see `%(program)s --help')

Typical use:

  %(program)s orphan -s static | grep "\.html"
"""

create="""usage: %(program)s create [OPTION]... TEMPLATE PAGE

create (cr): Create a new page

Arguments:

   PAGE:      path of page to create
   TEMPLATE:  the full path of the template to use

Options:

  All program options... (see `%(program)s --help')

Typical use:

  %(program)s create Templates/jimmyg.dwt new.html
"""

move="""usage: %(program)s move [OPTIONS]... SOURCE DEST

move (mv): Move a page or section

Arguments:

   SOURCE:  path of the page or directory to move
   DEST:    path of directory to move to

Options:

   -c, --config=CONFIG
                path to the config file
   -s, --site-root=SITE_ROOT
                path to the site root directory
   -l, --links  update links sitewide to the moved page(s)
   -C, --context-items
                update context items in the moved page(s)

  Plus all program options... (see `%(program)s --help')

Typical use:

  %(program)s move -Clc about.html src/page.html dst
"""

list="""usage: %(program)s list [OPTIONS]... [PAGE|TEMPLATE]

list (ls): List the regions and properties contained in a page or template

Arguments:

   PAGE:      the path of the page
   TEMPLATE:  the path of the template

Options:

  All program options... (see `%(program)s --help')

Typical use:

  %(program)s list page.html
"""

update="""usage: %(program)s update [OPTIONS]...

update (ud): Convert a source file to HTML using all available plugins

If -S is specified only the files under that directory are scanned. If
START_PATH is a file, only that file is updated, if it is a directory all
files in that directory are converted. If -r is specified, or -S is not
specified the search is recursive and all child directories are updated.

The -T, -C, -D and -L options specify what to update in any pages which
are found.

Options:

   -c, --config=CONFIG
          path to the config file
   -s, --site-root=SITE_ROOT
          path to the site root directory
   -S, --start-path=START_PATH
          the path to start the search at
   -r, --recursive
          recursivley convert all files under directory
   -T, --templates
          reapply the templates
   -C, --context-items
          reapply context library items
   -D, --dynamic-items
          reapply dynamic library items
   -L, --static-items
          reapply static library items

  Plus all program options... (see `%(program)s --help')

Typical use to udpdate an entire section:
        %(program)s update -c about.html -rTCDL -S blog/
"""

broken="""usage: %(program)s broken [OPTIONS]...

broken (br): Find broken links

Scans the entire site for broken links. If -S is specified only the files
under that directory are scanned, in which case the -c and -s options are
not required. If START_PATH is a file, only that file is converted, if it
is a directory all files in that directory are converted. If -r is
specified, or -S is not specified the search is recursive and all child
directories are scanned.

Options:

   -c, --config=CONFIG
         path to the config file
   -s, --site-root=SITE_ROOT
         path to the site root directory

  Plus all program options... (see `%(program)s --help')

Typical use:

  %(program)s broken -S blog/
"""

export="""usage: %(program)s export [OPTIONS]... [MYSQL_OPTIONS] DEST

update (ex): Export from another system to static files

Specify the export mode with -m. Currently only `wordpress-rst' is
supported.

Arguments:

   DEST:  directory to export the files to

Options:

   -c, --config=CONFIG
       path to the config file
   -s, --site-root=SITE_ROOT
       path to the site root directory
   -m, --mode=MODE
       export mode (only `wordpress-rst' supported)

  Plus all program options... (see `%(program)s --help')

MySQL Options:

   -B, --database=DATABASE
        MySQL database to export
   -h, --host=HOST
        host or IP address of the server
   -p, --port=PORT
        the port of the MySQL server
   -U, --username=USERNAME
        the username to use to connect
   -w, --password=PASSWORD
        specify password on the command line. Hint: more secure to use -i
   -i, --interactive
        prompt for a password

Typical use to export wordpress to reStructuredText:

  %(program)s export -m wordpress-rst -h db.example.com -B wp -U user -i blog/
"""

resize="""usage: %(program)s resize [OPTIONS]... -z 800x600 -F png -o test.rst FILES...

resize (rz): Create thumbnails for images and pre-popualte a .rst file

Arguments:

   FILES:  A list of files to convert

WARNING: If the output format is the same as the input format your input
files will be overwritten.

Options:

   -z, --size=SIZE
       the size for the thumbnails
   -F, --format=FORMAT
       the output format for the thumbnails
   -o, --output=OUTPUT
       the filename to contain the optional rst source

  Plus all program options... (see `%(program)s --help')

Typical use to export wordpress to reStructuredText:

  %(program)s resize -z 800x600 -F png -o holiday.rst holiday/*.JPG
"""

deploy="""usage: %(program)s deploy [OPTIONS]...

deploy (dp): Upload any local changes to the remote site

Either a config file containing SITE_ROOT and REMOTE_SCP must be specified
or the -s and -d options must be used. Internally the command uses `rsync'
but does not delete files on the remote server unless --delete is
specified.

Options:

   -c, --config=CONFIG
                  path to the config file
   -s, --site-root=SITE_ROOT
                  path to the site root directory
   -d, --remote-scp=REMOTE_SCP
                  remote directory in the format expected by the `scp'
                  program
   --delete       delete files on the remote server which aren't present
                  on the local server
   -n, --dry-run  show the changes to be made but don't make them
   --exclude-from=EXCLUDE_FROM
                  a file listing all the files not to deploy

  Plus all program options... (see `%(program)s --help')

Typical use:

  %(program)s deploy -s ./ -d user@server.example.com:path/to/site
"""

gallery="""usage: %(program)s [PROGRAM_OPTIONS] gallery SOURCE DEST

Automatically build galleries based on the file strucutre of the meta
directory specified as SOURCE and put them in DEST.

The order of files is a gallery is determined by stripping all characters
which aren't numbers from the filename and then numbering the files in
order

Arguments:

   SOURCE:  The meta sub-directory of the converted directory structure
   DEST:    An empty directory within which the galleries will be placed

  All PROGRAM_OPTIONS (see `%(program)s --help')
"""

sitemap="""   usage: %(program)s sitemap [OPTIONS]... SITEMAP

   sitemap (sm): Scan the site and rebuild a sitemap

   Arguments:

      SITEMAP:  path of the file to create

   Options:

      -c, --config=CONFIG
         path to the config file
      -s, --site-root=SITE_ROOT
         path to the site root directory
      -F, --format=FORMAT
         format for the sitemap, can be `html' for a human readable sitemap
         or `xml' for a search engine comaptible sitemap (see
         [1]http://sitemaps.org)
      -t, --template=TEMPLATE
         the template to use for the sitemap

     Plus all program options... (see `%(program)s --help')

   Typical use:

     %(program)s sitemap -c about.html sitemap.html

References

   Visible links
   1. http://sitemaps.org/
"""

metadata="""usage: %(program)s [PROGRAM_OPTIONS] metadata SOURCE DEST

Generate a gallery (-F gallery) or photo metadata file (-F photo) from a
CSV file.

If generating a gallery the file can conatin multiple columns but must
contain the following:

Path
        The name to use for the gallery

Title
        The title of the gallery

Description
        A description of the gallery

Index
        The relative path from the root to a thumbnail to represent the
        gallery

If generating a gallery the file can conatin multiple columns but must
contain the following:

In either case the first line in the CSV file will be treated as the
column headings. Any extra columns will be added to the gallery file and
displayed in the HTML version.

Arguments:

   SOURCE:  The path to the CSV file
   DEST:    The path to the gallery or photo metadata folder to contain
            the output from this command.

Options:

         -F, --format=FORMAT
              The type of CSV file we are using, photo or gallery

        All PROGRAM_OPTIONS (see `%(program)s --help')
"""

__program__="""usage: %(program)s [PROGRAM_OPTS] COMMAND [OPTIONS] ARGS

PROGRAM_OPTS (available to all commands):

   -q, --quiet    don't show info messages
   -v, --verbose  show debug messages as well as usual output
   --help         show this help message and exit
   --version      show program's version number and exit

COMMAND (alias):

Pages:

         create (cr):  create page from a template
         list (ls):    list page or template regions and properties
         get:          display contents of page or template region or
                       property
         set:          set page or template region or property
         update (ud):  update template, context, dynamic and static
                       library items

Site:

         convert (cv):  convert source file(s) to HTML using available
                        plugins
         deploy (dp):   upload local changes to remote site
         move (mv):     move or rename page or section
         sitemap (sm):  scan site and build sitemap
         broken (br):   find broken links
         orphans (or):  find orphaned files

Wordpress:

         export (ex):    export from another system to a static file
         redirect (rd):  generate Apache .htaccess with required
                         redirects

Gallery:

         resize (rz):    Create thumbnails for images and pre-popualte a .rst 
                         file
         thumb (gt):     convert pictures and videos to web format
         metadata (gm):  extract metadata from CSV files
         gallery (gc):   create galleries automatically from folders of
                         thumbs

Config Options (can be specifed in an HTML file):

   SITE_ROOT:   the local path of the site root directory
   REMOTE_SCP:  the remote directory path in the format understood by scp

Try `%(program)s COMMAND --help' for help on a specific command.
"""

