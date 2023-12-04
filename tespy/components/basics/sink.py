# -*- coding: utf-8

"""Module for class Sink.


This file is part of project TESPy (github.com/oemof/tespy). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location tespy/components/basics/sink.py

SPDX-License-Identifier: MIT
"""

import numpy as np

from tespy.components.component import Component


class Sink(Component):
    r"""
    A flow drains in a Sink.

    Parameters
    ----------
    label : str
        The label of the component.

    design : list
        List containing design parameters (stated as String).

    offdesign : list
        List containing offdesign parameters (stated as String).

    design_path : str
        Path to the components design case.

    local_offdesign : boolean
        Treat this component in offdesign mode in a design calculation.

    local_design : boolean
        Treat this component in design mode in an offdesign calculation.

    char_warnings : boolean
        Ignore warnings on default characteristics usage for this component.

    printout : boolean
        Include this component in the network's results printout.

    Example
    -------
    Create a sink and specify a label.

    >>> from tespy.components import Sink
    >>> si = Sink('a labeled sink')
    >>> si.component()
    'sink'
    >>> si.label
    'a labeled sink'
    """

    @staticmethod
    def component():
        return 'sink'

    @staticmethod
    def inlets():
        return ['in1']

    @staticmethod
    def get_mandatory_constraints():
        return {}

    def propagate_to_target(self, branch):
        return

    def propagate_wrapper_to_target(self, branch):
        branch["components"] += [self]
        return

    def exergy_balance(self, T0):
        r"""Exergy balance calculation method of a sink.

        A sink does not destroy or produce exergy. The value of
        :math:`\dot{E}_\mathrm{bus}` is set to the exergy of the mass flow to
        make exergy balancing methods more simple as in general a mass flow can
        be fuel, product or loss.

        Parameters
        ----------
        T0 : float
            Ambient temperature T0 / K.

        Note
        ----
        .. math::

            \dot{E}_\mathrm{bus} = \dot{E}_\mathrm{in}^\mathrm{PH}
        """
        self.E_P = np.nan
        self.E_F = np.nan
        self.E_bus = {
            "chemical": self.inl[0].Ex_chemical,
            "physical": self.inl[0].Ex_physical,
            "massless": 0
        }
        self.E_D = np.nan
        self.epsilon = self._calc_epsilon()
    """+F+F+F+F++++START++++F+F+F+F+    von Jubran"""
    def set_sink_costs(self, c_tot=None):
        self.Z_costs = np.nan
        self.C_F = np.nan
        self.C_P = np.nan
        self.C_D = np.nan
        self.r = np.nan
        self.f = np.nan

        if c_tot:
            self.inl[0].c_tot = c_tot
            # calculate inlet
            self.inl[0].Ex_tot = self.inl[0].Ex_physical + self.inl[0].Ex_chemical
            self.inl[0].C_tot = self.inl[0].c_tot * self.inl[0].Ex_tot
            self.Z_costs = self.outl[0].C_tot
            # approx costs per exergy unit fot T,M, PH and CH
            self.inl[0].C_therm = self.inl[0].C_tot * (self.inl[0].Ex_therm / self.inl[0].Ex_tot)
            self.inl[0].C_mech = self.inl[0].C_tot * (self.inl[0].Ex_mech / self.inl[0].Ex_tot)
            self.inl[0].C_chemical = self.inl[0].C_tot * (self.inl[0].Ex_chemical / self.inl[0].Ex_tot)

            self.inl[0].c_therm = 0 if self.inl[0].Ex_therm == 0 else self.inl[0].C_therm / self.inl[
                0].Ex_therm
            self.inl[0].c_mech = 0 if self.inl[0].Ex_mech == 0 else self.inl[0].C_mech / self.inl[0].Ex_mech
            self.inl[0].c_chemical = 0 if self.inl[0].Ex_chemical == 0 else self.inl[0].C_chemical / self.inl[
                0].Ex_chemical


    """+F+F+F+F++++END++++F+F+F+F+    von Jubran"""


