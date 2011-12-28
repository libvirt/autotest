import os, re

from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils, test

class libvirt_TCK(test.test):
    version = 1

    def setup(self, tarball='Sys-Virt-TCK-v0.1.0.tar.gz'):

        try:
            utils.system('perl -MModule::Build -e 1')
        except error.CmdError, e:
            raise error.JobError("Module::Build is required")


        tarpath = utils.unmap_url(self.bindir, tarball)
        utils.extract_tarball_to_dir(tarpath, self.srcdir)
        os.chdir(self.srcdir)

        output = utils.system_output('perl Makefile.PL 2>&1', retain_output=True)
        if re.search('not installed', output):
            raise error.JobError("Checking prerequisites error")

        utils.system('make')
        utils.system('make test')
        utils.system('make install')

    def initialize(self):
        pass

    def run_once(self):
        default_cfg = os.path.join(self.bindir, 'default.cfg')
        ret = utils.system('libvirt-tck -c %s -v --force' % default_cfg, ignore_status=True)
        if ret != 0:
            raise error.TestFail("Testing FAIL")
