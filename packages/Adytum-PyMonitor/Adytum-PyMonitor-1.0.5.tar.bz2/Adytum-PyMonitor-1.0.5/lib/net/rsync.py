# Python conterpart of rsync written by Vivian De Smedt
# Send any comment or bug report to vivian@vdesmedt.com.
from __future__ import nested_scopes

import os, os.path, shutil, glob, re, sys, getopt, stat

try:
	import win32file
except:
	win32file = None

class Cookie:
	def __init__(self):
		self.sink_root = ""
		self.target_root = ""
		self.quiet = 0
		self.recursive = 0
		self.relative = 0
		self.dry_run = 0
		self.time = 0
		self.update = 0
		self.cvs_ignore = 0
		self.ignore_time = 0
		self.delete = 0
		self.delete_excluded = 0
		self.size_only = 0
		self.modify_window = 2
		self.existing = 0
		self.filters = []
		self.case_sensitivity = 0
		if os.name == "nt":
			self.case_sensitivity = re.I

def visit(cookie, dirname, names):
	"""Copy files names from sink_root + (dirname - sink_root) to target_root + (dirname - sink_root)"""
	if os.path.split(cookie.sink_root)[1]: # Should be tested with (C:\Cvs -> C:\)! (C:\Archives\MyDatas\UltraEdit -> C:\Archives\MyDatas) (Cvs -> "")! (Archives\MyDatas\UltraEdit -> Archives\MyDatas) (\Cvs -> \)! (\Archives\MyDatas\UltraEdit -> Archives\MyDatas)
		dirname = dirname[len(cookie.sink_root) + 1:]
	else:
		dirname = dirname[len(cookie.sink_root):]
	target_dir = os.path.join(cookie.target_root, dirname)
	if not os.path.isdir(target_dir):
		makeDir(cookie, target_dir)
	sink_dir = os.path.join(cookie.sink_root, dirname)

	if cookie.delete and os.path.isdir(target_dir):
		# Delete files and folder in target not present in sink.
		for name in os.listdir(target_dir):
			if not name in names:
				target = os.path.join(target_dir, name)
				if os.path.isfile(target):
					removeFile(cookie, target)
				elif os.path.isdir(target):
					removeDir(cookie, target)
				else:
					pass

	filters = []
	if cookie.cvs_ignore:
		ignore = os.path.join(sink_dir, ".cvsignore")
		if os.path.isfile(ignore):
			filters = convertPatterns(ignore, "-")
	filters += cookie.filters

	if filters:
		name_index = 0
		while name_index < len(names):
			name = names[name_index]
			path = os.path.join(dirname, name)
			path = convertPath(path)
			if os.path.isdir(os.path.join(sink_dir, name)):
				path += "/"
			for filter in filters:
				if re.search(filter[1], path, cookie.case_sensitivity):
					if filter[0] == '-':
						sink = os.path.join(sink_dir, name)
						if cookie.delete_excluded:
							if os.path.isfile(sink):
								removeFile(cookie, sink)
							elif os.path.isdir(sink):
								removeDir(cookie, sink)
							else:
								raise "sink: %s not file not dir" % sink
						del(names[name_index])
						name_index -= 1
					elif filter[0] == '+':
						break
			name_index += 1

	for name in names:
		# Copy files and folder from sink to target.
		sink = os.path.join(sink_dir, name)
		#print sink
		target = os.path.join(target_dir, name)
		if os.path.exists(target):
			# When target already exit:
			if os.path.isfile(sink):
				if os.path.isfile(target):
					# file-file
					if shouldUpdate(cookie, sink, target):
						updateFile(cookie, sink, target)
				elif os.path.isdir(target):
					# file-folder
					removeDir(cookie, target)
					copyFile(cookie, sink, target)
				else:
					raise Exception("file-???")
			elif os.path.isdir(sink):
				if os.path.isfile(target):
					# folder-file
					removeFile(cookie, target)
					makeDir(cookie, target)
			else:
				raise Exception("???-*")

		elif not cookie.existing:
			# When target dont exist:
			if os.path.isfile(sink):
				# file
				copyFile(cookie, sink, target)
			elif os.path.isdir(sink):
				# folder
				makeDir(cookie, target)
			else:
				raise Exception("sink: %s not file not dir" % sink)


def log(cookie, message):
	if not cookie.quiet:
		try:
			print message
		except UnicodeEncodeError:
			print message.encode("utf8")
			
			
def logError(message):
	try:
		sys.stderr.write(message + "\n")
	except UnicodeEncodeError:
		sys.stderr.write(message.encode("utf8"))


def shouldUpdate(cookie, sink, target):
	sink_st = os.stat(sink)
	sink_sz = sink_st.st_size
	sink_mt = sink_st.st_mtime

	target_st = os.stat(target)
	target_sz = target_st.st_size
	target_mt = target_st.st_mtime

	if cookie.update:
		return target_mt < sink_mt - cookie.modify_window

	if cookie.ignore_time:
		return 1

	if target_sz != sink_sz:
		return 1

	if cookie.size_only:
		return 0

	return abs(target_mt - sink_mt) > cookie.modify_window


def copyFile(cookie, sink, target):
	if not cookie.dry_run:
		try:
			shutil.copyfile(sink, target)
		except:
			logError("Fail to copy %s\n" % sink)

		if cookie.time:
			try:
				s = os.stat(sink)
				os.utime(target, (s.st_atime, s.st_mtime));
			except:
				logError("Fail to copy timestamp of %s\n" % sink)

	log(cookie, "copy: %s to: %s" % (sink, target))


def updateFile(cookie, sink, target):
	if not cookie.dry_run:
		# Read only and hidden and system files can not be overridden.
		if win32file:
			filemode = win32file.GetFileAttributesW(target)
			win32file.SetFileAttributesW(target, filemode & ~win32file.FILE_ATTRIBUTE_READONLY & ~win32file.FILE_ATTRIBUTE_HIDDEN & ~win32file.FILE_ATTRIBUTE_SYSTEM)
		else:
			os.chmod(target, stat.S_IWUSR)

		try:
			shutil.copyfile(sink, target)
		except:
			logError("Fail to override %s\n" % sink)

		if cookie.time:
			try:
				s = os.stat(sink)
				os.utime(target, (s.st_atime, s.st_mtime));
			except:
				logError("Fail to copy timestamp of %s\n" % sink) # The utime api of the 2.3 version of python is not unicode compliant.

		if win32file:
			win32file.SetFileAttributesW(target, filemode)

	log(cookie, "update: %s to: %s" % (sink, target))


def removeFile(cookie, target):
	# Read only files could not be deleted.
	if not cookie.dry_run:
		os.chmod(target, stat.S_IWUSR)
		os.remove(target)
	log(cookie, "remove: %s" % target)


def makeDir(cookie, target):
	if not cookie.dry_run:
		os.makedirs(target)
	log(cookie, "make dir: %s" % target)


def removeDir(cookie, target):
	# Read only directory could not be deleted.
	if not cookie.dry_run:
		shutil.rmtree(target, True)
	log(cookie, "remove dir: %s" % target)


def convertPath(path):
	# Convert windows, mac path to unix version.
	separator = os.path.normpath("/")
	if separator != "/":
		path = re.sub(re.escape(separator), "/", path)

	# Help file, folder pattern to express that it should match the all file or folder name.
	path = "/" + path
	return path


def convertPattern(pattern, sign):
	"""Convert a rsync pattern that match against a path to a filter that match against a converted path."""

	# Check for include vs exclude patterns.
	if pattern[:2] == "+ ":
		pattern = pattern[2:]
		sign = "+"
	elif pattern[:2] == "- ":
		pattern = pattern[2:]
		sign = "-"

	# Express windows, mac patterns in unix patterns (rsync.py extension).
	separator = os.path.normpath("/")
	if separator != "/":
		pattern = re.sub(re.escape(separator), "/", pattern)

	# If pattern contains '/' it should match from the start.
	temp = pattern
	if pattern[0] == "/":
		pattern = pattern[1:]
	if temp[-1] == "/":
		temp = temp[:-1]

	# Convert pattern rules: ** * ? to regexp rules.
	pattern = re.escape(pattern)
	pattern = pattern.replace("\\*\\*", ".*")
	pattern = pattern.replace("\\*", "[^/]*")
	pattern = pattern.replace("\\*", ".*")

	if "/" in temp:
		# If pattern contains '/' it should match from the start.
		pattern = "^\\/" + pattern
	else:
		# Else the pattern should match the all file or folder name.
		pattern = "\\/" + pattern

	if pattern[-2:] != "\\/" and pattern[-2:] != ".*":
		# File patterns should match also folders.
		pattern += "\\/?"

	# Pattern should match till the end.
	pattern += "$"
	return (sign, pattern)


def convertPatterns(path, sign):
	"""Read the files for pattern and return a vector of filters"""
	filters = []
	f = open(path, "r")
	while 1:
		pattern = f.readline()
		if not pattern:
			break
		if pattern[-1] == "\n":
			pattern = pattern[:-1]

		if re.match("[\t ]*$", pattern):
			continue
		if pattern[0] == "#":
			continue
		filters += [convertPattern(pattern, sign)]
	f.close()
	return filters


def printUsage():
	"""Print the help string that should printed by rsync.py -h"""
	print "usage: rsync.py [options] source target"
	print """
 -q, --quiet              decrease verbosity
 -r, --recursive          recurse into directories
 -R, --relative           use relative path names
 -u, --update             update only (don't overwrite newer files)
 -t, --times              preserve times
 -n, --dry-run            show what would have been transferred
     --existing           only update files that already exist
     --delete             delete files that don't exist on the sending side
     --delete-excluded    also delete excluded files on the receiving side
 -I, --ignore-times       don't exclude files that match length and time
     --size-only          only use file size when determining if a file should
                          be transferred
     --modify-window=NUM  timestamp window (seconds) for file match (default=2)
 -C, --cvs-exclude        auto ignore files in the same way CVS does
     --exclude=PATTERN    exclude files matching PATTERN
     --exclude-from=FILE  exclude patterns listed in FILE
     --include=PATTERN    don't exclude files matching PATTERN
     --include-from=FILE  don't exclude patterns listed in FILE
     --version            print version number
 -h, --help               show this help screen

See http://www.vdesmedt.com/~vds2212/rsync.html for informations and updates.
Send an email to vivian@vdesmedt.com for comments and bug reports."""


def printVersion():
	print "rsync.py version 1.0.6"


def main(argv):
	cookie = Cookie()

	opts, args = getopt.getopt(argv[1:], "qrRntuCIh", ["quiet", "recursive", "relative", "dry-run", "time", "update", "cvs-ignore", "ignore-times", "help", "delete", "delete-excluded", "existing", "size-only", "modify-window=", "exclude=", "exclude-from=", "include=", "include-from=", "version"])
	for o, v in opts:
		if o in ["-q", "--quiet"]:
			cookie.quiet = 1
		if o in ["-r", "--recursive"]:
			cookie.recursive = 1
		if o in ["-R", "--relative"]:
			cookie.relative = 1
		elif o in ["-n", "--dry-run"]:
			cookie.dry_run = 1
		elif o in ["-t", "--time"]:
			cookie.time = 1
		elif o in ["-u", "--update"]:
			cookie.update = 1
		elif o in ["-C", "--cvs-ignore"]:
			cookie.cvs_ignore = 1
		elif o in ["-I", "--ignore-time"]:
			cookie.ignore_time = 1
		elif o == "--delete":
			cookie.delete = 1
		elif o == "--delete-excluded":
			cookie.delete = 1
			cookie.delete_excluded = 1
		elif o == "--size-only":
			cookie.size_only = 1
		elif o == "--modify-window":
			cookie.modify_window = int(v)
		elif o == "--existing":
			cookie.existing = 1
		elif o == "--exclude":
			cookie.filters += [convertPattern(v, "-")]
		elif o == "--exclude-from":
			cookie.filters += convertPatterns(v, "-")
		elif o == "--include":
			cookie.filters += [convertPattern(v, "+")]
		elif o == "--include-from":
			cookie.filters += convertPatterns(v, "+")
		elif o == "--version":
			printVersion()
			return 0
		elif o in ["-h", "--help"]:
			printUsage()
			return 0

	if len(args) <= 1:
		printUsage()
		return 1

	#print cookie.filters

	target_root = args[1]
	if os.path.supports_unicode_filenames:
		target_root = unicode(target_root, sys.getfilesystemencoding())
	cookie.target_root = target_root

	sinks = glob.glob(args[0])
	if not sinks:
		return 0

	sink_families = {}
	for sink in sinks:
		if os.path.supports_unicode_filenames:
			sink = unicode(sink, sys.getfilesystemencoding())
		sink_name = ""
		sink_root = sink
		while not sink_name:
			sink_root, sink_name = os.path.split(sink_root)
		if not sink_families.has_key(sink_root):
			sink_families[sink_root] = []
		sink_families[sink_root] += [sink_name]

	for sink_root in sink_families.keys():
		if cookie.relative:
			cookie.sink_root = ""
		else:
			cookie.sink_root = sink_root

		files = filter(lambda x: os.path.isfile(os.path.join(sink_root, x)), sink_families[sink_root])
		if files:
			visit(cookie, sink_root, files)

		folders = filter(lambda x: os.path.isdir(os.path.join(sink_root, x)), sink_families[sink_root])
		for folder in folders:
			folder_path = os.path.join(sink_root, folder)
			if not cookie.recursive:
				visit(cookie, folder_path, os.listdir(folder_path))
			else:
				os.path.walk(folder_path, visit, cookie)
	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))
