import virtualenv, textwrap


__all__ = ['create_scripts']
version = '0.4.0'


def create_scripts(src_repository, proj, release_version):
	_do_create_script(src_repository, proj, None)
	_do_create_script(src_repository, proj, repr(release_version))

def _do_create_script(src_repository, proj, release_version):
	boostrap_version = version
	escaped_substiution = '%s'  # so that I can use string substitutions within the script that results from substituting the recipe.
	escaped_percent = '%'
	recipe_ = _recipe % locals()
	open('%s-%s.py' % (proj, ['release', 'devel'][release_version is None]), 'w').write(virtualenv.create_bootstrap_script(recipe_))

_recipe = textwrap.dedent('''
import os, subprocess, sys

src_repository_ = '%(src_repository)s'
proj_ = '%(proj)s'
release_version_ = %(release_version)s

win32 = """
We require Python 2.5.1. You can download it here:

http://www.python.org/ftp/python/2.5.1/python-2.5.1.msi
"""

darwin = """
We require Python 2.5.1. You can download a Universal build here:

http://www.python.org/ftp/python/2.5.1/python-2.5.1-macosx.dmg 
"""

other = """
We require Python 2.5.1. This version of Python is often available in
your operating system's native package format (via apt-get or yum, for
instance). You can also easily build Python from source on Unix-like
systems. Here is the source download link for Python:

http://www.python.org/ftp/python/2.5.1/Python-2.5.1.tar.bz2
"""

def extend_parser(parser):
	parser.add_option(
		'--with-global-site-packages',
		dest='no_site_packages',
		action='store_false',
		help="Copy the contents of the global site-packages dir to the "
			"non-root site-packages")
	parser.set_default('no_site_packages', True)
	parser.remove_option('--no-site-packages')

def locate_installed_script(script_base_name):
	if sys.platform == 'win32':
		return os.path.join(bin_dir, script_base_name + '-script.py')
	else:
		return os.path.join(bin_dir, script_base_name)

def set_bin_dir(home_dir):
	global bin_dir
	if sys.platform == 'win32':
		bin_dir = os.path.join(home_dir, 'Scripts')
	else:
		bin_dir = os.path.join(home_dir, 'bin')

def run_bin_executable(prog, *args):
	cmd = [os.path.join(bin_dir, prog)]
	cmd.extend(args)
	subprocess.call(cmd)

def run_py_script(*args):
	run_bin_executable('python', *args)

def inst_package(package, *args):
	# We have to run the script explicitly because easy_install sets its exe to require admin
	# privs on Vista. We don't actually need such privs, so we avoid the elevation.
	run_py_script(locate_installed_script('easy_install'), package, *args)

def check_python():
	if sys.version_info < (2,5):
		if sys.platform == "darwin":
			print darwin
		elif sys.platform == "win32":
			print win32
		else:
			print other
		return False
	else:
		return True

def setup_tg_for_devel(code_root):
	os.chdir(code_root)
	if os.path.exists('setup.py'):
		run_py_script('setup.py', 'develop')
		run_py_script(locate_installed_script('tg-admin'), 'sql', 'create')
		return True

def after_install(options, home_dir):
	if not check_python():
		sys.exit()
	set_bin_dir(home_dir)
	if sys.platform == "win32":
		inst_package('pywin32')
	inst_package('tg_bootstrap >= %(boostrap_version)s')
	if release_version_ is None:
		code_root = os.path.join(home_dir, 'src')
		subprocess.call(['svn', 'co', src_repository_, code_root])
		setup_tg_for_devel(code_root) or setup_tg_for_devel(os.path.join(code_root, proj_))
	else:
		inst_package('%(escaped_substiution)s == %(escaped_substiution)s' %(escaped_percent)s (proj_, release_version_))
''')
