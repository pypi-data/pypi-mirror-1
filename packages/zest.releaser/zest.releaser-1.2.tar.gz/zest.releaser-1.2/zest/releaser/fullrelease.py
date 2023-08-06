"""Do the prerelease, actual release and post release in one fell swoop!
"""
import logging
import os


from zest.releaser import prerelease
from zest.releaser import release
from zest.releaser import postrelease

logger = logging.getLogger('fullrelease')


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")
    logger.info('Starting prerelease.')
    original_dir = os.getcwd()
    prerelease.main()
    os.chdir(original_dir)
    logger.info('Starting release.')
    release.main()
    os.chdir(original_dir)
    logger.info('Starting postrelease.')
    postrelease.main()
    os.chdir(original_dir)
    logger.info('Finished full release.')
