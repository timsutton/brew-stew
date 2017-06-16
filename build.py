#!/usr/bin/python

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from time import gmtime, strftime

BREW_BIN = '/usr/local/bin/brew'
INSTALL_LOCATION = '/usr/local'

# Some additional items which are erroneously not listed in `brew ls --unbrewed`
PKG_FILTERS = [
'bin/santactl',
'bin/autopkg',
'remotedesktop/RemoteDesktopChangeClientSettings.pkg',
'var', # exclude all of var to see what breaks
'Library',
]

def log_err(msg):
	print sys.stderr >> msg

def cmd_output(cmd, env={}):
	'''Run a brew command passed as a list, returns (stdout, stderr)
	env can optionally augment the environment passed to the process'''
	send_cmd = [BREW_BIN] + cmd
	new_env = os.environ.copy()
	new_env['HOMEBREW_NO_AUTO_UPDATE'] = '1'
	new_env.update(env)
	proc = subprocess.Popen(send_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
							env=new_env)
	out, err = proc.communicate()
	return (out.strip(), err)

def cmd_call(cmd, env={}):
	'''Just subprocess.calls the list of args to the `brew` command'''
	send_cmd = [BREW_BIN] + cmd
	new_env = os.environ.copy()
	new_env['HOMEBREW_NO_AUTO_UPDATE'] = '1'
	retcode = subprocess.call(send_cmd, env=new_env)
	return retcode

def stage_files(source_file_list, pkgroot, opts=['-a']):
	file_list_path = tempfile.mkstemp()[1]
	with open(file_list_path, 'w') as fd:
		fd.write('\n'.join(source_file_list))
	rsync_cmd = ['/usr/bin/rsync'] + opts
	rsync_cmd += ['--files-from', file_list_path, '/', pkgroot]
	print "Calling rsync command: %s" % rsync_cmd
	subprocess.call(rsync_cmd)

class BrewStewEnv(object):
	def __init__(self, brew_file):
		cmd_call(['analytics', 'off'])

		self.brew_list = []
		for line in open(brew_file, 'r').read().splitlines():
			if line.startswith("#"):
				continue
			self.brew_list.append(line)

		self.installed_json = []
		self.installed_formulae = []
		self._update_installed()

		self.non_homebrew_files = []
		self._update_unbrewed()

		self.prefix, _ = cmd_output(['--prefix'])
		self.filtered_pkg_files = []
		self.built_pkg_path = None

	def _update_installed(self):
		installed = []
		info_json, _ = cmd_output(['info', '--json=v1', '--installed'])
		self.installed_json = json.loads(info_json)
		for f in self.installed_json:
			installed.append((f['name'], f['installed'][0]['version']))
			if len(f['installed']) > 1:
				log_err("WARNING: Formula %s has more than one version installed, unexpected" % f['name'])
		self.installed_formulae = installed

	def _update_unbrewed(self):
		proc = subprocess.Popen([BREW_BIN, 'ls', '--unbrewed'], stdout=subprocess.PIPE)
		out, _ = proc.communicate()
		for line in out.splitlines():
			self.non_homebrew_files.append(line)

	def brew_update(self):
		cmd_call(['update'])

	def brew_install(self):
		for brew in self.brew_list:
			cmd_call(['install', brew])
		self._update_installed
		self._update_unbrewed

	def brew_test(self):
		for brew in self.brew_list:
			cmd_call(['test', brew])

	def cleanroom(self):
		if self.installed_formulae:
			rm_cmd = ['rm', '--force', '--ignore-dependencies']
			rm_cmd.extend([f for (f, ver) in self.installed_formulae])
			cmd_call(rm_cmd)
		cmd_call(['cleanup'])

	def build_pkg(self, version=None, output_path=None, strategy='subtractive'):
		if version is None:
			version = strftime('%Y.%m.%d', gmtime())
		self.built_pkg_path = os.path.join(os.getcwd(), 'stew_%s-%s.pkg' % (strategy, version))
		# TODO: see if we can still use '--install-location /usr/local' so we can avoid needing to include it
		# in the actual payload path. This is easy to do when we're packaging a '--root' in-place, but more
		# work if we
		pkgbuild_cmd = ['/usr/bin/pkgbuild', '--install-location', INSTALL_LOCATION, '--identifier', 'com.brewstew', '--version', version]

		if strategy == 'subtractive':
			pkgbuild_cmd += ['--root', self.prefix]
			# except we get warnings for these files, presumably because of the ++:
			# WARNING **** Can't compile pattern: share/mime/text/x-c++src.xml
			self.filtered_pkg_files += self.non_homebrew_files
			self.filtered_pkg_files += PKG_FILTERS
			self.filtered_pkg_files += [
				'.DS_Store',
				'.git',
				'Homebrew',	# brew core git repos
				'bin/brew', # brew CLI binstub
			]
			for pattern in self.filtered_pkg_files:
				pkgbuild_cmd += ['--filter', pattern]
			pkgbuild_cmd += [self.built_pkg_path]


		if strategy == 'additive':
			pkgroot = os.path.expanduser('~/Desktop/pkgroot')
			pkgbuild_cmd += ['--root', os.path.join(pkgroot, 'usr/local')]

			if os.path.exists(pkgroot):
				shutil.rmtree(pkgroot)
			# TODO: derive this from a variable/const
			# os.makedirs(os.path.join(pkgroot, 'usr/local'))
			os.mkdir(pkgroot)
			file_list = cmd_output(['ls', '--verbose'] + [name for (name, ver) in self.installed_formulae])[0].splitlines()
			stage_files(file_list, pkgroot)

			# recursively walk the brew prefix to find links of interest, according to this criteria:
			# - linked path contains 'Cellar' in the absolute pathname
			# - item isn't excluded by the exclusion regex
			#
			# TODO:
			# - could there still be anything here that's stale, i.e. from a
			#   previous formula that's no longer in our install list? if so,
			#   we could probably also add a check that any included item has
			#   to contain a path like 'Cellar/<formula>' so that we can count
			#   on it being relevant
			exclude_re = r'^\/usr\/local\/(bin\/brew|Homebrew).*$'
			symlinks = []
			print "Locating symlinks:"
			for root, dirs, files in os.walk(INSTALL_LOCATION):
				if re.match(exclude_re, root):
					continue
				for f in files:
					full_spath = os.path.join(root, f)
					if os.path.islink(full_spath):
						if 'Cellar' not in os.path.realpath(full_spath):
							continue
						linked_path = os.readlink(full_spath)
						print "Got link '%s'  -->  '%s'" % (full_spath, os.readlink(full_spath))
						symlinks.append(full_spath)
			print "Staging symlinks"
			stage_files(symlinks, pkgroot)

			print "Staging opt"
			opt_files = [os.path.join('/usr/local/opt', f) for f in os.listdir('/usr/local/opt')]
			stage_files(opt_files, pkgroot)

		print "Calling pkgbuild command: %s" % pkgbuild_cmd
		pkgbuild_cmd.append(self.built_pkg_path)
		subprocess.call(pkgbuild_cmd)

	def dump_pkg_files(self):
		subprocess.call(['/usr/sbin/pkgutil', '--payload-files', self.built_pkg_path])


def main():
	env = BrewStewEnv(sys.argv[1])
	env.cleanroom()
	env.brew_update()
	env.brew_install()
	# env.brew_test()
	# print env.non_homebrew_files
	env.build_pkg(strategy='additive')
	env.dump_pkg_files()


if __name__ == '__main__':
	main()