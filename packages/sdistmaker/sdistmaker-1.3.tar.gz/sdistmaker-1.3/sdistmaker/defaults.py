# Defaults for finding tags in an svn repository and creating sdist eggs out
# of it.
#
# You can get a print of the base defaults.py by doing
# ``sdists_from_tags --print-example_defaults``.  Save the output as a
# python file (suggestion: defaults.py).  You can then adapt it to your liking
# and use it with ``sdists_from_tags --defaults-file=defaults.py``.

# Svn url where to start searching for tag directories.
BASE = 'https://svn.plone.org/svn/collective/zest.releaser'

# If you run sdistmaker on the actual server where you host your subversion
# repository, a file:///path/to/your/svn.... url is way quicker. BASE is used
# as a fallback in case BASE_ON_SERVER isn't specified or if the file:/// url
# doesn't work.
BASE_ON_SERVER = ''

# Don't recurse into directories named like this:
BLACKLIST = [
    '.svn',
    '.attic',
    ]

# If you see these items in a directory, there won't be a usable tag deeper
# down, so just stop looking in this directory.
STOP_INDICATORS = [
    #'src',
    #'setup.py',
    #'version.txt',
    #'buildout.cfg',
    ]

# Name of the output "pypi" directory.
OUTDIR = 'var/private'
