from tespy.networks import Network
from tespy.components import (CycleCloser, Compressor, Valve, SimpleHeatExchanger)
from tespy.connections import Connection, Bus
from tespy.tools import ExergyAnalysis

# create a network object with R134a as fluid
nw = Network()

# set the unit system for temperatures to °C and for pressure to bar
nw.set_attr(T_unit='C', p_unit='bar', h_unit='kJ / kg')

# components
cc = CycleCloser('cycle closer')
co = SimpleHeatExchanger('condenser')
ev = SimpleHeatExchanger('evaporator')
va = Valve('expansion valve')
cp = Compressor('compressor')

# connections
c1 = Connection(cc, 'out1', ev, 'in1', label='1')
c2 = Connection(ev, 'out1', cp, 'in1', label='2')
c3 = Connection(cp, 'out1', co, 'in1', label='3')
c4 = Connection(co, 'out1', va, 'in1', label='4')
c0 = Connection(va, 'out1', cc, 'in1', label='0')

# add connections to the network (components are inside the connections)
nw.add_conns(c1, c2, c3, c4, c0)

co.set_attr(pr=0.98, Q=-1e6)
ev.set_attr(pr=0.98)
cp.set_attr(eta_s=0.85)

c2.set_attr(T=20, x=1, fluid={'R134a': 1})
c4.set_attr(T=80, x=0)

# compressor needs power (fuel of the heat pump)
power_in = Bus('power in')
power_in.add_comps({'comp': cp})
nw.add_busses(power_in)
# condenser removes heat (product of the heat pump)
heat_out = Bus('heat out')
heat_out.add_comps({'comp': co})
nw.add_busses(heat_out)


# start calculations
nw.solve(mode='design')
#nw.print_results()


exe_eco_input = {'condenser_Z': 50, 'evaporator_Z': 20, 'expansion valve_Z': 40, 'compressor_Z': 100}
ean = ExergyAnalysis(nw, E_F=[power_in], E_P=[heat_out], E_L=[])
ean.analyse(pamb=1.013, Tamb=28, Exe_Eco_An = True, Exe_Eco_Costs = exe_eco_input)
#ean.print_results(Exe_Eco_An=True)


"""
# FOR CYCLE CLOSER NEED TO REMOVE ONE CONNECTION
elif comp.component() == "cycle closer":
    print("cycle closer")
    a = np.zeros(colNum)  # line to add to A
    # add outlet of cycle closer ("start connection") as normal
    connNum = 0  # connection number for index in A
    for connection_in_network in conns_list:
        if comp.outl[0] == connection_in_network:  # better to use equals() ?
            a[connNum] = +1
        connNum += 1
    cyclecloser = comp
    cycleend = cyclecloser.inl[0]
    # find corresponding connection to cycleend in order to have only one connection for the closing point
    for compEnd in self.nw.comps['object']:
        if not compEnd.component() == "cycle closer" and compEnd.outl[0] == cycleend:
            connNum = 0
            for connection_in_network in conns_list:
                if compEnd.outl[0] == connection_in_network:  # better to use equals() ?
                    a[connNum] = +1
                    A = np.vstack([A, a]) if 'A' in locals() else a  # if A exists, add line a, otherwise A=a
                    b = np.vstack([b, -comp.Z_costs]) if 'b' in locals() else -comp.Z_costs
"""
