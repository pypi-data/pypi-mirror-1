"""Stabilize unstable.cfg's development eggs into tag checkouts for stable.cfg
"""
import logging
import re
import sys
import os
from pkg_resources import parse_version

import utils

logger = logging.getLogger('stabilize')


def check_for_files():
    """Make sure stable.cfg and unstable.cfg are present"""
    required_files = ['stable.cfg', 'unstable.cfg']
    available = os.listdir('.')
    for required in required_files:
        if required not in available:
            logger.critical("Required file %s not found.", required)
            sys.exit()
    logger.debug("stable.cfg and unstable.cfg found.")


def development_eggs():
    """Return list of development eggs from unstable.cfg."""
    unstable_lines = open('unstable.cfg').read().split('\n')
    (start,
     end,
     development_eggs,
     development_section) = utils.extract_option(unstable_lines, 'develop')
    return development_eggs


def determine_tags(directories):
    """Return desired tags for all development eggs"""
    results = []
    start_dir = os.path.abspath('.')
    for directory in directories:
        logger.debug("Determining tag for %s...", directory)
        os.chdir(directory)
        version = utils.extract_version()
        logger.debug("Current version is %r.", version)
        available_tags = utils.available_tags()
        # We seek a tag that's the same or less than the version as determined
        # by setuptools' version parsing. A direct match is obviously
        # right. The 'less' approach handles development eggs that have
        # already been switched back to development.
        available_tags.reverse()
        found = available_tags[0]
        parsed_version = parse_version(version)
        for tag in available_tags:
            parsed_tag = parse_version(tag)
            parsed_found = parse_version(found)
            if parsed_tag == parsed_version:
                found = tag
                logger.debug("Found exact match: %s", found)
                break
            if (parsed_tag >= parsed_found and
                parsed_tag < parsed_version):
                logger.debug("Found possible lower match: %s", tag)
                found = tag
        url = utils.svn_info()
        name, base = utils.extract_name_and_base(url)
        full_tag = base + 'tags/' + found
        logger.info("Picked tag %r for %s (currently at %r).",
                    full_tag, name, version)
        results.append(full_tag)
        os.chdir(start_dir)
    return results


def insert_development_eggs(tags):
    """Add development eggs to [buildout].

    First we need to find the buildout section. Then we check if there's a
    svn-extend-develop option, adding it if needed. Last we change or add our tags.
    """
    if not tags:
        logger.info("No tags, so doing nothing.")
        return
    stable_lines = open('stable.cfg').read().split('\n')

    # Check if the gp.svndevelop extension is installed.
    (start,
     end,
     options,
     section) = utils.extract_option(stable_lines, 'extensions')
    if start == None:
        contents = '\n'.join(stable_lines)
        contents = contents.replace('[buildout]',
                                    '[buildout]\nextensions =\n')
        open('stable.cfg', 'w').write(contents)
        # Rerun
        stable_lines = open('stable.cfg').read().split('\n')
        (start,
         end,
         options,
         section) = utils.extract_option(stable_lines, 'extensions')
    if 'gp.svndevelop' not in options:
        options.append('gp.svndevelop')
        lines = utils.format_option('extensions', options)
        logger.debug("New extension section: %s", lines)
        stable_lines[start:end] = lines
        contents = '\n'.join(stable_lines)
        open('stable.cfg', 'w').write(contents)

    stable_lines = open('stable.cfg').read().split('\n')
    (start,
     end,
     development_eggs,
     development_section) = utils.extract_option(stable_lines, 'svn-extend-develop')
    if start == None:
        # Oops, no develop=... line. We'll insert one ourselves after the
        # [buildout] header and rerun.
        contents = '\n'.join(stable_lines)
        contents = contents.replace('[buildout]',
                                    '[buildout]\nsvn-extend-develop =\n')
        open('stable.cfg', 'w').write(contents)
        logger.info("Added empty 'develop=' to [buildout] section in "
                    "stable.cfg and wrote it back to disk.")
        # Rerun
        stable_lines = open('stable.cfg').read().split('\n')
        (start,
         end,
         development_eggs,
         development_section) = utils.extract_option(stable_lines, 'svn-extend-develop')

    # Filter out existing tags.
    for tag in tags:
        name, base = utils.extract_name_and_base(tag)
        print development_eggs
        development_eggs = [egg for egg in development_eggs
                            if not egg.startswith(base)]

    # Add our tags.
    for tag in tags:
        name, base = utils.extract_name_and_base(tag)
        development_eggs.append('%s#egg=%s' % (tag, name))
    lines = utils.format_option('svn-extend-develop', development_eggs)
    logger.debug("New develop section: %s", lines)
    stable_lines[start:end] = lines

    contents = '\n'.join(stable_lines)
    open('stable.cfg', 'w').write(contents)
    logger.info("New stable.cfg written")


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")
    check_for_files()
    directories = development_eggs()
    tags = determine_tags(directories)
    insert_development_eggs(tags)
    msg = ["Most recent svn tags of our packages added:"]
    msg += ['* %s' % tag for tag in tags]
    msg = '\n'.join(msg)
    utils.show_diff_offer_commit(msg)
