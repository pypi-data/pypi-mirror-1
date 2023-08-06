# -*- coding: utf-8 -*-

import pymodels


class User(pymodels.Model):
    login = pymodels.Property(required=True)
    password = pymodels.Property(required=True)
    class Meta:
        must_have = {'login__exists': True, 'password__exists': True}
    def __unicode__(self):
        return self.login
