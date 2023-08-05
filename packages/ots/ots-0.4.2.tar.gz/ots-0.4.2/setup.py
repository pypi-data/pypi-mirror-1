import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
from setuptools.extension import Extension
from subprocess import Popen, PIPE

PKG_CONFIG="pkg-config"
def pkgconfig(packages):
    """Given a list of packages return a list of all includes and a
    list of all library dependencies. If the package doesn't exist and
    exception will be thrown
    """

    # Process Includes
    includes = "%s --cflags-only-I %s" % (PKG_CONFIG, packages)
    p = Popen([includes], shell=True,
              stdin=PIPE, stdout=PIPE, stderr=PIPE,
              close_fds=True)

    includes_list = [b[2:] for b in p.stdout.read().split()]
    p.wait()
    if p.returncode != 0: raise ValueError(p.stderr.read())

    # Process Libs
    libs = "%s --libs-only-l %s" % (PKG_CONFIG, packages)
    p = Popen([libs], shell=True,
              stdin=PIPE, stdout=PIPE, stderr=PIPE,
              close_fds=True)

    libs_list = [b[2:] for b in p.stdout.read().split()]
    p.wait()
    if p.returncode != 0: raise ValueError(p.stderr.read())

    return includes_list, libs_list

includes, libs = pkgconfig("libxml-2.0 glib-2.0")


setup(
    name = "ots",
    version = "0.4.2", 
    packages = ["src", "lib"],
    include_package_data=True,
    package_data={'lib': ['*.bz2']},
    ext_modules=[
    Extension("ots", ["src/ots.pyx"],
              libraries = [ "ots-1", ] + libs,
              include_dirs = ['/usr/include/libots-1',
                              '/usr/local/include/libots-1', ] + includes,
              )
    ],
    
    author = "Benjamin Saller",
    author_email = "bcsaller@objectrealms.net",
    description = "Python bindings around libots. For summarizing text.",
    license = "GPL 2.1",
    keywords = "text topics summarizing classification",
    long_description = """Python bindings to libots which allows for text
    auto-summarization and limited classification options.
    """,
    )
