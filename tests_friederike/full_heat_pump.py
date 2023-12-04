from tespy.networks import Network
import matplotlib.pyplot as plt
from tespy.connections import Connection
from CoolProp.CoolProp import PropsSI as PSI

def network_nw():
    # network
    from tespy.networks import Network
    working_fluid = "NH3"

    nw = Network(
        fluids=["water", working_fluid],
        T_unit="C", p_unit="bar", h_unit="kJ / kg", m_unit="kg / s"
    )
    return nw, working_fluid


def consumer_element(nw, working_fluid):
    from tespy.components import (Pump, Condenser, HeatExchangerSimple,
                                  CycleCloser, Source, Sink)
    # sources & sinks
    c_in = Source("refrigerant in")
    cons_closer = CycleCloser("consumer cycle closer")
    va = Sink("valve")

    # consumer system
    cd = Condenser("condenser")
    rp = Pump("recirculation pump")
    cons = HeatExchangerSimple("consumer")

    # connections
    # consumer cycle
    c0 = Connection(c_in, "out1", cd, "in1", label="0")
    c1 = Connection(cd, "out1", va, "in1", label="1")
    # element of main cycle
    c20 = Connection(cons_closer, "out1", rp, "in1", label="20")
    c21 = Connection(rp, "out1", cd, "in2", label="21")
    c22 = Connection(cd, "out2", cons, "in1", label="22")
    c23 = Connection(cons, "out1", cons_closer, "in1", label="23")

    nw.add_conns(c0, c1, c20, c21, c22, c23)

    # parameters
    cd.set_attr(pr1=0.99, pr2=0.99)
    rp.set_attr(eta_s=0.75)
    cons.set_attr(pr=0.99)

    """ At the hot inlet of the condenser we define the temperature, pressure and the
fluid vector. A good guess for pressure can be obtained from CoolProp’s PropsSI function. We
know that the condensation temperature must be higher than the consumer’s feed flow
temperature. Therefore we can set the pressure to a slightly higher value of that temperature’s
corresponding condensation pressure"""

    p_cond = PSI("P", "Q", 1, "T", 273.15 + 95, working_fluid) / 1e5  # 273.15 K + 90 feed flow T + 5 so that condensation temp higher than 90
    c0.set_attr(T=170, p=p_cond, fluid={"water": 0, working_fluid: 1})
    c20.set_attr(T=60, p=2, fluid={"water": 1, working_fluid: 0})
    c22.set_attr(T=90)

    # key design parameter
    cons.set_attr(Q=-230e3)
    nw.solve("design")
    nw.print_results()
    #ploting(nw)
    return nw, c1, cd, c0, p_cond


def ploting(nw):
    # Extract the components and connections information
    components = nw.comps.keys()
    connections = nw.conns.keys()

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot the components
    for component in components:
        x = nw.comps[component].xs
        y = nw.comps[component].y
        ax.scatter(x, y, label=component)

    # Plot the connections
    for connection in connections:
        x = [nw.conns[connection].inl.x, nw.conns[connection].outl.x]
        y = [nw.conns[connection].inl.y, nw.conns[connection].outl.y]
        ax.plot(x, y, '-', label=connection)

    # Add labels and legend
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.legend()

    # Show the plot
    plt.show()


def valve_and_eva_element(nw, working_fluid, c1, cd, c0, p_cond):
    from tespy.components import (Valve, Drum, HeatExchanger, Source, Sink)

    # components
    # ambient heat source
    amb_in = Source("source ambient")
    amb_out = Sink("sink ambient")
    # evaporator system
    va = Valve("valve")
    dr = Drum("drum")
    ev = HeatExchanger("evaporator")
    su = HeatExchanger("superheater")
    # virtual source
    cp1 = Sink("compressor 1")

    # connections

    # del source from cons cycle und define new one
    nw.del_conns(c1)
    c1 = Connection(cd, "out1", va, "in1", label="1")

    c2 = Connection(va, "out1", dr, "in1", label="2")
    c3 = Connection(dr, "out1", ev, "in2", label="3")  # just boiling liquid to ev as cold side, x = 0
    c4 = Connection(ev, "out2", dr, "in2", label="4")
    c5 = Connection(dr, "out2", su, "in2", label="5")  # saturated steam to superheater as cold side, x = 1
    c6 = Connection(su, "out2", cp1, "in1", label="6")
    nw.add_conns(c1, c2, c3, c4, c5, c6)

    c17 = Connection(amb_in, "out1", su, "in1", label="17")
    c18 = Connection(su, "out1", ev, "in1", label="18")
    c19 = Connection(ev, "out1", amb_out, "in1", label="19")
    nw.add_conns(c17, c18, c19)

    # parameter
    # set p after the valve by selecting the pressure in drum. Cold side
    p_evap = PSI("P", "Q", 1, "T", 273.15 + 5, working_fluid) / 1e5
    c4.set_attr(x=0.9, p=p_evap)

    # set parameter after superheating. Cold side
    h_sat = PSI("H", "Q", 1, "T", 273.15 + 15, working_fluid) / 1e3
    c6.set_attr(h=h_sat)

    # evaporator system hot side
    c17.set_attr(T=15, fluid={"water": 1, working_fluid: 0})
    c19.set_attr(T=9, p=1.013)

    # set pressures
    ev.set_attr(pr1=0.99)
    su.set_attr(pr1=0.99, pr2=0.99)

    nw.solve("design")
    nw.print_results()
    return nw, c6, c17, su, c0, cd, c1, c5, p_cond


def compressor_element(nw, working_fluid,c6, c17, su, c0, cd, c1, c5, p_cond):
    from tespy.components import Compressor, Splitter, Merge, HeatExchanger, Pump, Valve, Source, CycleCloser

    # components
    cp1 = Compressor("compressor 1")
    cp2 = Compressor("compressor 2")
    ic = HeatExchanger("intermittent cooling")
    hsp = Pump("heat source pump")
    sp = Splitter("splitter")
    me = Merge("merge")
    cv = Valve("control valve")
    hs = Source("ambient intake")
    cc = CycleCloser("heat pump cycle closer")

    # connections
    # del old connections and add the new ones
    nw.del_conns(c0, c6, c17)
    c0 = Connection(cc, "out1", cd, "in1", label="0")  # change from easy source to cycle closer
    c6 = Connection(su, "out2", cp1, "in1", label="6")  # change from easy sink to a compressor
    c17 = Connection(me, "out1", su, "in1", label="17")  # change from easy source to out of a merge system

    c7 = Connection(cp1, "out1", ic, "in1", label="7")
    c8 = Connection(ic, "out1", cp2, "in1", label="8")
    c9 = Connection(cp2, "out1", cc, "in1", label="9")

    c11 = Connection(hs, "out1", hsp, "in1", label="11")
    c12 = Connection(hsp, "out1", sp, "in1", label="12")
    c13 = Connection(sp, "out1", ic, "in2", label="13")
    c14 = Connection(ic, "out2", me, "in1", label="14")
    c15 = Connection(sp, "out2", cv, "in1", label="15")
    c16 = Connection(cv, "out1", me, "in2", label="16")

    nw.add_conns(c6, c7, c8, c9, c0, c11, c12, c13, c14, c15, c16, c17)

    # parameter
    pr = (c1.p.val / c5.p.val) ** 0.5
    cp1.set_attr(pr=pr)
    ic.set_attr(pr1=0.99, pr2=0.98)
    hsp.set_attr(eta_s=0.75)

    c0.set_attr(p=p_cond, fluid={"water": 0, working_fluid: 1})

    c6.set_attr(h=c5.h.val + 10)
    c8.set_attr(h=c5.h.val + 10)
    c7.set_attr(h=c5.h.val * 1.2)
    c9.set_attr(h=c5.h.val * 1.2)
    c11.set_attr(p=1.013, T=15, fluid={"water": 1, working_fluid: 0})
    c14.set_attr(T=30)

    nw.solve("design")
    nw.print_results()


if __name__ =='__main__':
    nw, working_fluid = network_nw()
    nw, c1, cd, c0, p_cond = consumer_element(nw, working_fluid)
    # only c1 and cd because c1 is connection to new element. cd is component connected by c1 to the new element. c0 for the element after valve and eva
    nw, c6, c17, su, c0, cd, c1, c5, p_cond = valve_and_eva_element(nw, working_fluid, c1, cd, c0, p_cond)
    # (c6, c17 --> su) and (c0 --> cd) and (c1, c5 for pressure values)
    compressor_element(nw, working_fluid,c6, c17, su, c0, cd, c1, c5, p_cond)
