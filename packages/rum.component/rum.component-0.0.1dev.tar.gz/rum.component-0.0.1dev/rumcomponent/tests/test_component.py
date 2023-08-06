from unittest import TestCase
import rumcomponent as component

config = {}
class MockComponent(component.Component):
    config = config

class Weapon(object):
    def __init__(self, damage=1):
        self.damage = damage
    def use(self):
        raise NotImplementedError( "I'm an abstract weapon")

class Axe(Weapon):
    def use(self):
        return self.damage

class Armor(object):
    factor = .8

class Robot(object):
    weapon = MockComponent("test.robot.weapon", "This robot's weapon")

    # tests Component without doc and default
    armor = MockComponent("test.robot.armor", default=lambda:None)

    def __init__(self):
        self.strength = 10

    def hurt(self, damage):
        if self.armor:
            factor = self.armor.factor
        else:
            factor = 1
        self.strength -= (damage * factor)

    def attack(self, other):
        other.hurt(self.weapon.use())
 
class TestComponent(TestCase):
    def setUp(self):
        config.clear()
        self.robot = Robot()
        self.other = Robot()

    def test_no_component_registered(self):
        self.assertRaises(component.NoComponentRegistered,
                          self.robot.attack, self.other)

    def test_no_component_found_as_declared_ep(self):
        config['test.robot.weapon'] = {'use':'i_dont_exist'}
        self.assertRaises(component.NoComponentFound,
                          self.robot.attack, self.other)

    def test_no_component_found_as_ep_path(self):
        config['test.robot.weapon'] = {'use':'i.dont:exist'}
        self.assertRaises(component.NoComponentFound,
                          self.robot.attack, self.other)

    def test_component_as_ep_path(self):
        config['test.robot.weapon'] = {'use':'rumcomponent.tests.test_component:Axe'}
        self.robot.attack(self.other)
        self.failUnlessEqual(self.other.strength, 9)

    def test_component_as_declared_ep(self):
        # 'axe' has been defined in setup.py from rum.component
        # this is an entry point
        config['test.robot.weapon'] = {'use':'axe'}
        self.robot.attack(self.other)
        self.failUnlessEqual(self.other.strength, 9)

    def test_component_as_class(self):
        config['test.robot.weapon'] = {'use':Axe}
        self.robot.attack(self.other)
        self.failUnlessEqual(self.other.strength, 9)

    def test_component_with_args(self):
        config['test.robot.weapon'] = {'use':'rumcomponent.tests.test_component:Axe',
                                  'damage': 2}
        self.robot.attack(self.other)
        self.failUnlessEqual(self.other.strength, 8)

    
    def test_component_from_object_config(self):
        class SuperRobot(Robot):
            config={
                'test.robot.weapon':
                {'use':Axe,
                'damage': 3}
            }
        
        super_robot = SuperRobot()
        super_robot.attack(self.other)
        self.failUnlessEqual(self.other.strength, 7)

    def test_two_components(self):
        config['test.robot.weapon'] = {'use':Axe}
        config['test.robot.armor'] = {'use':Armor}
        self.robot.attack(self.other)
        self.failUnlessAlmostEqual(self.other.strength, 9.2)

    def test_delete_component(self):
        config['test.robot.weapon'] = {'use':Axe}
        self.robot.attack(self.other)
        self.failUnlessEqual(self.other.strength, 9)
        del self.robot.weapon
        # component is reloaded
        self.robot.attack(self.other)
        # it is 8 because other has already been attacked
        self.failUnlessEqual(self.other.strength, 8)
