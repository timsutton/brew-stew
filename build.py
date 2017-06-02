#!/usr/bin/python

import json
import os
import subprocess
import sys

from time import gmtime, strftime

BREW_BIN = '/usr/local/bin/brew'

def cmd_output(cmd, env={}):
	'''Run a brew command passed as a list, returns (stdout, stderr)
	env can optionally augment the environment passed to the process'''
	send_cmd = [BREW_BIN] + cmd
	new_env = os.environ.copy().update(env)
	proc = subprocess.Popen(send_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
							env=new_env)
	out, err = proc.communicate()
	return (out.strip(), err)

def cmd_call(cmd, env={}):
	send_cmd = [BREW_BIN] + cmd
	new_env = os.environ.copy().update(env)
	proc = subprocess.call(send_cmd, env=new_env)

class BrewStewEnv(object):
	def __init__(self, brew_file):
		self.brew_list = []
		self.installed_formulae = []
		self.non_homebrew_files = []
		for line in open(brew_file, 'r').read().splitlines():
			if line.startswith("#"):
				continue
			self.brew_list.append(line)
		cmd_call(['analytics', 'off'])
		# self.prefix = subprocess.Popen([BREW_BIN, '--prefix'], stdout=subprocess.PIPE).communicate()[0].strip()
		self.prefix, _ = cmd_output(['--prefix'])
		self._update_installed()
		self._update_unbrewed()
		self.installed_json = []

	def _update_installed(self):
		proc = subprocess.Popen([BREW_BIN, 'ls', '--versions'], stdout=subprocess.PIPE)
		out, _ = proc.communicate()
		for line in out.splitlines():
			formula, version = line.split()
			self.installed_formulae.append(line.split())

	def _update_unbrewed(self):
		proc = subprocess.Popen([BREW_BIN, 'ls', '--unbrewed'], stdout=subprocess.PIPE)
		out, _ = proc.communicate()
		for line in out.splitlines():
			self.non_homebrew_files.append(line)

	def brew_install(self):
		for brew in self.brew_list:
			cmd_call(['install', brew])
		info_json = cmd_output(['info', '--json=v1', '--installed'])
		self.installed_json, _ = json.loads(info_json)


	def brew_test(self):
		for brew in self.brew_list:
			cmd_call(['test', brew])

	def cleanroom(self):
		if self.installed_formulae:
			rm_cmd = ['rm', '--force', '--ignore-dependencies']
			rm_cmd.extend(self.installed_formulae)
			cmd_call(rm_cmd)
		cmd_call(['cleanup'])

	def build_pkg(self, version):
		cmd = ['/usr/bin/pkgbuild']
		cmd += ['--root', self.prefix, '--install-location', self.prefix, '--identifier', 'com.foo', '--version', version]

		for path in self.non_homebrew_files:
			# don't pass --filter the absolute paths on disk - what you get from
			# `brew ls --unbrewed` (relative to the prefix) will match properly
			#
			# except we get warnings for these files, presumably because of the ++:
			# WARNING **** Can't compile pattern: share/mime/text/x-c++src.xml

			cmd += ['--filter', path]
		cmd += [
			'--filter', '.DS_Store',
			'--filter', '.git',
			# check if these absolute paths still match the filter
			'--filter', 'Homebrew', # brew core git repos
			'--filter', 'bin/brew', # brew CLI binstub
			]

		cmd += [os.path.expanduser('~/Desktop/brew') + '-%s.pkg' % version]

		subprocess.call(cmd)

	# debug tool for printing out the bom of the built package
	def dump_pkg_bom(self):
		pass


def main():
	env = BrewStewEnv(sys.argv[1])
	env.cleanroom()
	env.brew_install()
	# env.brew_test()
	# env.build_pkg(version=strftime('%Y.%m.%d', gmtime()))


if __name__ == '__main__':
	main()
