import os, re, shutil

from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils, test

class libvirt_TCK(test.test):
    version = 1
    TESTDIR = '/usr/share/libvirt-tck/tests'

    def setup(self, tarball='Sys-Virt-TCK-v0.1.0.tar.gz'):

        # install cpanminus script
        try:
            utils.system('(curl -L http://cpanmin.us | perl - App::cpanminus)2>&1')
        except error.CmdError, e:
            raise error.JobError("Failed to install cpanminus script.")

        tarpath = utils.unmap_url(self.bindir, tarball)
        utils.extract_tarball_to_dir(tarpath, self.srcdir)
        os.chdir(self.srcdir)

        output = utils.system_output('perl Makefile.PL 2>&1', retain_output=True)

        required_mods = list(set(re.findall("[^ ']*::[^ ']*", output)))

        # resolve perl modules dependencies
        if required_mods:
            for mod in required_mods:
                ret = utils.system('cpanm %s 2>&1' % mod)
                if ret != 0:
                    raise error.JobError("Failed to install module %s" % mod)

        utils.system('make')
        utils.system('make test')
        utils.system('make install')

    def initialize(self):
        pass

    def get_testcases(self, testcasecfg, item):
        flag = 0
        testcases = []
        fh = open(testcasecfg, "r")
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

            if flag == 1 and line[0].isdigit():
                testcases.append(line)
                continue

        fh.close()
        return testcases

    def run_once(self, args=[]):
        if not args:
            raise error.JobError("NO TEST avaliable")

        item = args

        default_cfg = os.path.join(self.bindir, 'default.cfg')
        ks_cfg = os.path.join(self.bindir, 'ks.cfg')

        testcase_cfg = os.path.join(self.bindir, 'testcase.cfg')
        item_path = os.path.join(libvirt_TCK.TESTDIR, item)
        testcases = self.get_testcases(testcase_cfg, item)

        shutil.copy2(ks_cfg, '/etc/libvirt-tck/ks.cfg')

        for testcase in testcases:
            testcase_path = os.path.join(item_path, testcase)
            ret = utils.system('export LIBVIRT_TCK_CONFIG=%s; perl %s 2>&1' %
                            (default_cfg, testcase_path), ignore_status=True)
            if ret != 0:
                raise error.TestFail("Testing FAIL")
