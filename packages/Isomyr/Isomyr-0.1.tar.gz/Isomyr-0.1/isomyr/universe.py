import math

import pygame
from pygame import display

from isomyr import handler
from isomyr.exceptions import DuplicateObjectError
from isomyr.objects.character import Player
from isomyr.thing import ThingOfThings


class Time(object):

    def __init__(self):
        self.time = 0

    def getTime(self):
        return(self.time)

    def updateTime(self):
        self.time = self.time + 1


class Universe(ThingOfThings):
    """
    The object that keeps track of all worlds. This is the top-level container
    for all games.
    """
    def __init__(self, worlds=None, sceneSize=None, *args, **kwds):
        super(Universe, self).__init__(*args, **kwds)
        self.worlds = worlds or []
        self.sceneSize = sceneSize or [400, 360]
        self.cosmologicalConstant = 10 ** -29 # g/cm3
        self.speedOfLight = 299792458 # m/s
        self.pi = math.pi
        self.gametime = Time()
        # Initialize the pygame display module.
        pygame.init()
        self.surface = display.set_mode(self.sceneSize)
        # Set up the causal relationships between events and event reactions
        # (handlers) for the objects in this world.
        handler.registerEventHandlers()

    def addWorld(self, name="", world=None, sceneSize=None):
        if name and not world:
            world = World(name=name, universe=self, sceneSize=sceneSize)
        world.universe = self
        self.worlds.append(world)
        self.addObject(world)
        return world

    def getWorld(self, name=""):
        # XXX up-call to getObect
        if not name and len(self.worlds) > 0:
            return self.worlds[0]
        super(Universe, self).getObject(name)

    def getPlayer(self):
        return self.getWorld().getPlayer()


class World(ThingOfThings):
    """
    The object that keeps track of all other objects.
    """
    def __init__(self, name="", sceneSize=None, universe=None):
        self.name = name
        self.universe = universe
        self.scenes = {}
        self.player = None

    def getUniverse(self):
        return self.universe

    def addScene(self, name="", sceneObject=None):
        if name and not sceneObject:
            sceneObject = Scene(name=name, world=self)
        sceneObject.world = self
        present = self.scenes.setdefault(name, sceneObject)
        if present != sceneObject:
            msg = ("An object with that name has already been added to the "
                    "scene.")
            raise DuplicateObjectError(msg)
        return sceneObject

    def getScene(self, name):
        return self.scenes.get(name)

    def getPlayer(self):
        return self.player

    def getSurface(self):
        return self.universe.surface

    def getGameTime(self):
        return self.universe.gametime.getTime()


def worldFactory(universe=None, name="", sceneSize=""):
    if not universe:
        universe = Universe()
    return universe.addWorld(name=name, sceneSize=sceneSize)


class Scene(ThingOfThings):
    """
    A collection of objects and a scenetype to hint at a background image.
    """

    def __init__(self, world=None, *args, **kwds):
        super(Scene, self).__init__(*args, **kwds)
        self.world = world
        self.view = None

    # XXX move into common base class with Thing... something like
    # SkinableMixin.
    def setSkin(self, skin):
        self.skin = skin

    def getUpdatableObjects(self):
        updatableObjects = []
        for objectInstance in self.objectList:
            if objectInstance.skin:
                updatableObjects.append(objectInstance)
        return updatableObjects

    def addPlayer(self, player=None, *args, **kwds):
        if not player:
            player = Player(*args, **kwds)
        self.world.player = player
        self.addObject(player)
        return player

    def removePlayer(self, player=None):
        self.removeObject(player)

    def getPlayer(self):
        return self.getObject(self.world.getPlayer().name)

    def setView(self, view):
        self.view = view

    def addObject(self, objectInstance):
        super(Scene, self).addObject(objectInstance)
        objectInstance.world = self.world
