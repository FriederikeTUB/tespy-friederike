from tespy.networks import Network
from tespy.components import (Source, Compressor, DiabaticCombustionChamber, Turbine, Sink)
from tespy.connections import Connection, Ref, Bus

# network
fluid_list = ["Ar", "N2", "O2", "CO2", "CH4", "H2O", "H2"]
nw = Network(fluids=fluid_list, p_unit="bar", T_unit="C")

# components
turbine = Turbine('Turbine')
comp = Compressor('Compressor')
chamber = DiabaticCombustionChamber('Combustion Chamber')
air_source = Source('Air Inlet')
exhaust_sink = Sink('Exhaust')
fuel_source = Source('Fuel')

# connections
so_to_comp = Connection(air_source, 'out1', comp, 'in1', label='1')
comp_to_chamber = Connection(comp, 'out1', chamber,'in1', label='2')
chamber_to_turbine = Connection(chamber, 'out1', turbine, 'in1', label='3')
turbine_to_exhaust = Connection(turbine, 'out1', exhaust_sink, 'in1', label='4')
fuel_to_chamber = Connection(fuel_source, 'out1', chamber, 'in2', label='5')

nw.add_conns(so_to_comp,fuel_to_chamber, comp_to_chamber, chamber_to_turbine, turbine_to_exhaust)
#nw.add_conns(fuel_to_chamber)

generator = Bus("generator")
generator.add_comps(
    {"comp": turbine, "char": 0.98, "base": "component"},  # 98 % mech. ele. efficiency
    {"comp": comp, "char": 0.98, "base": "bus"},  # 98 % mech. ele. efficiency
)
nw.add_busses(generator)

# parameters
# air source
so_to_comp.set_attr(
    p=1, T=20,
    fluid={
        "Ar": 0.0129, "N2": 0.7553, "H2O": 0,
        "CH4": 0, "CO2": 0.0004, "O2": 0.2314, "H2": 0
    }
)
# compressor
comp.set_attr(eta_s=0.85, pr=15)

# chamber
fuelgas = {
        "CO2": 0.04, "Ar": 0, "N2": 0, "O2": 0,
        "H2O": 0, "CH4": 0.96, "H2": 0
    }
fuel_to_chamber.set_attr(
    p=Ref(comp_to_chamber, 1.01, 0), T=20,
    fluid=fuelgas
)
# fuel_to_chamber.set_attr(p=Ref(comp_to_chamber, 1.00, 0))
chamber.set_attr(pr=0.99, eta=0.99, ti=10e6)
chamber_to_turbine.set_attr(T=1200)


# turbine
turbine_to_exhaust.set_attr(p=Ref(so_to_comp, 1, 0))  # ref obj: p of so_to_como. Factor 1, add 0
turbine.set_attr(eta_s=0.9)



# solve
nw.solve(mode="design")
nw.print_results()
