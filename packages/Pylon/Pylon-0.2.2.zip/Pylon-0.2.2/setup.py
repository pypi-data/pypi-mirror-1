#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

from setuptools import setup, find_packages

setup(author="Richard W. Lincoln",
      author_email="r.w.lincoln@gmail.com",
      description="Power system and energy market simulator.",
      url="http://rwl.github.com/pylon",
      version="0.2.2",
      entry_points={"console_scripts": ["pylon = pylon.main:main"],
          "gui_scripts": ["pylon_workbench = pylon.plugin.main:main [GUI]"]},
      install_requires=["Traits", "TraitsGUI", "PyBrain", "PyParsing",
          "PyExcelerator"],
      extras_require={"GUI": ["EnvisageCore", "EnvisagePlugins", "Chaco",
          "ConfigObj", "IPython", "TraitsBackendWX", "Puddle", "Godot"]},
      license="GPLv2",
      name="Pylon",
      include_package_data=True,
      exclude_package_data={"": ["*.ecore"], "doc/uml": ["*.dia"]},
      packages=find_packages(),
      test_suite="pylon.test",
      zip_safe=False)

# EOF -------------------------------------------------------------------------
