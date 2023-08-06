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

""" Defaines an action for solving the DC Optimal Power Flow problem.
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

from pylon.network import Network, NetworkReport
from pylon.ui.routine.dc_opf_view_model import DCOPFViewModel
from pylon.ui.report_view import opf_report_view

#------------------------------------------------------------------------------
#  "DCOPFAction" class:
#------------------------------------------------------------------------------

class DCOPFAction(Action):
    """ Action for solving the DC OPF problem.
    """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Solve a DC OPF for the current network"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&DC OPF"

    # A short description of the action used for tooltip text etc:
    tooltip = "DC Optimal Power Flow"

    # The action's image (displayed on tool bar tools etc):
#    image = ImageResource("blank.png", search_path=[IMAGE_PATH])

    # Keyboard accelerator:
    accelerator = "Ctrl+D"

    #--------------------------------------------------------------------------
    #  "DCOPFAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "DCOPFAction" interface:
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
            vm = DCOPFViewModel(network=network)
            vm.run = True

            report = NetworkReport(network)
            report.edit_traits(view=opf_report_view, kind="livemodal")
            del report

            vm.edit_traits(parent=self.window.control, kind="livemodal")

            resource.save(network)

        return

# EOF -------------------------------------------------------------------------
