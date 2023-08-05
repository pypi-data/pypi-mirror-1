""" options for this script -- topp.build.opencore """

def add_options(parser):

    ### add generic options
    
    parser.add_option('--create-site',
                      dest="create_site",
                      action="store_true",
                      default=False,
                      help="create openplans site and customizations")

    ### add options that override .ini file variables

    parser.add_context_option('--zope-port', 
                              dest='zope_port', 
                              help='Zope HTTP server port number.',
                              metavar='ZOPE-PORT'
                              )
    
    parser.add_context_option('--zeo-port', 
                              dest='zeo_port',
                              help='The port the ZEO server will listen on.', 
                              metavar="ZEO-PORT")

    parser.add_context_option('--debug-mode',
                              dest='debug_mode',
                              default='${zope/debug_mode}',
                              help="Run Zope in debug mode? (on/off, default defined by the distribution settings)",
                              metavar="DEBUG-MODE"
                              )

    parser.add_context_option('--with-zope',
                              dest='zope_source',
                              directory=True,
                              default='${srcdir}/${zope/package}',
                              help="Location of an existing Zope source checkout (must have write access?)",
                              metavar="/path/to/Zope-source-checkout",
                              )

    parser.add_context_option('--with-products',
                              dest='products',
                              directory=True,
                              default='${deploydir}/src/${opencore/package}',
                              help="Location of an existing Products bundle (will be symlinked in)",
                              metavar="/path/to/products-bundle-checkout",
                              )
    
    parser.add_context_option('--with-python',
                              dest='python',
                              help="Location of the python you want to use",
                              metavar="/path/to/python",
                              )

