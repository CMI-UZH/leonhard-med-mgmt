
## Installation
* `git clone` the repo and `cd` into it.
* Run `pip install -e .` to install the repo's python package.
  * If you get a `g++` error during installation, this may be due to a OSX Mojave, see [this StackOverflow answer](https://stackoverflow.com/questions/52509602/cant-compile-c-program-on-a-mac-after-upgrade-to-mojave).

## Utilities

### Code Sync
`leotools` automatically installs the `code-sync` package.
See the [`code-sync` documentation](https://github.com/uzh-dqbm-cmi/code-sync) for more details on usage.

### `build_image`

Add the custom packages path to your path in your `~/.bashrc`:

export PATH=$PATH:/cluster/home/lkink/custom_packages/bin/