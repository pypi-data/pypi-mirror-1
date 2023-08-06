from distutils.core import setup

setup(name = 'txrackspace',
    version = '0.1.2',
    description = 'A twisted python interface into the Rackspace Cloud',
    author = 'Alex Polvi',
    author_email = 'polvi@cloudkick.com',
    packages = ['txrackspace'],
    package_dir = {'txrackspace' : 'src/txrackspace' },
    license = 'BSD',
    url = 'http://github.com/cloudkick/txrackspace',
    requires = ['twisted', 'python_cjson']
) 
