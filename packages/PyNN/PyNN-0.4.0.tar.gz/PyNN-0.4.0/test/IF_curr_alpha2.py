"""
Simple test to compare iaf_neuron in NEST with StandardIF in NEURON.

Andrew Davison, UNIC, CNRS
May 2006

$Id: IF_curr_alpha2.py 341 2008-06-05 14:25:49Z apdavison $
"""

import sys

if hasattr(sys,"argv"):     # run using python
    simulator = sys.argv[-1]
else:
    simulator = "neuron"    # run using nrngui -python


exec("from pyNN.%s import *" % simulator)


id = setup(timestep=0.01,min_delay=0.1)

ifcells = create(IF_curr_alpha, {'i_offset' : 0.1, 'tau_refrac' : 0.1, 'v_thresh' : -52.2},n=5)

spike_source = create(SpikeSourceArray, {'spike_times': [0.1*float(i) for i in range(1,1001,1)]})

conn = connect(spike_source,ifcells,weight=1.5)

record_v(ifcells[0],"IF_curr_alpha2_%s.v" % simulator)
run(100.0)

end()

