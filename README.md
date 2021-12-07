# Clusty - The Cluster Environment Launch Assistant

The ``clusty`` package is meant to be used for quickly setting up of repetitive tasks performed on a cluster 
environment, such as a high performance computing (HPC) environment in research, or even for cloud machines, 
which require SSH authentication and repeated setup.

## Get started

To get started, a user can run the example by executing the following code in the root directory of this repository. 

**Important** is that before executing the script, you ssh-add all the required identities.

```
clusty start --config example.yaml
```

To stop all jobs and kill all screens, run
```
clusty stop --config example.yaml
```

## Configure clusty

The configuration for the 


## Clusters

Adding new default clusters to the package can be accomplished by adding a Cluster class in the cluster folder. We 
would encourage users to fork the repository if they want to use different clusters, as this package only implements 
cluster residing with the Swiss Federal Institute of Technology (ETH). 

### Implemented cluster

#### LeonhardMed @ ETH

#### Euler @ ETH


## Contributing

New standard functions to be executed on a cluster are welcomed to be added to the configuration file, e.g. Docker, 
Docker Compose, Kubernetes, Kedro, etc. unless they can be executed as a single line command.
Please read the CONTRIBUTING.md file for code style guidelines and conventions. 

