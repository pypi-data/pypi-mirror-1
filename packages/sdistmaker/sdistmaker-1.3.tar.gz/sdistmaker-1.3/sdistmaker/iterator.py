"""Makes sdists from tags.

A short hint on how it works is in the README.txt.
"""
import commands
import imp
import logging
import optparse
import os
import sys

from tha.tagfinder import extracter
from tha.tagfinder import finder
from tha.tagfinder import lister
import pkg_resources

from sdistmaker import maker

# We import our own defaults, these can be overridden.
from sdistmaker.defaults import BASE
from sdistmaker.defaults import BASE_ON_SERVER
from sdistmaker.defaults import BLACKLIST
from sdistmaker.defaults import STOP_INDICATORS
from sdistmaker.defaults import OUTDIR

DEFAULTS = ['BASE',
            'BASE_ON_SERVER',
            'BLACKLIST',
            'STOP_INDICATORS',
            'OUTDIR']

logger = logging.getLogger('exporter')


def override_global_constants(defaults_file):
    """Import the constants from the passed-in defaults file"""
    logger.debug("Loading defaults from %s", defaults_file)
    defaults = imp.load_source('defaults', defaults_file)
    globals_dict = globals()
    for constant in DEFAULTS:
        try:
            globals_dict[constant] = getattr(defaults, constant)
        except AttributeError:
            logger.debug("Default for %s not overridden.", constant)


def main(defaults_file=None, python=None):
    """Main method, called by bin/sdists_from_tags"""
    usage = "Usage: %prog"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Show debug output")
    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet", default=False,
                      help="Show minimal output")
    parser.add_option("-d", "--defaults-file",
                      dest="defaults_file", default=None,
                      help="File with custom defaults")
    parser.add_option("--print-example-defaults",
                      action="store_true",
                      dest="print_example_defaults", default=False,
                      help="File with custom defaults")
    (options, args) = parser.parse_args()

    if options.verbose:
        log_level = logging.DEBUG
    elif options.quiet:
        log_level = logging.WARN
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level,
                        format="%(levelname)s: %(message)s")

    if options.print_example_defaults:
        print pkg_resources.resource_string('sdistmaker', 'defaults.py')
        sys.exit(0)

    if defaults_file:
        override_global_constants(defaults_file)
        logger.debug("Loaded defaults from %s", defaults_file)
    if options.defaults_file:
        override_global_constants(options.defaults_file)
        logger.debug("Loaded defaults from %s", options.defaults_file)

    start = BASE
    rewrite_for_base = False
    if BASE_ON_SERVER:
        logger.debug(
            "Looking if the server base (%s) is usable instead of %s",
            BASE_ON_SERVER, BASE)
        output = commands.getoutput("svn list %s" % BASE_ON_SERVER)
        if not 'Unable' in output:
            start = BASE_ON_SERVER
            rewrite_for_base = True
        else:
            logger.warn("BASE_ON_SERVER (%s) is not available: %s",
                        BASE_ON_SERVER, output)
    startpoint = lister.SvnLister(start, ignore=BLACKLIST)
    info_extracter = extracter.BaseExtracter
    destination = os.path.abspath(OUTDIR)
    if not os.path.exists(destination):
        logger.warn("Destination dir %s does not exist, creating it",
                    destination)
        os.makedirs(destination)

    logger.info("Looking for tags in %s", start)
    info = finder.Finder(startpoint, info_extracter,
                         stop_indicators=STOP_INDICATORS)
    for project in info.projects:
        name = project.name
        for tag in project.tags:
            tgz = name + '-' + tag + '.tar.gz'
            tgz = os.path.join(destination, name, tgz)
            if os.path.exists(tgz):
                logger.info("%s already exists, skipping", tgz)
                continue

            url = project.tag_location(tag)
            if rewrite_for_base:
                url = url.replace(BASE, BASE_ON_SERVER)
            logger.info("Found tag %s for %s: %s",
                        tag, name, url)
            try:
                maker.make_sdist(tag=url,
                                 destination=destination,
                                 python=python)
            except maker.SdistCreationError:
                logger.error("sdist creation for %s failed", url)
