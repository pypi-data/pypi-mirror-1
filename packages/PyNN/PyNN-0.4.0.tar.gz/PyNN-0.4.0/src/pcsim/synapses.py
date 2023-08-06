# ==============================================================================
# Synapse Dynamics classes for pcsim
# $Id: synapses.py 296 2008-04-04 12:15:18Z apdavison $
# ==============================================================================

from pyNN import common


class SynapseDynamics(common.SynapseDynamics):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Dynamic synapses are not available for this simulator.")

class STDPMechanism(common.STDPMechanism):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("STDP is not available for this simulator.")

class TsodkysMarkramMechanism(common.ModelNotAvailable):
    pass

class AdditiveWeightDependence(common.ModelNotAvailable):
    pass

class MultiplicativeWeightDependence(common.ModelNotAvailable):
    pass

class SpikePairRule(common.ModelNotAvailable):
    pass
