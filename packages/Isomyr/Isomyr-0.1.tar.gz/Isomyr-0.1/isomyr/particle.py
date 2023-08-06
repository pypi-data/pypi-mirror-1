"""
Special Objects which are have complex behaviour.
"""
from random import randint

from isomyr.objects import GravityObject, PhysicalObject


class Destructor(GravityObject):
    """
    A class for objects which delete themselves when they collide with
    another object.

    die: Flag to say if the object should destroy itself: boolean
    scene: The current scene of the object: scene class
    """
    def __init__(self, pos, size, objtype, scene, fixed=False):
        super(Destructor, self).__init__(pos, size, fixed=fixed)
        self.die = False
        self.scene = scene

    def act(self):
        """Redefined tick function for self destruction on collision."""
        super(Destructor, self).act()
        if self.die is True:
            self.scene.object_group.remove(self)

    def eventCollision(self, otherObject, impactSide):
        """
        Redefined collision event handler for self destruction on collision.
        """
        self.die = True


class Exploder(PhysicalObject):

    def __init__(self, pos, size, objtype, scene, fixed=True):
        super(Exploder, self).__init__(pos, size, fixed=fixed)
        self.new_object_time = 0
        self.scene = scene

    def act(self):
        super(Exploder, self).act()
        if self.new_object_time == 100:
            pos = [randint(20, 130), randint(20, 130), 100]
            self.scene.object_group.append(
                Destructor(pos, [30, 30, 30], 8, self.scene))
            self.new_object_time = 0
        self.new_object_time = self.new_object_time+1


class DelayedDestructor(GravityObject):
    """A class for objects which delete themselves after a set period. 
 
    die: Flag to say if the object should destroy itself: boolean
    scene: The current scene of the object: scene class
    new_object_time: Time in ticks for when this object will disolve (destroy
        itself): integer
    """
    def __init__(self, pos, size, objtype, scene, fixed = False):
        super(DelayedDestructor, self).__init__(pos, size, fixed=fixed)
        self.die = False
        self.new_object_time = 0
        self.scene = scene

    def act(self):
        """
        Redefined tick function for self destruction after a delay in time.
        """
        super(DelayedDestructor, self).act()
        if self.new_object_time == 100:
            pos = [randint(20, 130), randint(20, 130), 100]
            self.scene.object_group.remove(self)
        self.new_object_time = self.new_object_time + 1


class Disolver(PhysicalObject):

    def __init__(self, pos, size, objtype, scene, fixed=True):
        super(Disolver, self).__init__(pos, size, fixed=fixed)
        self.new_object_time = 0
        self.scene = scene

    def act(self):
        super(Disolver, self).act()
        if self.new_object_time == 30:
            pos = [randint(10, 170), randint(10, 170), 100]
            self.scene.object_group.append(
                DelayedDestructor(pos, [20, 30, 30], 8, self.scene))
            self.new_object_time = 0
        self.new_object_time = self.new_object_time + 1
