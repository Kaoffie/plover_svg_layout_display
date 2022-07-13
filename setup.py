#!/usr/bin/env python3

from setuptools import setup

from plover_build_utils.setup import BuildPy, BuildUi, Develop

BuildPy.build_dependencies.append('build_ui')
BuildUi.hooks = ['plover_build_utils.pyqt:fix_icons']
Develop.build_dependencies.append('build_py')
CMDCLASS = {
    'build_py': BuildPy,
    'build_ui': BuildUi,
    'develop': Develop,
}

setup(cmdclass=CMDCLASS)
