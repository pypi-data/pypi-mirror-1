#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Defines a tree editor for Pylon resources """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance
from enthought.traits.ui.api import View, Group, Item, HGroup, VGroup, Tabbed

from enthought.plugins.workspace.resource_editor import ResourceEditor

from pylon.api import Network
from pylon.ui.network_tree import network_tree_editor

#------------------------------------------------------------------------------
#  "PylonTreeEditor" class:
#------------------------------------------------------------------------------

class PylonTreeEditor(ResourceEditor):
    """ Defines a workbench editor for editing network resources with
    a view based on a tree control.

    """

    #--------------------------------------------------------------------------
    #  "NetworkTreeEditor" interface
    #--------------------------------------------------------------------------

    # The network object provided by the edited resource
    document = Instance(Network)

    #--------------------------------------------------------------------------
    #  "TraitsUIEditor" interface
    #--------------------------------------------------------------------------

    def create_ui(self, parent):
        """ Creates the traits UI that represents the editor """

        self.document = document = self.provider.create_document(self.obj)

        ui = self.edit_traits(
            view=self._create_view(), parent=parent, kind="subpanel"
        )

        # Dynamic notification of document object modification
        document.on_trait_change(self.on_document_modified)

        return ui

    #--------------------------------------------------------------------------
    #  "ResourceEditor" interface
    #--------------------------------------------------------------------------

    def _create_view(self):
        """ Create a view with a tree editor """

        network_tree_editor.on_select = self._on_select
        network_tree_editor.on_dclick = self._on_dclick
        network_tree_editor.editable = False

        view = View(
            Group(
                Item(
                    name="document", id=".document",
                    editor=network_tree_editor, resizable=True
                ),
                show_labels=False, show_border=False,
                orientation="vertical"
            ),
            id="pylon.plugin.network_tree_editor.network_tree_view",
            help=False, resizable=True,
            undo=False, revert=False,
            width=0.3, height=0.3,
        )

        return view


    def _on_dclick(self, object):
        """ Handle tree node activation """

        object.edit_traits(parent=self.window.control, kind="livemodal")


    def _on_select(self, object):
        """ Handle tree node selection """

        # No properties view for the whole network
        if isinstance(object, Network):
            self.selected = None
        else:
            self.selected = object

# EOF -------------------------------------------------------------------------
