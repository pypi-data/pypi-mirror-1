import os
import sys

from topp.build.lib import TOPPbuild
from topp.utils.error import error
from topp.build.opencore import options
from topp.build.opencore.tasks import pil, opencore, zope

### global variables

help = """Constructs a ready-to-run OpenCore instance from
scratch, installing Zope, Plone, and all other dependencies.  
"""

app = 'opencore'

def create_builder():
    # check python version
    if not sys.hexversion >= 33817584:
        error("this build requires at least python 2.4.3. please update.")

    # options for workingenv
    workingenv_opts = ('--home', '-r', '${opencore/requirements}' )

    # create the builder with the distributions available
        
    builder = TOPPbuild(app, 
                        workingenv_opts=workingenv_opts,
                        distributions=('local', 'live'),
                        help=help)

    # add command line options
    options.add_options(builder)

    # PIL for graphics
    builder.add_task(pil.install, name='PIL', help="don't install PIL")

    # parse options
    builder.parse_args()

    # test to make sure workingenv --home was used
    wenv = os.environ.get('WORKING_ENV')
    if wenv and builder.options.in_place:
        if not os.path.exists(os.path.join(wenv, 'lib', 'python')):
            error("workingenv must be created with --home")        

    # set variables
    builder.set_variable('zope_instance', 
                         '${deploydir}/zope') # INSTANCE_HOME
    builder.set_variable('zeo_instance', '${deploydir}/zeo')
    builder.set_variable('zope_home', '${deploydir}/lib/zope')

    # Whether to send email on login/join
    EMAILCONFIRMATION = 'True'
    if builder.options.dist == 'local':
        # configure based on whether an SMTP server is running
        from smtplib import SMTP
        import socket
        try:
            SMTP('localhost')
        except socket.error:
            EMAILCONFIRMATION = 'False'
    builder.set_variable('emailconfirmation', EMAILCONFIRMATION)

    # Zope / Plone
    builder += zope.mkzope
    builder += zope.mkzeo
    builder += zope.linkzope
    builder += zope.linkzopebinaries

    # opencore
    if builder.options.create_site:
        builder += opencore.create_site
        builder.set_final_message(os.path.join('${moduledir}', 'results-site-created.txt'))
    else:
        builder += opencore.install
        builder.set_final_message(os.path.join('${moduledir}', 'results-installed.txt'))

    return builder

def main():
    builder = create_builder()
    builder.install()
