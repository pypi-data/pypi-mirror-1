"""Exports list of tags suitable for find-links.

A short hint on how it works is in the README.txt.
"""
from datetime import datetime
from distutils.version import LooseVersion
from tempfile import mkstemp
import imp
import logging
import os
import re
import sys
import shutil

import py

# We import our own defaults, these can be overridden.
from tha.taglist.defaults import BASE
from tha.taglist.defaults import BASE_ON_SERVER
from tha.taglist.defaults import BLACKLIST
from tha.taglist.defaults import STOP_INDICATORS
from tha.taglist.defaults import OUTFILE
from tha.taglist.defaults import HTMLSTART
from tha.taglist.defaults import HTMLEND
from tha.taglist.defaults import ENTRY

DEFAULTS = ['BASE',
            'BASE_ON_SERVER',
            'BLACKLIST',
            'STOP_INDICATORS',
            'OUTFILE',
            'HTMLSTART',
            'HTMLEND',
            'ENTRY']


logger = logging.getLogger('exporter')


def find_tag_directories(start):
    """Recursively yield tag directories.

    Omit directories that are blacklisted and stop recursing once you
    see one of the stop indicator files.

    """
    logger.debug('Entering %s', start)
    tagdir = start.join('tags')
    if tagdir.check():
        yield tagdir
    else:
        contents = start.listdir()
        content_names = [content.basename for content in contents]
        for stop_indicator in STOP_INDICATORS:
            if stop_indicator in content_names:
                logger.debug("Stop indicator %s found", stop_indicator)
                return
        for item in contents:
            if item.basename in BLACKLIST:
                logger.debug("Blacklisted item: %s", item.basename)
                continue
            # Assumption: directory
            info = item.info()
            if info.kind != 'dir':
                continue
            # Recurse
            for item in find_tag_directories(item):
                yield item


def extract_name(setup_py):
    """Return name according to the setup.py"""
    pattern = re.compile(r"""
    name\W*=\W*    # 'name =  ' with possible whitespace
    [\"\']         # Opening (double) quote.
    (?P<name>.+?)  # Something, but match non-greedy, store in 'name'
    [\"\']         # Closing (double) quote.
    """, re.VERBOSE)
    for line in setup_py.readlines():
        match = pattern.search(line)
        if match:
            name = match.group('name').strip()
            logger.debug("Extracted name %r from line %r",
                         name, line)
            return name
    logger.warn("Couldn't find name in the setup.py")
    return 'Unkown name'


def check_tag(setup_py, tag, name):
    """Check whether the svn tag matches the version in setup.py.

    Versions can be grabbed from various strange places (a
    version.txt in plone projects, for instance), so if we cannot find
    anything we won't treat that as a failure.

    Note that we cannot run 'python setup.py --version' as we need a
    full checkout of the whole project for that. So we content
    ourselves with a simple regex.

    Sometimes you make tags with names like 'reinout-snapshot-2' for
    historical purposes. Those will never match with the version
    inside the setup.py and aren't intended to. So ignore them.

    """

    parsed_version = LooseVersion(tag).version
    if not isinstance(parsed_version[0], int):
        logger.debug("Tag doesn't start with a number, so we omit the "
                     "tag/version check as that'll be bogus.")
        return

    pattern = re.compile(r"""
    version\W*=\W*    # 'version =  ' with possible whitespace
    [\"\']            # Opening (double) quote.
    (?P<version>.+?)  # Something, but match non-greedy, store in 'version'
    [\"\']            # Closing (double) quote.
    """, re.VERBOSE)
    for line in setup_py.readlines():
        if 'version' in line:
            logger.debug("Line with 'version' found: %r", line)
        match = pattern.search(line)
        if match:
            version = match.group('version').strip()
            logger.debug("Extracted version %r from line %r",
                         version, line)
            if tag == version:
                logger.debug("Version in setup.py matches the tag.")
                return
            else:
                logger.warn("Tag %s doesn't match setup.py version %s "
                            "for package %s.", tag, version, name)
    logger.debug("Couldn't find name in the setup.py")


def find_tags(directory):
    """Return (tag, name, url) per subdirectory"""
    for item in directory.listdir():
        # Make sure it is a directory.
        info = item.info()
        if info.kind != 'dir':
            continue
        # Make sure there's a setup.py.
        setup_py = item.join('setup.py')
        if not setup_py.check():
            logger.warn("Tag dir without setup.py: %s", item)
            continue
        tag = item.basename
        name = extract_name(setup_py)
        check_tag(setup_py, tag, name)
        url = item.url
        if BASE_ON_SERVER:
            if url.startswith(BASE_ON_SERVER):
                url = url.replace(BASE_ON_SERVER, BASE)
        yield (tag, name, url)
        

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


def main(defaults_file=None, specific_outfile=None):
    """Main method, called by bin/taglist

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
    handle, outfile_name = mkstemp(suffix='.html', prefix='taglist')
    outfile = open(outfile_name, 'w')
    logger.debug("Writing to tempfile %s", outfile_name)
    today = datetime.now().ctime()
    outfile.write(HTMLSTART % dict(date=today))
    if BASE_ON_SERVER:
        start = py.path.svnurl(BASE_ON_SERVER)
        if not start.check():
            # Fall back to svn+ssh use.
            start = py.path.svnurl(BASE)
    else:
        start = py.path.svnurl(BASE)
    for tagsdir in find_tag_directories(start):
        for tag, name, url in find_tags(tagsdir):
            logger.info("Found tag %s for %s: %s",
                        tag, name, url)
            outfile.write(ENTRY % dict(tag=tag, name=name, url=url))
    outfile.write(HTMLEND)
    outfile.close()
    target = os.path.join(os.getcwd(), OUTFILE)
    if specific_outfile:
        # For overriding from buildout.
        target = specific_outfile
    shutil.move(outfile_name, target)
    # ^^^ os.rename fails cross-filesystem.
    # Maybe unnecessary, but on one system the resulting file wasn't
    # readable for apache when created by another user. We'll just
    # make it world readable.
    os.chmod(target, 0644)
    logger.info("Generated list written to %s", target)

