#!/usr/bin/env python
"""
This module provides an interface to the pet-cache script.
"""

import sys
import optparse
import pkg_resources
import email
import fillparagraph
import operator

__all__ = ['show', 'showpkg', 'pkgnames', 'main']


#############
#
# Commands
#

def showpkg(args):
	return _showcmd(args, print_showpkg_info)

def show(args):
	return _showcmd(args, print_show_info)

def _showcmd(args, printfunc):
	packages = []
	errs = []
	for pkgname in args:
		try:
			packages.append(pkg_resources.get_distribution(pkgname))
		except pkg_resources.DistributionNotFound:
			errs.append("W: Unable to locate package %s" % pkgname)

	if packages:
		for pkg in packages:
			printfunc(pkg)

	for e in errs:
		print >>sys.stderr, e

	if not packages:
		print >>sys.stderr, "E: No packages found"
		return 100


def pkgnames(args):
	prefix = ''
	if args:
		prefix = args[0]

	getname = operator.attrgetter('project_name')
	pkgnames = map(getname, pkg_resources.working_set)
	if prefix:
		# do a sloppy match if prefix is lower-case, a more precise
		# match if it contains upper-case characters
		if prefix.islower():
			prefixed = lambda s: s.lower().startswith(prefix)
		else:
			prefixed = lambda s: s.startswith(prefix)
		pkgnames = filter(prefixed, pkgnames)
	for name in pkgnames:
		print >>sys.stdout, name

#############
#
# Utility functions
#

def print_showpkg_info(pkg, out=sys.stdout):
	""" Prints extended information about a package to the output
	stream defined in `out` (defaults to stdout)
	"""
	print >>out, "Package:", pkg.project_name
	print >>out, "Version:"
	print >>out, "%s (%s)" % (pkg.version, pkg.location)

	print >>out, "Reverse Depends:"
	rdepends = get_reverse_dependancies(pkg)
	if rdepends:
		print >>out, ', '.join(
			[ "%s" % d for d in rdepends ]
			)

	print >>out, "Dependancies:"

	dependancies = get_dependancies(pkg)
	if not dependancies:
		print >>out, "None"
	deps = ', '.join([ str(d) for d in dependancies ])
	print >>out, deps

def print_show_info(pkg, out=sys.stdout):
	""" Prints extended information about a package to the output
	stream defined in `out` (defaults to stdout)
	"""
	# TODO: these items could be reorder to be a bit more user friendly
	pkginfo = get_pkginfo(pkg)
	print >>out, "Package:", pkg.project_name

	altinfo = pkginfo.copy()
	# suppress the output of these attributes
	suppress = ['Name', 'Description', 'Platform']
	for x in suppress:
		del altinfo[x]

	items = [ (k, altinfo[k]) for k in sorted(altinfo.keys()) ]
	for k, v in items:
		print >>out, "%s: %s" % (k, v)

	# massage the description so that it displays nicely
	print >>out, "Description:"
	desc = pkginfo['Description']
	desc = fillparagraph.fill_paragraphs(desc, 59)
	desc = ' ' + desc.replace('\n', '\n ')
	print >>out, desc

	#print >>out, "Instlled Size:", # TODO, might be nice
	deps = ', '.join([ str(d) for d in get_dependancies(pkg) ])

	print >>out, "Platform:", pkg.platform and pkg.platform or 'Any'
	print >>out, "Depends:", deps
	print >>out, "Filename:", pkg.location
	print >>out, ''
	print >>out, ''

def get_reverse_dependancies(pkg):
	""" Return a list of Distribution objects that need this package.
	"""
	target_req = pkg.as_requirement()
	dists = pkg_resources.working_set
	#print 'XXX', list(dists)
	rdeps = []
	for dist in dists:
		for req in dist.requires():
			if target_req in req:
				rdeps.append(dist)
				break
	return rdeps

def get_dependancies(pkg):
	""" Return a list of Requirement objects that this package needs.
	"""
	return pkg.requires()

def get_pkginfo(dist):
	""" Return a dictionary of package information for the
	Distribution `dist`.
	"""
	try:
		return dict(email.message_from_string(dist.get_metadata('PKG-INFO')))
	except email.Errors.MessageError, e:
		err = "E: Failed to parse option '%s' in PKG-INFO file for %s" % \
			  (e, dist)
		raise Exception(err)

def get_module_func(fname):
	return globals().get(fname)

def main(args=None):
	if not args:
		args = sys.argv[1:]

	usage = """\
Usage: 	pet-cache [options] show pkg1 [pkg2 ...]
        pet-cache [options] pkgnames [prefix]

pet-cache is a simple command line interface for querying the Python
package file cache.

Commands:
    show - Show a readable detailed record of a package
    showpkg - Similar to 'show'
    pkgnames - Display all packages in the cache, optionally filtered
        to names that begin with the supplied prefix

Options:
    --help (-h) This help text.
"""
	if '--help' in args \
		   or '-h' in args \
		   or '-?' in args \
		   or not args:
		print usage
		return

	commands = ['showpkg', 'show', 'pkgnames']

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
