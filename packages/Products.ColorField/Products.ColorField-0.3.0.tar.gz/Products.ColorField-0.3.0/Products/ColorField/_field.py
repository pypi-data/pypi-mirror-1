##############################################################################
#
# ColorField
# Copyright (C) 2007 buerosterngasse*
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.Registry import registerField, registerWidget
from Products.ColorField.config import *
from Products.Archetypes.Registry import registerPropertyType

class ColorWidget(atapi.StringWidget):
    _properties = atapi.StringWidget._properties.copy()
    _properties.update(
        {'macro' : 'colorpicker',
         'helper_js': ('colorpicker.js',),
         'allow_brightness':True,
        })

class ColorField(atapi.StringField):
    _properties = atapi.StringField._properties.copy()
    _properties.update({
        'widget': ColorWidget,
        'output_format':OUTPUT_FORMAT,
        'show_prefix':True,
        })

    security = ClassSecurityInfo()
    def convertColor(self,colorstring):
        """ Convert color to a given color format """

        if self.output_format == 'HexColor':
           return self.HTMLColorToHexColor(colorstring)
        elif self.output_format == 'RGB':
           return self.HTMLColorToRGB(colorstring)
        elif self.output_format == 'PilColor':
           return self.HTMLColorToPILColor(colorstring)
        elif self.output_format == 'HTMLColor':
             if self.show_prefix != True and colorstring[0] == '#':
                return colorstring[1:]
        return colorstring

    # color converting methods taken from:
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/266466

    def HTMLColorToHexColor(self,colorstring):
        """ convert an (R, G, B) tuple to #RRGGBB """

        colorstring = colorstring.strip()
        if colorstring[:2] == '0x': return colorstring
        #raise str(colorstring[:2])
        if colorstring[0] == '#': colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
        if self.show_prefix != True:
           return colorstring
        hexcolor = '0x%s' % colorstring
        return hexcolor

    def HTMLColorToRGB(self,colorstring):
        """ convert #RRGGBB to an (R, G, B) tuple """
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return (r, g, b)

    def HTMLColorToPILColor(self,colorstring):
        """ converts #RRGGBB to PIL-compatible integers"""
        colorstring = colorstring.strip()
        while colorstring[0] == '#': colorstring = colorstring[1:]
        # get bytes in reverse order to deal with PIL quirk
        colorstring = colorstring[-2:] + colorstring[2:4] + colorstring[:2]
        # finally, make it numeric
        color = int(colorstring, 16)
        return color

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        value = atapi.StringField.get(self, instance, **kwargs)
        if value:
           return self.convertColor(value)

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        value = atapi.StringField.get(self, instance, **kwargs)
        
        return value


    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        atapi.StringField.set(self, instance, value, **kwargs)

registerWidget(ColorWidget,
               title="Color picker",
               description=("ColorWidget"),
               used_for=("Products.Archetypes.public.StringField",)
               )

registerField(ColorField,
    title="Color",
    description=("ColorField")
    )


registerPropertyType('allow_brightness', 'boolean', ColorWidget)
registerPropertyType('output_format', 'string', ColorField)
registerPropertyType('show_prefix', 'boolean', ColorField)
