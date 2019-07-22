
## Installation
* `git clone` the repo and `cd` into it.
* Run `pip install -e .` to install the repo's python package.
  * If you get a `g++` error during installation, this may be due to a OSX Mojave, see [this StackOverflow answer](https://stackoverflow.com/questions/52509602/cant-compile-c-program-on-a-mac-after-upgrade-to-mojave).

## Code Sync

After installing this package, the `code_sync` tool will be available from the command line. 

The `code_sync` script allows you to auto-sync any changes to code in a local directory to a remote machine, relying on `rsync`. 
Since git is not accessible from LeonhardMed, this allows you to edit code on your local environment and run it on LeonhardMed seamlessly.
`code_sync` can be used with any remote machine, for example also with ScienceCloud machines.

### Example usage for connecting to LeoMed:
`code_sync --local_dir mylocaldir/ --remote_dir myremotedir/ --target medinfmk --port 2222`

### Prerequisites

`code_sync` relies on your `~/.ssh/config`, which should contain `ControlMaster` and entries for each machine you want to connect to:

```bash
ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p:

Host medinfmk login.medinfmk.leonhard.ethz.ch
    User lkink
    HostName login.medinfmk.leonhard.ethz.ch
    ProxyCommand ssh -Y %r@jump.leomed.ethz.ch -W %h:%p

Host sciencecloud 111.111.111.111
    User ubuntu
    HostName 111.111.111.111
```

### Notes
**Starting**
* In order to run `code_sync`, you must have an ssh connection open in another window. Once you've entered your password there, `code_sync` uses that connection.  
* When you start this script, nothing will happen  until a file in the `local_dir` is touched. This is normal!

**Stopping**
* You can safely quit `code_sync` with control-c.

**About `code_sync` + `git`**
* The destination directory should not be treated as an active git repo. 
The destination dir must exist already, but need not already be empty.
If the destination directory is a git repo already, it will be overwritten with the "git state" of the local git directory. 
* **Do not run git commands from the destination terminal** on the destination directory. 
The destination dir will have its contents synced to exactly match the local dir, including when you checkout a different branch on local. 
* The sync command adheres to any filters set by `.gitignore` files within the specified directories.
It also excludes `.git` and `.ipynb` files.
