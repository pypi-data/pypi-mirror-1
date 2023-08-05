# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: domain.py 34 2006-11-05 18:57:20Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha2.2/ispmanccp/controllers/domain.py $
# $LastChangedDate: 2006-11-05 18:57:20 +0000 (Sun, 05 Nov 2006) $
#             $Rev: 34 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from ispmanccp.models.domain import ChangeDomainPassword
from ispmanccp.lib.base import *

class DomainController(BaseController):
    # Verbose descriptions
    accounts_verbose = _("%(ispmanAccounts)s of %(ispmanMaxAccounts)s accounts.")
    vhosts_verbose = _("%(ispmanVhosts)s of %(ispmanMaxVhosts)s vhosts.")

    def index(self):
        # Translate -1 to unlimited for more readability
        if self.dominfo['ispmanMaxVhosts'] == '-1':
            self.dominfo['ispmanMaxVhosts'] = _('unlimited')
        if self.dominfo['ispmanMaxAccounts'] == '-1':
            self.dominfo['ispmanMaxAccounts'] = _('unlimited')

        # Grab Current Accounts and VHosts Totals
        self.dominfo['ispmanVhosts'] = get_domain_vhost_count(self.domain)
        self.dominfo['ispmanAccounts'] = get_domain_user_count(self.domain)

        # Construct verbose descriptions
        c.accounts_verbose = self.accounts_verbose % self.dominfo
        c.vhosts_verbose = self.vhosts_verbose % self.dominfo

        c.dominfo = self.dominfo
        return render_response('domain.index')

    @rest.dispatch_on(POST='changepass_post')
    def changepass(self):
        c.dominfo = self.dominfo
        return render_response('domain.changepass')

    @validate(template='domain.changepass', schema=ChangeDomainPassword(), form='changepass')
    def changepass_post(self):
        if request.method == 'GET':
            return redirect_to(action='changepass')

        domain = request.POST['ispmanDomain']
        passwd = request.POST['new_pass']
        print "Changing password for domain '%s'. LDAP Bind will fail shortly." % domain
        retcode = g.ispman.changeDomainPassword(domain, passwd)
        if retcode != 1:
            session['message'] = _('Problems occured while changing password.')
            session.save()
            return redirect_to(action='changepass')

        session['message'] = _('Operation successfull.')
        session.save()
        return redirect_to(action='index')

