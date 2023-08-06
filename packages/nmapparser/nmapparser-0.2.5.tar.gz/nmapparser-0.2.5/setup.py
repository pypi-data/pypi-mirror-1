from distutils.core import setup

package_to_install = "nmapparser"

setup(
    name = package_to_install,
    version = '0.2.5',
    description = 'A nmap xml parser',
    author='Guilherme Polo',
    author_email = 'ggpolo@gmail.com',
    packages = [package_to_install],
    )
