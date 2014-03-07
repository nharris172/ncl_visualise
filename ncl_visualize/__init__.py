import shapefile
import pygame

class StaticLoader:
    def __init__(self,_canvas):
        self.canvas = _canvas
    def Polygon(self,shp_file,color=(0,0,0)):
        polys = []
        sf = shapefile.Reader(shp_file)
        shapes = sf.shapes()
        for shape in shapes:
            shape_shape = []
            for p in  shape.points:
                shape_shape.append(self.canvas.RW_to_screen(p))
            polys.append(shape_shape)
        self.canvas.static.append({'shp':polys,'color':color,'type':'POLY'})
        

class Canvas:
    def __init__(self,_topleft,_bottomright,_width):
        self.topleft = _topleft
        self.bottomright =_bottomright
        self.width = int(_width)
        self.realworld_width = float(self.bottomright[0] -self.topleft[0])
        self.realworld_height =float(self.topleft[1] - self.bottomright[1])
        self.height =int( self.realworld_height/self.realworld_width*self.width)
        self.size = [self.width,self.height]
        self.LoadStatic = StaticLoader(self)
        self.static = []
        self.bg_color = (0,0,0)
        
    def start_screen(self,):
        pygame.init()
        #create pygame screen
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        
        
    def set_background_color(self,bg_color):
        self.bg_color = bg_color
        
    def RW_to_screen(self,coords,):
        x,y = coords
        x=float(x)
        y=float(y)
        return int((x-self.topleft[0])/(self.realworld_width/self.width)),int((self.topleft[1] - y) / (self.realworld_height/self.height))

    def fill_screen(self,):
        self.screen.fill(self.bg_color)

    def draw_static(self,):
        for stat in self.static:
            if stat['type'] == 'POLY':
                for points in stat['shp']:
                    pygame.draw.polygon(self.screen,stat['color'],points)
                    
    def draw_line(self,line,color,weight):
        pygame.draw.line(self.screen,color,self.RW_to_screen(line[0]),self.RW_to_screen(line[1]),weight)
        
    def draw_point(self,point,color,weight):
        pygame.draw.circle(self.screen,  color, self.RW_to_screen(point), weight)
        
    def annotate(self,text,position):
        if position == 'BOTTOM_LEFT':
            pos = (10, self.height-30)
        myfont = pygame.font.SysFont("arial", 25)
        myfont.set_bold(True)
        #display time in bottom left
        label = myfont.render(str(text), 1, (255,0,0))
        self.screen.blit(label, pos)  
            
    def check_quit(self,):
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                return True # Flag that we are done so we exit this loop
            
    def record(self,filename):
        pygame.image.save(self.screen, filename)
            
    def tick(self,):
        pygame.display.flip()
        self.clock.tick(20)#this try to draw 20 frames a second
            
    def finish(self,):
        pygame.quit ()
            