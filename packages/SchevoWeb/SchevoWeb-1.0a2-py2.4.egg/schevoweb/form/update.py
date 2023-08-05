"""Update fieldspaces.

For copyright, license, and warranty, see bottom of file.
"""

import dispatch

from schevo import base
from schevo.constant import UNASSIGNED
from schevo import query


@dispatch.generic()
def update(db, obj, kw, prefix='', **options):
    """Update a Schevo object's fields using keywords.

    - ``db``: The Schevo database being used.

    - ``obj``: The object whose fields will be updated.
    
    - ``kw``: Dictionary of {key: string-value} pairs, usually from
      HTTP POST data.

    - ``prefix``: The prefix that key names start with in ``kw``.

    Returns a dictionary containing {key: (message, exception)} items
    representing errors occurring during the update.
    """


@update.when('isinstance(obj, query.Intersection)')
def update_intersection(db, obj, kw, prefix='', **options):
    errors = {}
    index = 0
    for subquery in obj.queries:
        sub_kw = kw.get(str(index), {})
        errors.update(
            update(db, subquery, sub_kw, prefix, **options))
        index += 1
    return errors


@update.when('isinstance(obj, query.Match)')
def update_match(db, obj, kw, prefix='', **options):
    # Update operator.
    operator_name = kw.get('operator', None)
    if operator_name:
        obj.operator = operator_name
    # Update value.
    value = kw.get('value', '')
    field = obj.FieldClass(obj, 'value')
    field.assign(value)
    obj.value = field.get()
    return {}


@update.when('isinstance(obj, base.classes_using_fields)')
def update_fields(db, obj, kw, prefix='', **options):
    """Additional options:

    - ``update_unassigned``: Update fields to UNASSIGNED of an
      _unassigned_fieldname value is found.

    - ``update_assigned``: Update fields' assigned status based on
      existence of _assigned_fieldname values.
    """
    f = obj.f
    errors = {}
    update_unassigned = options.get('update_unassigned', False)
    update_assigned = options.get('update_assigned', False)
    for name in f:
        field = f[name]
        # Ignore readonly fields.
        if field.readonly:
            continue
        # Check for existence of new field value.
        if prefix:
            kw_name = prefix + name
            unassigned_kw_name = prefix + '_unassigned_' + name
            assigned_kw_name = prefix + '_assigned_' + name
        else:
            kw_name = name
            unassigned_kw_name = '_unassigned_' + name
            assigned_kw_name = '_assigned_' + name
        if kw_name in kw:
            value = kw[kw_name]
        elif field.required:
            # Field is required, but not found.
            value = UNASSIGNED
        else:
            # Field is not required, and not found.
            value = None
        # If UNASSIGNED is checked and we are updating it, that trumps
        # everything else.
        if update_unassigned and kw.get(unassigned_kw_name, False):
            value = UNASSIGNED
        # Set the value if it was given.
        if value is not None:
            try:
                # Set the value on the object.
                value = field.convert(value, db)
                field.verify(value)
                setattr(obj, name, value)
            except (AttributeError, ValueError, TypeError), e:
                errors[name] = (e.args[0], e)
        # Check for assigned flag.
        if update_assigned:
            field.assigned = bool(kw.get(assigned_kw_name, False))
    return errors


# Copyright (C) 2001-2006 Orbtech, L.L.C.
#
# Schevo
# http://schevo.org/
#
# Orbtech
# 709 East Jackson Road
# Saint Louis, MO  63119-4241
# http://orbtech.com/
#
# This toolkit is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This toolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
