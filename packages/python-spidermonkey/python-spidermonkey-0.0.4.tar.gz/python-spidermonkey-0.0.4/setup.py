"""\
Python/JavaScript bridge module, making use of Mozilla's spidermonkey
JavaScript implementation.  Allows implementation of JavaScript classes,
objects and functions in Python, and evaluation and calling of JavaScript
scripts and functions respectively.  Borrows heavily from Claes Jacobssen's
Javascript Perl module, in turn based on Mozilla's 'PerlConnect' Perl binding.
""",

import os
import subprocess as sp
import sys
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, Extension

def find_sources(extensions=[".c", ".cpp"]):
    ret = []
    for dpath, dnames, fnames in os.walk("./spidermonkey"):
        for fname in fnames:
            if os.path.splitext(fname)[1] in extensions:
                ret.append(os.path.join(dpath, fname))
    return ret

def nspr_config():
    pipe = sp.Popen("nspr-config --cflags --libs",
                        shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    (stdout, stderr) = pipe.communicate()
    if pipe.wait() != 0:
        raise RuntimeError("Failed to get nspr config.")
    bits = stdout.split()
    ret = {"include_dirs": [], "library_dirs": [], "libraries": []}
    prfx = {"-I": "include_dirs", "-L": "library_dirs", "-l": "libraries"}
    for b in bits:
        ret[prfx[b[:2]]].append(b[2:])
    return ret

def platform_config():
    sysname = os.uname()[0]
    machine = os.uname()[-1]
   
    config = nspr_config()
    config["include_dirs"].append("spidermonkey/%s-%s" % (sysname, machine))
    config["extra_compile_args"] = [
        "-DJS_THREADSAFE",
        "-DPOSIX_SOURCE",
        "-D_BSD_SOURCE",
        "-Wno-strict-prototypes"
    ]

    if sysname == "Linux":
        config["extra_compile_args"].extend([
            "-DHAVE_VA_COPY",
            "-DVA_COPY=va_copy"
            ])

    if sysname in ["Darwin", "Linux"]:
        config["extra_compile_args"].append("-DXP_UNIX")
    else:
        raise RuntimeError("Unknown system name: %s" % sysname)

    return config

setup(
    name = "python-spidermonkey",
    version = "0.0.4",
    license = "MIT",
    author = "Paul J. Davis",
    author_email = "paul.joseph.davis@gmail.com",
    description = "JavaScript / Python bridge.",
    long_description = __doc__,
    url = "http://github.com/davisp/python-spidermonkey",
    download_url = "http://github.com/davisp/python-spidermonkey.git",
    zip_safe = False,
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: JavaScript',
        'Programming Language :: Other',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    setup_requires = [
        'setuptools>=0.6c8',
    ],

    ext_modules =  [
        Extension(
            "spidermonkey",
            sources=find_sources(),
            **platform_config()
        )
    ],

    test_suite = 'nose.collector',

)
