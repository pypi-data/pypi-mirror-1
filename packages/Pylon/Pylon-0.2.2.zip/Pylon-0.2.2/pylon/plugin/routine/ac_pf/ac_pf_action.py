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

""" Action for solving the AC Power Flow problem.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.io.api import File
from enthought.traits.api import Instance
from enthought.traits.ui.menu import Action
from enthought.pyface.api import ImageResource
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

from puddle.resource.resource_adapter import PickleFileIResourceAdapter

from pylon.api import Network
from pylon.ui.routine.ac_pf_view_model import ACPFViewModel

#------------------------------------------------------------------------------
#  "ACPFAction" class:
#------------------------------------------------------------------------------

class ACPFAction(Action):
    """ Action for solving the AC Power Flow problem.
    """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Solve the AC Power Flow for the current network"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&AC PF"

    # A short description of the action used for tooltip text etc:
    tooltip = "AC Power Flow"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("ac")

    # Keyboard accelerator:
    accelerator = "Alt+A"

    #--------------------------------------------------------------------------
    #  "ACPFAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "ACPFAction" interface:
    #--------------------------------------------------------------------------

    def _selection_changed_for_window(self, new):
        """ Enables the action when a File object is selected.
        """
        if len(new) == 1:
            selection = new[0]
            if isinstance(selection, File) and (selection.ext == ".pkl"):
                self.enabled = True
            else:
                self.enabled = False
        else:
            self.enabled = False

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def _enabled_default(self):
        """ Trait initialiser.
        """
        if self.window.selection:
            sel = self.window.selection[0]
            if isinstance(sel, File) and (sel.ext == ".pkl"):
                return True
            else:
                return False
        else:
            return False


    def perform(self, event):
        """ Perform the action.
        """
        selected = self.window.selection[0]
        resource = PickleFileIResourceAdapter(selected)
        network = resource.load()

        if isinstance(network, Network):
            vm = ACPFViewModel(network=network)
            vm.run = True
            vm.edit_traits(parent=self.window.control, kind="livemodal")

            resource.save(network)

        return

# EOF -------------------------------------------------------------------------
