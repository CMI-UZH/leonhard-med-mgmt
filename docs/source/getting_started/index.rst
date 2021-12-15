.. _getting_started:

Getting started
================

The ``clusty`` package simplifies executing workflows on a cluster environment, 
such as a high-performance computing 
(HPC) cluster, or even on cloud machines that require SSH authentication.

The tool can be run on an endpoint that has access to the cluster. After setting
up a configuration file, starting the tool will: 

#. Create a connection from your endpoint to the cluster (in a ``screen`` 
   session)
#. Submit a batch job on the cluster (in a ``screen`` session), requesting the 
   cluster resources specified in the configuration file.
#. Executing the commands specified in the configuration file. Optionally, 
   this can be done inside a ``singularity`` container.
#. If web apps such as ``jupyter`` are launched, the tool can also create 
   tunnels, facilitating access to the web apps. 


Installation
-------------

Installing the stable release
******************************
To install the latest stable release of 
`clusty from PyPI <https://pypi.org/project/clusty/>`_, run

.. code-block:: bash

  pip install clusty


Installing the development version
************************************
To install the development version of 
`clusty from github <https://github.com/uzh-dqbm-cmi/clusty>`_, run

.. code-block:: bash

  pip install git+https://github.com/uzh-dqbm-cmi/clusty.git


Preparation
-----------
Setting up your SSH configuration
*********************************

For ``clusty`` to reach a cluster, you first need to configure your SSH connection 
so that you can access the cluster via a ``cluster-ssh-alias``. Furthermore, you need to 
``ssh-add`` all the required identities to the ``ssh-agent``. To test your SSH 
access, connect to the cluster by running

.. code-block:: bash

  ssh <cluster-ssh-alias>


``Clusty`` configuration file
**********************************

To define a workflow that can be executed via ``clusty``, you need to set up a  
``.yaml`` configuration file. The 
`example.yaml <https://github.com/uzh-dqbm-cmi/clusty/blob/master/example.yaml>`_ 
can serve as a starting point. It consists of two main sections: a cluster 
definition and a job definition.

Cluster definition
...................

The ``cluster`` definition specifies the cluster, the order of jobs that should be 
executed, and, optionally, a list of tunnel bindings. The jobs are only listed
here. Their definition happens in the ``batch_jobs`` section below.

.. code-block:: yaml

  # Cluster definition: define which cluster the user wants to use
  cluster:
    id: leomed                      # Identifies the class to be used for login and other procedures
    host: medinfmk                  # Name of ssh host to use to connect to (not required: default is set by cluster class)
    setup: False                    # Define if the setup of the cluster in the ssh local file is necessary (not required)
    batch_jobs:                     # List of batch jobs that can be launched in parallel on the cluster
      - jupyter                     # Name identifying the batch job to run, listed here in the correct order
    tunnels:                        # Tunnel bindings
      - 8102:jupyter:8102


.. pull-quote::

  * The ``id`` provided here needs to be defined as the ``id`` of a cluster 
    class. For an example, see 
    `leonhard_med.py <https://github.com/uzh-dqbm-cmi/clusty/blob/master/clusty/clusters/ETH/leonhard_med.py>`_.
  * ``host``: Specify the ``<cluster-ssh-alias>`` here. If none is provided, it will be 
    derived from the cluster class. For an example, see 
    `leonhard_med.py <https://github.com/uzh-dqbm-cmi/clusty/blob/master/clusty/clusters/ETH/leonhard_med.py>`_.
  * ``batch_jobs`` specifies a list of batch jobs in the order in which they 
    need to be run. All jobs need to be defined in the ``batch_jobs`` section 
    (below).
  * ``tunnels`` specifies tunnel bindings that should be created. The name specified in 
    the middle (here: ``jupyter``)  needs to be included in the 
    ``cluster: batch_jobs`` list and defined in the ``batch_jobs`` section.


Job definition
...................

The ``batch_jobs`` section specifies the environment and details of a batch job.
Only defining a job here will not execute it on the cluster. To execute a job, 
it needs to be referenced in the ``cluster: batch_jobs`` section (see above).
The ``batch_jobs`` definition can be split into three sections: 
i) basic settings, resources, and environment, ii) run commands, and 
iii) specification of reserved run commands.

Basic settings, resources, and environment
:::::::::::::::::::::::::::::::::::::::::::


.. code-block:: yaml

  batch_jobs:
    jupyter:                        # Some identifier for the batch job - used to name the screen where this is launched
      id: notebook                  # Name to be used for the screen to identify it (defaults to the batch_job name)
      duration: 1                   # Duration of the batch job in hours
      cpu: 1                        # Number of CPU cores requested
      memory: 10                    # Memory required per core in GB
      gpu: 0                        # Number of GPUs attached to batch job
      gpu_model: GeForceGTX1080Ti   # GPU model used
      env:                          # Environment variables that need to be available in the batch job (works with $vars)
        - PROJECT_DIR=/cluster/work/path_to_data

.. pull-quote::

  * Job ``name`` (here: ``jupyter``) needs to be unique and will be referenced 
    in the ``cluster: batch_jobs`` section.
  * ``duration``, ``cpu``, ``memory``, ``gpu``, and ``gpu_model`` specify 
    resources that will be requested when submitting the batch job to the 
    cluster.
  * ``env`` specifies environment variables which will be set inside the batch 
    job.


Run commands 
:::::::::::::

Next, a list should be specified, defining the commands that should be run in the
batch job. These commands can be any shell commands available on the system, 
or reserved run commands. The reserved run commands can further
be specified (see below). At the moment, the reserved run commands are:

* ``SINGULARITY``: Execute a singularity container and run all subsequent 
  commands inside this container.
* ``JUPYTER``: Start a ``jupyter`` notebook server

.. code-block:: yaml

  # Run commands
      run:                  # Series of commands to run in the batch screen
        - SINGULARITY       # Run the singularity command (special flag)
        - cd /opt/project   # Actual shell command to run in the batch screen
        - JUPYTER           # Run the jupyter command (special flag)

.. pull-quote::

  In this example, 

  * after the batch job is launched, the ``singularity`` 
    container based on the image specified below 
    (``batch_jobs: jupyter: singularity: image``) will be executed.
  * Inside the container, the shell will change into ``/opt/project``. 
    ``/opt/project`` is bound to ``$PROJECT_DIR`` outside the container 
    (see ``batch_jobs: jupyter: singularity: bindings`` below), which is defined as 
    ``/cluster/work/path_to_data`` (see ``batch_jobs: jupyter: env`` above).
  * Finally, a ``jupyter`` server will be started, and 
  * a tunnel (specified in ``cluster: tunnels``) to the ``jupyter`` port 
    (specified in ``batch_jobs: jupyter: jupyter: port``) will be set up, enabling 
    access to the user interface.


Specification of reserved run commands
::::::::::::::::::::::::::::::::::::::::

When the reserved run commands ``SINGULARITY`` or ``JUPYTER`` are executed 
(specified in ``batch_jobs: jupyter: run``), further options can be set:

.. code-block:: yaml

  # Reserved run commands
      singularity:
        image: $PROJECT_DIR/containers/my_container.img     # Image to use
        home: $HOME                                         # Home binding
        bindings:
          - $PROJECT_DIR:/opt/project                       # Directories binding
      jupyter:                      
        port: 8102                                          # Tunnelling binding port



Execution
---------
After the configuration file is set up, the workflow can be executed via 

.. code-block:: bash

  clusty start --config clusty_config.yaml

To terminate all screen sessions, run 

.. code-block:: bash

  clusty stop --config clusty_config.yaml

