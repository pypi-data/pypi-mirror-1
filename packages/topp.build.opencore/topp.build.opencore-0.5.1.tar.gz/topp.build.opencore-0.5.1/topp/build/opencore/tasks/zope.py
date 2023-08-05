"""Tasks to download, configure, compile and install Zope."""

import os

join = os.path.join

from buildit.task import Task
from topp.build.lib.taskfuncs import copyskeleton
from buildit.commandlib import Patch

checkout = Task(
    'Checkout Zope',
    namespaces='zope',
    workdir='${srcdir}',
    targets=['${zope_source}'],
    commands = ['svn co ${./svn_url} ${./package}']
    )

resourcedir = join('${moduledir}', 'resources')

patch_zope = Task(
    'Patch Zope',
    namespaces='zope',
    workdir='${zope_source}',
    targets=['${zope_source}/test.py.origorig',
             '${zope_source}/lib/python/AccessControl/__init__.py.origorig',
             '${zope_source}/lib/python/Products/__init__.py.origorig',
             ],
    commands = [Patch("test.py", join(resourcedir, 'test.py.diff'), '0'),
                Patch("lib/python/Products/__init__.py", 
                      join(resourcedir, 'Products.diff'), '0'),
                Patch("lib/python/AccessControl/__init__.py", 
                      join(resourcedir, 'accontrol.diff'), '0'),
                ],
    dependencies=(checkout,)
    )

compile_zope = Task(
    'Compile Zope',
    namespaces='zope',
    targets=['${zope_source}/bin',],
    workdir='${zope_source}',
    commands=['./configure --prefix=${zope_source}',
              'make',
              'make inplace',
              ],
    dependencies=(patch_zope,)
    )

mkzeo = Task(
    'Install a zeo instance',
    namespaces='zope',
    targets='${zeo_instance}/bin/zeoctl',
    workdir='${zope_source}',
    commands=[ 'bin/mkzeoinstance.py ${zeo_instance} ${zeo_port}',],
    dependencies=(compile_zope,)
    )

copy_skel = copyskeleton(fromdir='${moduledir}/skel/zope',
                         todir='${zope_source}/custom_skel',
                         name='copy zope skeleton files',
                         namespaces='zope'
                         )

mkzope = Task(
    'Install a zope instance',
#    namespaces='zope',
    targets=['${zope_instance}/bin/runzope', '${zope_instance}/bin/zopectl'],
    workdir='${zope_source}',
    commands=[
        'bin/mkzopeinstance.py --dir ${zope_instance} --user ${zope_user}:${zope_password} --skelsrc ${zope_source}/custom_skel',
        ],
    dependencies=(compile_zope, copy_skel),
    )

linkzope = Task(
    'link zope home to zope source',
    targets='${zope_home}',
    commands=[ 'ln -s ${zope_source} ${zope_home}' ],
    dependencies=(checkout,)
    )

linkzopebinaries = Task(
    "link zope binaries to be in the env's PATH",
    targets=['${deploydir}/bin/zopectl', '${deploydir}/bin/zeoctl'],
    commands=['ln -s ${deploydir}/zope/bin/zopectl ${deploydir}/bin/',
              'ln -s ${deploydir}/zeo/bin/zeoctl ${deploydir}/bin/'],
    dependencies=(mkzope, mkzeo)
    )
