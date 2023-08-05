# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: ispman_helpers.py 90 2006-12-09 20:59:07Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha2/ispmanccp/lib/ispman_helpers.py $
# $LastChangedDate: 2006-12-09 20:59:07 +0000 (Sat, 09 Dec 2006) $
#             $Rev: 90 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

from formencode.variabledecode import variable_decode
from pylons import request, g, cache
from pylons.decorators.cache import beaker_cache
from ispmanccp.lib.helpers import to_unicode, asbool
from ispmanccp.lib.decorators import perlexcept

APP_CONF = g.pylons_config.app_conf

ispman_cache = cache.get_cache('ispman')

allowed_user_attributes = (
    'dn', 'dialupAccess', 'radiusProfileDn', 'uid', 'uidNumber', 'gidNumber',
    'homeDirectory', 'loginShell', 'ispmanStatus', 'ispmanCreateTimestamp',
    'ispmanUserId', 'ispmanDomain', 'DestinationAddress', 'DestinationPort',
    'mailQuota', 'mailHost', 'fileHost', 'cn', 'mailRoutingAddress',
    'FTPStatus', 'FTPQuotaMBytes', 'mailAlias', 'sn', 'mailLocalAddress',
    'userPassword', 'mailForwardingAddress', 'givenName')

updatable_attributes = (
    'ispmanStatus', 'mailQuota', 'mailAlias', 'sn', 'userPassword',
    'givenName', 'updateUser', 'uid', 'mailForwardingAddress', 'ispmanDomain',
    'FTPQuotaMBytes', 'FTPStatus', 'mailHost', 'fileHost', 'dialupAccess',
    'radiusProfileDN'
)


def get_cache(domain):
    return cache.get_cache(domain)


def get_domain_users(domain, attr_list): #attributes_to_retrieve):
    """Function to get the `attr_list` from all users on `domain`"""
    if attr_list.count('ispmanUserId') < 1:
        attr_list.append('ispmanUserId')

    userlist = to_unicode(g.ispman.getUsers(domain, attr_list))
    if not userlist:
        return []
    decorated = [(dict_['ispmanUserId'], dict_) for dict_ in userlist.values()]
    decorated.sort()
    result = [dict_ for (key, dict_) in decorated]
    return result


def address_exists_on_domain(domain, address):
    users = get_domain_users(
        domain,
        [
            "ispmanUserId",
            "mailAlias",
            "mailLocalAddress",
            #"mailForwardingAddress"
        ]
    )
    for user in users:
        for key, val, in user.iteritems():
            if isinstance(val, list):
                for n in range(len(val)):
                    if val[n] == address:
                        return user["ispmanUserId"]
            elif val == address:
                return user["ispmanUserId"]
    return None


def get_users_list(domain, letter, sortby=None, sort_ascending=True):
    domain_users = get_domain_users(
        domain, [
            "dn",
            "givenName",
            "sn",
            "cn",
            "ispmanCreateTimestamp",
            "ispmanUserId",
            "mailLocalAddress",
            "mailForwardingAddress",
            "userPassword",
            "mailQuota",
            "mailAlias",
            "FTPQuotaMBytes",
            "FTPStatus"
        ]
    )

    userlist = []
    lengths = {}
    for user in domain_users:
        user_id = user['ispmanUserId']
        lengths[user_id] = {}

        # Aparently Genshi converts what it can to strings,
        # we have to make these lists
        if 'mailAlias' in user:
            lengths[user_id]['aliases'] = len(user['mailAlias'])

        if 'mailForwardingAddress' in user:
            lengths[user_id]['forwards'] = len(user['mailForwardingAddress'])

        if letter == 'All' or user_id.upper().startswith(letter):
            userlist.append(user)

    # let's save some time and return right away if we don't need any sorting
    if len(userlist) <= 1:
        return lengths, userlist

    decorated = [(dict_[sortby], dict_) for dict_ in userlist]
    decorated.sort()

    if not sort_ascending:
        decorated.reverse()
    result = [dict_ for (key, dict_) in decorated]
    return lengths, result


def get_user_info(uid, domain):
    user_info = to_unicode(g.ispman.getUserInfo(uid + '@' + domain, domain))
    lengths = {}
    lengths[uid] = {}
    if 'mailAlias' in user_info:
        lengths[uid]['aliases'] = len(user_info['mailAlias'])
    if 'mailForwardingAddress' in user_info:
        lengths[uid]['forwards'] = len(user_info['mailForwardingAddress'])
    user_info['mailQuota'] = int(user_info['mailQuota'])/1024
    return lengths, user_info


def get_perl_cgi(params_dict):
    params_dict = variable_decode(params_dict)
    cgi = g.perl.eval('$cgi = new CGI;')
    cgi.charset("UTF-8")
    for key, val in params_dict.iteritems():
        if key in updatable_attributes:
            if isinstance(val, list):
                cgi.param(key, '\n'.join(val))
            else:
                cgi.param(key, str(val))
    return cgi


@perlexcept
def update_user_info(attrib_dict):
    cgi = get_perl_cgi(attrib_dict)
    return asbool(g.ispman.update_user(cgi))


def get_user_attribute_values(id, domain, attribute):
    return to_unicode(
        g.ispman.getUserAttributeValues(id, domain, attribute)
    )

@perlexcept
def delete_user(post_dict):
    cgi = get_perl_cgi(post_dict)
    return asbool(g.ispman.deleteUser(cgi))


def user_exists(user_id):
    uid = user_id + '@' + request.POST['ispmanDomain']
    return bool(int(g.ispman.userExists(uid)))


# cache it for 5 minutes
@beaker_cache(expire=300, query_args=True)
def get_domain_info(domain):
    return to_unicode(dict(
        g.ispman.getDomainInfo(domain, 2))
    )


def get_domain_vhost_count(domain):
    return to_unicode(g.ispman.getVhostCount(domain))


def get_domain_user_count(domain):
    return to_unicode(g.ispman.getUserCount(domain))


# cache it for 1 hour
@beaker_cache(expire=3600, query_args=True)
def get_default_acount_vars():
    defaults = {}
    defaults['defaultUserFtpQuota'] = to_unicode(
        g.ispman.getConf('defaultUserFtpQuota')
    )
    defaults['defaultUserMailQuota'] = to_unicode(
        g.ispman.getConf('defaultUserMailQuota')
    )
    return defaults

@perlexcept
def add_user(attrib_dict):
    cgi = get_perl_cgi(attrib_dict)
    return g.ispman.addUser(cgi)


def ldap_search(ldap_filter="objectClass=*",
                attrs=None,
                scope="sub",
                sort='ispmanUserId',
                ascending=True):

    base = APP_CONF['ispman_ldap_base_dn']
    if attrs is not None:
        results = to_unicode(
            g.ispman.getEntriesAsHashRef(base, ldap_filter, attrs, scope)
        )
    else:
        results = to_unicode(
            g.ispman.getEntriesAsHashRef(base, ldap_filter)
        )
    entries = []

    if not results:
        return None

    for dn in results:
        vals = results[dn]
        vals['dn'] = dn
        entries.append(vals)

    if len(entries) <= 1:
        return entries

    decorated = [(dict_[sort], dict_) for dict_ in entries]
    decorated.sort()

    if not ascending:
        decorated.reverse()

    result = [dict_ for (key, dict_) in decorated]
    return result
