"""Store version info separately for use in __init__.py and setup.py"""
bzr_plugin_name = 'automirror'
bzr_plugin_version = (0, 1, 0, 'final', 0)
bzr_minimum_version = (0, 15, 0)

if bzr_plugin_version[3] == 'final':
    version_string = '%d.%d.%d' % bzr_plugin_version[:3]
else:
    version_string = '%d.%d.%d%s%d' % bzr_plugin_version
__version__ = version_string
