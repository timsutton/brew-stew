# brew-stew
Monolithic homebrew packages for dev environment deployment

## Usage

`build.py <path_to_list_file>`

## Approaches

A couple possible approaches being played with in terms of the logic for determining what goes in the package, which are for now just termed as 'subtractive' and 'additive'. Currently the build script defaults to `additive`.

### Subtractive

Building the package by packaging up all of `/usr/local`, and attempting to filter out certain items we know aren't part of brew. We can get a list of files not managed by brew using `brew ls --unbrewed`, but it seems to at least mix symlinks like `/usr/local/bin/santactl`. This is a bit of a shotgun approach and seems like it would be very easy to capture things we don't want.

### Additive

Using tools like `brew ls --verbose <formula>` to list all the files known to be installed by a formula, stage these to an alternate package root using `rsync` to preserve modes, and package from this root instead. What we don't yet have is the logic to also include symlinks or the `opt` brew directories. This may be easy to do ourselves by following naming conventions, even if brew doesn't provide an obvious way to do it.

## Reporting

For now, the `BrewStewEnv.build_report()` method saves a file, `report.json`, in the current directory. Eventually this can be made more configurable or be bundled in a directory along with a built package.
