import sys
import distutils.core
distutils.core._setup_stop_after = 'config'

import setup
setup.dist.run_command('build_ext')
build_ext = setup.dist.get_command_obj('build_ext')

import sys
sys.path.insert(0, build_ext.build_lib)

import tests
import tests.support
tests.support.run_all_tests(tests=tests.all_tests)
