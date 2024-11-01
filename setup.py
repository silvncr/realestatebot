from pathlib import Path

from realestatebot import __author__, __doc__, __license__, __module__, __version__
from setuptools import setup

setup(
	name=__module__,
	version=__version__,
	description=__doc__,
	long_description=Path('README.md').read_text(),
	long_description_content_type='text/markdown',
	url=f'https://github.com/{__author__}/{__module__}',
	author=__author__,
	include_package_data=True,
	license=__license__,
	packages=[__module__],
	package_data={},
	install_requires=[
		'alive-progress==3.2.0',
		'pandas==2.2.3',
		'python-dotenv==1.0.1',
		'realestate-data==0.1.0',
		'requests==2.32.3',
	],
	setup_requires=['pytest_runner'],
	python_requires='>=3.12',
	scripts=[],
	tests_require=['pytest'],
	entry_points={},
	zip_safe=True,
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
)
