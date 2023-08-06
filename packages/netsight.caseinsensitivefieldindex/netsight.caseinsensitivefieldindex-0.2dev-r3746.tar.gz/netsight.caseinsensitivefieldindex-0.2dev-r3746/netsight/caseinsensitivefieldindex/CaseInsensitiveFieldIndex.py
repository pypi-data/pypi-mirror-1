##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Simple column indices.

$Id: FieldIndex.py 40218 2005-11-18 14:39:19Z andreasjung $
"""

from Globals import DTMLFile
from cgi import escape
from BTrees.IIBTree import IISet, union, intersection
from Products.PluginIndexes.common import safe_callable
from Products.PluginIndexes.common.util import parseIndexRequest
_marker = []

from Products.PluginIndexes.common.UnIndex import UnIndex


class CaseInsensitiveFieldIndex(UnIndex):
    """Index for simple fields.
    """

    __implements__ = UnIndex.__implements__

    meta_type="CaseInsensitiveFieldIndex"

    manage_options= (
        {'label': 'Settings',
         'action': 'manage_main',
         'help': ('FieldIndex','FieldIndex_Settings.stx')},
        {'label': 'Browse',
         'action': 'manage_browse',
         'help': ('FieldIndex','FieldIndex_Settings.stx')},
    )


    # Copied from UnIndex.py with .lower() added to the key
    def _apply_index(self, request, cid='', type=type):
        """Apply the index to query parameters given in the request arg.

        The request argument should be a mapping object.

        If the request does not have a key which matches the "id" of
        the index instance, then None is returned.

        If the request *does* have a key which matches the "id" of
        the index instance, one of a few things can happen:

          - if the value is a blank string, None is returned (in
            order to support requests from web forms where
            you can't tell a blank string from empty).

          - if the value is a nonblank string, turn the value into
            a single-element sequence, and proceed.

          - if the value is a sequence, return a union search.

        If the request contains a parameter with the name of the
        column + '_usage', it is sniffed for information on how to
        handle applying the index.

        If the request contains a parameter with the name of the
        column = '_operator' this overrides the default method
        ('or') to combine search results. Valid values are "or"
        and "and".

        If None is not returned as a result of the abovementioned
        constraints, two objects are returned.  The first object is a
        ResultSet containing the record numbers of the matching
        records.  The second object is a tuple containing the names of
        all data fields used.

        FAQ answer:  to search a Field Index for documents that
        have a blank string as their value, wrap the request value
        up in a tuple ala: request = {'id':('',)}
        """
        record = parseIndexRequest(request, self.id, self.query_options)
        if record.keys==None: return None

        index = self._index
        r     = None
        opr   = None

        # experimental code for specifing the operator
        operator = record.get('operator',self.useOperator)
        if not operator in self.operators :
            raise RuntimeError,"operator not valid: %s" % escape(operator)

        # depending on the operator we use intersection or union
        if operator=="or":  set_func = union
        else:               set_func = intersection

        # Range parameter
        range_parm = record.get('range',None)
        if range_parm:
            opr = "range"
            opr_args = []
            if range_parm.find("min")>-1:
                opr_args.append("min")
            if range_parm.find("max")>-1:
                opr_args.append("max")

        if record.get('usage',None):
            # see if any usage params are sent to field
            opr = record.usage.lower().split(':')
            opr, opr_args=opr[0], opr[1:]

        if opr=="range":   # range search
            if 'min' in opr_args: lo = min(record.keys)
            else: lo = None
            if 'max' in opr_args: hi = max(record.keys)
            else: hi = None
            if hi:
                setlist = index.items(lo,hi)
            else:
                setlist = index.items(lo)

            for k, set in setlist:
                if isinstance(set, int):
                    set = IISet((set,))
                r = set_func(r, set)
        else: # not a range search
            for key in record.keys:
                key = str(key).lower()
                set=index.get(key, None)
                if set is None:
                    set = IISet(())
                elif isinstance(set, int):
                    set = IISet((set,))
                r = set_func(r, set)

        if isinstance(r, int):  r=IISet((r,))
        if r is None:
            return IISet(), (self.id,)
        else:
            return r, (self.id,)

    def _get_object_datum(self,obj, attr):
        # self.id is the name of the index, which is also the name of the
        # attribute we're interested in.  If the attribute is callable,
        # we'll do so.
        try:
            datum = getattr(obj, attr)
            if safe_callable(datum):
                datum = datum()
        except AttributeError:
            datum = _marker
        return str(datum).lower()


    query_options = ["query","range"]

    manage = manage_main = DTMLFile('dtml/manageCaseInsensitiveFieldIndex', globals())
    manage_main._setName('manage_main')


manage_addCaseInsensitiveFieldIndexForm = DTMLFile('dtml/addCaseInsensitiveFieldIndex', globals())

def manage_addCaseInsensitiveFieldIndex(self, id, extra=None,
                REQUEST=None, RESPONSE=None, URL3=None):
    """Add a field index"""
    return self.manage_addIndex(id, 'CaseInsensitiveFieldIndex', extra=extra, \
             REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
