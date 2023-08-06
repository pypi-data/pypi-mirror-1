import pygame

from isomyr.gui.component import (
    TitleView, SceneView, InventoryView)


class View(object):

    def __init__(self, scene, displayOffset, titleFile="", font=None,
                 titleView=None, sceneView=None, inventoryView=None):
        self.scene = scene
        # Offset from the top left corner of the window for the isomyr
        # display.
        self.displayOffset = displayOffset
        self.viewSize = self.getSurface().get_size()
        self.titleFile = titleFile
        self.font = font
        self.views = []
        self.changedRectangles = []
        self.loadFont(font)
        self.initializeViews(titleView=titleView, sceneView=sceneView,
                             inventoryView=inventoryView)
        # Initialize the display.
        self.redrawDisplay()

    def initializeViews(self, titleView, sceneView, inventoryView):
        if not titleView:
            titleView = TitleView(self)
        if not sceneView:
            sceneView = SceneView(self)
        if not inventoryView:
            inventoryView = InventoryView(self)
        for view in [titleView, sceneView, inventoryView]:
            self.views.append(view)

    def getView(self, viewType):
        for viewInstance in self.views:
            if isinstance(viewInstance, viewType):
                return viewInstance

    def updateDisplay(self):
        self.updateTitle()
        self.updateScene()
        self.updateInventory(self.scene.world.player)

    def redrawDisplay(self):
        self.scene.setView(self)
        self.updateTitle()
        self.getView(SceneView).redrawDisplay()
        self.updateInventory(self.scene.world.player)

    def updateTitle(self):
        self.getView(TitleView).updateDisplay()

    def updateScene(self):
        self.getView(SceneView).updateDisplay()

    def updateInventory(self, player):
        self.getView(InventoryView).updateDisplay(player)

    def getSurface(self):
        return self.scene.world.getSurface()

    def loadFont(self, font):
        """
        Load the default font.
        """
        if not font:
            self.font = pygame.font.SysFont(
                "bitstreamverasansmono", 10, bold=False, italic=False)
        else:
            self.font = font

    def setScene(self, scene):
        self.scene = scene
