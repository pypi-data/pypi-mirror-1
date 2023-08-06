# -*- coding: utf-8 -*-

#######################################################################
# MJoin
# Copyright (C) 2008  Simone Cansella (aka checkm)
#                       <matto.scacco@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################

def color (string):
    colors = {"default":0, "black":30, "red":31, "green":32, "yellow":33,
          "blue":34,"magenta":35, "cyan":36, "white":37, "black":38,
          "black":39} #33[%colors%m
    
    for color in colors:
        color_string = "\033[%dm\033[1m" % colors[color]
        string = string.replace("<%s>" % color, color_string).replace("</%s>" % color, "\033[0m")
    
    return string