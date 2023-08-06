"""Exports list of tags suitable for find-links.

A short hint on how it works is in the README.txt.
"""
from datetime import datetime
import commands
from distutils.version import LooseVersion
from tempfile import mkstemp
import imp
import logging
import os
import shutil
import sys

from jinja2 import Environment
from jinja2 import PackageLoader

# We import our own defaults, these can be overridden.
from tha.taglist.defaults import BASE
from tha.taglist.defaults import BASE_ON_SERVER
from tha.taglist.defaults import BLACKLIST
from tha.taglist.defaults import STOP_INDICATORS
from tha.taglist.defaults import OUTFILE

from tha.tagfinder import extracter
from tha.tagfinder import finder
from tha.tagfinder import lister

DEFAULTS = ['BASE',
            'BASE_ON_SERVER',
            'BLACKLIST',
            'STOP_INDICATORS',
            'OUTFILE']


jinja_env = Environment(loader=PackageLoader('tha.taglist', 'templates'))
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


def update_latest(latest, tag, name, url):
    """Latest is a dict {package: version}"""
    new_version = LooseVersion(tag).version
    if not isinstance(new_version[0], int):
        return
    if name not in latest:
        latest[name] = tag
        return
    current_version = LooseVersion(latest[name]).version
    if new_version > current_version:
        latest[name] = tag


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
    template = jinja_env.get_template('index.html')

    today = datetime.now().ctime()

    start = BASE
    if BASE_ON_SERVER:
        output = commands.getoutput("svn list %s" % BASE_ON_SERVER)
        if not 'Unable' in output:
            start = BASE_ON_SERVER
    startpoint = lister.SvnLister(start, ignore=BLACKLIST)
    info_extracter = extracter.BaseExtracter
    latest = {}
    entries = []

    info = finder.Finder(startpoint, info_extracter,
                         stop_indicators=STOP_INDICATORS)
    for project in info.projects:
        name = project.name
        for tag in project.tags:
            url = project.tag_location(tag)
            if url.startswith(BASE_ON_SERVER):
                url = url.replace(BASE_ON_SERVER, BASE)
            logger.info("Found tag %s for %s: %s",
                        tag, name, url)
            update_latest(latest, tag, name, url)
            entries.append(dict(tag=tag, name=name, url=url))

    content = template.render(today=today,
                              entries=entries,
                              latest=latest)

    # Create tempfile
    handle, outfile_name = mkstemp(suffix='.html', prefix='taglist')
    logger.debug("Writing to tempfile %s", outfile_name)
    open(outfile_name, 'w').write(content)

    target = os.path.join(os.getcwd(), OUTFILE)
    if specific_outfile:
        # For overriding from buildout.
        target = specific_outfile

    shutil.move(outfile_name, target)
    os.chmod(target, 0644)
    logger.info("Generated list written to %s", target)
