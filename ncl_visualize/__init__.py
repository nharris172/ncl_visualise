class Canvas:
	def __init__(self,_topleft,_bottomright,_width):
		self.topleft = _topleft
		self.bottomright =_bottomright
		self.width = int(_width)
		self.realworld_width = float(self.bottomright[0] -self.topleft[0])
		self.realworld_height =float(self.topleft[1] - self.bottomright[1])
		self.height =int( self.realworld_height/self.realworld_width*self.width)
		self.size = [self.width,self.height]
	def RW_to_screen(self,coords,):
		x,y = coords
		x=float(x)
		y=float(y)
		return int((x-self.topleft[0])/(self.realworld_width/self.width)),int((self.topleft[1] - y) / (self.realworld_height/self.height))