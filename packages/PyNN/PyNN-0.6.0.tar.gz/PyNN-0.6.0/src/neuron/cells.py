# encoding: utf-8
"""
Standard cells for the neuron module.

$Id: cells.py 704 2010-02-03 14:18:33Z apdavison $
"""

from pyNN import common, cells
from neuron import h, nrn, hclass
from math import pi
import logging

logger = logging.getLogger("PyNN")

def _new_property(obj_hierarchy, attr_name):
    """
    Returns a new property, mapping attr_name to obj_hierarchy.attr_name.
    
    For example, suppose that an object of class A has an attribute b which
    itself has an attribute c which itself has an attribute d. Then placing
      e = _new_property('b.c', 'd')
    in the class definition of A makes A.e an alias for A.b.c.d
    """
    def set(self, value):
        obj = reduce(getattr, [self] + obj_hierarchy.split('.'))
        setattr(obj, attr_name, value)
    def get(self):
        obj = reduce(getattr, [self] + obj_hierarchy.split('.'))
        return getattr(obj, attr_name)
    return property(fset=set, fget=get)


class SingleCompartmentNeuron(nrn.Section):
    """docstring"""
    
    synapse_models = {
        'current':      { 'exp': h.ExpISyn, 'alpha': h.AlphaISyn },
        'conductance' : { 'exp': h.ExpSyn,  'alpha': h.AlphaSyn },
    }

    def __init__(self, syn_type, syn_shape, c_m, i_offset,
                 v_init, tau_e, tau_i, e_e, e_i):
        
        # initialise Section object with 'pas' mechanism
        nrn.Section.__init__(self)
        self.seg = self(0.5)
        self.L = 100
        self.seg.diam = 1000/pi # gives area = 1e-3 cm2
                
        self.syn_type = syn_type
        self.syn_shape = syn_shape
        self.v_init = v_init
        
        # insert synapses
        assert syn_type in ('current', 'conductance'), "syn_type must be either 'current' or 'conductance'. Actual value is %s" % syn_type
        assert syn_shape in ('alpha', 'exp'), "syn_type must be either 'alpha' or 'exp'"
        synapse_model = StandardIF.synapse_models[syn_type][syn_shape]
        self.esyn = synapse_model(0.5, sec=self)
        self.isyn = synapse_model(0.5, sec=self)
        if self.syn_type == 'conductance' and self.syn_shape == 'exp':
            self.esyn_TM = h.tmgsyn(0.5, sec=self)
            self.isyn_TM = h.tmgsyn(0.5, sec=self)
        
        # insert current source
        self.stim = h.IClamp(0.5, sec=self)
        self.stim.delay = 0
        self.stim.dur = 1e12
        self.stim.amp = i_offset

        # for recording spikes
        self.spike_times = h.Vector(0)
        self.gsyn_trace = {}
        self.recording_time = 0
        

    @property
    def excitatory(self):
        return self.esyn

    @property
    def inhibitory(self):
        return self.isyn
    
    @property
    def excitatory_TM(self):
        if hasattr(self, 'esyn_TM'):
            return self.esyn_TM
        else:
            return None

    @property
    def inhibitory_TM(self):
        if hasattr(self, 'isyn_TM'):
            return self.isyn_TM
        else:
            return None

    def area(self):
        """Membrane area in µm²"""
        return pi*self.L*self.seg.diam

    c_m      = _new_property('seg', 'cm')
    i_offset = _new_property('stim', 'amp')
    
    def _get_tau_e(self):
        return self.esyn.tau
    def _set_tau_e(self, value):
        self.esyn.tau = value
        if hasattr(self, 'esyn_TM'):
            self.esyn_TM.tau = value
    tau_e = property(fget=_get_tau_e, fset=_set_tau_e)
    
    def _get_tau_i(self):
        return self.isyn.tau
    def _set_tau_i(self, value):
        self.isyn.tau = value
        if hasattr(self, 'isyn_TM'):
            self.isyn_TM.tau = value
    tau_i = property(fget=_get_tau_i, fset=_set_tau_i)
    
    def _get_e_e(self):
        return self.esyn.e
    def _set_e_e(self, value):
        self.esyn.e = value
        if hasattr(self, 'esyn_TM'):
            self.esyn_TM.e = value
    e_e = property(fget=_get_e_e, fset=_set_e_e)
    
    def _get_e_i(self):
        return self.isyn.e
    def _set_e_i(self, value):
        self.isyn.e = value
        if hasattr(self, 'isyn_TM'):
            self.isyn_TM.e = value
    e_i = property(fget=_get_e_i, fset=_set_e_i)
    
    def record(self, active):
        if active:
            rec = h.NetCon(self.source, None)
            rec.record(self.spike_times)
    
    def record_v(self, active):
        if active:
            self.vtrace = h.Vector()
            self.vtrace.record(self(0.5)._ref_v)
            if not self.recording_time:
                self.record_times = h.Vector()
                self.record_times.record(h._ref_t)
                self.recording_time += 1
        else:
            self.vtrace = None
            self.recording_time -= 1
            if self.recording_time == 0:
                self.record_times = None
    
    def record_gsyn(self, syn_name, active):
        # how to deal with static and T-M synapses?
        # record both and sum?
        if active:
            self.gsyn_trace[syn_name] = h.Vector()
            self.gsyn_trace[syn_name].record(getattr(self, syn_name)._ref_g)
            if not self.recording_time:
                self.record_times = h.Vector()
                self.record_times.record(h._ref_t)
                self.recording_time += 1
        else:
            self.gsyn_trace[syn_name] = None
            self.recording_time -= 1
            if self.recording_time == 0:
                self.record_times = None
    
    def memb_init(self, v_init=None):
        if v_init:
            self.v_init = v_init
        assert self.v_init is not None, "cell is a %s" % self.__class__.__name__
        for seg in self:
            seg.v = self.v_init
        #self.seg.v = self.v_init

    def set_Tsodyks_Markram_synapses(self, ei, U, tau_rec, tau_facil, u0):
        if self.syn_type == 'current':
            raise Exception("Tsodyks-Markram mechanism only available for conductance-based synapses.")
        elif self.syn_shape == 'alpha':
            raise Exception("Tsodyks-Markram mechanism not available for alpha-function-shaped synapses.")
        elif ei == 'excitatory':
            syn = self.esyn_TM
        elif ei == 'inhibitory':
            syn = self.isyn_TM
        else:
            raise Exception("Tsodyks-Markram mechanism not yet implemented for user-defined synapse types. ei = %s" % ei)
        syn.U = U
        syn.tau_rec = tau_rec
        syn.tau_facil = tau_facil
        syn.u0 = u0

    def set_parameters(self, param_dict):
        for name in self.parameter_names:
            setattr(self, name, param_dict[name])


class LeakySingleCompartmentNeuron(SingleCompartmentNeuron):
    
    def __init__(self, syn_type, syn_shape, tau_m, c_m, v_rest, i_offset,
                 v_init, tau_e, tau_i, e_e, e_i):
        SingleCompartmentNeuron.__init__(self, syn_type, syn_shape, c_m, i_offset,
                                         v_init, tau_e, tau_i, e_e, e_i)
        self.insert('pas')
        
    def __set_tau_m(self, value):
        #print "setting tau_m to", value, "cm =", self.seg.cm
        self.seg.pas.g = 1e-3*self.seg.cm/value # cm(nF)/tau_m(ms) = G(uS) = 1e-6G(S). Divide by area (1e-3) to get factor of 1e-3
    def __get_tau_m(self):
        #print "tau_m = ", 1e-3*self.seg.cm/self.seg.pas.g, "cm = ", self.seg.cm
        return 1e-3*self.seg.cm/self.seg.pas.g

    def __get_cm(self):
        #print "cm = ", self.seg.cm
        return self.seg.cm
    def __set_cm(self, value): # when we set cm, need to change g to maintain the same value of tau_m
        #print "setting cm to", value
        tau_m = self.tau_m
        self.seg.cm = value
        self.tau_m = tau_m

    v_rest = _new_property('seg.pas', 'e')
    tau_m  = property(fget=__get_tau_m, fset=__set_tau_m)
    c_m    = property(fget=__get_cm, fset=__set_cm) # if the property were called 'cm'
                                                    # it would never get accessed as the
                                                    # built-in Section.cm would always
                                                    # be used first


class StandardIF(LeakySingleCompartmentNeuron):
    """docstring"""
    
    def __init__(self, syn_type, syn_shape, tau_m=20, c_m=1.0, v_rest=-65,
                 v_thresh=-55, t_refrac=2, i_offset=0, v_reset=None,
                 v_init=None, tau_e=5, tau_i=5, e_e=0, e_i=-70):
        if v_init is None:
            v_init = v_rest
        if v_reset is None:
            v_reset = v_rest
        LeakySingleCompartmentNeuron.__init__(self, syn_type, syn_shape, tau_m, c_m, v_rest,
                                              i_offset, v_init, tau_e, tau_i, e_e, e_i)       
        # insert spike reset mechanism
        self.spike_reset = h.ResetRefrac(0.5, sec=self)
        self.spike_reset.vspike = 40 # (mV) spike height
        self.source = self.spike_reset
        
        # process arguments
        self.parameter_names = ['c_m', 'tau_m', 'v_rest', 'v_thresh', 't_refrac',   # 'c_m' must come before 'tau_m'
                                'i_offset', 'v_reset', 'v_init', 'tau_e', 'tau_i']
        if syn_type == 'conductance':
            self.parameter_names.extend(['e_e', 'e_i'])
        self.set_parameters(locals())
        

    v_thresh = _new_property('spike_reset', 'vthresh')
    v_reset  = _new_property('spike_reset', 'vreset')
    t_refrac = _new_property('spike_reset', 'trefrac')


class BretteGerstnerIF(LeakySingleCompartmentNeuron):
    """docstring"""
    
    def __init__(self, syn_type, syn_shape, tau_m=20, c_m=1.0, v_rest=-65,
                 v_thresh=-55, t_refrac=2, i_offset=0,
                 v_init=None, tau_e=5, tau_i=5, e_e=0, e_i=-70,
                 v_spike=0.0, v_reset=-70.6, A=4.0, B=0.0805, tau_w=144.0,
                 w_init=0.0, delta=2.0):
        if v_init is None:
            v_init = v_rest
        LeakySingleCompartmentNeuron.__init__(self, syn_type, syn_shape, tau_m,
                                              c_m, v_rest, i_offset, v_init,
                                              tau_e, tau_i, e_e, e_i)
    
        # insert Brette-Gerstner spike mechanism
        self.adexp = h.AdExpIF(0.5, sec=self)
        self.source = self.seg._ref_v
        
        self.parameter_names = ['c_m', 'tau_m', 'v_rest', 'v_thresh', 't_refrac',
                                'i_offset', 'v_reset', 'v_init', 'tau_e', 'tau_i',
                                'A', 'B', 'tau_w', 'delta', 'w_init', 'v_spike']
        if syn_type == 'conductance':
            self.parameter_names.extend(['e_e', 'e_i'])
        self.set_parameters(locals())
    
    v_thresh = _new_property('adexp', 'vthresh')
    v_reset  = _new_property('adexp', 'vreset')
    t_refrac = _new_property('adexp', 'trefrac')
    B        = _new_property('adexp',  'b')
    A        = _new_property('adexp',  'a')
    ## using 'A' because for some reason, cell.a gives the error "NameError: a, the mechanism does not exist at PySec_170bb70(0.5)"   
    tau_w    = _new_property('adexp',  'tauw')
    delta    = _new_property('adexp',  'delta')
    w_init   = _new_property('adexp',  'winit') # w_init not defined in .mod file - needs to be
    #v_init   = _new_property('seg',  'v') #?? something involving FInitialize
    
    def __set_v_spike(self, value):
        self.adexp.vspike = value
        self.adexp.vpeak = value + 10.0
    def __get_v_spike(self):
        return self.adexp.vspike
    v_spike = property(fget=__get_v_spike, fset=__set_v_spike)
    
    def __set_tau_m(self, value):
        self.seg.pas.g = 1e-3*self.seg.cm/value # cm(nF)/tau_m(ms) = G(uS) = 1e-6G(S). Divide by area (1e-3) to get factor of 1e-3
        self.adexp.GL = self.seg.pas.g * self.area() * 1e-2 # S/cm2 to uS
    def __get_tau_m(self):
        return 1e-3*self.seg.cm/self.seg.pas.g
    
    def __set_v_rest(self, value):
        self.seg.pas.e = value
        self.adexp.EL = value
    def __get_v_rest(self):
        return self.seg.pas.e
    tau_m  = property(fget=__get_tau_m, fset=__set_tau_m)   
    v_rest = property(fget=__get_v_rest, fset=__set_v_rest)
    
    def record(self, active):
        if active:
            self.rec = h.NetCon(self.source, None,
                                self.get_threshold(), 0.0, 0.0,
                                sec=self)
            self.rec.record(self.spike_times)

    def get_threshold(self):
        return self.adexp.vspike

class SingleCompartmentTraub(SingleCompartmentNeuron):
    
    def __init__(self, syn_type, syn_shape, c_m=1.0, e_leak=-65,
                 i_offset=0, v_init=None, tau_e=5, tau_i=5, e_e=0, e_i=-70,
                 gbar_Na=20000, gbar_K=6000, g_leak=10, ena=50,
                 ek=-90, v_offset=-63):
        if v_init is None:
            v_init = v_rest
        SingleCompartmentNeuron.__init__(self, syn_type, syn_shape, c_m, i_offset,
                                         v_init, tau_e, tau_i, e_e, e_i)
        self.source = self.seg._ref_v
        self.insert('k_ion')
        self.insert('na_ion')
        self.insert('hh_traub')
        self.parameter_names = ['c_m', 'e_leak', 'i_offset', 'v_init', 'tau_e',
                                'tau_i', 'gbar_Na', 'gbar_K', 'g_leak', 'ena',
                                'ek', 'v_offset']
        if syn_type == 'conductance':
            self.parameter_names.extend(['e_e', 'e_i'])
        self.set_parameters(locals())

    # not sure ena and ek are handled correctly
    
    e_leak   = _new_property('seg.hh_traub', 'el')
    v_offset = _new_property('seg.hh_traub', 'vT')
    gbar_Na  = _new_property('seg.hh_traub', 'gnabar')
    gbar_K   = _new_property('seg.hh_traub', 'gkbar')
    g_leak   = _new_property('seg.hh_traub', 'gl')
    
    def get_threshold(self):
        return 10.0
    
    
class RandomSpikeSource(hclass(h.NetStimFD)):
    
    parameter_names = ('start', '_interval', 'duration')
    
    def __init__(self, start=0, _interval=1e12, duration=0):
        self.start = start
        self.interval = _interval
        self.duration = duration
        self.noise = 1
        self.spike_times = h.Vector(0)
        self.source = self
        self.switch = h.NetCon(None, self)

    def _set_interval(self, value):
        self.switch.weight[0] = -1
        self.switch.event(h.t+1e-12, 0)
        self.interval = value
        self.switch.weight[0] = 1
        self.switch.event(h.t+2e-12, 1)
    def _get_interval(self):
        return self.interval
    _interval = property(fget=_get_interval, fset=_set_interval)

    def record(self, active):
        if active:
            self.rec = h.NetCon(self, None)
            self.rec.record(self.spike_times)


class VectorSpikeSource(hclass(h.VecStim)):

    parameter_names = ('spike_times',)

    def __init__(self, spike_times=[]):
        self.spike_times = spike_times
        self.source = self
            
    def _set_spike_times(self, spike_times):
        try:
            self._spike_times = h.Vector(spike_times)
        except RuntimeError:
            raise common.InvalidParameterValueError("spike_times must be an array of floats")
        self.play(self._spike_times)
            
    def _get_spike_times(self):
        return self._spike_times
            
    spike_times = property(fget=_get_spike_times,
                           fset=_set_spike_times)
            
    def record(self, active):
        """
        Since spike_times are specified by user, recording is meaningless, but
        we need to provide a stub for consistency with other models.
        """
        pass
    
            
# == Standard cells ============================================================

class IF_curr_alpha(cells.IF_curr_alpha):
    """Leaky integrate and fire model with fixed threshold and alpha-function-
    shaped post-synaptic current."""
    
    translations = common.build_translations(
        ('tau_m',      'tau_m'),
        ('cm',         'c_m'),
        ('v_rest',     'v_rest'),
        ('v_thresh',   'v_thresh'),
        ('v_reset',    'v_reset'),
        ('tau_refrac', 't_refrac'),
        ('i_offset',   'i_offset'),
        ('tau_syn_E',  'tau_e'),
        ('tau_syn_I',  'tau_i'),
        ('v_init',     'v_init'),
    )
    model = StandardIF
    
    def __init__(self, parameters):
        cells.IF_curr_alpha.__init__(self, parameters) # checks supplied parameters and adds default
                                                        # values for not-specified parameters.
        self.parameters['syn_type']  = 'current'
        self.parameters['syn_shape'] = 'alpha'

class IF_curr_exp(cells.IF_curr_exp):
    """Leaky integrate and fire model with fixed threshold and
    decaying-exponential post-synaptic current. (Separate synaptic currents for
    excitatory and inhibitory synapses."""
    
    translations = common.build_translations(
        ('tau_m',      'tau_m'),
        ('cm',         'c_m'),
        ('v_rest',     'v_rest'),
        ('v_thresh',   'v_thresh'),
        ('v_reset',    'v_reset'),
        ('tau_refrac', 't_refrac'),
        ('i_offset',   'i_offset'),
        ('tau_syn_E',  'tau_e'),
        ('tau_syn_I',  'tau_i'),
        ('v_init',     'v_init'),
    )
    model = StandardIF
    
    def __init__(self, parameters):
        cells.IF_curr_exp.__init__(self, parameters)
        self.parameters['syn_type']  = 'current'
        self.parameters['syn_shape'] = 'exp'


class IF_cond_alpha(cells.IF_cond_alpha):
    """Leaky integrate and fire model with fixed threshold and alpha-function-
    shaped post-synaptic conductance."""
    
    translations = common.build_translations(
        ('tau_m',      'tau_m'),
        ('cm',         'c_m'),
        ('v_rest',     'v_rest'),
        ('v_thresh',   'v_thresh'),
        ('v_reset',    'v_reset'),
        ('tau_refrac', 't_refrac'),
        ('i_offset',   'i_offset'),
        ('tau_syn_E',  'tau_e'),
        ('tau_syn_I',  'tau_i'),
        ('v_init',     'v_init'),
        ('e_rev_E',    'e_e'),
        ('e_rev_I',    'e_i')
    )
    model = StandardIF
    
    def __init__(self, parameters):
        cells.IF_cond_alpha.__init__(self, parameters) # checks supplied parameters and adds default
                                                       # values for not-specified parameters.
        self.parameters['syn_type']  = 'conductance'
        self.parameters['syn_shape'] = 'alpha'


class IF_cond_exp(cells.IF_cond_exp):
    """Leaky integrate and fire model with fixed threshold and 
    exponentially-decaying post-synaptic conductance."""
    
    translations = common.build_translations(
        ('tau_m',      'tau_m'),
        ('cm',         'c_m'),
        ('v_rest',     'v_rest'),
        ('v_thresh',   'v_thresh'),
        ('v_reset',    'v_reset'),
        ('tau_refrac', 't_refrac'),
        ('i_offset',   'i_offset'),
        ('tau_syn_E',  'tau_e'),
        ('tau_syn_I',  'tau_i'),
        ('v_init',     'v_init'),
        ('e_rev_E',    'e_e'),
        ('e_rev_I',    'e_i')
    )
    model = StandardIF
    
    def __init__(self, parameters):
        cells.IF_cond_exp.__init__(self, parameters) # checks supplied parameters and adds default
                                                       # values for not-specified parameters.
        self.parameters['syn_type']  = 'conductance'
        self.parameters['syn_shape'] = 'exp'


class IF_facets_hardware1(cells.IF_facets_hardware1):
    """Leaky integrate and fire model with conductance-based synapses and fixed
    threshold as it is resembled by the FACETS Hardware Stage 1. For further
    details regarding the hardware model see the FACETS-internal Wiki:
    https://facets.kip.uni-heidelberg.de/private/wiki/index.php/WP7_NNM
    """

    translations = common.build_translations(
        ('v_rest',     'v_rest'),
        ('v_thresh',   'v_thresh'),
        ('v_reset',    'v_reset'),
        ('g_leak',     'tau_m',    "0.2*1000.0/g_leak", "0.2*1000.0/tau_m"),
        ('tau_syn_E',  'tau_e'),
        ('tau_syn_I',  'tau_i'),
        ('e_rev_I',    'e_i')
    )
    model = StandardIF

    def __init__(self, parameters):
        cells.IF_facets_hardware1.__init__(self, parameters)
        self.parameters['syn_type']  = 'conductance'
        self.parameters['syn_shape'] = 'exp'
        self.parameters['i_offset']  = 0.0
        self.parameters['c_m']       = 0.2
        self.parameters['t_refrac']  = 1.0
        self.parameters['e_e']       = 0.0
    
       
class HH_cond_exp(cells.HH_cond_exp):
    
    translations = common.build_translations(
        ('gbar_Na',    'gbar_Na', 1e-6),   
        ('gbar_K',     'gbar_K', 1e-6),    
        ('g_leak',     'g_leak', 1e-6),    
        ('cm',         'c_m'),  
        ('v_offset',   'v_offset'),
        ('e_rev_Na',   'ena'),
        ('e_rev_K',    'ek'), 
        ('e_rev_leak', 'e_leak'),
        ('e_rev_E',    'e_e'),
        ('e_rev_I',    'e_i'),
        ('tau_syn_E',  'tau_e'),
        ('tau_syn_I',  'tau_i'),
        ('i_offset',   'i_offset'),
        ('v_init',     'v_init'),
    )
    model = SingleCompartmentTraub

    def __init__(self, parameters):
        cells.HH_cond_exp.__init__(self, parameters) # checks supplied parameters and adds default
                                                     # values for not-specified parameters.
        self.parameters['syn_type']  = 'conductance'
        self.parameters['syn_shape'] = 'exp'

class SpikeSourcePoisson(cells.SpikeSourcePoisson):
    """Spike source, generating spikes according to a Poisson process."""

    translations = common.build_translations(
        ('start',    'start'),
        ('rate',     '_interval',  "1000.0/rate",  "1000.0/_interval"),
        ('duration', 'duration'),
    )
    model = RandomSpikeSource


class SpikeSourceArray(cells.SpikeSourceArray):
    """Spike source generating spikes at the times given in the spike_times array."""

    translations = common.build_translations(
        ('spike_times', 'spike_times'),
    )
    model = VectorSpikeSource
       
        
class EIF_cond_alpha_isfa_ista(cells.EIF_cond_alpha_isfa_ista):
    """
    Exponential integrate and fire neuron with spike triggered and sub-threshold
    adaptation currents (isfa, ista reps.) according to:
    
    Brette R and Gerstner W (2005) Adaptive Exponential Integrate-and-Fire Model as
    an Effective Description of Neuronal Activity. J Neurophysiol 94:3637-3642

    See also: IF_cond_exp_gsfa_grr
    """
    
    translations = common.build_translations(
        ('v_init',     'v_init'),
        ('w_init',     'w_init'),
        ('cm',         'c_m'),
        ('tau_refrac', 't_refrac'), 
        ('v_spike',    'v_spike'),
        ('v_reset',    'v_reset'),
        ('v_rest',     'v_rest'),
        ('tau_m',      'tau_m'),
        ('i_offset',   'i_offset'), 
        ('a',          'A',        0.001), # nS --> uS
        ('b',          'B'),
        ('delta_T',    'delta'), 
        ('tau_w',      'tau_w'), 
        ('v_thresh',   'v_thresh'), 
        ('e_rev_E',    'e_e'),
        ('tau_syn_E',  'tau_e'), 
        ('e_rev_I',    'e_i'), 
        ('tau_syn_I',  'tau_i'),
    )
    model = BretteGerstnerIF
    
    def __init__(self, parameters):
        cells.EIF_cond_alpha_isfa_ista.__init__(self, parameters)
        self.parameters['syn_type']  = 'conductance'
        self.parameters['syn_shape'] = 'alpha'

class EIF_cond_exp_isfa_ista(cells.EIF_cond_exp_isfa_ista):
    """Like EIF_cond_alpha_isfa_ista, but with single-exponential synapses."""
    
    translations = EIF_cond_alpha_isfa_ista.translations
    model = BretteGerstnerIF
    
    def __init__(self, parameters):
        cells.EIF_cond_exp_isfa_ista.__init__(self, parameters)
        self.parameters['syn_type']  = 'conductance'
        self.parameters['syn_shape'] = 'exp'