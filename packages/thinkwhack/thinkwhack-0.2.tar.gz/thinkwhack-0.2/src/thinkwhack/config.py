#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# 
# Copyright 2008 by Jürgen Geuter <tante@the-gay-bar.com> 
#
# thinkwhack - triggering actions on your hdaps-enabled  laptop
#
# This file is part of thinkwhack.
#
# thinkwhack is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# only, as published by the Free Software Foundation.
#
# thinkwhack is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU General Public License
# version 3 along with thinkwhack.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>
# for a copy of the GPLv3 License.
########################################################################


from configobj import ConfigObj
from validate import Validator, VdtValueError
import os.path

def get_conf():
    """Read the user's configuration, in case there's none, use the defaults"""
    conf = ConfigObj(os.path.join(os.path.expanduser("~"),".thinkwhack"),configspec="/usr/share/thinkwhack/defaults")
    vdt = Validator()
    conf.validate(vdt)
    return conf


