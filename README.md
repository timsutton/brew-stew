# brew-stew

Monolithic homebrew packages for dev/build environment deployment. The goal of this project is to be able to build a single self-contained homebrew installation in the format of a macOS installer package.

The package contains the entire homebrew installation at its default location of `/usr/local`, so it is designed to be built on an isolated system and the package deployed to build/dev machines _instead of_ using `brew` directly on the target system(s). It should, however, play nice with any other binaries/applications which may be installed to `/usr/local` on the target.

## Usage

`brew-stew [-v] <path_to_list_file> <path_to_output_dir>`

Use `-h` to see full help. Use `-v` to print `DEBUG` level output to stdout. `INFO` level is currently output by default.

The "list_file" is simply a text file with a list of formulae. A few samples are included in the `sample_listfiles` directory.

## Approaches

A couple possible approaches being played with in terms of the logic for determining what goes in the package, which are for now just termed as 'subtractive' and 'additive'. Currently the build script defaults to `additive`.

### Subtractive

Building the package by packaging up all of `/usr/local`, and attempting to filter out certain items we know aren't part of brew. We can get a list of files not managed by brew using `brew ls --unbrewed`, but it seems to at least mix symlinks like `/usr/local/bin/santactl`. This is a bit of a shotgun approach and seems like it would be very easy to capture things we don't want.

### Additive

Using tools like `brew ls --verbose <formula>` to list all the files known to be installed by a formula, stage these to an alternate package root using `rsync` to preserve modes, and package from this root instead. What we don't yet have is the logic to also include symlinks or the `opt` brew directories. This may be easy to do ourselves by following naming conventions, even if brew doesn't provide an obvious way to do it.

## Reporting

Currently several report files are saved in the output directory alongside the installer package:

### report.json

`report.json` currently contains the following:

- exhaustive output from `brew info --json=v1`
- output of `santactl fileinfo` from every executable detected in the Cellar
- a summary, currently containing only formula names and versions

See [this wiki page](https://github.com/timsutton/brew-stew/wiki/Report-JSON) for sample JSON report output for a build of just the `cowsay` formula.

### build_debug.log

Full debug output of the command, regardless of verbose level specified in the tool. Note that currently there is still a lot of output from `brew` itself which is not yet being redirected through the logger, so this currently information we're logging explicitly and nothing directly output `brew` commands.

### package_bom.txt

This is the output of `lsbom` on the `Bom` file from the package, which is a complete list of all files with ownerships and modes in the package.

### formula_versions.txt

This is a simple textfile with a list of formulae and versions for easy readability and diff'ing. For example:

```
dnsmasq 2.77_1
docker 17.05.0
jpeg 8d
libtiff 4.0.8
xz 5.2.3
```
