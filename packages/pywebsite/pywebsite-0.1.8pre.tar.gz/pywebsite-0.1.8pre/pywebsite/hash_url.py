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

For hashing arguments to a url, to make sure they are ok.

This is useful as a cheap url signing.  Not to be used for anything important
 but it should stop people from faking basic url stuff.

As an example, say you wanted to store shopping cart information, and you 
 wanted to deter casual tampering.  Then you could generate the url, then 
 create a hash of it.  Then people can only use the urls you generated.
"""

import hashlib

def hash_url(values, salt, keys = None, length_used = None):
    """ hash_url(values, salt, keys = None) -> hash
        Returns a hash for the keys/values and salt given.

        Useful for making sure the url is a valid one.

        values - a list of the value parts of '&key=value'
        keys - a list of the key parts of '&key=value'
        salt - a secret string to salt the hash.

        The keys/values do not include the hash value.  That is, do not 
        include the value returned by this function in the hash in key/values.
    """

    if keys is None:
        parts = [str(v) for v in values]
    else:
        parts = [str(k) + str(v) for k,v in zip(keys, values)]

    # Add salt to taste.  Making you thirsty?
    parts.append(salt)

    the_hash = hashlib.md5(''.join(parts)).hexdigest()

    if length_used is not None:
        the_hash = the_hash[:length_used]

    return the_hash

def url_ok(values, salt, hash, keys = None, length_used = None):
    """ url_ok(values, salt, hash, keys = None, length_used = None) -> Bool
        Returns True if the url keys/values match the given hash.

        values - a list of the value parts of '&key=value'
        salt - a secret string to salt the hash.
        hash - the hash to check with.
        keys - a list of the key parts of '&key=value'
        length_used - if None use the full length of the hash.  If an 
                      integer, then use that length of the hash.
    """
    the_hash = hash_url(values, salt, keys)
    if length_used is not None:
        the_hash = the_hash[:length_used]

    if hash == the_hash:
        return True
    else:
        return False





