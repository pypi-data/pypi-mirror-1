#!/usr/bin/env python

from distutils.core import setup
from distutils.command.build import build as _build
import os

class build(_build):
    """Add nrnivmodl to the end of the build process."""

    def run(self):
        _build.run(self)
        nrnivmodl = self.find_nrnivmodl()
        if nrnivmodl:
            print "nrnivmodl found at", nrnivmodl
            import subprocess
            p = subprocess.Popen(nrnivmodl, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         close_fds=True, cwd=os.path.join(os.getcwd(),'build/lib/pyNN/hoc'))
            result = p.wait()
            # test if nrnivmodl was successful
            if result != 0:
                errorMsg = p.stderr.readlines()
                print "Unable to compile NEURON extensions. Error message was:"
                print errorMsg
            else:
                print "Successfully compiled NEURON extensions."
        else:
            print "Unable to find nrnivmodl. It will not be possible to use the pyNN.neuron module."
        
    def find_nrnivmodl(self):
        """Try to find the nrnivmodl executable."""
        path = os.environ.get("PATH", "").split(os.pathsep)
        nrnivmodl = ''
        for dir_name in path:
            abs_name = os.path.abspath(os.path.normpath(os.path.join(dir_name, "nrnivmodl")))
            if os.path.isfile(abs_name):
                nrnivmodl = abs_name
                break
        return nrnivmodl
      
setup(
    name = "PyNN",
    version = "0.4.0",
    package_dir={'pyNN': 'src'},
    packages = ['pyNN','pyNN.nest2','pyNN.nest1','pyNN.pcsim','pyNN.neuron'],
    package_data = {'pyNN': ['hoc/*.hoc', 'hoc/*.mod']},
    author = "The NeuralEnsemble Community",
    author_email = "davison at unic cnrs-gif fr",
    description = "A Python package for simulator-independent specification of neuronal network models",
    license = "CeCILL http://www.cecill.info/",
    keywords = "computational neuroscience simulation neuron nest pcsim neuroml",
    url = "http://neuralensemble.org/PyNN/",
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: Other/Proprietary License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering'],
    cmdclass = {'build': build},
)

