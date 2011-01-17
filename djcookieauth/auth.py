# -*- coding: utf-8 -*-
# This file is part of dj-cookieauth released under the Apache 2 license. 
# See the NOTICE for more information.

"""
monkey patch django to support sha256 to encode/decode password"""

import hashlib

from django.utils.encoding import smart_str

_auth_patched = None
def patch_auth():
    global _auth_patched
    
    if _auth_patched is not None:
        return
    
    from django.contrib.auth import models
    
    old_get_hexdigest = models.get_hexdigest
    def _get_hexdigest(algorithm, salt, raw_password):
        raw_password, salt = smart_str(raw_password), smart_str(salt)
        if algorithm == 'sha256':
            return hashlib.sha256(salt + raw_password).hexdigest()
        return old_get_hexdigest(algorithm, salt, raw_password)


    def _set_password(self, raw_password):
        if raw_password is None:
            self.set_unusable_password()
        else:
            import random
            algo = 'sha256'
            salt = _get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = _get_hexdigest(algo, salt, raw_password)
            self.password = '%s$%s$%s' % (algo, salt, hsh)
        

    models.get_hexdigest = _get_hexdigest
    models.User.set_password = _set_password
    _auth_patched = True
