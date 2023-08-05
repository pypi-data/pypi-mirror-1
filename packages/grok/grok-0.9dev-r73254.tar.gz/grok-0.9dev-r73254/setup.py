from setuptools import setup, find_packages

setup(
    name='grok',
    version='0.9',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='https://launchpad.net/grok',
    download_url='svn://svn.zope.org/repos/main/grok/trunk#egg=grok-dev',
    description='Grok: Now even cavemen can use Zope 3!',
    long_description=open('README.txt').read(),
    license='ZPL',

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,    
    install_requires=['setuptools'],
)
