from distutils.core import setup

setup(name = 'txrackspace',
    version = '0.1.1',
    description = 'A twisted python interface into the Rackspace Cloud',
    author = 'Alex Polvi',
    author_email = 'polvi@cloudkick.com',
    packages = ['txrackspace'],
    package_dir = {'txrackspace' : 'src/txrackspace' },
    url = 'http://github.com/polvi/txrackspace',
    install_requires = ['twisted', 'python-cjson>=1.0.5']
) 
