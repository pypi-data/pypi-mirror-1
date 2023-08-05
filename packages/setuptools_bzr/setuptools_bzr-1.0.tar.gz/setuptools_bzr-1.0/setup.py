# setuptools plugin for bzr
# Barry Warsaw <barry@python.org>

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
from setuptools_bzr import __version__


setup(
    name            = 'setuptools_bzr',
    version         = __version__,
    description     = 'setuptools plugin for bzr',
    author          = 'Barry Warsaw',
    author_email    = 'barry@python.org',
    license         = 'PSF',
    # For historical reasons, the code lives under a different project name.
    url             = 'https://launchpad.net/setuptoolsbzr',
    keywords        = 'distutils setuptools setup',
    packages        = find_packages(),
    entry_points    = {
        'setuptools.file_finders': [
            'bzr = setuptools_bzr:find_files_for_bzr',
            ],
        },
    install_requires = {
        'bzr': ['bzr'],
        },
    )
