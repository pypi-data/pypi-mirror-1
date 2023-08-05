# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: helpers.py 123 2007-01-09 21:34:22Z s0undt3ch $
# =============================================================================
#             $URL: http://ccp.ufsoft.org/svn/tags/0.0.1alpha3.1/ispmanccp/lib/helpers.py $
# $LastChangedDate: 2007-01-09 21:34:22 +0000 (Tue, 09 Jan 2007) $
#             $Rev: 123 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons import h
from pylons.i18n import _, set_lang, get_lang
from pylons.helpers import log
from genshi.builder import tag


def wrap_helpers(localdict):
    from genshi import Markup
    def helper_wrapper(func):
        def wrapped_helper(*args, **kw):
            return Markup(func(*args, **kw))
        wrapped_helper.__name__ = func.__name__
        return wrapped_helper
    for name, func in localdict.iteritems():
        if not callable(func) or not func.__module__.startswith('webhelpers.rails'):
            continue
        localdict[name] = helper_wrapper(func)
wrap_helpers(locals())

# Don't know why but this import needs to be done after the wrapper
from datetime import date
from paste.deploy.converters import asbool as paste_asbool
# random_pass imports
import string
import random
# check_path_perms imports
import os
import sys
from pwd import getpwuid
from grp import getgrgid
from stat import ST_MODE


def date_from_tstamp(tstamp):
    return date.fromtimestamp(int(tstamp))


def convert_size(size):
    """ Helper function  to convert ISPMan sizes to readable units. """
    return h.number_to_human_size(int(size)*1024)


def get_nav_class_state(url, request, partial=False):
    """ Helper function that just returns the 'active'/'inactive'
    link class based on the passed url. """
    if partial:
        _url = h.url_for(
            controller=request.environ['pylons.routes_dict']['controller'],
            action=None,
            id=None
        )
    else:
        _url = h.url_for(
            controller=request.environ['pylons.routes_dict']['controller'],
            action=request.environ['pylons.routes_dict']['action'],
            id=None
        )

    if url == request.path_info:
        return 'active'
    elif url.startswith(_url) and partial:
        return 'active'
    elif url == _url:
        return 'active'
    else:
        return 'inactive'

def to_unicode(in_obj):
    """ Function to convert whatever we can to unicode."""
    if not in_obj: # or in_obj == '':
        pass
    elif isinstance(in_obj, unicode) or isinstance(in_obj, int):
        return in_obj
    elif isinstance(in_obj, str):
        return unicode(in_obj, 'UTF-8')
    elif isinstance(in_obj, list):
        return [to_unicode(x) for x in in_obj] # if x not in ('', u'', None)]
    elif isinstance(in_obj, dict):
        def conv_to_list(obj):
            if isinstance(obj, str) or isinstance(obj, unicode):
                return [to_unicode(obj)]
            else:
                return to_unicode(obj)
        out_dict = {}
        for key, val in in_obj.iteritems():
            if key == 'mailAlias':
                out_dict[key] = conv_to_list(val)
            elif key == 'mailForwardingAddress':
                out_dict[key] = conv_to_list(val)
            else:
                out_dict[key] = to_unicode(val)
        return out_dict
    else:
        try:
            return to_unicode(dict(in_obj))
        except: # Failed to convert to dict
            pass
        try:
            return to_unicode(list(in_obj))
        except: # Failed to convert to list
            pass
    return in_obj


def remap_user_dict(form_dict, user_dict):
    uid = user_dict['ispmanUserId']
    lengths = {}
    lengths[uid] = {}

    for key, val in form_dict.iteritems():
        if isinstance(val, list):
            # Make shure we're not passing empty mailAlias and/or
            # mailForwardingAddress's
            new_list = to_unicode(val)
            if len(new_list) > 0:
                user_dict[key] = new_list
        else:
            user_dict[key] = to_unicode(val)
    # calculate lenghts
    try:
        lengths[uid]['forwards'] = len(user_dict['mailForwardingAddress'])
    except:
        pass # there are no forwards
    try:
        lengths[uid]['aliases'] = len(user_dict['mailAlias'])
    except:
        pass # there are no aliases

    return lengths, user_dict


def random_pass(alpha, num):
    """
    Returns a human-readble password (say rol86din instead of
    a difficult to remember K8Yn9muL )
    From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/410076
    """
    vowels = ['a','e','i','o','u']
    consonants = [a for a in string.ascii_lowercase if a not in vowels]
    digits = string.digits

    ####utility functions
    def a_part(slen):
        ret = ''
        for i in range(slen):
            if i%2 ==0:
                randid = random.randint(0,20) #number of consonants
                ret += consonants[randid]
            else:
                randid = random.randint(0,4) #number of vowels
                ret += vowels[randid]
        return ret

    def n_part(slen):
        ret = ''
        for i in range(slen):
            randid = random.randint(0,9) #number of digits
            ret += digits[randid]
        return ret

    ###
    fpl = alpha/2
    if alpha % 2 :
        fpl = int(alpha/2) + 1
    lpl = alpha - fpl

    start = a_part(fpl)
    mid = n_part(num)
    end = a_part(lpl)

    return u"%s%s%s" % (start,mid,end)


def asbool(obj):
    try:
        return bool(int(obj))
    except:
        return paste_asbool(obj)


def check_path_perms(path):
    """Function to check a path's permissions.
    Based on recipe found on:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/436211
    """
    path = os.path.abspath(path)

    if not os.access(path, os.F_OK):
        print "I'm bailing out!"
        print
        print "%r does not exist." % path
        print
        print "Please correct the above problems and run again..."
        sys.exit(1)

    path_perms = os.stat(path)
    running_uid = os.getuid()
    running_gid = os.getgid()
    running_uid_name = getpwuid(running_uid)[0]
    running_gid_name = getgrgid(running_gid)[0]
    R_MSK, W_MSK, X_MSK, Z_MSK =   4,   2,   1,   0
    R_STR, W_STR, X_STR, Z_STR = 'r', 'w', 'x', '-'

    def iff( test_, then_, else_ ): # then_, else_ always get evaled so pls be atoms
        if test_:
            return then_
        else:
            return else_

    def mode2str( mode ):
        r, w, x = mode & R_MSK, mode & W_MSK, mode & X_MSK
        return iff( r, R_STR, Z_STR ) + iff( w, W_STR, Z_STR ) + iff( x, X_STR, Z_STR )

    def fullmode2str( mode ):
        u, g, o = mode >> 6 & 0x7, mode >> 3 & 0x7, mode & 0x7
        return mode2str( u ) + mode2str( g ) + mode2str( o )

    if not os.access(path, os.F_OK) or not os.access(path, os.X_OK):
        print "I'm bailing out!"
        print "I don't have read access to %r." % path
        print "I'm running as '%s(%i):%s(%i)' and directory is\n" \
                "owned by '%s(%i):%s(%i) with perms '%s'." % \
                (
                    running_uid_name,
                    running_uid,
                    running_gid_name,
                    running_gid,
                    getpwuid(path_perms[4])[0],
                    path_perms[4],
                    getgrgid(path_perms[5])[0],
                    path_perms[5],
                    fullmode2str(path_perms[ST_MODE])
                )
        print
        print "Please correct the above problems and run again..."
        sys.exit(1)
