##    pywebsite - Python Website Library
##    Copyright (C) 2009 Rene Dudfield
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Rene Dudfield
##    renesd@gmail.com
"""
For signing and verifying urls.

This is useful as a cheap url signing.  Not to be used for anything important
 but it should stop people from faking basic url stuff.

As an example, say you wanted to store shopping cart information, and you 
 wanted to deter casual tampering.  Then you could generate the url, then 
 create a hash of it.  Then people can only use the urls you generated.

Shopping cart data is a good example of something *NOT* to trust this with.
"""

import hashlib, hmac

def sign(values, secret_salt, keys = None, length_used = None):
    """ sign(values, secret_salt, keys = None) -> hash
        Returns a hash for the keys/values and secret_salt given.

        Useful for making sure the url is a valid one.

        values:      list of the value parts of '&key=value'
        keys:        list of the key parts of '&key=value'
        secret_salt: secret string to secret_salt the hash.

        The keys/values do not include the hash value.  That is, do not 
        include the value returned by this function in the hash in key/values.
    """
    if keys is None:
        parts = [str(v) for v in values]
    else:
        parts = ["%s=%s" % (k,v) for k,v in zip(keys, values)]

    # Add secret_salt to taste.  Making you thirsty?
    # NOTE: We add the secret secret_salt to the end to avoid a 
    # length extension attack.
    parts.append(secret_salt)

    # NOTE: we use a separator so that eg ['aa', 'bb'] != ['aab', 'b']
    a_sep = ','
    msg = a_sep.join(parts)

    # NOTE: using hmac with sha1 http://en.wikipedia.org/wiki/HMAC
    try:
        the_hash = hmac.new(secret_salt, msg, hashlib.sha1).hexdigest()
    except TypeError:
        encoded_key = secret_salt.encode()
        encoded_msg = msg.encode()
        the_hash = hmac.new(encoded_key, encoded_msg, hashlib.sha1).hexdigest()

    if length_used is not None:
        the_hash = the_hash[:length_used]

    return the_hash

def verify(values, secret_salt, hash, keys = None, length_used = None):
    """ verify(values, secret_salt, hash, 
               keys = None, length_used = None) -> Bool
        Returns True if the url keys/values match the given hash.

        values:      list of the value parts of '&key=value'
        secret_salt: secret string to secret_salt the hash.
        hash:        the hash to check with.
        keys:        list of the key parts of '&key=value'
        length_used: if None use the full length of the hash.  If an 
                       integer, then use that length of the hash.
    """
    the_hash = sign(values, secret_salt, keys, length_used)

    if hash == the_hash:
        return True
    else:
        return False





