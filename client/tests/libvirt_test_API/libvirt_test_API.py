import os, re, shutil

from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils, test

class libvirt_test_API(test.test):
    version = 1

    def setup(self, tarball='libvirt-test-API.tar.gz'):

        tarpath = utils.unmap_url(self.bindir, tarball)
        self.srcdir = os.path.join(self.bindir, 'libvirt-test-API')
        utils.extract_tarball_to_dir(tarpath, self.srcdir)

        required_rpms = ['pexpect', 'nmap']
        for rpm in required_rpms:
            ret = utils.system('rpm -qa|grep %s' % rpm)
            if ret != 0:
                raise error.JobError("%s is required" % rpm)

    def initialize(self):
        pass

    def get_configfile(self, config_files_conf, item):
        flag = 0
        testcases = []
        fh = open(config_files_conf, "r")
        for eachLine in fh:
            line = eachLine.strip()

            if line.startswith('#'):
                continue

            if flag == 0 and not line:
                continue

            if item == line[:-1]:
                flag = 1
                continue

            if flag == 1 and not line:
                flag = 0
                break

            if flag == 1 and line.endswith('.conf'):
                testcases.append(line)
                continue

        fh.close()
        return testcases

    def run_once(self, args = ''):
        if not args:
            raise error.JobError("NO TEST avaliable")

        item = args

        os.chdir(self.srcdir)

        env_cfg = os.path.join(self.bindir, 'env.cfg')
        kickstart_cfg = os.path.join(self.bindir, 'kickstart.cfg')

        shutil.copy2(env_cfg, self.srcdir)
        shutil.copy2(kickstart_cfg, self.srcdir)

        config_files_cfg = os.path.join(self.bindir, 'config_files.cfg')
        test_items = self.get_configfile(config_files_cfg, item)
        if not test_items:
            raise error.JobError("NO TEST avaliable")

        for item in test_items:
            ret = utils.system('python libvirt-test-api.py -c cases/%s 2>&1' % item)
            if ret != 0:
                raise error.TestFail("Testing FAIL")
