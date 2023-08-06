# Defaults for finding tags in an svn repository and creating sdist eggs out
# of it.
# You can override it from your buildout by providing a similar file
# yourself and passing it along to tha.taglist's main() method.
# Similarly, you can pass along a specific outfile (handy if you want
# something relative to your buildout directory).
#
# [buildout]
# parts = sdists
#
# [sdists]
# recipe = zc.recipe.egg
# eggs = tha.sdistmaker
# scripts = sdists_from_tags
# arguments =
#     defaults_file='${buildout:directory}/defaults.py',


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

# Name of the output "pypi directory.
OUTDIR = 'var/private'

