from distutils.core import setup, Extension

setup	(name = 'python-krb5',
	version = '0.2',
	description = 'Kerberos 5 Bindings for Python',
        long_description = """
This extension all python programs to access the MIT Kerberos 5 libraries to manipulate principals and credentials.
""",
	author = 'Benjamin Montgomery',
	author_email = 'bmontgom@montynet.org',
	classifiers = [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: C',
		'Topic :: System :: Systems Administration :: Authentication/Directory'
		],
	ext_modules = 	[Extension	('krb5', 
					['python-krb5.c', 'principal.c', 'credential.c', 'error.c'],
					libraries = ['krb5', 'com_err']
					)
			]
	)
