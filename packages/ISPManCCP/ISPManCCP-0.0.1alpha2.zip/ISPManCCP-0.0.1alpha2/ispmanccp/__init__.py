# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: __init__.py 2 2006-08-26 17:51:50Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha2/ispmanccp/__init__.py $
# $LastChangedDate: 2006-08-26 18:51:50 +0100 (Sat, 26 Aug 2006) $
#             $Rev: 2 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================
"""
ispmanccp

This file loads the finished app from ispmanccp.config.middleware.

"""

from ispmanccp.config.middleware import make_app
