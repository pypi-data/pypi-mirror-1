"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/__init__.py $
$Id: __init__.py 25637 2004-11-18 15:21:56Z dbinger $
"""

from dulcinea.site_util import SiteModule
local = SiteModule('local')
local_ui = SiteModule('local_ui')
del SiteModule
# local and local_ui are site-specific 'modules' that can be imported
# from dulcinea.  This allows code in dulcinea to use site-specific
# values.
# import local and local_ui from here, but do not access
# their attributes at the module level or you may have
# circular import problems.
# Don't do this:
#     from dulcinea.local import foo # Bad.
#     ...
#     foo()
# Do this:
#     from dulcinea import local # Good.
#     ...
#     local.foo()
