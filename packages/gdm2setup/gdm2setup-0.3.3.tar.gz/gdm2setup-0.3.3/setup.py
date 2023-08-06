from distutils.core import setup
 
setup(name='gdm2setup',
	version='0.3.3',
	author='Garth Johnson',
	author_email='growlf@biocede.com',
	description='GDM2 Setup utility and libraries',
	long_description=open('README').read(),
	license='GPL2',
	url='https://launchpad.net/gdm2setup/',
	packages=['gdm2'],
	package_data = {'gdm2': ['gdm2setup.glade']},

	scripts=['gdm2setup'],
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: X11 Applications :: GTK',
		'Environment :: X11 Applications :: Gnome',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python',
		'Topic :: Desktop Environment :: Gnome',
		'Topic :: System :: Installation/Setup',
		'Topic :: System :: Systems Administration',
		'Topic :: Utilities',
		],
	data_files=[
		('/usr/share/applications', ['gdm2setup.desktop']),
		('/usr/bin', ['gdm2setup']),
		]

)
