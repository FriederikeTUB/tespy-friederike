from tespy.networks import Network
from tespy.components import (DiabaticCombustionChamber, Turbine, Source, Sink, Compressor)
from tespy.connections import Connection, Ref, Bus
from tespy.tools import ExergyAnalysis
from chemical_exergy.libChemExAhrendts import Chem_Ex

nw = Network(p_unit="bar", T_unit="C")

# components
cp = Compressor("compressor")
cc = DiabaticCombustionChamber("combustion chamber")
tu = Turbine("turbine")
air = Source("air source")
fuel = Source("fuel source")
fg = Sink("flue gas sink")

# connections
c1 = Connection(air, "out1", cp, "in1", label="1")
c2 = Connection(cp, "out1", cc, "in1", label="2")
c3 = Connection(cc, "out1", tu, "in1", label="3")
c4 = Connection(tu, "out1", fg, "in1", label="4")
c5 = Connection(fuel, "out1", cc, "in2", label="5")
nw.add_conns(c1, c2, c3, c4, c5)

# define parameters
cc.set_attr(pr=1, eta=1)
cp.set_attr(eta_s=0.85, pr=15)
tu.set_attr(eta_s=0.90)
c1.set_attr(
    p=1, T=20,
    fluid={"Ar": 0.0129, "N2": 0.7553, "CO2": 0.0004, "O2": 0.2314}
)
c3.set_attr(m=30)
c4.set_attr(p=Ref(c1, 1, 0))
c5.set_attr(m=1, p=1, T=20, fluid={"CO2": 0.03, "CH4": 0.92, "H2": 0.05})


# bus (necessary ???)                       same result as if adding it after solving
generator = Bus("generator")
generator.add_comps(
    {"comp": tu, "char": 0.98, "base": "component"},
    {"comp": cp, "char": 0.98, "base": "bus"},
)
nw.add_busses(generator)

# solve
nw.solve(mode='design')
nw.print_results()


""" +++ exergy analysis +++ """
# define ambient
T_amb = 10
p_amp = 1

# define busses (no need to add them to system)
fuel_bus = Bus("fuel")
fuel_bus.add_comps({"comp": fuel, "base": "bus"})

loss_bus = Bus("loss")
loss_bus.add_comps({"comp": fg, "base": "component"})

# exergy analysis
ean = ExergyAnalysis(network=nw, E_F=[fuel_bus], E_P=[generator], E_L=[])
ean.analyse(pamb=1.013, Tamb=20, Chem_Ex = Chem_Ex)
ean.print_results()

