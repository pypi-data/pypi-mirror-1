# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: app_globals.py 100 2006-12-12 22:11:46Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha3.1/ispmanccp/lib/app_globals.py $
# $LastChangedDate: 2006-12-12 22:11:46 +0000 (Tue, 12 Dec 2006) $
#             $Rev: 100 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import os
import sys
from ispmanccp.lib.helpers import check_path_perms

class Globals(object):

    def __init__(self, global_conf, app_conf, **extra):
        """
        You can put any objects which need to be initialised only once
        here as class attributes and they will be available as globals
        everywhere in your application and will be intialised only once,
        not on every request.

        ``global_conf``
            The same as variable used throughout ``config/middleware.py``
            namely, the variables from the ``[DEFAULT]`` section of the
            configuration file.

        ``app_conf``
            The same as the ``kw`` dictionary used throughout 
            ``config/middleware.py`` namely, the variables the section 
            in the config file for your application.

        ``extra``
            The configuration returned from ``load_config`` in 
            ``config/middleware.py`` which may be of use in the setup of 
            your global variables.

        """
        ispman_installdir = os.path.abspath(app_conf['ispman_base_dir'])
        check_path_perms(ispman_installdir)

        try:
            import perl
        except ImportError:
            print "You need the pyperl module installed."
            print "You can get it from:"
            print "   http://www.felix-schwarz.name/files/opensource/pyperl/"
            sys.exit(1)

        # Get Perl's @INC reference
        inc = perl.get_ref("@INC")

        # Add ISPMan lib directory to perl's @INC
        ispman_libs = os.path.join(ispman_installdir, 'lib')
        check_path_perms(ispman_libs)
        inc.append(ispman_libs)
        # Setup an ISPMan instance
        perl.require('ISPMan')
        perl.require('CGI')

        try:
            # Make ISPMan recognize us as a Control Panel
            self.ispman = perl.eval(
                '$ENV{"HTTP_USER_AGENT"} = "PYTHON-CCP"; ' +
                '$ispman = ISPMan->new() or die "$@"'
            )
        except Exception, e:
            print e

        self.ldap_host = self.ispman.getConf('ldapHost')
        self.ldap_version = self.ispman.getConf('ldapVersion')
        self.ldap_base_dn = self.ispman.getConfig('ldapBaseDN')

        # Also pass the perl reference for further use within the app
        self.perl = perl
        pass

    def __del__(self):
        """
        Put any cleanup code to be run when the application finally exits
        here.
        """
        pass
