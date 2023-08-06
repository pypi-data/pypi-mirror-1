# Defaults for tha.taglist.
# You can override it from your buildout by providing a similar file
# yourself and passing it along to tha.taglist's main() method.
# Similarly, you can pass along a specific outfile (handy if you want
# something relative to your buildout directory).
#
# [buildout]
# parts = taglist
#
# [taglist]
# recipe = zc.recipe.egg
# eggs = tha.taglist
# scripts = taglist
# arguments =
#     defaults_file='${buildout:directory}/defaults.py',
#     specific_outfile='${buildout:directory}/www/index.html'


# Svn url where to start searching for tag directories.
BASE = 'https://svn.plone.org/svn/collective/zest.releaser'

# On the server, a file:///.... url is way quicker. BASE is a fallback
# in case this isn't specified or if the file:/// url doesn't work.
BASE_ON_SERVER = ''

# Don't recurse into directories named like this:
BLACKLIST = [
    '.svn',
    '.attic',
    ]

# If you see these, there won't be a usable tag deeper down, so just
# stop looking in this directory.
STOP_INDICATORS = [
    #'src',
    #'setup.py',
    #'version.txt',
    #'buildout.cfg',
    ]

# Name of the output file. Used if you don't pass along a specific one
# to the main() method.
# Absolute paths stay absolute, relative paths are relative to the
# current working directory.
OUTFILE = 'generated.html'

