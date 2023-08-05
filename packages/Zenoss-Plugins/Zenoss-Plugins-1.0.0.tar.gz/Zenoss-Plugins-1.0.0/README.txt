The zenoss plugins collect information about a computer's CPU, memory,
disk, io, or process activity and reports it in name-value pair
format.  These name-value pairs can be graphed in the Zenoss web
application.

The zenoss plugins are platform specific, and certain platforms offer
plugins that are not implemented on other platforms.  The following
command can be used to determine the list of supported plugins on the
detected platform:

  # list the plugins that are defined on the detected platform
  $ zenplugin.py --list-plugins

  platform 'darwin' supports the following plugins:
    mem
    process
    disk

The --report-platform option can be used to print out the platform
that has been detected.  It is used as follows:

  # report the detected platform
  $ zenplugin.py --detect-platform

  darwin


Some plugins require additional command line arguments in order to
function.  An example of this requirement is the disk monitor.  The
disk monitor plugin must be passed an argument that defines which
filesystem should be reported on.  Plugin arguments are provided
immediately after the plugin name, as illustrated below:

  # report the disk utilization for /var
  $ zenplugin.py disk /var

  DISK OK;|availBlocks=14251580 usedBlocks=63512052 totalBlocks=78019632 


Other plugins may require keyword provided arguments in order to
function.  None of the plugins currently require it, but in the future
they may honor keyword arguments as follows:

  # report the disk utilization for /var
  $ zenplugin.py disk /var --debug=10



