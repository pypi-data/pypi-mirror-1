import commands
import logging
import optparse
import os
import shutil
import sys
import tempfile


logger = logging.getLogger('maker')


class SdistCreationError(Exception):
    pass


def output(cmd):
    status, out = commands.getstatusoutput(cmd)
    if status is not 0:
        logger.error("Something went wrong:")
        logger.error(out)
        raise SdistCreationError()
    return out


def make_sdist(tag=None, destination=None, python=None):
    destination = os.path.abspath(destination)
    tempdir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    if python is None:
        python = sys.executable
    setup = python + ' setup.py '

    cmd = 'svn co %s %s' % (tag, tempdir)
    logger.debug("Doing checkout of %s", tag)
    output(cmd)
    os.chdir(tempdir)

    logger.debug("Detecting name and version..")
    cmd = setup + '--name'
    name = output(cmd).strip()
    logger.debug("Name: %s", name)
    cmd = setup + '--version'
    version = output(cmd).strip()
    logger.debug("Version: %s", version)

    logger.debug("Making sdist tarball...")
    cmd = setup + 'sdist'
    logger.debug(output(cmd))

    targetdir = os.path.join(destination, name)
    if not name in os.listdir(destination):
        logger.info("Creating directory %s", targetdir)
        os.mkdir(targetdir)

    tarball = name + '-' + version + '.tar.gz'
    target_filename = os.path.join(targetdir, tarball)
    logger.debug("Copying tarball to %s", target_filename)
    shutil.copy(os.path.join('dist', tarball),
                target_filename)
    os.chdir(original_dir)
    shutil.rmtree(tempdir)
    return target_filename


def main(tag=None, destination=None):
    """bin/make_sdist: create an sdist for a single tag"""
    usage = "Usage: %prog TAG DESTINATION"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Show debug output")
    parser.add_option("-q", "--quiet",
                      action="store_true", dest="quiet", default=False,
                      help="Show minimal output")
    (options, args) = parser.parse_args()

    if options.verbose:
        log_level = logging.DEBUG
    elif options.quiet:
        log_level = logging.WARN
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level,
                        format="%(levelname)s: %(message)s")

    if tag is None:
        if len(args) == 0:
            logger.warn("Tag not specified")
            parser.print_help()
            sys.exit(1)
        tag = args.pop(0)
    if destination is None:
        if len(args) == 0:
            logger.warn("Destination not specified")
            parser.print_help()
            sys.exit(1)
        destination = args.pop()

    buildout_bindir = os.path.dirname(
        os.path.abspath(sys.argv[0]))
    python = os.path.join(buildout_bindir, 'python')
    if not os.path.exists(python):
        python = None

    filename = make_sdist(tag, destination, python)
    logger.info("Created %s", filename)
