"""Tasks to download, configure, compile and install OpenCore."""

import os
join = os.path.join

from buildit.task import Task
from topp.build.lib.taskfuncs import copyskeleton
from buildit.commandlib import Substitute, InFileWriter

from topp.build.lib.commands import EasyInstall, TarballExtractor

# Products 
# these should be done in a better way, more svn-friendly
def products(prepend=''):
    """
    ATContentTypes            DataGridField                
    ATReferenceBrowserWidget  DocFinderTab                 ResourceRegistries
    AddRemoveWidget           ExtendedPathIndex            RichDocument
    ExternalEditor               SecureMailHost
    Fate                         TeamSpace
    Anonymailer               Five                         ZopeVersionControl
    Archetypes                GenericSetup                 contentmigration
    CMFActionIcons            GroupUserFolder              
    CMFCalendar               MailBoxer                    
    CMFCore                   MaildropHost                 i18ntestcase
    CMFDefault                Marshall                     intelligenttext
    CMFDiffTool               MimetypesRegistry            kupu
    OFolder
    CMFDynamicViewFTI         PageCacheManager             listen
    CMFEditions               PasswordResetTool            membrane
    CMFFormController         PlacelessTranslationService  
    CMFPlacefulWorkflow       PloneErrorReporting          ploneundelete
    CMFPlone                  PloneLanguageTool            remember
    CMFQuickInstallerTool     PlonePAS                     statusmessages
    CMFSetup                  PloneTestCase                testing
    CMFSquidTool              PloneTranslations            txtfilter
    CMFTestCase               PluggableAuthService         
    CMFTopic                  PluginRegistry               validation
    CMFUid                    Poi                          wicked
    CacheSetup                PolicyHTTPCacheManager
    DCWorkflow                PortalTransforms
    """
    return [ join(prepend, i) for i in products.__doc__.split() ]

bin_skel = copyskeleton(name='copy bin/ skeleton',
                        fromdir='${moduledir}/skel/bin',
                        todir='${deploydir}/bin',
                        targets=['${deploydir}/bin/accept_certificates.sh', 
                                 '${deploydir}/bin/pollzope.sh']
                        )

checkout = Task(
    'Checkout OpenPlans bundle from subversion',
    namespaces='opencore',
    targets = products('${products}'),
    commands=[ 
        '${deploydir}/bin/accept_certificates.sh',        
        'svn co ${./repository_url_bundle} ${products}', ],
    dependencies=(bin_skel,)
    )

install_bundle = Task(
    'Install Opencore bundle',
    targets = products('${zope_instance}/Products'),
    commands=[ 'ln -fs ${products}/* ${zope_instance}/Products/', ],
    dependencies=(checkout,),
    )

admin_file = Task(
    'Creating TOPP_ADMIN_INFO',
    namespaces='universal',
    targets = '${./topp_admin_info_filename}',
    commands = [ 'mkdir -p `dirname ${./topp_admin_info_filename}`',
                 'echo ${zope_user}:${zope_password} > ${./topp_admin_info_filename}',
                 'chmod 660 ${./topp_admin_info_filename}' ],
    )

checkout_xinha = Task(
    'Checkout xinha',
    workdir='${deploydir}/src/opencore/opencore/nui',
    commands=['svn co http://svn.xinha.webfactional.com/tags/0.92beta xinha'],
    dependencies=(install_bundle,),
    targets='${deploydir}/src/opencore/opencore/nui/xinha',
    )

install = Task(
    'Install OpenCore',
    namespaces=['opencore', 'zope'],
    workdir='${deploydir}',
    commands=['touch ${deploydir}/.workingenv/opencore-products-installed.txt'],
    targets=['${zope_instance}/Products',
             '${deploydir}/.workingenv/opencore-products-installed.txt'
             ],
    dependencies=(install_bundle, checkout_xinha, admin_file)
    )

runzeo = Task(
    'start zeo',
    workdir='${zeo_instance}',
    commands=['bin/zeoctl start'],
    dependencies=(install,),
    )

runzope = Task(
    'start zope',
    workdir='${zope_instance}',
    commands=['bin/zopectl fg &> log/firstrun.log & echo -n $! > var/firstrun.pid',
              '${deploydir}/bin/pollzope.sh',
              'kill `cat var/firstrun.pid`',
              '! ps `cat var/firstrun.pid`',
              'bin/zopectl start'],
    dependencies=(runzeo,),
    )

create_site = Task(
    'creating OpenPlans site',
    workdir='${zope_instance}',
    commands=[ '${deploydir}/bin/create-site.sh' ],
    dependencies=(runzope, bin_skel)
    )
