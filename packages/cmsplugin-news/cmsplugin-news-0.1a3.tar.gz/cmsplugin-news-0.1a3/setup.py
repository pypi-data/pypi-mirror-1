from setuptools import setup, find_packages

setup(
    name='cmsplugin-news',
    version='0.1a3',
    description='This is a news plugin for the django-csm',
    author='Harro van der Klauw',
    author_email='hvdklauw@gmail.com',
    url='http://bitbucket.org/MrOxiMoron/cmsplugin-news/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools', 'setuptools_bzr'],
)
