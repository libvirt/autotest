import test, re, os
from autotest_utils import *

class libhugetlbfs(test.test):
	version = 3

	# http://downloads.sourceforge.net/libhugetlbfs/libhugetlbfs-1.2.tar.gz
	def setup(self, tarball = 'libhugetlbfs-1.2.tar.gz'):
		tarball = unmap_url(self.bindir, tarball, self.tmpdir)
		extract_tarball_to_dir(tarball, self.srcdir)
		os.chdir(self.srcdir)

		system('make')

	def execute(self, dir = None, pages_requested = 20):
		check_kernel_ver("2.6.16")

		# Check huge page number
		pages_available = 0
		if os.path.exists('/proc/sys/vm/nr_hugepages'):
			system('echo %d > /proc/sys/vm/nr_hugepages' % \
							pages_requested)
			pages_available = int(open('/proc/sys/vm/nr_hugepages', 'r').readline())
		else:
			raise TestError('Kernel does not support hugepages')
		if pages_available < pages_requested:
			raise TestError('%d huge pages available, < %d pages requested' % (pages_available, pages_requested))

		# Check if hugetlbfs has been mounted
		if not file_contains_pattern('/proc/mounts', 'hugetlbfs'):
			if not dir:
				dir = os.path.join(self.tmpdir, 'hugetlbfs')
				os.makedirs(dir)
			system('mount -t hugetlbfs none %s' % dir)

		os.chdir(self.srcdir)

		profilers = self.job.profilers
		if profilers.present():
			profilers.start(self)
			os.chdir(self.srcdir)
		system('make check')
		if profilers.present():
			profilers.stop(self)
			profilers.report(self)

		system('umount %s' % dir)
