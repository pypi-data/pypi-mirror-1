"""Tasks to download, compile and install Python Imaging Library."""

from buildit.task import Task
from topp.build.lib.commands import DistUtilInstaller

install = Task(
    'Install Python Imaging Library',
    namespaces='pil',
    workdir='${srcdir}',
    targets='${deploydir}/bin/pilconvert.py',
    commands=[ DistUtilInstaller('${./download_url}') ],
    )

