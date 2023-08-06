"""Makes sdists from tags.

A short hint on how it works is in the README.txt.
"""
import commands
import imp
import logging
import os
import sys

from tha.tagfinder import extracter
from tha.tagfinder import finder
from tha.tagfinder import lister

from tha.sdistmaker import maker

# We import our own defaults, these can be overridden.
from tha.sdistmaker.defaults import BASE
from tha.sdistmaker.defaults import BASE_ON_SERVER
from tha.sdistmaker.defaults import BLACKLIST
from tha.sdistmaker.defaults import STOP_INDICATORS
from tha.sdistmaker.defaults import OUTDIR

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
    """Main method, called by bin/sdists_from_tags

    Start with -v to get INFO level logging, -vv for DEBUG level
    logging.

    """
    level = logging.WARN
    if '-v' in sys.argv[1:]:
        level = logging.INFO
    if '-vv' in sys.argv[1:]:
        level = logging.DEBUG
    logging.basicConfig(level=level,
                        format="%(levelname)s: %(message)s")
    if defaults_file:
        override_global_constants(defaults_file)

    start = BASE
    rewrite_for_base = False
    if BASE_ON_SERVER:
        output = commands.getoutput("svn list %s" % BASE_ON_SERVER)
        if not 'Unable' in output:
            start = BASE_ON_SERVER
            rewrite_for_base = True
    startpoint = lister.SvnLister(start, ignore=BLACKLIST)
    info_extracter = extracter.BaseExtracter
    destination = os.path.abspath(OUTDIR)

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
