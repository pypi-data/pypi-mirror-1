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

""" An extension to the Core Package that in association with the Terminal
    class models Connectivity, that is the physical definition of how equipment
    is connected together. In addition it models Topology, that is the logical
    definition of how equipment is connected via closed switches. The Topology
    definition is independent of the other electrical characteristics.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Instance, Bool, Range, Enum

from enthought.traits.ui.api \
    import View, Group, Item, VGroup, HGroup, InstanceEditor

from CIM13.Core \
    import IdentifiedObject, Terminal

#------------------------------------------------------------------------------
#  "TopologicalIsland" class:
#------------------------------------------------------------------------------

class TopologicalIsland(IdentifiedObject):
    """ An electrically connected subset of the network. Topological islands
        can change as the current network state changes (i.e., disconnect
        switches, breakers, etc. change state).
    """

    AngleRef_TopologicalNode = Instance("TopologicalNode")

    # A topological node belongs to a topological island.
    TopologicalNodes = List(Instance("TopologicalNode"),
        opposite="TopologicalIsland")

#------------------------------------------------------------------------------
#  "TopologicalNode" class:
#------------------------------------------------------------------------------

class TopologicalNode(IdentifiedObject):
    """ A set of connectivity nodes that, in the current network state, are
        connected together through any type of closed switches, including
        jumpers. Topological nodes can change as the current network state
        changes (i.e., switches, breakers, etc. change state).
    """

    # Several ConnectivityNode(s) may combine together to form a single
    # TopologicalNode, depending on the current state of the network.
    ConnectivityNodes = List(Instance("ConnectivityNode"),
        desc="connectivity nodes that form the topological node",
        opposite="TopologicalNode")

    # A topological node belongs to a topological island.
    TopologicalIsland = Instance("TopologicalIsland",
        opposite="TopologicalNodes")

    # True if node energized.
#    energized = Bool(True)

    # Net injection active power.
    netInjectionP = Float(desc="net injection active power")

    # Net injection reactive power.
    netInjectionQ = Float(desc="net injection reactive power")

    # Phase angle of node.
    phaseAngle = Float(desc="phase angle of node")

    # Voltage of node.
    voltage = Float(desc="voltage of node")

    # Set if node is load carrying.
    loadCarrying = Bool(desc="True if node is load carrying")

#------------------------------------------------------------------------------
#  "ConnectivityNode" class:
#------------------------------------------------------------------------------

class ConnectivityNode(IdentifiedObject):
    """ Connectivity nodes are points where terminals of conducting equipment
        are connected together with zero impedance.
    """

    # Terminals interconnect with zero impedance at a node.  Measurements on a
    # node apply to all of its terminals.
    Terminals = List(Instance(Terminal), opposite="ConductingEquipment")

    # Several ConnectivityNode(s) may combine together to form a single
    # TopologicalNode, depending on the current state of the network.
    TopologicalNode = Instance(TopologicalNode, opposite="ConnectivityNodes")

# EOF -------------------------------------------------------------------------
