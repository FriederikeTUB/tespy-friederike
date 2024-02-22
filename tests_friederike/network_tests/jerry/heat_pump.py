from tespy.networks import Network
from tespy.components import (HeatExchanger, Compressor, CycleCloser, Valve, Source, Sink)
from tespy.connections import Connection, Bus
from CoolProp.CoolProp import PropsSI as CPSI
from tespy.tools import ExergyAnalysis
from tespy.tools.helpers import get_chem_ex_lib
chemexlib = get_chem_ex_lib("Ahrendts")
#import plotly.graph_objects as go

wf = 'R1233ZD(E)'       # REFPROP::
si = 'H2O'              # REFPROP::

# Definition des Netwerks
nw = Network(fluids=[wf, si], T_unit='C', p_unit='bar', h_unit='kJ / kg', m_unit='kg / s', Q_unit='kW')

# Definition der Komponenten
GK = HeatExchanger('Gaskühler')
VD = HeatExchanger('Verdampfer')
DR = Valve('Drossel')
KP = Compressor('Kompressor')

# Definition der Quelle, Senke und des Kreislaufzusammenschlusses
se_ein = Source('Senke ein')
se_aus = Sink('Senke aus')

qu_ein = Source('Quelle ein')
qu_aus = Sink('Quelle aus')

KR = CycleCloser('Kreislaufzusammenschluss')

# Verbindungen des Kreislaufs
c21 = Connection(KR, 'out1', GK, 'in1', label="21")
c22 = Connection(GK, 'out1', DR, 'in1', label="22")
c23 = Connection(DR, 'out1', VD, 'in2', label="23")
c24 = Connection(VD, 'out2', KP, 'in1', label="24")
c21_cc = Connection(KP, 'out1', KR, 'in1', label="21_cc")

# Verbindungen der Quelle
c11 = Connection(qu_ein, 'out1', VD, 'in1', label="11")
c12 = Connection(VD, 'out1', qu_aus, 'in1', label="12")

# Verbindungen der Senke
c13 = Connection(se_ein, 'out1', GK, 'in2', label="13")
c14 = Connection(GK, 'out2', se_aus, 'in1', label="14")

nw.add_conns(c21, c22, c23, c24, c21_cc, c11, c12, c13, c14)

# Setzen der Startparameter für die Komponenten
GK.set_attr(pr1=1, pr2=1, Q=-1e7)
VD.set_attr(pr1=1, pr2=1)
KP.set_attr(eta_s=0.76)

# Setzen Startparameter der Verbindungen des Kreislaufs
h_c22 = CPSI("H", "P", 57 * 1e5, "T", 273.15+165, wf) * 1e-3
c22.set_attr(h=h_c22, p=57)

c23.set_attr(p=8.334)

h_c24 = CPSI("H", "P", 8.334 * 1e5, "T", 273.15+90.1, wf) * 1e-3
c24.set_attr(h=h_c24, fluid={'R1233ZD(E)': 1, 'H2O': 0})

# Setzen Startparameter der Verbindungen der Quelle
c11.set_attr(T=95, p=5, fluid={'R1233ZD(E)': 0, 'H2O': 1})
c12.set_attr(T=90)

# Setzen Startparameter der Verbindungen der Senke
c13.set_attr(T=160, p=20, fluid={'R1233ZD(E)': 0, 'H2O': 1})
c14.set_attr(T=190)

#Lösen des Netzwerks
nw.solve(mode='design')
nw.print_results()

#Setzen der Betriebsparameter
c22.set_attr(h=None, p=80.18)
GK.set_attr(ttd_l=10)
c23.set_attr(p=None)
VD.set_attr(ttd_l=5)
c24.set_attr(h=None, Td_bp=0.1)

# Definition der Energieströme
el = Bus('elektrische Leistung')
el.add_comps(
    {'comp': KP, 'char': 1, 'base': 'bus'})

wae_zu = Bus('Wärmequelle')
wae_zu.add_comps(
    {'comp': qu_ein, 'base': 'bus'},
    {'comp': qu_aus})

wae_ab = Bus('Wärmesenke')
wae_ab.add_comps(
    {'comp': se_ein, 'base': 'bus'},
    {'comp': se_aus})

nw.add_busses(el, wae_zu, wae_ab)

#Lösen des Netzwerks
nw.solve(mode='design')
nw.print_results()

#Durchführung der Exergianalyse
p_umg = 1
T_umg = 25

# exergy and exergoeconomic analysis
exe_eco_input = {'Gaskühler_Z': 5, 'Drossel_Z': 2, 'Kompressor_Z': 4, 'Verdampfer_Z': 4,
                 'Quelle ein_c': 0.02, 'Senke ein_c': 0.01, 'elektrische Leistung_c': 0.1}
ean = ExergyAnalysis(nw, E_P=[wae_ab], E_F=[el, wae_zu])
ean.analyse(pamb=p_umg, Tamb=T_umg)
ean.evaluate_exergoeconomics(Exe_Eco_Costs=exe_eco_input, Tamb=T_umg)
ean.print_results(Exe_Eco_An=True)

"""
# Erstellung des Grassmanndiagramms
links, nodes = ean.generate_plotly_sankey_input()
fig = go.Figure(go.Sankey(
    arrangement="snap",
    node={
        "label": nodes,
        'pad': 11,
        'color': 'orange'},
    link=links),
    layout=go.Layout({'width': 1450})
    )
fig.update_layout(
    font_size=20
)
fig.show()
"""
