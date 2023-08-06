import os

from pygame import (K_DOWN, K_LEFT, K_RETURN,
                    K_RIGHT, K_SPACE, K_UP, K_l, K_x, K_z)

from isomyr.config import Keys
from isomyr.engine import Engine
from isomyr.objects.portal import Portal
from isomyr.skin import Skin, DirectedAnimatedSkin
from isomyr.util import ImageLoader
from isomyr.thing import MovableThing, PhysicalThing, PortableThing
from isomyr.universe import worldFactory


dirname = os.path.dirname(__file__)


# Set the custom keys for the game.
custom_keys = Keys(
    left=K_LEFT,
    right=K_RIGHT,
    up=K_UP,
    down=K_DOWN,
    jump=K_SPACE,
    pick_up=K_z,
    drop=K_x,
    examine=K_l,
    using=K_RETURN)


# An image loader that lets us run the tutorial anywhere the isomyr library
# can be imported (i.e., you don"t have to be in the same directory as the
# tutorial to run it).
image_loader = ImageLoader(dirname, transparency=(255, 255, 255))


def setupWorld():
    """
    Create the world, the scenes that can be visited, the objects in the
    scenes, and the player.
    """
    # Create the world.
    world = worldFactory(name="Game World")

    # Create the first scene.
    bedroom = world.addScene("bedroom")
    bedroom.setSkin(
        Skin(image_loader.load("bedroom.png")))

    # Create the second scene.
    lounge = world.addScene("lounge")
    lounge.setSkin(
        Skin(image_loader.load("lounge.png")))

    # Create the player and set his animated skin.
    ian_curtis = bedroom.addPlayer(
        name="Ian Curtis", location=[90, 90, 100], size=[14, 14, 50],
        velocityModifier=2)
    south_facing = image_loader.load([
        "player/ian_curtis1.png", "player/ian_curtis2.png",
        "player/ian_curtis3.png"])
    east_facing = image_loader.load([
        "player/ian_curtis4.png", "player/ian_curtis5.png",
        "player/ian_curtis6.png"])
    ian_curtis.setSkin(
        DirectedAnimatedSkin(south_facing, east_facing,
                             frameSequence=[0, 2, 2, 1, 1, 2, 2, 0]))

    # Build the non-skinned bedroom scene objects (we'll re-use these for the
    # lounge scene).
    ground = PhysicalThing(
        "ground", [-1000, -1000, -100], [2000, 2000, 100])
    wall0 = PhysicalThing("wall", [180, 0, -20], [20, 180, 120])
    wall1 = PhysicalThing("wall", [0, 180, -20], [180, 20, 120])
    wall2 = PhysicalThing("wall", [0, -20, -20], [180, 20, 120])
    wall3 = PhysicalThing("wall", [-20, 0, -20], [20, 180, 120])

    # Build the skinned bedroom scene objects.
    door = Portal(
        name="door", location=[180, 105, 0], size=[10, 30, 56], toScene=lounge,
        toLocation=[10, 115, 0])
    door.setSkin(Skin(image_loader.load(["door.png"])))

    bed = MovableThing(
        name="bed", location=[0, 100, 0], size=[70, 52, 28], fixed=False)
    bed.setSkin(Skin(image_loader.load(["bed.png"])))

    guitar = PortableThing(
        name="guitar", location=[60, 0, 40], size=[20, 12, 20])
    guitar.setSkin(Skin(image_loader.load(["guitar.png"])))

    # Populate the bedroom (the player has already been added).
    bedroom.addObjects([
        ground, wall0, wall1, wall2, wall3, door,
        bed, guitar, ian_curtis])

    # Build the skinned lounge scene objects.
    door = Portal(
        name="door", location=[0, 105, 0], size=[10, 30, 56], toScene=bedroom,
        toLocation=[160, 115, 00])
    door.setSkin(
        Skin(image_loader.load(["door.png"])))

    sofa = PhysicalThing(
        name="sofa", location=[0, 0, 0], size=[39, 66, 37], fixed=False)
    sofa.setSkin(
        Skin(image_loader.load(["sofa.png"])))

    amp = PortableThing(name="amp", location=[60, 0, 25], size=[16, 10, 18])
    amp.setSkin(
        Skin(image_loader.load(["amp.png"])))

    # Populate the lounge.
    lounge.addObjects([
        ground, wall0, wall1, wall2, wall3, door,
        sofa, amp,
        ])

    return world


def run():
    # Setup the pygame display, the window caption and its icon.
    world = setupWorld()
    # Create an isomyr engine and start it.
    engine = Engine(world=world, offset=[200, 172], keys=custom_keys,
                    titleFile=os.path.join(dirname, "titlebar.png"))
    engine.start()


if __name__ == "__main__":
    run()
