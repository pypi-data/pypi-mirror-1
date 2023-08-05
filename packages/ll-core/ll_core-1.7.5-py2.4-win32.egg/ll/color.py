# -*- coding: iso-8859-1 -*-

## Copyright 2004-2007 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004-2007 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


"""
<module>ll.color</module> provides classes and functions for handling RGB colors.
"""


__version__ = "$Revision: 1.2 $"[11:-2]
# $Source: /data/cvsroot/LivingLogic/Python/core/src/ll/color.py,v $


import colorsys

from ll import misc


class Color(object):
	"""
	A <class>Color</class> object represents a color with red, green and
	blue components.
	"""
	__slots__ = ("_channels", )
	
	def __init__(self, r=0.0, g=0.0, b=0.0):
		"""
		Create a <class>Color</class> with the red, green, and blue components
		<arg>r</arg>, <arg>g</arg> and <arg>b</arg>. Values will be clipped to
		the range [<lit>0.0</lit>; <lit>1.0</lit>].
		"""
		self._channels = (max(0., min(float(r), 1.0)), max(0., min(float(g), 1.0)), max(0., min(float(b), 1.0)))

	@classmethod
	def fromrgb(cls, r, g, b):
		"""
		Create a <class>Color</class> object from the RGB values <arg>r</arg>, <arg>g</arg> and <arg>b</arg>.
		See the <pyref property="rgb"><property>rgb</property></pyref> property for more info.
		"""
		c = cls()
		c.rgb = (r, g, b)
		return c

	@classmethod
	def fromrgb4(cls, r4, g4, b4):
		"""
		Create a <class>Color</class> object from the 4 bit RGB values <arg>r4</arg>, <arg>g4</arg> and <arg>b4</arg>.
		See the <pyref property="rgb4"><property>rgb4</property></pyref> property for more info.
		"""
		c = cls()
		c.rgb4 = (r4, g4, b4)
		return c

	@classmethod
	def fromrgb8(cls, r8, g8, b8):
		"""
		Create a <class>Color</class> object from the 8 bit RGB values <arg>r8</arg>, <arg>g8</arg> and <arg>b8</arg>.
		See the <pyref property="rgb8"><property>rgb8</property></pyref> property for more info.
		"""
		c = cls()
		c.rgb8 = (r8, g8, b8)
		return c

	@classmethod
	def fromint4(cls, int4):
		"""
		Create a <class>Color</class> object from the 12 bit RGB integer <arg>int4</arg>.
		See the <pyref property="int4"><property>int4</property></pyref> property for more info.
		"""
		c = cls()
		c.int4 = int4
		return c

	@classmethod
	def fromint8(cls, int8):
		"""
		Create a <class>Color</class> object from the 24 bit RGB integer <arg>int8</arg>.
		See the <pyref property="int8"><property>int8</property></pyref> property for more info.
		"""
		c = cls()
		c.int8 = int8
		return c

	@classmethod
	def fromcss(cls, s):
		"""
		Create a <class>Color</class> object from the &css; color string <arg>s</arg>.
		See the <pyref property="css"><property>css</property></pyref> property for more info.
		"""
		c = cls()
		c.css = s
		return c

	@classmethod
	def fromhsv(cls, h, s, v):
		"""
		Create a <class>Color</class> object from the hue, saturation and value values <arg>h</arg>, <arg>s</arg> and <arg>v</arg>.
		See the <pyref property="hsv"><property>hsv</property></pyref> property for more info.
		"""
		c = cls()
		c.hsv = (h, s, v)
		return c

	@classmethod
	def fromhls(cls, h, l, s):
		"""
		Create a <class>Color</class> object from the hue, luminance and saturation values <arg>h</arg>, <arg>l</arg> and <arg>s</arg>.
		See the <pyref property="hls"><property>hls</property></pyref> property for more info.
		"""
		c = cls()
		c.hls = (h, l, s)
		return c

	def __repr__(self):
		return "Color(%r, %r, %r)" % tuple(self._channels)

	def __str__(self):
		return self.css

	class r(misc.propclass):
		"""
		The red value as a float between <lit>0.0</lit> and <lit>1.0</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return self._channels[0]
		def __set__(self, r):
			self._channels = (max(0., min(float(r), 1.0)), self._channels[1], self._channels[2])

	class g(misc.propclass):
		"""
		The green value as a float between <lit>0.0</lit> and <lit>1.0</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return self._channels[1]
		def __set__(self, g):
			self._channels = (self._channels[0], max(0., min(float(g), 1.0)), self._channels[2])

	class b(misc.propclass):
		"""
		The blue value as a float between <lit>0.0</lit> and <lit>1.0</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return self._channels[2]
		def __set__(self, b):
			self._channels = (self._channels[0], self._channels[1], max(0., min(float(b), 1.0)))

	class r4(misc.propclass):
		"""
		The red value as an int between <lit>0</lit> and <lit>15</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return int(15.*self._channels[0]+0.5)
		def __set__(self, r4):
			self._channels = (max(0., min(r4/15., 1.)), self._channels[1], self._channels[2])

	class g4(misc.propclass):
		"""
		The green value as an int between <lit>0</lit> and <lit>15</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return int(15.*self._channels[1]+0.5)
		def __set__(self, g4):
			self._channels = (self._channels[0], max(0., min(g4/15., 1.)), self._channels[2])

	class b4(misc.propclass):
		"""
		The blue value as an int between <lit>0</lit> and <lit>15</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return int(15.*self._channels[2]+0.5)
		def __set__(self, b4):
			self._channels = (self._channels[0], self._channels[1], max(0., min(b4/15., 1.)))

	class r8(misc.propclass):
		"""
		The red value as an int between <lit>0</lit> and <lit>255</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return int(255.*self._channels[0]+0.5)
		def __set__(self, r8):
			self._channels = (max(0., min(r8/255., 1.)), self._channels[1], self._channels[2])

	class g8(misc.propclass):
		"""
		The green value as an int between <lit>0</lit> and <lit>255</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return int(255.*self._channels[1]+0.5)
		def __set__(self, g8):
			self._channels = (self._channels[0], max(0., min(g8/255., 1.)), self._channels[2])

	class b8(misc.propclass):
		"""
		The blue value as an int between <lit>0</lit> and <lit>255</lit>. The value will be clipped on setting.
		"""
		def __get__(self):
			return int(255.*self._channels[2]+0.5)
		def __set__(self, b8):
			self._channels = (self._channels[0], self._channels[1], max(0., min(b8/255., 1.)))

	class int4(misc.propclass):
		"""
		The RGB value as a 12 bit integer. Red is bit 8&ndash;11, green is bit 4&ndash;7 and blue is bit 0&ndash;3)
		"""
		def __get__(self):
			rgb4 = self.rgb4
			return (rgb4[0]<<8) + (rgb4[1]<<4) + rgb4[2]
		def __set__(self, rgb4):
			self.rgb4 = (rgb4>>8 & 0xf, rgb4>>4 & 0xf, rgb4&0xf)

	class int8(misc.propclass):
		"""
		The RGB value as a 24 bit integer. Red is bit 16&ndash;23, green is bit 8&ndash;15 and blue is bit 0&ndash;7)
		"""
		def __get__(self):
			rgb8 = self.rgb8
			return (rgb8[0]<<16) + (rgb8[1]<<8) + rgb8[2]
		def __set__(self, rgb8):
			self.rgb8 = (rgb8>>16 & 0xff, rgb8>>8 & 0xff, rgb8&0xff)

	def __getitem__(self, index):
		"""
		Return the red, green or blue value (depending on whether <arg>index</arg> is <lit>0</lit>, <lit>1</lit> or <lit>2</lit>)
		as a float value between <lit>0.0</lit> and <lit>1.0</lit>.
		"""
		return self._channels[index]

	def __setitem__(self, index, value):
		"""
		Set the red, green or blue value (depending on whether <arg>index</arg> is <lit>0</lit>, <lit>1</lit> or <lit>2</lit>).
		The value should be between <lit>0.0</lit> and <lit>1.0</lit>. Values outside this range will be clipped.
		"""
		channels = list(self._channels)
		channels[index] = max(0., min(float(x), 1.))
		self._channels = tuple(channels)

	def __len__(self):
		"""
		Always returns <lit>3</lit>.
		"""
		return 3

	class rgb(misc.propclass):
		"""
		The red, green and blue value as a float tuple with values between <lit>0.0</lit> and <lit>1.0</lit>. Values will be clipped on setting.
		"""
		def __get__(self):
			return self._channels
		def __set__(self, rgb):
			self._channels = tuple([max(0., min(float(x), 1.)) for x in rgb])

	class rgb4(misc.propclass):
		"""
		The red, green and blue value as an int tuple with values between <lit>0</lit> and <lit>15</lit>. Values will be clipped on setting.
		"""
		def __get__(self):
			return tuple([int(15.*x+0.5) for x in self._channels])
		def __set__(self, rgb4):
			self._channels = tuple([max(0., min(x/15., 1.)) for x in rgb4])

	class rgb8(misc.propclass):
		"""
		The red, green and blue value as an int tuple with values between <lit>0</lit> and <lit>255</lit>. Values will be clipped on setting.
		"""
		def __get__(self):
			return tuple([int(255.*x+0.5) for x in self._channels])
		def __set__(self, rgb8):
			self._channels = tuple([max(0., min(x/255., 1.)) for x in rgb8])

	class css(misc.propclass):
		"""
		<self/> formatted as a &css; color string. On setting all formats from &css;2 are supported
		(i.e. <lit>'#<rep>xxx</rep>'</lit>, <lit>'#<rep>xxxxxx</rep>'</lit>, <lit>rgb(<rep>n</rep>,
		<rep>n</rep>, <rep>n</rep>)</lit>, <lit>rgb(<rep>n</rep>%, <rep>n</rep>%, <rep>n</rep>%)</lit>
		and color names like <lit>'red'</lit>).
		"""
		def __get__(self):
			s = "#%06x" % self.int8
			if s[1]==s[2] and s[3]==s[4] and s[5]==s[6]:
				s = "#%s%s%s" % (s[1], s[3], s[5])
			return s
		def __set__(self, s):
			if s.startswith("#"):
				i = int(s[1:], 16)
				if len(s) == 4:
					self.int4 = i
					return
				elif len(s) == 7:
					self.int8 = i
					return
			elif s.startswith("rgb(") and s.endswith(")"):
				channels = []
				for x in s[4:-1].split(","):
					x = x.strip()
					if x.endswith("%"):
						v = float(x[:-1])/100.
					else:
						v = float(x)/255.
					channels.append(v)
				self.rgb = channels
				return
			elif s in csscolors:
				self.rgb = csscolors[s].rgb
				return
			raise ValueError("can't interpret %s as css value" % s)

	class hsv(misc.propclass):
		"""
		<self/> as a HSV (<z>hue, saturation, value</z>) triple. All three values are between
		<lit>0.0</lit> and <lit>1.0</lit>. On setting hue will be used modulo <lit>1.0</lit>,
		saturation and value will be clipped to the range [<lit>0.0</lit>; <lit>1.0</lit>].
		"""
		def __get__(self):
			return colorsys.rgb_to_hsv(*self.rgb)
		def __set__(self, (h, s, v)):
			self.rgb = colorsys.hsv_to_rgb(h % 1.0, max(0., min(s, 1.)), max(0., min(v, 1.)))

	class hls(misc.propclass):
		"""
		<self/> as a HLS (<z>hue, luminance, saturation</z>) triple. All three values are between
		<lit>0.0</lit> and <lit>1.0</lit>. On setting hue will be used modulo <lit>1.0</lit>,
		luminance and saturation will be clipped to the range [<lit>0.0</lit>; <lit>1.0</lit>].
		"""
		def __get__(self):
			return colorsys.rgb_to_hls(*self.rgb)
		def __set__(self, (h, l, s)):
			self.rgb = colorsys.hls_to_rgb(h % 1.0, max(0., min(l, 1.)), max(0., min(s, 1.)))

	class lum(misc.propclass):
		"""
		The luminance value from the <pyref property="hls"><property>hls</property></pyref>
		property.
		"""
		def __get__(self):
			return colorsys.rgb_to_hls(*self.rgb)[1]
		def __set__(self, lum):
			(h, l, s) = self.hls
			self.rgb = colorsys.hls_to_rgb(h, max(0., min(lum, 1.)), s)

	def abslum(self, f):
		"""
		Return a copy of <self/> with <arg>f</arg> added to the luminocity.
		"""
		(h, l, s) = self.hls
		return self.fromhls(h, l+f, s)

	def rellum(self, f):
		"""
		Return a copy of <self/> where the luminocity has been modified: If <arg>f</arg>
		if positive the luminocity will be increased, with <lit><arg>f</arg>==1</lit>
		giving a luminocity of 1. If <arg>f</arg> is negative, the luminocity
		will be decreased with <lit><arg>f</arg>==-1</lit> giving a luminocity
		of 0. <lit><arg>f</arg>==0</lit> will leave the luminocity unchanged.
		"""
		(h, l, s) = self.hls
		if f > 0:
			l += (1-l)*f
		elif f < 0:
			l += l*f
		return self.fromhls(h, l, s)


###
### Color constants (don't modify!)
###

maroon = Color.fromrgb8(0x80, 0x00, 0x00)
red = Color.fromrgb8(0xff, 0x00, 0x00)
orange = Color.fromrgb8(0xff, 0xA5, 0x00)
yellow = Color.fromrgb8(0xff, 0xff, 0x00)
olive = Color.fromrgb8(0x80, 0x80, 0x00)
purple = Color.fromrgb8(0x80, 0x00, 0x80)
fuchsia = Color.fromrgb8(0xff, 0x00, 0xff)
white = Color.fromrgb8(0xff, 0xff, 0xff)
lime = Color.fromrgb8(0x00, 0xff, 0x00)
green = Color.fromrgb8(0x00, 0x80, 0x00)
navy = Color.fromrgb8(0x00, 0x00, 0x80)
blue = Color.fromrgb8(0x00, 0x00, 0xff)
aqua = Color.fromrgb8(0x00, 0xff, 0xff)
teal = Color.fromrgb8(0x00, 0x80, 0x80)
black = Color.fromrgb8(0x00, 0x00, 0x00)
silver = Color.fromrgb8(0xc0, 0xc0, 0xc0)
gray = Color.fromrgb8(0x80, 0x80, 0x80)


csscolors = {
	"maroon": maroon,
	"red": red,
	"orange": orange,
	"yellow": yellow,
	"olive": olive,
	"purple": purple,
	"fuchsia": fuchsia,
	"white": white,
	"lime": lime,
	"green": green,
	"navy": navy,
	"blue": blue,
	"aqua": aqua,
	"teal": teal,
	"black": black,
	"silver": silver,
	"gray": gray,
}


def multiply(c1, c2):
	"""
	Multiplies the colors <arg>c1</arg> and <arg>c2</arg>.
	"""
	c1 = c1.rgb
	c2 = c2.rgb
	return Color(c1[0]*c2[0], c1[1]*c2[1], c1[2]*c2[2])


def screen(c1, c2):
	"""
	Does a negative multiplication of the colors <arg>c1</arg> and <arg>c2</arg>.
	"""
	c1 = c1.rgb
	c2 = c2.rgb
	return Color(1.-(1.-c1[0])*(1.-c2[0]), 1.-(1.-c1[1])*(1.-c2[1]), 1.-(1.-c1[2])*(1.-c2[2]))


def mix(*args):
	"""
	Calculates a weighted mix of the colors from <arg>args</arg>. Items in <arg>args</arg>
	or either <pyref class="Color">colors</pyref> (in which case the weight will be <lit>1.</lit>)
	or (color, weight) tuples.
	"""
	channels = [0., 0., 0.]
	sum = 0.
	for arg in args:
		if isinstance(arg, Color):
			(c, w) = (arg, 1.)
		else:
			(c, w) = arg
		for j in xrange(3):
			channels[j] += w*c[j]
		sum += w
	if not sum:
		raise ValueError("at least one of the weights must be >0")
	for j in xrange(3):
		channels[j] /= sum
	return Color.fromrgb(*channels)
