# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: domain.py 26 2006-11-03 19:29:49Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha1/ispmanccp/models/domain.py $
# $LastChangedDate: 2006-11-03 19:29:49 +0000 (Fri, 03 Nov 2006) $
#             $Rev: 26 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from formencode import validators, Schema
from ispmanccp.models.validators import *

class ChangeDomainPassword(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    ispmanDomain = validators.String(not_empty=True)
    cur_pass = CurrentPassword(not_empty=True)
    new_pass = SecurePassword(not_empty=True)
    chk_pass = validators.String(not_empty=True)
    chained_validators = [
        validators.FieldsMatch('new_pass', 'chk_pass')
    ]
