"""Base class and handlers for convert plugins"""

import logging

log = logging.getLogger(__name__)

class Plugin(object):
    """\
    Base class for plugins which handle files in a specific way.

    In the config file, individual folders can have a specific plugin
    order specified. All directories are implied to have the 
    ``default`` last. Here's an example:
    
        /blog: blog, graphic

    This would specify that for the ``/blog`` directory and any files or
    folders after it, the ``blog`` plugin should get the first attempt to convert
    the file followed by the ``graphic`` plugin and then, if neither of them can
    convert the file, the ``default`` plugin is used.

    It is up to each plugin to decide what the user_files, all and generated_files options mean in the context of that plugin.

    """
    def __init__(self, config, force, user_files, generated_files, site_root):
        self.user_files = user_files
        self.generated_files = generated_files
        self.site_root = site_root
        self.force = force
        # This should come last in case the plugin needs the earlier information   
        self.config = self.parse_config(config)

    def parse_config(self, config):
        return None
 
    def on_enter_directory(self, directory):
        """\
        Triggered when the convert command enters a directory

        Can return ``True`` or ``False``. 

        ``True``
            the plugin handles everything from here on in for this directory,
            so the convert command doesn't need to do any more work
        
        ``False``
            the convert command still has responsibility for this directory

	Even if ``False`` is returned the plugin can still handle individual
        files by responding to ``on_file`` events for files in this directory or by
        responding to ``on_leave_directory()`` events. 

        """
        return False

    def on_leave_directory(self, directory):
        """\
        Triggered when the converter leaves a directory, the return value is not currently used.
        """
        return False

    def on_file(self, filename):
        """\
	IMPORTANT: You should not change the ``page`` or ``template`` arguments
        if they are present and you should be prepared to create them if they aren't.

	Returns a tuple, the first item of which can be ``True`` or ``False``
        with the following meanings: 

        ``True``
            the plugin handled the file and it is now converted.
        
        ``False``
            the convert command still has responsibility for converting this file

	The second and third arguments should be the page and template
        instances if they were present or you created them.
        """
        return False

def handle_directory_enter(directory, plugins):
    log.debug('Handling enter %r', directory)
    found = False
    for plugin in plugins:
        handled = plugin.on_enter_directory(directory)
        if handled:
            return True
    return False

def handle_directory_leave(directory, plugins):
    log.debug('Handling leave %r', directory)
    found = False
    for plugin in plugins:
        handled = plugin.on_leave_directory(directory)
        if handled:
            return True
    return False

def handle_file(path, plugins):
    log.debug('Handling file %r', path)
    found = False
    for plugin in plugins:
        stop = plugin.on_file(path)
        if stop:
            found = True
            break
    if not found:
        log.debug('No plugin found to handle file %r'%path)

