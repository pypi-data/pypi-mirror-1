# Copyright (c) 2008
# Authors: KissBooth Contributors (see docs/CREDITS.txt)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

from kss.core import KSSView, force_unicode, kssaction

class KSSDemoView(KSSView):

    @kssaction
    def getDivContentWithParms(self, param1, param2):
        """ returns div content """
        txt = force_unicode(param1 + param2, 'utf')
        self.getCommandSet('core').replaceInnerHTML('div#demo', '<h1>it worked</h1>')
        self.getCommandSet('core').replaceInnerHTML('div#demo', '<h1 id="workedagain">%s</h1>' % (txt, ))
        return self.render()
