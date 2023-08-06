# Smug
# Copyright 2008 Andrew McNabb <amcnabb-smug@mcnabbs.org>
#
# This file is part of Smug.
#
# Smug is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Smug is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models

STATUS_CHOICES = (
        ('s', 'Submitted'),
        ('a', 'Approved'),
        ('r', 'Rejected'),
        ('w', 'Withdrawn'),
        )

class Patch(models.Model):
    status = models.CharField('Status', max_length=1, choices=STATUS_CHOICES,
            default='i')
    timestamp = models.DateTimeField(auto_now=True)
    path = models.CharField('Path', max_length=200)
    diff = models.TextField('Diff')
    changelog = models.CharField('Changelog', max_length=80)
    parent = models.CharField('Parent Commit', max_length=40)

    class Meta:
        verbose_name_plural="Patches"

# vim: et sw=4 sts=4
