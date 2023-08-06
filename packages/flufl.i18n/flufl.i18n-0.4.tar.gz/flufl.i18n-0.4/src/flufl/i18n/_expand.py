# Copyright (C) 2009 by the Free Software Foundation, Inc.
#
# This file is part of flufl.i18n
#
# flufl.i18n is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# flufl.i18n is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.i18n.  If not, see <http://www.gnu.org/licenses/>.

"""String interpolation."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'expand',
    ]


import logging
# pylint: disable-msg=W0402
from string import Template

# pylint: disable-msg=C0103
log = logging.getLogger('flufl.i18n')



def expand(template, substitutions, template_class=Template):
    """Expand string template with substitutions.

    :param template: A PEP 292 $-string template.
    :type template: string
    :param substitutions: The substitutions dictionary.
    :type substitutions: dict
    :param template_class: The template class to use.
    :type template_class: class
    :return: The substituted string.
    :rtype: string
    """
    # Python 2.6 requires ** dictionaries to have str, not unicode keys, so
    # convert as necessary.  Note that string.Template uses **.  For our
    # purposes, keys should always be ascii.  Values though can be anything.
    cooked = substitutions.__class__()
    for key in substitutions:
        if isinstance(key, unicode):
            key = key.encode('ascii')
        cooked[key] = substitutions[key]
    try:
        return template_class(template).safe_substitute(cooked)
    except (TypeError, ValueError):
        # The template is really screwed up.
        log.exception('broken template: %s', template)
