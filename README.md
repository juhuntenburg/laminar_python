# laminar_python
Tools for laminar analysis of the cortical sheet in Python. Most modules are Python versions of [CBS Tools](https://www.nitrc.org/projects/cbs-tools/)

## How to use this repo

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
