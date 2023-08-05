# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: accounts.py 102 2006-12-13 19:52:57Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha2/ispmanccp/controllers/accounts.py $
# $LastChangedDate: 2006-12-13 19:52:57 +0000 (Wed, 13 Dec 2006) $
#             $Rev: 102 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from string import uppercase, digits
from ispmanccp.lib.base import *
from ispmanccp.models.accounts import *


class AccountsController(BaseController):

    #@beaker_cache(expire='never')
    def index(self):
        """Main Index."""
        nav_1st_half = ['All']
        nav_1st_half.extend(list(digits))
        c.nav_2nd_half = list(uppercase)
        c.nav_1st_half = nav_1st_half
        c.domain = self.domain
        return render_response('accounts.index')


    #@beaker_cache(expire=180)
    def userlist(self):
        """Action that returns the user list for the passed start key."""
        sort_by = request.POST['sort_by']
        sort_how = h.asbool(request.POST['sort_how'])

        if 'None' in request.POST['letter']:
            c.users = []
            return render_response('accounts.snippets.userlist')

        if 'letter' in request.POST:
            start_letter = request.POST['letter']
        else:
            start_letter = 'All'

        c.lengths, userlist = get_users_list(self.domain,
                                             start_letter,
                                             sortby=sort_by,
                                             sort_ascending=sort_how)

        if not userlist:
            c.error = _("No results retrieved.")
        else:
            c.users = userlist
        return render_response('accounts.snippets.userlist')


    def search(self):
        """Action that returns an html list of entries for the
        auto-complete search field."""
        sort_by = request.POST['sort_by']
        if sort_by not in ("ispmanUserId", "mailLocalAddress", "givenName", "sn"):
            sort_by = "ispmanUserId"
        sort_how = h.asbool(request.POST['sort_how'])
        search_str = request.POST['uidsearch']

        userlist = get_domain_users(
            self.domain,
            [
                "ispmanUserId",
                "mailLocalAddress",
                "givenName",
                "sn",
                "cn",
                "mailAlias",
                "mailForwardingAddress"
            ]
        )

        def _search_user_attributes(user_dict):
            for key, val in user_dict.iteritems():
                if isinstance(val, list):
                    for n in range(len(val)):
                        if val[n].find(search_str) != -1:
                            return n, key, True
                elif user_dict[key].find(search_str) != -1:
                    return None, key, True
            return None, None, False

        html = u'<ul>\n'
        for user in userlist:
            idx_found, attr_found, user_found = _search_user_attributes(user)
            if user_found:
                html += '<li>\n'
                html += u'<span class="informal">%(cn)s</span>\n'
                html += u'<div class="uid">%(ispmanUserId)s</div>\n'
                if attr_found in ('mailAlias', 'mailForwardingAddress'):
                    pre_html = u'<div class="email">\n'
                    pre_html += u'<span class="informal"><em>'
                    pre_html += u'<b>%s</b> %s</em></span>'
                    pre_html += u'</div>\n'
                    if attr_found == 'mailAlias':
                        html += pre_html % (_('Alias:'),
                                            user[attr_found][idx_found])
                    else:
                        html += pre_html % (_('Forwarding:'),
                                            user[attr_found][idx_found])
                else:
                    html += u'<div class="email">'
                    html += u'<span class="informal"><em><b>' + _('Email:')
                    html += '</b> %(mailLocalAddress)s</em></span>'
                    html += u'</div>\n'
                html += u'</li>'
                html = html % user
        html += u'</ul>\n'
        return Response(html)


    def get_stored_pass(self, id):
        """Action that restores the stored password of the user."""
        uid = id + '@' + self.domain
        c.userinfo = {}
        c.userinfo['userPassword'] = get_user_attribute_values(uid, self.domain, 'userPassword')
        return render_response('accounts.snippets.password')



    @rest.dispatch_on(POST='delete_post')
    def delete(self, id):
        """Action to delete the account."""
        if request.method == 'POST':
            print request.POST
        c.lengths, c.userinfo = get_user_info(id, self.domain)
        return render_response('accounts.deleteuser')


    @validate(template='accounts.deleteuser', schema=AccountDelete(), form='delete')
    def delete_post(self, id):
        """The real work for the above action."""
        if request.method != 'POST':
            redirect_to(action="delete", id=id)

        retval = delete_user(request.POST)
        if not retval:
            session['message'] = _('Backend Error')
            session.save()
            self.message = 'Backend Error'
            h.redirect_to(action="delete", id=id)
        session['message'] = _('Operation Successfull')
        session.save()
        redirect_to(action="index", id=None)



    #@beaker_cache(expire=180)
    @rest.dispatch_on(POST='edit_post')
    def edit(self, id):
        """Action to edit the account details."""
        c.lengths, c.userinfo = get_user_info(id, self.domain)
        if c.form_result:
            # Form has been submited
            # Assign the form_result to c.userinfo
            c.lengths, c.userinfo = h.remap_user_dict(c.form_result, c.userinfo)
        return render_response('accounts.edituser')


    @validate(template='accounts.edituser', schema=AccountUpdate(), form='edit', variable_decode=True)
    def edit_post(self, id):
        """The real work for the above action, where modifications
        are made permanent."""
        if request.method != 'POST':
            redirect_to(action='edit', id=id)
        user_dict = request.POST.copy()
        user_dict['uid'] = user_dict['uid'] + '@' + self.domain
        uid = user_dict['uid']
        retval = update_user_info(user_dict)
        if not retval:
            session['message'] = _('Backend Error')
            session.save()
            h.redirect_to(action="edit", id=id)
        session['message'] = _('Operation Successfull')
        session.save()
        redirect_to(action="index", id=None)


    @rest.dispatch_on(POST='new_post')
    def new(self, id):
        """Action to create a new account."""
        # Can the domain have more accounts
        max_accounts = int(get_domain_user_count(self.domain))
        if self.dominfo['ispmanMaxAccounts'] == 'unlimited':
            cur_accounts = -1
        else:
            cur_accounts = int(self.dominfo['ispmanMaxAccounts'])
        if max_accounts != -1 and cur_accounts + 1 > max_accounts:
            session['message'] = _(
                'You cannot create more accounts. Allowed maximum reached.'
            )
            session.save()
            redirect_to(action="index", id=None)

        # It can, let's continue
        c.defaults = get_default_acount_vars()
        c.dominfo = self.dominfo
        c.password = self._generate_new_password()
        if 'ispmanUserId' not in request.POST:
            c.userinfo = {'ispmanUserId': u'please change me'}

        if c.form_result:
            c.lengths, c.userinfo = h.remap_user_dict(c.form_result, request.POST.copy())
        return render_response('accounts.newuser')


    @validate(template='accounts.newuser', schema=AccountCreate(), form='new', variable_decode=True)
    def new_post(self, id):
        """The real work for the above action, where modifications
        are made permanent."""
        if request.method != 'POST':
            redirect_to(action='new', id=None)
        # DO SOMETHING

        userinfo = request.POST.copy()
        # add some account defaults
        userinfo['dialupAccess'] = u'disabled'
        userinfo['radiusProfileDN'] = u'cn=default, ou=radiusprofiles, ' + g.ldap_base_dn

        userinfo['fileHost'] = self.dominfo['ispmanDomainDefaultFileServer']

        if not h.asbool(userinfo['ForwardingOnly']):
            userinfo['mailHost'] = self.dominfo['ispmanDomainDefaultMailDropHost']

        retval = add_user(userinfo)
        if not retval:
            session['message'] = _('Backend Error')
            session.save()
            h.redirect_to(action="new", id=None)

        # Choose message to display  based on the account being forwarding only or not
        if h.asbool(userinfo['ForwardingOnly']):
            session['message'] = _(
                'Account added. You now need to setup a forwarding address.'
            )
        else:
            session['message'] = _(
                'Account added. You can now setup alias and/or forwarding addresses.'
            )
        session.save()
        redirect_to(action="edit", id=userinfo['ispmanUserId'])


    def _generate_new_password(self):
        """Private method that returns a new random password(value)."""
        APP_CONF = request.environ['paste.config']['app_conf']
        numbers = int(APP_CONF['passwords_non_letter_min_chars'])
        alpha = int(APP_CONF['passwords_min_length']) - numbers
        return h.random_pass(alpha, numbers)


    def generate_new_password(self):
        """Action that returns a new random password(rendered html)."""
        c.password = self._generate_new_password()
        return render_response('accounts.snippets.newpassword')

