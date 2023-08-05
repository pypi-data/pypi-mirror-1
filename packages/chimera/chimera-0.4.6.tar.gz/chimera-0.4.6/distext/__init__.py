"""This package contains extensions to distutils"""


from test import TestCommand
from doc import DocCommand
from install import InstallCommand

import utils

__all__ = ['TestCommand', 'DocCommand', 'InstallCommand',
           'utils']

