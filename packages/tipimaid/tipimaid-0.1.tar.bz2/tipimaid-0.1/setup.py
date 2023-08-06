from distutils.core import setup

DESCRIPTION = """
Tipimaid is a collection of tools to ease the handling of Apache logs. It can
be used as a piped logger for Apache and allows you to distribute log entries
to different logfiles according to their virtual host information and the date
and time of the request. Logging can be done either locally or over the network
so that you can concentrate logs of a server farm on one logging computer.

The Tipimaid collection comprises four scripts which are:

	tipimaid.py
		Used either as a piped logging tool or receives its loglines from
		``tipimaid_server.py``. It rotates logfiles and distributes loglines
		to different logfiles and is able to execute stuff when a file is rotated.

	tipimaid_sender.py
		Used as a piped logging tool to send loglines across the network to
		``tipimaid_server.py``

	tipimaid_server.py
		receives loglines sent by ``tipimaid_sender.py`` or netcat_ and outputs
		them to stdout where they are usually piped to ``tipimaid.py``

	tipimaid_mergelogs.py
		The disaster recovery tool if something went terribly wrong during
		logging over the network. It does a mergesort of several logfiles and
		outputs chronologically sorted loglines to stdout.

.. _netcat: http://netcat.sourceforge.net/
"""


setup(
	name='tipimaid',
	version='0.1',
	author='Nikolas Tautenhahn',
	author_email='nik@livinglogic.de',
	url='http://flloss.livinglogic.de/wiki/tipimaid',
	download_url='http://cheeseshop.python.org/pypi/tipimaid',
	keywords='Apache, logging, piped logging, chronolog, split logs, netcat, rotate logs',
	description='tipimaid supports piped logging (local and over the net) for apache web servers with automatic log rotation and splitting according to domains',
	long_description=DESCRIPTION,
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Programming Language :: Python :: 2.3',
		'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
		'Topic :: Internet :: WWW/HTTP :: Site Management'
	],
	license='GPLv3',
	scripts=['tipimaid.py', 'tipimaid_sender.py', 'tipimaid_server.py', 'tipimaid_mergelogs.py'],
)
