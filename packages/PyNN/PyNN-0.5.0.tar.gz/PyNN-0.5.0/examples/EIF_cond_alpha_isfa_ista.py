"""
Test of the EIF_cond_alpha_isfa_ista model

Andrew Davison, UNIC, CNRS
December 2007

$Id: EIF_cond_alpha_isfa_ista.py 647 2009-06-09 12:37:02Z apdavison $
"""

from pyNN.utility import get_script_args

simulator_name = get_script_args(1)[0]  
exec("from pyNN.%s import *" % simulator_name)


setup(timestep=0.01,min_delay=0.1,max_delay=4.0,debug=True)

ifcell = create(EIF_cond_alpha_isfa_ista,
                {'i_offset': 1.0, 'tau_refrac': 2.0, 'v_spike': -40})
print ifcell.get_parameters()
    
record_v(ifcell,"Results/EIF_cond_alpha_isfa_ista_%s.v" % simulator_name)
run(200.0)

end()

