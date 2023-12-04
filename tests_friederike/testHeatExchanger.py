import numpy.ma

from tespy.networks import Network
from tespy.components import (Source, Sink, SimpleHeatExchanger)
from tespy.connections import Connection, Bus
from tespy.tools import analyses, ExergyAnalysis
import numpy as np

# network
nw = Network(fluids=["Water"], T_unit="C", p_unit="bar", h_unit="kJ / kg")

# components
hx = SimpleHeatExchanger("My Heat Exchanger")
so = Source("My Source")
si = Sink("My Sink")

# Connections
c1 = Connection(so, 'out1', hx, 'in1', label="My Inlet")
c2 = Connection(hx, 'out1', si, 'in1', label="My Outlet")

nw.add_conns(c1, c2)

# define parameters
hx.set_attr(pr=0.5, Q=+10000000)
c1.set_attr(fluid={'Water':1.0}, T=30, p=10, m=40)


""" +++ exergy analysis +++ """
# define ambient
T_amb = 5
p_amp = 1

# define busses
heat_in_B = Bus('Heat In')
heat_in_B.add_comps({'comp': hx, 'char': +1})

mass_flow_B = Bus('water flow')
mass_flow_B.add_comps({'comp': so, 'base': 'bus'}, {'comp': si})

# add busses to network
nw.add_busses(heat_in_B, mass_flow_B)

# solve network
nw.solve(mode='design')
#nw.print_results()

# exergy and exergoeconomic analysis
exe_eco_input = {'My Source_c': 0.02}
ean = ExergyAnalysis(nw, E_F=[heat_in_B], E_P=[mass_flow_B], E_L=[])
ean.analyse(pamb=p_amp, Tamb=T_amb, Exe_Eco_An = True, Exe_Eco_Costs = exe_eco_input)
#ean.print_results(Exe_Eco_An=True)



"""
fruit = 'Apple'
isApple = True if fruit == 'Apple' else False
print(isApple)

colNum = 7
a=np.zeros(colNum)      # line to add to A
a[2]=+1
A = np.vstack([A, a]) if 'A' in locals() else a
b = np.vstack([b, 2]) if 'b' in locals() else [3]

print(A)
print(b)

a=np.zeros(colNum)      # line to add to A
a[2]=+1

if 'A' in locals():     # A exists already
    A = np.vstack([A, a])
else:
    A = a

if 'b' in locals():     # A exists already
    b = np.vstack([b, 2])
else:
    b=[3]

print(A)
print(b)



print()

for bus in nw.busses.values():
    for comp in bus.comps.index:
        bus_val = comp.E_bus['chemical'] + comp.E_bus['physical'] + comp.E_bus['massless']
        if bus.comps.loc[comp, 'base'] == 'component':
            print(bus.label, comp.label, "out", bus_val)
        if bus.comps.loc[comp, 'base'] == 'bus':
            print(bus.label, comp.label, "in", bus_val)

for comp in nw.comps['object']:
    print(comp.label, ": ", comp.E_bus)
    print(comp.E_bus['chemical'])
    print(comp.E_bus['physical'])
    print(comp.E_bus['massless'])
    # find out whether energy/mass flows into ('base' is 'bus') or out of ('base' is 'component') component
    #print(comp.E_bus.get_attr('base'))

for bus in nw.busses.values():
    print(f"Bus value of Bus \"{bus.label}\" is {bus.get_attr('P').val}")
    for parameter in bus.comps:
        print(parameter)

print()
for comp in nw.comps['object']:
    print(comp.label, ": ", comp.Z_costs)
print()
for conn in nw.conns['object']:
    print(conn.label, ": ", conn.c_T, ", ", conn.c_M, ", ", conn.c_CH)
"""





