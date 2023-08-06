# Small utility methods.
import logging
import os
import re
import sys
import urllib
from commands import getoutput

logger = logging.getLogger('utils')

WRONG_IN_VERSION = ['svn', 'dev', '(']


def filefind(name):
    """Return first found file matching name (case-insensitive)."""
    for dirpath, dirnames, filenames in os.walk('.'):
        if '.svn' in dirpath:
            # We are inside a .svn directory.
            continue
        if '.svn' not in dirnames:
            # This directory is not handled by subversion.  Example:
            # run prerelease in
            # https://svn.plone.org/svn/collective/feedfeeder/trunk
            # which is a buildout, so it has a parts directory.
            continue
        for filename in filenames:
            if filename.lower() == name.lower():
                fullpath = os.path.join(dirpath, filename)
                logger.debug("Found %s", fullpath)
                return fullpath


def extract_version():
    if os.path.exists('version.txt'):
        f = open('version.txt', 'r')
        version = f.read().strip()
        stripped_version = version.replace(' ', '')
    elif os.path.exists('setup.py'):
        version = getoutput('/usr/bin/env python2.4 setup.py --version').strip()
        stripped_version = version.replace(' ', '')
    else:
        stripped_version = None
    return stripped_version


def history_file():
    """Return history file location."""
    for name in ['HISTORY.txt', 'CHANGES.txt']:
        history = filefind(name)
        if history:
            return history


def ask(question):
    """Ask the question in y/n form and return True/False."""
    print question + " (y/n)?"
    input = raw_input()
    return 'y' in input.lower()


def fix_rst_heading(heading, below):
    """If the 'below' line looks like a reST line, give it the correct length.
    """
    if len(below) == 0:
        return below
    first = below[0]
    if first not in '-=':
        return below
    below = first * len(heading)
    return below


def show_diff_offer_commit(message):
    """Show the svn diff and offer to commit it."""
    diff = getoutput('svn diff')
    logger.info("The 'svn diff':\n\n%s\n", diff)
    if ask("OK to commit this?"):
        commit = getoutput('svn commit -m "%s"' % message)
        logger.info(commit)


def update_version(version):
    """Find out where to change the version and change it.

    There are two places where the version can be defined. The first one is
    some version.txt that gets read by setup.py. The second is directly in
    setup.py.
    """
    current = extract_version()
    versionfile = filefind('version.txt')
    if versionfile:
        open(versionfile, 'w').write(version + '\n')
        logger.info("Changed %s to %r", versionfile, version)
        return
    good_version = "version = '%s'" % version
    pattern = re.compile(r"""
    version\W*=\W*   # 'version =  ' with possible whitespace
    \d               # Some digit, start of version.
    """, re.VERBOSE)
    line_number = 0
    setup_lines = open('setup.py').read().split('\n')
    for line in setup_lines:
        match = pattern.search(line)
        if match:
            logger.debug("Matching version line found: %r", line)
            setup_lines[line_number] = good_version
            break
        line_number += 1
    contents = '\n'.join(setup_lines)
    open('setup.py', 'w').write(contents)
    logger.info("Set setup.py's version to %r", version)


def cleanup_version(version):
    """Check if the version looks like a development version."""
    for w in WRONG_IN_VERSION:
        if version.find(w) != -1:
            logger.debug("Version indicates development: %s.", version)
            version = version[:version.find(w)].strip()
            logger.debug("Removing debug indicators: %r", version)
    return version


def extract_headings_from_history(history_lines):
    """Return list of dicts with version-like headers."""
    pattern = re.compile(r"""
    (?P<version>.*)  # Version string
    \(               # Opening (
    (?P<date>.*)     # Date
    \)               # Closing )
    \W*$             # Possible whitespace at end of line.
    """, re.VERBOSE)
    headings = []
    line_number = 0
    for line in history_lines:
        match = pattern.search(line)
        if match:
            result = {'line': line_number,
                      'version': match.group('version').strip(),
                      'date': match.group('date'.strip())}
            headings.append(result)
            logger.debug("Found heading: %r", result)
        line_number += 1
    return headings


def svn_info():
    """Return svn url"""
    our_info = getoutput('svn info')
    url = [line for line in our_info.split('\n')
           if 'URL:' in line][0]
    return url.replace('URL:', '').strip()


def base_from_svn():
    base = svn_info()
    for remove in ['trunk', 'tags', 'branches']:
        base = base.split(remove)[0]
    logger.debug("Base url is %s", base)
    return base


def extract_name_and_base(url):
    """Return name and base svn url from svn url."""
    base = url
    for remove in ['trunk', 'tags', 'branches']:
        base = base.split(remove)[0]
    logger.debug("Base url is %s", base)
    parts = base.split('/')
    parts = [part for part in parts if part]
    name = parts[-1]
    logger.debug("Name is %s", name)
    return name, base


def available_tags():
    """Return available tags."""
    base = base_from_svn()
    tag_info = getoutput('svn list %stags' % base)
    if "non-existent in that revision" in tag_info:
        print "tags dir does not exist at %s" % base + 'tags'
        if ask("Shall I create it"):
            cmd = 'svn mkdir %stags -m "Creating tags directory."' % (base)
            logger.info("Running %r", cmd)
            print getoutput(cmd)
            tag_info = getoutput('svn list %stags' % base)
        else:
            sys.exit(0)
    if 'Could not resolve hostname' in tag_info:
        logger.error('Network problem: %s', tag_info)
        sys.exit()
    tags = [line.replace('/', '') for line in tag_info.split('\n')]
    logger.debug("Available tags: %r", tags)
    return tags


def name_from_svn():
    base = base_from_svn()
    parts = base.split('/')
    parts = [p for p in parts if p]
    return parts[-1]


def extract_option(buildout_lines, option_name):
    """Return info on an option (like 'develop=...').

    Return start/end line numbers, actual option lines and a list of
    options.
    """
    pattern = re.compile(r"""
    ^%s        # Line that starts with the option name
    \W*=       # Followed by an '=' with possible whitespace before it.
    """ % option_name, re.VERBOSE)
    line_number = 0
    first_line = None
    for line in buildout_lines:
        match = pattern.search(line)
        if match:
            logger.debug("Matching %s line found: %r", option_name, line)
            start = line_number
            first_line = line
            break
        line_number += 1
    if not first_line:
        logger.error("'%s = ....' line not found.", option_name)
        return (None, None, None, None)
    option_values = [first_line.split('=')[1]]
    for line in buildout_lines[start + 1:]:
        line_number += 1
        if ('=' in line or '[' in line):
            if not '#egg=' in line:
                end = line_number
                break
        option_values.append(line)
    option_values = [item.strip() for item in option_values
                        if item.strip()]
    logger.info("Found option values: %r.", option_values)
    option_section = buildout_lines[start:end]
    return (start,
            end,
            option_values,
            option_section)


def format_option(name, options):
    """Return lines with formatted option."""
    lines = ['%s =' % name]
    for option in options:
        if option.startswith('#'):
            # Comments must start in the first column, so don't indent them.
            lines.append(option)
        else:
            lines.append('    %s' % option)
    lines.append('')
    return lines


def package_in_pypi(package):
    """Check whether the package is registered on pypi"""
    url = 'http://pypi.python.org/simple/%s' % package
    result = urllib.urlopen(url).read().strip()
    if package in result:
        # Some link with the package name is present. If the package doesn't
        # exist on pypi, the result would be 'Not Found'.
        return True
    else:
        logger.debug("Package not found on pypi: %r", result)
        return False
