# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: validators.py 113 2007-01-08 19:25:59Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha2.2/ispmanccp/models/validators.py $
# $LastChangedDate: 2007-01-08 19:25:59 +0000 (Mon, 08 Jan 2007) $
#             $Rev: 113 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import os
import re

from formencode import validators, FancyValidator, Invalid
from formencode.variabledecode import variable_decode
from pylons import request, h, g
from pylons.helpers import log
from pylons.i18n import _
from ispmanccp.lib.ispman_helpers import address_exists_on_domain


class CurrentPassword(FancyValidator):
    """ Validator to check the domain's current password."""
    def _to_python(self, value, state):
        # Strip any leading/trailing whitespace
        return value.strip()

    def validate_python(self, value, state):
        ldap_pass = g.ispman.getDomainAttribute(
            request.POST['ispmanDomain'], 'userPassword').strip()
        coded_pass = g.ispman.encryptPassWithMethod(
            value, g.ispman.getConf('userPassHashMethod')).strip()
        if coded_pass != ldap_pass:
            raise Invalid(_("Current password not correct"),
                                     value, state)


class PasswordsMatch(validators.UnicodeString):
    """ Validator that does not complain about the empty value. This is to
    allow the update of a user's account, which if pass is the same as the
    stored one, no modification is made. If a value is found, then check
    against the first value and fail if they dont match."""
    def validate_python(self, value, state):
        if value is '':
            return value

        to_match = request.POST['userPassword']
        if value != to_match:
            raise Invalid(_("Passwords do not match."), value, state)


class SecurePassword(validators.UnicodeString):
    """Validator to enforce some minimaly secure passwords."""

    config = request.environ['paste.config']['app_conf']
    bad_passwords_file = config['bad_passwords_file'] or None
    min_length = int(config['passwords_min_length']) or 5
    min_non_letter = int(config['passwords_non_letter_min_chars']) or 1
    letter_regex = re.compile(r'[a-zA-Z]')

    messages = {
        'too_few': _(
            'Your password must be longer than %(min_length)i characters long'
        ),
        'non_letter': _(
            'You must include at least %(min_non_letter)i numeric '
            'character(s) your password',
        ),
        'non_dict': _(
            'Please do not base your password on a dictionary term'),
    }

    def _to_python(self, value, state):
        # Strip any leading/trailing whitespace
        return value.strip()

    def validate_python(self, value, state):
        if len(value) < self.min_length:
            raise Invalid(self.message(
                "too_few", state, min_length=self.min_length), value, state)

        non_letters = self.letter_regex.sub('', value)
        if len(non_letters) < self.min_non_letter:
            raise Invalid(self.message(
                "non_letter", state, min_non_letter=self.min_non_letter),
                value, state)

        if self.bad_passwords_file:
            if not os.path.isfile(self.bad_passwords_file):
                log(_("The file setting for bad_passwords_file %r is not a "
                      "valid one, please correct it or comment it out" % \
                      self.bad_passwords_file
                     )
                   )
            else:
                f = open(self.bad_passwords_file)
                lower = value.strip().lower()
                for line in f:
                    if line.strip().lower() == lower:
                        raise Invalid(self.message(
                            "non_dict", state), value, state)


class ValidMailAlias(validators.Email):
    """Validator that checks if the alias being added is for the same
    domain. We won't allow alias to remote emails."""

    messages = {
        'same_domain': _(
            "The alias must be kept under the same domain: %(domain)s"
        ),
        'not_unique': _(
            'This address is already taken. Please choose a diferent one.'
        ),
        'duplicate': _("Don't duplicate mail aliases."),
        'equal_to_local': _(
            "This alias is equal to your local address. There's no need to.")
    }

    def validate_python(self, value, state):
        # Check for duplicate alias on the same user.
        if variable_decode(request.POST)['mailAlias'].count(value) > 1:
            raise Invalid(self.message('duplicate', state), value, state)

        domain = request.POST['ispmanDomain']
        uid = request.POST['ispmanUserId']

        # Check if alias is equal to local address
        if uid + '@' + domain == value:
            raise Invalid(self.message('equal_to_local', state), value, state)

        # Check if alias is within the domain
        if not value.endswith(domain):
            raise Invalid(self.message('same_domain', state, domain=domain),
                          value, state)

        # Check if alias is not yet taken by another user
        not_unique = address_exists_on_domain(domain, value)
        if not_unique != None and not_unique != uid:
            raise Invalid(self.message('not_unique', state), value, state)

        # Finally check if alias complies with a normal email address
        validators.Email.validate_python(self, value, state)


class CorrectNamesValidator(validators.UnicodeString):
    """Validator for person's names, which normally don't include numbers,
    underscores, etc. We do although, allow spaces in case we'd like to add
    more than one name, ie, FirstName: Steve Jonas, LastName: Alchemy."""

    messages = {
        'not_valid_singular': _('%(chars)s is not allowed on names.'),
        'not_valid_plural': _('%(chars)s are not allowed on names.')
    }

    def validate_python(self, value, state):
        validators.UnicodeString.validate_python(self, value, state)
        if value:
            chars = re.findall(r'[^\w\s]|[0-9]|[_]', value, re.U)
            if chars:
                if len(chars) == 1:
                    raise Invalid(
                        self.message(
                            'not_valid_singular', state, chars=u''.join(chars)
                    ), value, state)
                else:
                    raise Invalid(
                        self.message(
                            'not_valid_singular', state, chars=u''.join(chars)
                        ), value, state)

class UniqueUserId(validators.UnicodeString):
    """Validator for user Id's. Allow everythin in the unicode charecter map,
    plus dot's, plus scores, ie(a_good.user-id)."""

    messages = {
        'not_valid_singular': _('%(chars)s is not allowed on names.'),
        'not_valid_plural': _('%(chars)s are not allowed on names.'),
        'not_unique': _('This User ID is already taken.'),
        'change_uid': _('Please change User ID.')
    }

    def _from_python(self, value, state):
        return validators.UnicodeString._from_python(value.lower())

    def validate_python(self, value, state):
        if value == u'please change me':
            raise Invalid(
                self.message('change_uid', state), value, state)

        from ispmanccp.lib.ispman_helpers import user_exists
        validators.UnicodeString.validate_python(self, value, state)
        if value:
            chars = re.findall(r'[^\w\.-]', value, re.U)
            if chars:
                print len(chars)
                if len(chars) == 1:
                    raise Invalid(
                        self.message(
                            'not_valid_singular', state, chars=u''.join(chars)
                    ), value, state)
                else:
                    raise Invalid(
                        self.message(
                            'not_valid_plural', state, chars=u''.join(chars)
                        ), value, state)
        if user_exists(value):
            raise Invalid(
                self.message(
                    'not_unique', state), value, state)


class ForwardingOnlyValidator(FancyValidator):
    """Validator that makes sure an admin set's up at least one
    forwarding address for a forwarding only account."""

    messages = {
        'not_enough_forwards': _(
            "This is a forwarding only account. Like such, you need to "
            "setup at least one forwarding address."
        )
    }

    def validate_python(self, value, state):
        post_vars = variable_decode(request.POST)
        if 'mailForwardingAddress' not in post_vars and h.asbool(post_vars['ForwardingOnly']):
            raise Invalid(
                self.message('not_enough_forwards', state),
                value,
                state
            )
