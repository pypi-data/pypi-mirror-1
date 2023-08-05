#!/usr/bin/env python
"""
This module provides an interface to the pet-cache script.
"""

from setuptools.command.easy_install import main as easy_install
import optparse
import pkg_resources
import operator
import sys

__all__ = ['install', 'source', 'remove', 'update', 'upgrade', 'main']


#############
#
# Commands
#

def install(args):
	if not args:
		return "E: You must supply at least one package name"
	easy_install(args)

def source(args):
	if not args:
		return "E: You must supply at least one package name"
	easy_install(['--editable', '--build-directory=.'] + args)

def remove(args):
   	if not args:
		return "E: You must supply at least one package name"
	easy_install(['--multi-version'] + args)

def update(args):
	if not args:
		return "E: You must supply at least one package name"
	easy_install(['--upgrade'] + args)

def upgrade(args):
	if args:
		return "E: The 'upgrade' command does not take any arguments."
	distname = operator.attrgetter('project_name')
	packages = map(distname, pkg_resources.working_set)
	return update(packages)


#############
#
# Utility functions
#

def get_module_func(fname):
	return globals().get(fname)

def main(args=None):
	if not args:
		args = sys.argv[1:]

	usage = """\
Usage:  pet-get [options] upgrade
        pet-get [options] install|remove pkg1 [pkg2 ...]
        pet-get [options] update pkg1 [pkg2 ...]
        pet-get [options] source pkg1 [pkg2 ...]

pet-get is a simple command line interface for downloading and managing
Python packages.  It wraps setuptool's 'easy_install' script and
accepts the same options.

Commands:
    install - Install new packages
    update - Update packages to the latest version
    upgrade - Update ALL packages
    remove - De-activate a package
    source - Install editable packages in the current directory
    
We will now print the options from 'easy_install' that may be passed
to pet-get:
"""
	if '--help' in args \
		   or '-h' in args \
		   or '-?' in args \
		   or not args:
		print usage
		easy_install(['--help'])
		return

	commands = ['install', 'source', 'remove', 'update', 'upgrade']

	# find the earliest command in the arguments list
	command = ''
	for x in args:
		if x in commands:
			# we found the first real command
			command = x
			break
		elif not x.startswith('-'):
			# oops, something that is not a command or an option
			return "E: '%s' is not a valid package command" % x

	if not command:
		return "E: You must supply a package command"

	# we don't want the package command getting passed down
	args.remove(command)

	fun = get_module_func(command)
	if not fun:
		return "E: '%s' is not a valid package command" % command

	return fun(args)

if __name__ == '__main__':
	main()
