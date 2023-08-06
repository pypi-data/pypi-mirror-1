from pylispng import meta
from pylispng.util import dist


dist.setup(
    name=meta.name,
    version=meta.version,
    description=meta.description,
    author=meta.author,
    author_email="duncan@adytum.us",
    url=meta.projectURL,
    packages=dist.findPackages(),
    scripts=['bin/pylisp-ng'],
    long_description=dist.catReST(
        'docs/PRELUDE.txt',
        'README',
        'TODO',
        'docs/HISTORY.txt',
        'docs/DEPENDENCIES.txt',
        'docs/FOOTNOTES.txt',
        stop_on_errors=True,
        out=True),
    license='LGPL 2.1',
    classifiers=[
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'Intended Audience :: Science/Research',
       'Programming Language :: Python',
       'Programming Language :: Lisp',
       'Topic :: Software Development :: Interpreters',
       'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
       ],
    )
