import commands
import logging
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
    print "Doing checkout of", tag
    output(cmd)
    os.chdir(tempdir)

    print "Detecting name and version"
    cmd = setup + '--name'
    name = output(cmd).strip()
    print "Name:", name
    cmd = setup + '--version'
    version = output(cmd).strip()
    print "Version:", version

    print "Making sdist tarball"
    cmd = setup + 'sdist'
    logger.debug(output(cmd))

    targetdir = os.path.join(destination, name)
    if not name in os.listdir(destination):
        print "Creating directory", targetdir
        os.mkdir(targetdir)

    tarball = name + '-' + version + '.tar.gz'
    print "Copying tarball", tarball
    shutil.copy(os.path.join('dist', tarball),
                os.path.join(targetdir, tarball))
    os.chdir(original_dir)
    shutil.rmtree(tempdir)


def main(tag=None, destination=None):
    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s: %(message)s")
    usage = 'make_sdist [tag [destination]]'
    args = sys.argv[1:]
    if tag is None:
        if len(args) == 0:
            print usage
            sys.exit(1)
        tag = args.pop(0)
    if destination is None:
        if len(args) == 0:
            print usage
            sys.exit(1)
        destination = args.pop()

    buildout_bindir = os.path.dirname(
        os.path.abspath(sys.argv[0]))
    python = os.path.join(buildout_bindir, 'python')
    if not os.path.exists(python):
        python = None

    make_sdist(tag, destination, python)
