from ispmanccp.lib.base import *

class LockedController(BaseController):
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
        if self.dominfo['ispmanDomainLocked'] == 'false':
            h.redirect_to('/')

        c.domain_locked = True
        return render_response('locked.index')
