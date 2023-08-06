# -*- coding: utf-8 -*-
#
# Copyright © 2009  Ignacio Vazquez-Abrams All rights reserved.
#
# This copyrighted material is made available to anyone wishing to use, modify,
# copy, or redistribute it subject to the terms and conditions of the GNU
# General Public License v.2.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.  You should have
# received a copy of the GNU General Public License along with this program;
# if not, write to the Free Software Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA 02110-1301, USA. Any Red Hat trademarks that are
# incorporated in the source code or documentation are not subject to the GNU
# General Public License and may only be used or replicated with the express
# permission of Red Hat, Inc.
#
'''
.. moduleauthor:: Ignacio Vazquez-Abrams <ivazquez@fedoraproject.org>
'''
from fedora.client import AuthError
from fedora.django import connection, person_by_id

import django.contrib.auth.models as authmodels
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

# Map FAS user elements to model attributes
_fasmap = {
    'id': 'id',
    'username': 'username',
    'email': 'email',
}

def _new_group(group):
    try:
        g = authmodels.Group.objects.get(id=group['id'])
    except authmodels.Group.DoesNotExist:
        g = authmodels.Group(id=group['id'])
    g.name = group['name']
    g.save()
    return g

def _syncdb_handler(sender, **kwargs):
    # Import FAS groups
    verbosity = kwargs.get('verbosity', 1)
    if verbosity > 0:
        print _('Loading FAS groups...')
    try:
        gl = connection.send_request('group/list', 
            auth_params={'username': settings.FAS_USERNAME,
            'password': settings.FAS_PASSWORD})
    except AuthError:
        if verbosity > 0:
            print _('Unable to load FAS groups. Did you set '
                'FAS_USERNAME and FAS_PASSWORD?')
    else:
        groups = gl['groups']
        for group in groups:
            _new_group(group)
        if verbosity > 0:
            print _("FAS groups loaded. Don't forget to unset "
                'FAS_USERNAME and FAS_PASSWORD.')

class FasUserManager(authmodels.UserManager):
    def user_from_fas(self, user):
        """
        Creates a user in the table based on the structure returned
        by FAS
        """
        d = {}
        for k, v in _fasmap.iteritems():
            d[v] = user[k]
        u = FasUser(**d)
        u.set_unusable_password()
        u.is_active = user['status'] == 'active'
        admin = (user['username'] in
            getattr(settings, 'FAS_ADMINS', ()))
        u.is_staff = admin
        u.is_superuser = admin
        if getattr(settings, 'FAS_GENERICEMAIL', True):
            u.email = u._get_email()
        u.save()
        for group in user['approved_memberships']:
            g = _new_group(group)
            u.groups.add(g)
        u.save()
        return u

class FasUser(authmodels.User):
    def _get_name(self):
        userinfo = person_by_id(self.id)
        return userinfo['human_name']

    def _get_email(self):
        return '%s@fedoraproject.org' % self.username

    name = property(_get_name)

    objects = FasUserManager()

    def get_full_name(self):
        return self.name.strip()
