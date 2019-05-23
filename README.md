
## Wiki
This repository  contains documentation for using Leonhard Med in the [wiki](https://github.com/CMI-UZH/leonhard-med-mgmt/wiki). 

## Installation
* `git clone` the repo and `cd` into it.
* Run `pip install -e .` to install the repo's python package.
  * If you get a `g++` error during installation, this may be due to a OSX Mojave, see [this StackOverflow answer](https://stackoverflow.com/questions/52509602/cant-compile-c-program-on-a-mac-after-upgrade-to-mojave).

## Code Sync

After installing this package, the `code_sync` tool will be available from the command line. 

The `code_sync` script allows you to auto-sync any changes to code in a local directory to a remote machine, relying on `rsync`. 
Since git is not accessible from LeonhardMed, this allows you to edit code on your local environment and run it on LeonhardMed seamlessly.


### Example usage for connecting to LeoMed:
`code_sync --local_dir mylocaldir/ --remote_dir myremotedir/ --target medinfmk --port 2222`

### Prerequisites

`code_sync` relies on your `~/.ssh/config`, which should contain the following:

```bash
Host medinfmk login.medinfmk.leonhard.ethz.ch
    User lkink
    HostName login.medinfmk.leonhard.ethz.ch
    ProxyCommand ssh -Y %r@jump.leomed.ethz.ch -W %h:%p
    ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p:
```

### Notes
* When you start this script, it will be silent until any file in the `local_dir` is touched. This is normal!
* You can safely quit `code_sync` with control-c.
* The destination directory should not be treated as an active git repo. 
The destination dir must exist already, but need not already be empty.
If the destination directory is a git repo already, it will be overwritten with the "git state" of the local git directory. 
* **Do not run git commands from the destination terminal** on the destination directory. 
The destination dir will have its contents synced to exactly match the local dir, including when you checkout a different branch on local. 
* The sync command adheres to any filters set by `.gitignore` files within the specified directories.
It also excludes `.git` and `.ipynb` files.
