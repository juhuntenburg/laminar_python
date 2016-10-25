# Python tools for laminar analysis of the cortical sheet.

This repository contains Python versions of several modules of [CBS Tools](https://www.nitrc.org/projects/cbs-tools/) that are useful for laminar
analysis. [1] [2]

### How to use laminar_python

1. Clone this repository

   `git clone https://github.com/juhuntenburg/laminar_python.git`

2. Download and unpack the Python egg containing the cbstools compiled in Python:
https://github.com/piloubazin/cbstools-public/blob/master/python/cbstoolsjcc-python.tar.gz

   `tar -xf cbstoolsjcc-python.tar.gz`

3. Add the location of the unpacked Python egg directory to your PYTHONPATH

   `export PYTHONPATH=$PYTHONPATH:/path/to/eggdirectory/`


You should now be able to import the modules in Python. Try:
```python
import volumetric_layering
```

[1] Bazin et al. (2014). A computational framework for ultra-high resolution cortical segmentation at 7Tesla. http://doi.org/10.1016/j.neuroimage.2013.03.077

[2] Waehnert et al. (2014). Anatomically motivated modeling of cortical
laminae. http://doi.org/10.1016/j.neuroimage.2013.03.078
