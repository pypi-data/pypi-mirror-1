"""
------------------------------------------------------------------------------
Name:         ICategorizable.py
Purpose:      An interface contract for objects that interact with
              CategoryManager, this may be depricated
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2005 by Deximer, Inc.
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
"""

from Interface import Interface

class ICategorizable(Interface):
    ''' Object can interact with CategoryManager
    '''
    def listVocab():
        ''' Generate vabulary for taxonomy field provided in schema
	'''

