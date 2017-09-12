""" Module used for interacting with SPEC functionality """
import logging
import os
import shutil
import subprocess

def test(binary, test_dir, config):
    regression_script = os.path.join(config.testing['regression_dir'], 'common', 'regression-main', 'regression.py')
    fake_diablo_dir = os.path.join(config.testing['regression_dir'], 'common', 'fakediablo')
    fake_diablo_bin = 'fakediablo.sh'

    # Create the test directory and copy over the binary
    shutil.copy(binary, config.default['input_source_directory'])

    # Execute the regression script
    conf_file = os.path.join(os.path.dirname(config.default['input_source_directory']), 'spec2006_test.conf')
    result = subprocess.check_output([regression_script, '-c', conf_file, '-T', test_dir, '-d', fake_diablo_dir, '-p', fake_diablo_bin, config.default['binary_name']], stderr=subprocess.DEVNULL, universal_newlines=True).splitlines()[-1]
    assert result == 'OK', 'SPEC regression script failed!'
