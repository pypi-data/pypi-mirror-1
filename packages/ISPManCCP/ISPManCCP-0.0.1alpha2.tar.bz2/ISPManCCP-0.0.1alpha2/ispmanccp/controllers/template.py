# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: template.py 2 2006-08-26 17:51:50Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha2/ispmanccp/controllers/template.py $
# $LastChangedDate: 2006-08-26 18:51:50 +0100 (Sat, 26 Aug 2006) $
#             $Rev: 2 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from ispmanccp.lib.base import *

class TemplateController(BaseController):
    def view(self, url):
        """
        This is the last place which is tried during a request to try to find a 
        file to serve. It could be used for example to display a template::
        
            def view(self, url):
                return render_response(url+'.myt')
        
        The default is just to abort the request with a 404 File not found
        status message.
        """
        abort(404)
