import pygame

class EventHandler:
    def __init__(self, screeninfo, renderer, foldengine):
        self.sw, self.sh = screeninfo
        self.renderer = renderer
        self.foldengine = foldengine
        self.camera = self.renderer.camera
        self.points = self.renderer.points
        self.faces = self.renderer.faces

        self.grab = False
        self.orbit = False
        self.selected = None
        self.orbitsens = 0.01
        
        self.modes = {
            "vertexEdit": False
        }

    def initializeEvents(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                selected = "F1"
                if selected != None:
                    self.grab = True
            if event.button == 2:
                self.orbit = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.grab = False
            if event.button == 2:
                self.orbit = False
        elif event.type == pygame.MOUSEMOTION:
            if self.orbit:
                self.camera.orbit(event.rel[0] * self.orbitsens, -event.rel[1] * self.orbitsens)
            elif self.grab:
                self.selected = "F1"
                self.foldengine.foldGrab("E", "F", self.selected, (pygame.mouse.get_pos(), event.rel, (self.sw, self.sh)), (self.camera.view_transform))
    
        # Scroll zoom
        elif event.type == pygame.MOUSEWHEEL:
            scrollsens = 0.1
            self.camera._zoom(-event.y * scrollsens)

        # Letter keys
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                for mode in self.modes.keys():
                    self.modes[mode] = False
            if event.key == pygame.K_v:
                self.swapMode("vertexEdit")
    
    def swapMode(self, mode):
        enabled = self.modes[mode]
        for mode in self.modes.keys():
            self.modes[mode] = False
        if not enabled:
            self.modes[mode] = True
