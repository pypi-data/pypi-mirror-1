# ------------------------------------------------------------------------------
# Copyright (c) 2009 Tristam MacDonald
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of DarkCoda nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

import pyglet

from shape import Rectangle
from container import Container

class VerticalLayout(Container):
	"""Vertically arranging and resizing layout"""
	def __init__(self, **kwargs):
		'''Create a vertical layout
		
		Keyword arguments:
		name -- unique widget identifier
		hpadding -- horizontal space before child items
		vpadding -- vertical space between child items
		autosizex -- shoudl the container adopt the horizontal size of its children?
		'''
		self.hpadding = kwargs.get('hpadding', 5)
		self.vpadding = kwargs.get('vpadding', 5)
		self.autosizex = kwargs.get('autosizex', False)
		
		Container.__init__(self, **kwargs)
	
	def update_layout(self):
		Container.update_layout(self)
		
		totalw = 0
		totalh = self.vpadding
		
		for c in self.children[::-1]:
			c.x, c.y = self.hpadding, totalh
			if c.w > totalw:
				totalw = c.w
			totalh += c.h + self.vpadding
		
		if self.autosizex:
			self._w = self.hpadding*2 + totalw
		self._h = totalh
