#!/usr/bin/python

def write_arg(cmd, basename, filename):
    argname = os.path.splitext(basename)[0]
    value = getattr(cmd.distribution, argname, None)
    if value is not None:
        value = '\n'.join(value)+'\n'
    cmd.write_or_delete_file(argname, filename, value)


from setuptools import setup, find_packages
setup(
    name = "pyvb",
    version = "0.0.4",
    packages = find_packages('src'),
    install_requires = [],
    package_dir = {'':'src'},
    scripts=[],
    zip_safe=False,
    author = "Adam Boduch",
    author_email = "adam@enomaly.com",
    description = "Python VirtualBox API.",
    license = "GPL",
    url = "http://enomalism.com/api/pyvb/",   
)
