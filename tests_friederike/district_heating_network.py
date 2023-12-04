from tespy.networks import Network
from tespy.components import (HeatExchangerSimple, Valve, Pump, Pipe, CycleCloser)
from tespy.connections import Connection, Ref

# create a network and specify a list of fluids
fluid_list = ['Water']
nw = Network(fluids=fluid_list)

# set a unit system. Default is SI-units
nw.set_attr(T_unit='C', p_unit='bar', h_unit='kJ / kg')

# components
consumer = HeatExchangerSimple('Consumer')
cv = Valve('Valve')
return_pipe = Pipe('Return Pipe')
feed_pipe = Pipe('Feed Pipe')
cc = CycleCloser('Cycle Closer')
heat_source = HeatExchangerSimple('Heat Source')
pump = Pump('Pump')

# connections
cc_heat_source = Connection(cc, 'out1', heat_source, 'in1', label='0')
heat_source_pump = Connection(heat_source, 'out1', pump, 'in1', label='1')
pump_feed_pipe = Connection(pump, 'out1', feed_pipe, 'in1', label='2')
feed_pipe_consumer = Connection(feed_pipe, 'out1', consumer, 'in1', label='3')
consumer_valve = Connection(consumer, 'out1', cv, 'in1', label='4')
valve_return_pipe = Connection(cv, 'out1', return_pipe, 'in1', label='5')
return_pipe_cc = Connection( return_pipe, 'out1', cc, 'in1', label='6')

nw.add_conns(cc_heat_source, heat_source_pump, pump_feed_pipe, feed_pipe_consumer, consumer_valve, valve_return_pipe
             , return_pipe_cc)

# parameters
# consumer
consumer.set_attr(Q=-5000, pr=0.98)
# flow temperature
feed_pipe_consumer.set_attr(T = 80)
# return temperature
consumer_valve.set_attr(T=50)

# pump
pump.set_attr(pr=7, eta_s = 0.8)

# return pipe
return_pipe.set_attr(Q=-200, pr=0.98)

# heat source
heat_source.set_attr(pr=0.98)
heat_source_pump.set_attr(p=1, fluid={'Water': 1})

# feed pipe
feed_pipe.set_attr(Q=-200, pr=0.98)

nw.solve(mode='design')
nw.print_results()

