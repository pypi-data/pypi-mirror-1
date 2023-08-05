from setuptools import setup
import sys, os

from tg_bootstrap.bootstrap import version

f = open(os.path.join(os.path.dirname(__file__), 'docs', 'index.txt'))
long_description = f.read().strip()
f.close()

setup(name='tg_bootstrap',
		version=version,
		description="Bootstrap a TurboGears app in a VirtualEnv",
		long_description=long_description,
		classifiers=[
			'Development Status :: 4 - Beta',
			'Intended Audience :: Developers',
			'License :: OSI Approved :: MIT License',
			],
		install_requires=["virtualenv == 1.0"],
		keywords='setuptools deployment installation virtualenv turbogears',
		author='Arlo Belshee',
		author_email='a+tg_bootstrap@arlim.org',
		url='http://pypi.python.org/pypi/tg_bootstrap',
		license='MIT',
		py_modules=[],
		packages=['tg_bootstrap'],
		zip_safe=True,
	)
