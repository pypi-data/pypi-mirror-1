# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: environment.py 27 2006-11-03 23:09:28Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha2.1/ispmanccp/config/environment.py $
# $LastChangedDate: 2006-11-03 23:09:28 +0000 (Fri, 03 Nov 2006) $
#             $Rev: 27 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================
import os

import webhelpers
import pylons.config

from ispmanccp.config.routing import make_map

def load_environment(global_conf={}, app_conf={}):
    map = make_map(global_conf, app_conf)
    # Setup our paths
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = {'root_path': root_path,
             'controllers': os.path.join(root_path, 'controllers'),
             'templates': [os.path.join(root_path, path) for path in \
                           ('components', 'templates')],
             'static_files': os.path.join(root_path, 'public')
             }

    # The following options are passed directly into Myghty, so all configuration options
    # available to the Myghty handler are available for your use here
    myghty = {}
    myghty['log_errors'] = True

    myghty['escapes'] = dict(l=webhelpers.auto_link, s=webhelpers.simple_format)

    # Add your own Myghty config options here, note that all config options will override
    # any Pylons config options

    # Return our loaded config object
    return pylons.config.Config(myghty, map, paths)
