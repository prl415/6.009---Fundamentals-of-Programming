# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 01:01:56 2021

@author: Mustafa
"""

"""6.009 Fall 2019 Lab 9 -- 6.009 Zoo"""

from math import acos
# NO OTHER IMPORTS ALLOWED!

class Constants:
    """
    A collection of game-specific constants.

    You can experiment with tweaking these constants, but
    remember to revert the changes when running the test suite!
    """
    # width and height of keepers
    KEEPER_WIDTH = 30
    KEEPER_HEIGHT = 30

    # width and height of animals
    ANIMAL_WIDTH = 30
    ANIMAL_HEIGHT = 30

    # width and height of food
    FOOD_WIDTH = 10
    FOOD_HEIGHT = 10

    # width and height of rocks
    ROCK_WIDTH = 50
    ROCK_HEIGHT = 50

    # thickness of the path
    PATH_THICKNESS = 30

    TEXTURES = {
        'rock': '1f5ff',
        'animal': '1f418',
        'SpeedyZookeeper': '1f472',
        'ThriftyZookeeper': '1f46e',
        'CheeryZookeeper': '1f477',
        'food': '1f34e'
    }

    FORMATION_INFO = {'SpeedyZookeeper':
                       {'price': 9,
                        'interval': 55,
                        'throw_speed_mag': 20},
                      'ThriftyZookeeper':
                       {'price': 7,
                        'interval': 45,
                        'throw_speed_mag': 7},
                      'CheeryZookeeper':
                       {'price': 10,
                        'interval': 35,
                        'throw_speed_mag': 2}}

class NotEnoughMoneyError(Exception):
    """A custom exception to be used when insufficient funds are available
    to hire new zookeepers. You may leave this class as is."""
    pass


################################################################################
################################################################################

class Game:
    def __init__(self, game_info):
        """Initializes the game.

        `game_info` is a dictionary formatted in the following manner:
          { 'width': The width of the game grid, in an integer (i.e. number of pixels).
            'height': The height of the game grid, in an integer (i.e. number of pixels).
            'rocks': The set of tuple rock coordinates.
            'path_corners': An ordered list of coordinate tuples. The first
                            coordinate is the starting point of the path, the
                            last point is the end point (both of which lie on
                            the edges of the gameboard), and the other points
                            are corner ("turning") points on the path.
            'money': The money balance with which the player begins.
            'spawn_interval': The interval (in timesteps) for spawning animals
                              to the game.
            'animal_speed': The magnitude of the speed at which the animals move
                            along the path, in units of grid distance traversed
                            per timestep.
            'num_allowed_unfed': The number of animals allowed to finish the
                                 path unfed before the player loses.
          }
        """
        self.width = game_info['width']
        self.height = game_info['height']
        self.rocks = game_info['rocks']
        self.path_corners = game_info['path_corners']
        self.money = game_info['money']
        self.spawn_interval = game_info['spawn_interval']
        self.animal_speed = game_info['animal_speed']
        self.num_allowed_unfed = game_info['num_allowed_unfed']
        self.game_state = 'ongoing'
        self.clock = 0
        self.new_keeper = None
        self.animal_formations = []
        self.food_formations = []
        self.keeper_formations = []
        self.rock_formations = [Rock(loc) for loc in game_info['rocks']]

    def render(self):
        """Renders the game in a form that can be parsed by the UI.

        Returns a dictionary of the following form:
          { 'formations': A list of dictionaries in any order, each one
                          representing a formation. The list should contain 
                          the formations of all animals, zookeepers, rocks, 
                          and food. Each dictionary has the key/value pairs:
                             'loc': (x, y), 
                             'texture': texture, 
                             'size': (width, height)
                          where `(x, y)` is the center coordinate of the 
                          formation, `texture` is its texture, and `width` 
                          and `height` are its dimensions. Zookeeper
                          formations have an additional key, 'aim_dir',
                          which is None if the keeper has not been aimed, or a 
                          tuple `(aim_x, aim_y)` representing a unit vector 
                          pointing in the aimed direction.
            'money': The amount of money the player has available.
            'status': The current state of the game which can be 'ongoing' or 'defeat'.
            'num_allowed_remaining': The number of animals which are still
                                     allowed to exit the board before the game
                                     status is `'defeat'`.
          }
        """
        
        render_info = {'formations': [animal.get_object_info() for animal in self.animal_formations] +
                                     [food.get_object_info() for food in self.food_formations] + 
                                     [keeper.get_object_info() for keeper in self.keeper_formations] + 
                                     [rock.get_object_info() for rock in self.rock_formations],
                       'money': self.money,
                       'status': self.game_state,
                       'num_allowed_remaining': self.num_allowed_unfed}
        
        return render_info

    def timestep(self, mouse=None):
        """Simulates the evolution of the game by one timestep.

        In this order:
            (0. Do not take any action if the player is already defeated.)
            1. Compute any changes in formation locations, then remove any
                off-board formations.
            2. Handle any food-animal collisions, and remove the fed animals
                and eaten food.
            3. Throw new food if possible.
            4. Spawn a new animal from the path's start if needed.
            5. Handle mouse input, which is the integer coordinate of a player's
               click, the string label of a particular zookeeper type, or `None`.
            6. Redeem one unit money per animal fed this timestep.
            7. Check for the losing condition to update the game status if needed.
        """
        if self.game_state == 'ongoing':
            self.update_formations(mouse)
            self.check_collisions()
            self.throw_food()
            self.spawn_animal()
            self.redeem_money()
            self.check_game_state()
            self.clock += 1
            
    def update_formations(self, mouse):
        '''
        Helper function for 'timestep'. Updates the formations based on 
        the current timestep
        '''
        self.move_animals()
        self.move_food()
        self.remove_off_boards()
        self.add_keeper(mouse)
        
    #### Creation of new formations ####
    
    def spawn_animal(self): 
        '''
        Helper function for 'timestep'. Creates new Animal object at loc: path[0]
        '''
        if self.clock % self.spawn_interval == 0:
            self.animal_formations.append(Animal(self.path_corners[0], self.animal_speed, self.path_corners, 0))
    
    def add_keeper(self, mouse):
        '''
        Helper function for the 'update_formations'. 
        mouse: One of the following:
               - A string which indicates type of the keeper that will be added
               - A tuple of two integers which is location of the keeper 
                 will be added
               - None
        If mouse is keeper type, this info will be save. If mouse is loc, 
        keeper type previously determined will be added. Otherwise nothing
        will happened
        
        '''
        if mouse is not None:
            print()
            print('Mouse click: ', mouse)
            print('Keepers are: ', self.keeper_formations)
            print('Keeper selected as: ', self.new_keeper)
            
        if mouse is None:
            return
        
        if mouse in Constants.FORMATION_INFO:
            self.new_keeper = mouse
            return
        
        if self.new_keeper is not None:
            
            keeper_type = self.new_keeper
            loc = mouse
            price = Constants.FORMATION_INFO[keeper_type]['price']
            
            if self.check_balance(price) and self.check_loc(loc):
                self.keeper_formations.append(Keeper(loc, keeper_type, self.clock))
                self.money -= price
                self.new_keeper = None
                return
        
        if self.new_keeper is None:
            if self.keeper_formations[-1].aim_dir is None:
                aim_dir = mouse
                keeper_loc = self.keeper_formations[-1].loc
                if aim_dir != keeper_loc:
                    x, y = (keeper_loc[0] - aim_dir[0], keeper_loc[1] - aim_dir[1])
                    mag = (x**2 + y**2)**0.5
#                    print('Keeper\'s Location is: ', keeper_loc)
#                    print('Point of click:', aim_dir)
#                    print('Vector from the center of the keeper to the point of click: ', x, y)
#                    print('Unit vector of it: ', (-x/mag, -y/mag))
#                    print()
                    self.keeper_formations[-1].aim_dir = (-x/mag, -y/mag)
                    self.keeper_formations[-1].create_sight(self.path_corners)
#                    print('Sight of the keeper is: ', self.keeper_formations[-1].sight)
                            
        
                
    #### Creation of new formations ####
    
    #### Movement of the formations ####
    
    def move_animals(self):
        '''
        Helper function for 'update_formations'. Changes current positions of 
        the Animal objects
        '''
        offboards = []
        for animal in self.animal_formations:
            is_offboard = animal.update_loc()
            if is_offboard:
                offboards.append(animal)
                
        for offboard in offboards:
            self.animal_formations.remove(offboard)
            self.num_allowed_unfed -= 1
    
    def move_food(self):
        '''
        Helper function for 'update_formations'. Changes current positions of 
        the Food objects
        '''
        offboards = []
        for food in self.food_formations:
            x, y = food.loc
            speed = food.speed
            move_dir_x, move_dir_y  = food.direction
            food.loc = x + speed * move_dir_x, y + speed * move_dir_y
            
    
    def remove_off_boards(self):
        '''
        Helper function for 'update_formations'. Removes the objects which are
        moved to outside of the game board
        '''
        pass
    
    #### Movement of the formations ####
            
    #### Checking various properties ####
    
    def check_collisions(self):
        '''
        Helper function for 'timestep'. Removes the Animal-Food object pairs
        that overlap with each other
        '''
        food_to_animal = dict()
        animal_to_food = dict()
        removed_food_set = set()
        removed_animal_set = set()
        
        for i in range(len(self.food_formations)):
            
            food = self.food_formations[i]
            f_x, f_y = food.loc
            f_w, f_h = food.width, food.height
            
            for j in range(len(self.animal_formations)):
                
                animal = self.animal_formations[j]
                a_x, a_y = animal.loc
                a_w, a_h = animal.width, animal.height
                
                if abs(a_x - f_x) < (f_w/2 + a_w/2) and abs(a_y - f_y) < (f_h/2 + a_h/2):
                    
                    food_to_animal.setdefault(i, set()).add(j)
                    animal_to_food.setdefault(j, set()).add(i)
                    removed_food_set.add(self.food_formations[i])
                    removed_animal_set.add(self.animal_formations[j])
                        
        num_collisions = self.get_num_collisions(food_to_animal, animal_to_food)
        
        for food in removed_food_set:
            self.food_formations.remove(food)
        
        for animal in removed_animal_set:
            self.animal_formations.remove(animal)
        
        self.money += num_collisions
        
        
    def get_num_collisions(self, food_to_animal, animal_to_food):
        # TODO: Solve this case
        '''
        I could't handle the case when multiple food collide with single animal
        '''
        animal_to_multiple_food = {}
        for animal in animal_to_food:
            count = 0
            for food in food_to_animal:
                if animal in food_to_animal[food]:
                    count += 1
            if count > 1:
                animal_to_multiple_food[animal] = count
                
        num_of_collisions = sum([len(food_to_animal[food]) for food in food_to_animal])
        
        num_of_collisions -= sum([(len(animal_to_food[animal]) - 1) for animal in animal_to_multiple_food])
        
        return num_of_collisions
            
    
    def check_balance(self, price):
        '''
        Helper function for 'add_keeper'. Checks whether the current balance
        is enough to add given keeper. If it is enough returns True, otherwise
        function will raise NotEnoughMoneyError
        '''
        if self.money < price:
            self.new_keeper = None
            raise NotEnoughMoneyError
        
        return True
    
    
    def get_dir(self, segment):
        delta_x = segment[1][0] - segment[0][0]
        delta_y = segment[1][1] - segment[0][1]
        f = lambda delta: 0 if delta == 0 else round(delta/abs(delta))
        return f(delta_x), f(delta_y)
    
    def check_loc(self, loc):
        '''
        Helper function for 'add_keeper'. Checks whether given loc doesn't 
        overlap with locations of the rocks, keepers on the board or the path.
        Returns True if there is no overlap with objects on the board, 
        otherwise False
        '''
        r_w, r_h = Constants.ROCK_WIDTH,Constants.ROCK_HEIGHT
        k_w, k_h = Constants.KEEPER_WIDTH, Constants.KEEPER_HEIGHT
        
        #Check for rocks
        for rock in self.rock_formations:
            r_x, r_y = rock.loc
            if abs(loc[0] - r_x) < (r_w/2 + k_w/2) and abs(loc[1] - r_y) < (r_h/2 + k_h/2):
                return False
            
        #Check for other keepers
        for keeper in self.keeper_formations:
            k_x, k_y = keeper.loc
            if abs(loc[0] - k_x) < k_w and abs(loc[1] - k_y) < k_h:
                return False
            
        #Check for the path collisions
        path_size = Constants.PATH_THICKNESS
        for i in range(len(self.path_corners) - 1):
            segment = self.path_corners[i:i+2]
            del_x, del_y = self.get_dir(segment)
            path_loc = (1 - del_x)*segment[0][0] + (1 - del_y)*segment[0][1]
            keeper_loc = (1 - del_x)*loc[0] + (1 - del_y)*loc[1]
            
            if del_x != 0:
                for x in range(segment[0][0], segment[1][0], del_x):
                    distance = (abs(loc[0] - x)**2 + abs(keeper_loc - path_loc)**2)**0.5
                    if distance < path_size/2 + k_w/2:
                        print('Direction of the path:', del_x, del_y)
                        print(f'Loc of the path is {path_loc} and Loc of the keeper is {keeper_loc}')
                        print(f'Segment is between {i} and {i+1}')
                        print('Due to path')
                        return False
            
            if del_y != 0:
                for y in range(segment[0][1], segment[1][1], del_y):
                    distance = (abs(loc[1] - y)**2 + abs(keeper_loc - path_loc)**2)**0.5
                    if distance < path_size/2 + k_w/2:
                        print('Direction of the path:', del_x, del_y)
                        print(f'Loc of the path is {path_loc} and Loc of the keeper is {keeper_loc}')
                        print(f'Segment is between {i} and {i+1}')
                        print('Due to path')
                        return False
                        
#            if abs(keeper_loc - path_loc) < (path_size/2):
#                print('Direction of the path:', del_x, del_y)
#                print(f'Loc of the path is {path_loc} and Loc of the keeper is {keeper_loc}')
#                print(f'Segment is between {i} and {i+1}')
#                print('Due to path')
#                return False
            
        return True
    
    def check_game_state(self):
        if self.num_allowed_unfed < 0:
            self.game_state = 'defeat'
    
    def redeem_money(self):
        pass
    
    def throw_food(self):
        for keeper in self.keeper_formations:
            #Keeper can throw food at most once in his/her time interval
#            print(f'Interval of the current keeper is {keeper.interval} at timestep {self.clock}')
#            print('Foods are: ', self.food_formations)
            if (keeper.placed_time + self.clock) % keeper.interval == 0 and keeper.aim_dir is not None:
#            if self.clock % keeper.interval == 0 and keeper.aim_dir is not None:
                if self.any_animal_in_sight(keeper.aim_dir, keeper.sight):
                    self.food_formations.append(Food(keeper.loc, keeper.throw_speed_mag, keeper.aim_dir))
                
    def any_animal_in_sight(self, aim_dir, line_of_sight):
        path_size = Constants.PATH_THICKNESS
        for animal in self.animal_formations:
            for sight in line_of_sight:
#                if abs(sight[0] - animal.loc[0]) < animal.width/2 and abs(sight[1] - animal.loc[1]) < animal.height/2:
                tip_1 = (sight[0] + path_size*aim_dir[0]/2, sight[1] + path_size*aim_dir[1]/2)
                tip_2 = (sight[0] - path_size*aim_dir[0]/2, sight[1] - path_size*aim_dir[1]/2)
                if self.check_tips([tip_1, tip_2], animal.loc):
                    print('A animal detectedddddd')
                    print('Animal loc: ', animal.loc)
                    print('Sight is: ', sight)
#                    print('Tip 1: ', tip_1)
#                    print('Tip_2: ', tip_2)
#                    print()
                    return True
        return False
                
    def check_tips(self, tips, loc):
        animal_width, animal_height = Constants.ANIMAL_WIDTH, Constants.ANIMAL_HEIGHT
        for tip in tips:
            if abs(tip[0] - loc[0]) < animal_width/2 and abs(tip[1] - loc[1]) < animal_height/2:
                return True
        return False
    
                
            
    #### Checking various properties ####


################################################################################
################################################################################
# TODO: Add a Formation class and at least two additional classes here.
#class Formation

class Formations:
    def __init__(self, loc, formation_type):
        self.texture = Constants.TEXTURES[formation_type]
        self.loc = loc
        self.type = formation_type
    
    def update_loc(self, loc):
        self.loc = loc
        
    def get_object_info(self):
        '''
        Returns a dictionary which contains various info about the given
        Formation object
        {'loc': Current location of the object as tuple of integers (x, y),
         'tecture': Texture of the object,
         'size': Size of the object as tuple of integers (width, height)}
        '''
        if self.type not in Constants.FORMATION_INFO:
            info_dict = {'loc': self.loc,
                         'texture': self.texture,
                         'size': (self.width, self.height)}
            
        else:
            info_dict = {'loc': self.loc,
                         'texture': self.texture,
                         'size': (self.width, self.height),
                         'aim_dir': self.aim_dir}
            
        return info_dict
   
    def get_dir(self, segment):
        delta_x = segment[1][0] - segment[0][0]
        delta_y = segment[1][1] - segment[0][1]
#        print('Current segment: ', self.segment)
        f = lambda delta: 0 if delta == 0 else round(delta/abs(delta))
        return f(delta_x), f(delta_y)
    
                
class Keeper(Formations):
    def __init__(self, loc, keeper_type, placed_time, aim_dir = None):
        '''
        Initializes the keeper with given loc and keeper_type
        '''
        Formations.__init__(self, loc, keeper_type)
        self.width = Constants.KEEPER_WIDTH
        self.height = Constants.KEEPER_HEIGHT
        self.price = Constants.FORMATION_INFO[keeper_type]['price']
        self.interval = Constants.FORMATION_INFO[keeper_type]['interval']
        self.throw_speed_mag = Constants.FORMATION_INFO[keeper_type]['throw_speed_mag']
        self.aim_dir = aim_dir
        self.placed_time = placed_time
        self.sight = []
    
    def get_unit_vector(self, loc1, loc2):
        x1, y1 = loc1[0], loc1[1]
        x2, y2 = loc2[0], loc2[0]
        distance_between_points = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        unit_vector = ((x2 - x1)/distance_between_points, (y2 - y1)/distance_between_points)
        return unit_vector
    
    
        
    def create_sight(self, path):
        loc = self.loc
        for i in range(len(path) - 1):
            segment = path[i:i+2]
            del_x, del_y = self.get_dir(segment)
            path_loc = ((1 - del_x)*segment[0][0], (1 - del_y)*segment[0][1])
            keeper_loc = ((1 - del_x)*loc[0], (1 - del_y)*loc[1])
            vector_a = (path_loc[0] - keeper_loc[0], path_loc[1] - keeper_loc[1])
            print(f'Direction is', del_x, del_y)
            print(f'Keeper loc is {keeper_loc} and Path loc is {path_loc}')
            magnitude_a = (vector_a[0]**2 + vector_a[1]**2)**0.5
            unit_vector_a = (vector_a[0]/magnitude_a, vector_a[1]/magnitude_a)
            unit_vector_b = self.aim_dir
            ratio = unit_vector_a[0]*unit_vector_b[0] + unit_vector_a[1]*unit_vector_b[1]
            angle_between_vectors = acos(ratio)
            rad_to_deg = angle_between_vectors*180/3.14
            print('Degree between them: ', rad_to_deg)
            print()
            if rad_to_deg > 0 and rad_to_deg < 90:
                sight_length = magnitude_a/ratio
                distance = (sight_length**2 - magnitude_a**2)**0.5
                sight_loc_1 = (del_x*distance + path_loc[0], del_y*distance + path_loc[1])
#                sight_loc_2 = (path_loc[0] - del_x*distance , path_loc[1] - del_y*distance)
                self.sight.append(sight_loc_1)
#                self.sight.append(sight_loc_2)
                
class Animal(Formations):
    def __init__(self, loc, speed, path, index):
        Formations.__init__(self, loc, 'animal')
        self.width = Constants.ANIMAL_WIDTH
        self.height = Constants.ANIMAL_HEIGHT
        self.speed = speed
        self.index = index
        self.path = path
        self.segment = (self.path[index], self.path[index + 1])
        self.hor, self.ver = self.get_dir(self.segment)
    
    def is_there_corner(self, remaining = None):
        if remaining is None:
            remaining = self.speed
        return remaining > (abs(self.loc[0] - self.segment[1][0]) + abs(self.loc[1]- self.segment[1][1]))
    
    def make_turn(self, remaining):
        self.index += 1
        try:
            delta_x = abs(self.segment[1][0] - self.loc[0])
            delta_y = abs(self.segment[1][1] - self.loc[1])  
            remaining = remaining - (delta_x + delta_y)
            self.loc = self.segment[1]
            self.segment = (self.path[self.index], self.path[self.index + 1])
            self.hor, self.ver = self.get_dir(self.segment)
            if self.is_there_corner(remaining):
                self.make_turn(remaining)
            else:
                self.loc = (self.loc[0] + remaining*self.hor, self.loc[1] + remaining*self.ver)
        except:
            return True
    
    def update_loc(self):
        if not self.is_there_corner():
            self.loc = (self.loc[0] + self.speed*self.hor, self.loc[1] + self.speed*self.ver)
        else:
            is_offboard = self.make_turn(self.speed)
            if is_offboard:
                return True
            
            
            
class Food(Formations):
    def __init__(self, loc, speed, direction):
        Formations.__init__(self, loc, 'food')
        self.width = Constants.FOOD_WIDTH
        self.height = Constants.FOOD_HEIGHT
        self.speed = speed
        self.direction = direction
            
class Rock(Formations):
    def __init__(self, loc):
        Formations.__init__(self, loc, 'rock')
        self.width = Constants.ROCK_WIDTH
        self.height = Constants.ROCK_HEIGHT

################################################################################
################################################################################



if __name__ == '__main__':
   pass
