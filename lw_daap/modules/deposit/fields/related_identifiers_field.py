# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.

# This file is part of Zenodo.
# Copyright (C) 2012, 2013 CERN.
##
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
##
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from wtforms import TextAreaField
from lw_daap.modules.invenio_deposit.field_base import WebDepositField
from wtforms.compat import text_type
from wtforms.validators import ValidationError
import re


__all__ = ['RelatedIdentifiersField']

_RE_DOI = re.compile("(^$|(doi:)?10\.\d+(.\d+)*/.*)", flags=re.I)


def doi_list_validator(form, field):
    errors = []
    if isinstance(field.data, list):
        for doi in field.data:
            if not _RE_DOI.match(doi):
                errors.append(doi)
        if len(errors) > 2:
            s = "%s and %s" % (", ".join(errors[:-1]), errors[-1])
            raise ValidationError(
                ("The provided DOIs %s are invalid - they should look"
                 " similar to '10.1234/foo.bar'.") % s)
        elif len(errors) > 1:
            s = "%s and %s" % (errors[0], errors[1])
            raise ValidationError(
                ("The provided DOIs %s are invalid - they should look"
                 " similar to '10.1234/foo.bar'.") % s)
        elif len(errors) > 0:
            raise ValidationError(
                ("The provided DOI is invalid - it should look similar"
                 " to '10.1234/foo.bar'."))


class RelatedIdentifiersField(WebDepositField, TextAreaField):

    def __init__(self, **kwargs):
        self._icon_html = '<i class="icon-barcode"></i>'
        kwargs['validators'] = [doi_list_validator]
        super(RelatedIdentifiersField, self).__init__(**kwargs)

    # def _value(self):
    #     if not self.data:
    #         return ""
    #     if isinstance(self.data, list):
    #         return text_type("\n".join(self.data))
    #     else:
    #         return text_type(self.data)
