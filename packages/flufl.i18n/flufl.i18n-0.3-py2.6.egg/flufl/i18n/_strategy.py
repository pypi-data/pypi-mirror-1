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

"""Module contents."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'PackageStrategy',
    ]


import os
import gettext



# pylint: disable-msg=R0903
class PackageStrategy:
    """A strategy that finds catalogs based on package paths."""

    def __init__(self, name, package):
        """Create a catalog lookup strategy.

        :param name: The application's name.
        :type name: string
        :param package: The package path to the message catalogs.  This
            strategy uses the __file__ of the package path as the directory
            containing `gettext` messages.
        :type package_name: module
        """
        self.name = name
        self._messages_dir = os.path.dirname(package.__file__)

    def __call__(self, language_code):
        """Find the catalog for the language.

        :param language_code: The language code to find.
        :type language_code: string
        :return: A `gettext` catalog.
        :rtype: `gettext.NullTranslations` or subclass
        """
        # gettext.translation() requires None or a sequence.
        try:
            return gettext.translation(
                self.name, self._messages_dir, [language_code])
        except IOError:
            # Fall back to untranslated source language.
            return gettext.NullTranslations()
