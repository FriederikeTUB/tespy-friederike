from tespy.networks import Network
from tespy.components import (Source, Sink, DiabaticCombustionChamber)
from tespy.connections import Connection, Bus, Ref
from tespy.tools import ExergyAnalysis
from chemical_exergy.libChemExAhrendts import Chem_Ex


nw = Network(T_unit="C", p_unit="bar", h_unit="kJ / kg")

# components
chamber = DiabaticCombustionChamber('Combustion Chamber')
air = Source('Air Inlet')
exhaust = Sink('Exhaust')
fuelgas = Source('Fuel')

# connections
c1 = Connection(air, 'out1', chamber, 'in1', label='Air to Chamber')
c2 = Connection(fuelgas, 'out1', chamber, 'in2', label='Fuel to Chamber')
c3 = Connection(chamber, 'out1', exhaust, 'in1', label='to Exhaust')

nw.add_conns(c1, c2, c3)

# define parameters
chamber.set_attr(pr=1, eta=0.99, ti=10e6)
c1.set_attr(
    p=1.0, T=20,
    fluid={"Ar": 0.0129, "N2": 0.7553, "CO2": 0.0004, "O2": 0.2314})
c2.set_attr(
    p=Ref(c1, 1.0, 0), T=20,
    fluid={"CO2": 0.04, "CH4": 0.96})
c3.set_attr(T=1200)

# solve
nw.solve(mode='design')
nw.print_results()


""" +++ exergy analysis +++ """
# define ambient
p_amb = 0.1
T_amb = 25

# define busses (no need to add them to system)
heat_in = Bus('Heat In')
heat_in.add_comps({'comp': fuelgas, 'base': 'bus'})

air_in = Bus('Air In')
air_in.add_comps({'comp': air, 'base': 'bus'})

exhaust_out = Bus('Exhaust Gas')
exhaust_out.add_comps({'comp': exhaust})

# exergy analysis
ean = ExergyAnalysis(nw, E_P=[exhaust_out], E_F=[heat_in, air_in], E_L=[])
ean.analyse(pamb=p_amb, Tamb=T_amb, Chem_Ex=Chem_Ex)
ean.print_results()







