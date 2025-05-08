Transition Systems from LTL Optimal Multi-Agent Planner (LOMAP)
=======================================

This is a bare-bones version of the LOMAP repository described below. It has been modified to support Python 3 and NetworkX 3.1, and only includes the functionality required to use transition systems.

LTL Optimal Multi-Agent Planner (LOMAP) is a python package for automatic
planning of optimal paths for multi-agent systems.
See the directory 'examples' (either in the source archive or in the
installation directory) for examples.

Copyright (C) 2012-2015, Alphan Ulusoy (alphan@bu.edu)

Copyright (C) 2013-2020, Cristian-Ioan Vasile (cvasile@lehigh.edu,
                                               cristian.ioan.vasile@gmail.com)

## Installation Instructions

Linux (Ubuntu) -- using Anaconda
1. Clone the _ts_ repository
  * Navigate to desired location
  * Run the following line in shell:

  ```bash
  git clone https://github.com/wpi-automata/ts.git
  ```

2. Install necessary dependencies:

  * Run the following lines in shell:

    ```bash
    conda create --name <desired env name>
    conda activate <desired env name>
    conda install matplotlib networkx numpy pyyaml
    ```

Perform either 3.a. or 3.b. depending on your operating system.

3.a. (Ubuntu only) Set `$PYTHONPATH` to include the location of the _lomap_ library:
  * Run the following line in shell:

      ```bash
      export PYTHONPATH="${PYTHONPATH}:/path/to/ts"
      ```

  * Optionally make this setting persistent:

      ```bash
      echo 'export PYTHONPATH="${PYTHONPATH}:/path/to/ts"' >> ~/.bashrc
      ```
3.b. (Windows) Install lomap to your Anaconda environment
* Activate your Anaconda environment (if not already active)

    ```
    conda activate <env name from step 2.>
    ```

* Navigate to the ts folder

* Install
    ```
    pip install -e .
    ```
    
4. Test if the setup worked properly:
  * Navigate to `/ts/lomap/tests`
  * Run any of the Python test files
    * Ex. `python test_yaml.py`

### Common Issues:
1. ```python
      ImportError: No module named lomap.classes
   ```
  * Problem: The _lomap_ library is not in the path variable `PYTHONPATH`
  * Possible Solution: Manually add the parent directory of _lomap_ to your Python directory
    ```bash
    cd <lomap_parent_directory>
    export PYTHONPATH="$PYTHONPATH:$PWD"
    ```

2. ```python
      File "/usr/bin/pip", line 9, in <module>
      from pip import main
      ImportError: cannot import name main
   ```
  * Problem: Wrong version of _pip_ (are using Python 3 _pip_)
  * Solution: Run commands with _pip2_

3. ```python
   AttributeError: 'Graph' object has no attribute 'nodes_iter' (or other graph issues)
   ```
  * Problem: Facing issue with compatibility between networkx 1.1 and 2.2
  * Solution: Navigate to file with error and delete the "_iter" portion


## Running 575 Project Code

Use environment.yml with the following command to make it work:

    ```bash
    conda env create -f environment.yml
    conda activate ts_spot_env
    ```

Example usage:

    ```bash
    python3 find_path_from_spec_and_ts.py ../tests/triangle_graph.yaml "F obs && ! F c" -o automaton.txt -p path.txt -s 100
    ```

# Copyright and Warranty Information

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.

A copy of the GNU General Public License is included in this
distribution, in a file called 'license.txt'.
