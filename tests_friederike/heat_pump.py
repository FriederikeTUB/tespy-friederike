from CoolProp.CoolProp import PropsSI
from tespy.networks import Network

# create a network and specify a list of fluids
fluid_list = ['R134a']
my_plant = Network(fluids=fluid_list)

# set a unit system. Default is SI-units
my_plant.set_attr(T_unit='C', p_unit='bar', h_unit='kJ / kg')


from tespy.components import (CycleCloser, Compressor, Valve, HeatExchangerSimple)
# import and apply components. Parameters for components are generally optional. Label is mandatory.
# That means tha name of the component HeatExchangerSimple is ev with
# the label evaporator As the connections hold the information, which components are connected in which way,
# we do not need to pass the components to the network.
cc = CycleCloser('cycle closer')  # start and end of cycle. like node
# heat sink
co = HeatExchangerSimple('condenser')
# heat source
ev = HeatExchangerSimple('evaporator')
va = Valve('expansion valve')
cp = Compressor('compressor')


from tespy.connections import Connection
# use Connections to link two component
# outlet of com 1 to inlet of com 2: source to target.  the fluid properties at the source will be equal
# to the properties at the target.
# The basic specification options are:
#
# mass flow (m)
#
# volumetric flow (v)
#
# pressure (p)
#
# enthalpy (h)
#
# temperature (T)
#
# a fluid vector (fluid)


# connections of heat pump
c1 = Connection(cc, 'out1', ev, 'in1', label='1')
c2 = Connection(ev, 'out1', cp, 'in1', label='2')
c3 = Connection(cp, 'out1', co, 'in1', label='3')
c4 = Connection(co, 'out1', va, 'in1', label='4')
c0 = Connection(va, 'out1', cc, 'in1', label='0')

# this line is crutial: you have to add all connections to your network. No need to pass the components to the network.
# but the connections must be added to the network

my_plant.add_conns(c1, c2, c3, c4, c0)


# set the component and connection parameters.
co.set_attr(pr=0.98)
ev.set_attr(pr=0.98)
cp.set_attr(eta_s=0.85)

c2.set_attr(T=20, x=1, fluid={'R134a': 1}, m=5)
c4.set_attr(T=80, x=0)

# solve
my_plant.solve(mode='design')
my_plant.print_results()

print(f'COP = {abs(co.Q.val) / cp.P.val}')
print('test')


# print(PropsSI("T","P",10000,"Q",0,"Water"))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
  ...
