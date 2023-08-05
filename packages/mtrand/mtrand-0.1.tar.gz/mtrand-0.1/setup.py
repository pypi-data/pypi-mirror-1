import os

from distutils.core import setup, Extension
mtrand_src = 'mtrand.c'

mtrand = Extension('mtrand',
                   sources=[os.path.join('mtrand', x) for x in 
                            [mtrand_src, 'randomkit.c', 'initarray.c',
                            'distributions.c', 'gamma.c', 'polevl.c', 'isnan.c',
                            'const.c']],
                   include_dirs=['mtrand'],
                   libraries=['m'],
                  )

setup(name='mtrand',
      version="0.1",
      author="Robert Kern",
      author_email="robert.kern@gmail.com",
      description="Mersenne Twister PRNG for Numeric",
      long_description="""Implements the Mersenne Twister PRNG for Numeric. It
is intended to replace the RANLIB PRNG in SciPy.""",
      license="MIT",
      url="http://starship.python.net/crew/kernr/source/",
      download_url="http://starship.python.net/crew/kernr/source/",
      ext_modules=[mtrand],
      classifiers = [f.strip() for f in """
        Development Status :: 4 - Beta
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: MIT License
        Operating System :: MacOS :: MacOS X
        Operating System :: Microsoft :: Windows
        Operating System :: POSIX
        Programming Language :: Python
        Programming Language :: C
        Topic :: Scientific/Engineering
        Topic :: Software Development :: Libraries :: Python Modules
        """.splitlines() if f.strip()],
      )
