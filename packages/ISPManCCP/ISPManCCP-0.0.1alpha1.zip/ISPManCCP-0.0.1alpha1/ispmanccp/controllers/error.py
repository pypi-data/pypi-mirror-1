# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: error.py 2 2006-08-26 17:51:50Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha1/ispmanccp/controllers/error.py $
# $LastChangedDate: 2006-08-26 18:51:50 +0100 (Sat, 26 Aug 2006) $
#             $Rev: 2 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import os.path
from paste import fileapp
from pylons.middleware import media_path, error_document_template
from pylons.util import get_prefix
from ispmanccp.lib.base import *

class ErrorController(BaseController):
    """
    Class to generate error documents as and when they are required. This behaviour of this
    class can be altered by changing the parameters to the ErrorDocuments middleware in 
    your config/middleware.py file.
    """

    def document(self):
        """
        Change this method to change how error documents are displayed
        """
        page = error_document_template % {
            'prefix': get_prefix(request.environ),
            'code': request.params.get('code', ''),
            'message': request.params.get('message', ''),
        }
        return Response(page)

    def img(self, id):
        return self._serve_file(os.path.join(media_path, 'img', id))
        
    def style(self, id):
        return self._serve_file(os.path.join(media_path, 'style', id))

    def _serve_file(self, path):
        fapp = fileapp.FileApp(path)
        return fapp(request.environ, self.start_response)
