"""6.009 Fall 2019 Lab 10 -- 6.009 Zoo"""

from math import ceil
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

    CRAZY_NAP_LENGTH = 125

    CRAZY_ENDURANCE = 6

    TRAINEE_THRESHOLD = 3

    TEXTURES = {
        'rock': '1f5ff',
        'animal': '1f418',
        'SpeedyZookeeper': '1f472',
        'ThriftyZookeeper': '1f46e',
        'CheeryZookeeper': '1f477',
        'food': '1f34e',
        'Demon': '1f479',
        'VHS': '1f4fc',
        'TraineeZookeeper': '1f476',
        'CrazyZookeeper': '1f61c',
        'SleepingZookeeper': '1f634'
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
                        'throw_speed_mag': 2}, 

                      'TraineeZookeeper':
                       {'price': 4,
                        'interval': 65,
                        'throw_speed_mag': 1},
                      'CrazyZookeeper':
                        {'price': 11,
                         'interval': 10,
                         'throw_speed_mag': 13},

                      'Demon': 
                       {'width': 50,
                        'height': 50,
                        'radius': 75,
                        'multiplier': 2,
                        'price': 8},
                      'VHS':
                       {'width': 30,
                        'height': 30,
                        'radius': 75, 
                        'multiplier': 0.5,
                        'price': 5}}

# New spec for timestep(self, mouse):
# 
# (0. Do not take any action if the player is already defeated.)
#  1. Compute the new speed of animals based on the presence of nearby VHS cassettes or demons.
#  2. Compute any changes in formation locations and remove any off-board formations.
#  3. Handle any food-animal collisions, and remove the fed animals and the eaten food.
#  4. Upgrade trainee zookeeper if needed.
#  5. Throw new food if possible.
#  6. Spawn a new animal from the path's start if needed.
#  7. Handle mouse input, which is the integer tuple coordinate of a player's click, the string 
#     label of a particular particular zookeeper type, `'Demon'`, `'VHS'`, or `None`.
#  8. Redeem one dollar per animal fed this timestep.
#  9. Check for the losing condition.

class NotEnoughMoneyError(Exception):
    """A custom exception to be used when insufficient funds are available
    to hire new zookeepers. You may leave this class as is."""
    pass

def get_dir(segment):
    delta_x = segment[1][0] - segment[0][0]
    delta_y = segment[1][1] - segment[0][1]
    f = lambda delta: 0 if delta == 0 else round(delta/abs(delta))
    return f(delta_x), f(delta_y)

def get_unit_vector(loc1, loc2):
    x, y = (loc2[0] - loc1[0], loc2[1] - loc1[1])
    distance = get_distance(loc1, loc2)
    
    return x/distance, y/distance

def get_distance(loc1, loc2):
    x, y = (loc2[0] - loc1[0], loc2[1] - loc1[1])
    distance = (x**2 + y**2)**0.5
    
    return distance
    

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
        self.gameboard_width = game_info['width']
        self.gameboard_height = game_info['height']
        self.rocks = game_info['rocks']
        self.path_corners = game_info['path_corners']
        self.money = game_info['money']
        self.spawn_interval = game_info['spawn_interval']
        self.animal_speed = game_info['animal_speed']
        self.num_allowed_unfed = game_info['num_allowed_unfed']
        self.game_state = 'ongoing'
        self.clock = 0
        self.new_formation = None
        self.keeper_added = False
        self.animal_formations = []
        self.food_formations = []
        self.keeper_formations = []
        self.artifact_formations = []
        self.frightened = []
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
                                     [artifact.get_object_info() for artifact in self.artifact_formations] +
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
            self.compute_speed_of_animals()
            self.update_formations(mouse)
            self.check_food_animal_collisions()
            self.throw_food()
            self.spawn_animal()
            self.check_game_state()
            self.clock += 1
            
    def update_formations(self, mouse):
        '''
        Helper function for 'timestep'. Updates the formations based on 
        the current timestep
        '''
        self.move_animals()
        self.move_food()
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
        
        if mouse is None:
            return
        
        if mouse in Constants.FORMATION_INFO:
            self.new_formation = mouse
            return
        
        if self.new_formation is not None:
            
            formation_type = self.new_formation
            loc = mouse
            price = Constants.FORMATION_INFO[formation_type]['price']
            
            if self.check_balance(price) and self.check_loc(loc, formation_type):
                
                if formation_type in ('Demon', 'VHS'):
                    self.artifact_formations.append(Artifact(loc, formation_type))
                else:
                    self.keeper_formations.append(Keeper(loc, formation_type, self.clock))
                    self.keeper_added = True
                    
                self.money -= price
                self.new_formation = None
                return
        
        if self.new_formation is None and self.keeper_added:
            if self.keeper_formations[-1].aim_dir is None:
                aim_dir = mouse
                keeper_loc = self.keeper_formations[-1].get_loc()
                if aim_dir != keeper_loc:
                    x, y = get_unit_vector(keeper_loc, aim_dir)
                    self.keeper_formations[-1].set_aim_dir(x, y) 
                    self.keeper_formations[-1].create_sight(self.path_corners)
                    self.keeper_added = False
    
    def throw_food(self):
        '''
        Helper function for 'timestep' function. If conditions are satisfied
        new food object will be created
        '''
        for keeper in self.keeper_formations:
            
            if keeper.get_keeper_type() == 'CrazyZookeeper': 
                if keeper.is_crazy_keeper_napping():
                    keeper.update_nap_length()
                    continue
            
            if self.check_throw_interval(keeper):
                if self.any_animal_in_sight(keeper.get_aim_dir(), keeper.get_line_of_sight()):
                    
                    if keeper.get_keeper_type() == 'CrazyZookeeper':
                        keeper.update_crazy_endurance()
                        
                    if keeper.get_keeper_type() == 'TraineeZookeeper':
#                        keeper.update_training_threshold()
                        self.food_formations.append(Food(keeper.get_loc(), keeper.get_throw_speed(), keeper.get_aim_dir(), True, keeper))
                        continue
                    
                    self.food_formations.append(Food(keeper.get_loc(), keeper.get_throw_speed(), keeper.get_aim_dir()))
                            
    #### Creation of new formations ####
    #-----------------------------------------
    
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
            
        self.remove_off_boards(self.animal_formations)
    
    def move_food(self):
        '''
        Helper function for 'update_formations'. Changes current positions of 
        the Food objects
        '''
        
        for food in self.food_formations:
            x, y = food.get_loc()
            speed = food.get_speed()
            move_dir_x, move_dir_y  = food.get_direction()
            food.set_loc(x + speed * move_dir_x, y + speed * move_dir_y)
        
        self.remove_off_boards(self.food_formations)

    def remove_off_boards(self, formations):
        '''
        Helper function for 'update_formations'. Removes the objects which are
        moved to outside of the game board
        '''
        offboards = []        
        game_board_width, game_board_height = self.get_gameboard_sizes()
        
        for formation in formations:
            formation_x, formation_y = formation.get_loc()
            if formation_x <= game_board_width and formation_x >= 0:
               if formation_y <= game_board_height and formation_y >= 0: 
                   pass
            else:
                offboards.append(formation)
        
        for offboard in offboards:
            formations.remove(formation)
            
    def compute_speed_of_animals(self):
        for animal in self.animal_formations:
            animal_loc = animal.get_loc()
            animal_speed = self.animal_speed
            
            for artifact in self.artifact_formations:
                
                artifact_loc = artifact.get_loc()
                artifact_range = artifact.get_range()
                artifact_multiplier = artifact.get_multiplier()
                
                if get_distance(animal_loc, artifact_loc) <= artifact_range:
                    animal_speed *= artifact_multiplier
                    
            animal.set_speed(ceil(animal_speed))
    
    #### Movement of the formations ####
    #------------------------------------------
            
    #### Checking various properties ####
    
    def check_food_animal_collisions(self):
        '''
        Helper function for 'timestep'. Removes the Animal-Food object pairs
        that overlap with each other
        '''
        food_to_animal = dict()
        animal_to_food = dict()
        foods_thrown_by_trainee = dict()
        removed_food_set = set()
        removed_animal_set = set()
        
        for i in range(len(self.food_formations)):
            
            food = self.food_formations[i]
            f_x, f_y = food.get_loc()
            f_w, f_h = food.width, food.height
            
            for j in range(len(self.animal_formations)):
                
                animal = self.animal_formations[j]
                a_x, a_y = animal.get_loc()
                a_w, a_h = animal.width, animal.height
                
                if abs(a_x - f_x) < (f_w/2 + a_w/2) and abs(a_y - f_y) < (f_h/2 + a_h/2):
                    
                    if food.is_thrown_by_trainee():
#                        foods_thrown_by_trainee(i) = j
                        thrower = food.get_thrower()
                        thrower.update_training_threshold()
                        food.thrown_by_trainee = False
                        
                        
                    
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
        '''
        Calculates the number of collisions
        Arguments: 
            -food_to_animal: A dictionary maps the food to the collided animals
            -animal_to_food: A dictionary maps the animal to the collided foods
            
        Returns:
            -An integer that represents number of collisions
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
            self.new_formation = None
            raise NotEnoughMoneyError
        
        return True
    
    def check_loc(self, loc, new_formation):
        '''
        Helper function for 'add_keeper'. Checks whether given loc doesn't 
        overlap with locations of the rocks, keepers on the board or the path.
        Returns True if there is no overlap with objects on the board, 
        otherwise False
        '''
        
        return self.check_formation_collisions(loc, new_formation) and self.check_path_collisions(loc, new_formation)
                
    
    def check_formation_collisions(self, loc, new_formation):
        
        if new_formation in ('Demon', 'VHS'):
            new_formation_width = Constants.FORMATION_INFO[new_formation]['width']
            new_formation_height = Constants.FORMATION_INFO[new_formation]['height']
            
        else:
            new_formation_width = Constants.KEEPER_WIDTH
            new_formation_height = Constants.KEEPER_HEIGHT
            
        #Check for other formations
        for formation_type in (self.artifact_formations, self.keeper_formations, self.rock_formations):
            for formation in formation_type:
                
                formation_x, formation_y = formation.get_loc()
                formation_width, formation_height = formation.get_sizes()
                allowable_x_distance = new_formation_width/2 + formation_width/2
                allowable_y_distance = new_formation_height/2 + formation_height/2
                
                if abs(loc[0] - formation_x) < allowable_x_distance and abs(loc[1] - formation_y) < allowable_y_distance:
                    return False
                
        return True
    
    def check_path_collisions(self, loc, new_formation):
        path_size = Constants.PATH_THICKNESS
        
        if new_formation in ('Demon', 'VHS'):
            new_formation_width = Constants.FORMATION_INFO[new_formation]['width']
            new_formation_height = Constants.FORMATION_INFO[new_formation]['height']
        else:
            new_formation_width = Constants.KEEPER_WIDTH
            new_formation_height = Constants.KEEPER_HEIGHT
            
        for i in range(len(self.path_corners) - 1):
            segment = self.path_corners[i:i+2]
            del_x, del_y = get_dir(segment)
            
            #Path along x-direction
            if del_x != 0:
                
                path_loc = (1 - del_y)*segment[0][1]
                formation_loc = (1 - del_y)*loc[1]
                
                for x in range(segment[0][0], segment[1][0], del_x):
                    
                    distance = (abs(loc[0] - x)**2 + abs(formation_loc - path_loc)**2)**0.5
                    if distance < path_size/2 + new_formation_width/2:
                        return False
            
            #Path along y-direction
            if del_y != 0:
                
                path_loc = (1 - del_x)*segment[0][0]
                formation_loc = (1 - del_x)*loc[0]
                
                for y in range(segment[0][1], segment[1][1], del_y):
                    
                    distance = (abs(loc[1] - y)**2 + abs(formation_loc - path_loc)**2)**0.5
                    
                    if distance < path_size/2 + new_formation_height/2:
                        return False
                    
        return True
                
    
    def check_game_state(self):
        if self.num_allowed_unfed < 0:
            self.game_state = 'defeat'
    
    def any_animal_in_sight(self, aim_dir, line_of_sight):
        '''
        Helper function for throw_food. Checks whether there is an animal in 
        line of sight of the keeper
        '''
        path_size = Constants.PATH_THICKNESS
        
        for animal in self.animal_formations:
            min_distance_x = animal.width/2 + abs(aim_dir[0])*path_size/2
            min_distance_y = animal.width/2 + abs(aim_dir[1])*path_size/2
            animal_loc = animal.get_loc()
            
            if abs(line_of_sight[0] - animal_loc[0]) <  min_distance_x and abs(line_of_sight[1] - animal_loc[1]) < min_distance_y:
                return True
            
        return False
    
    def check_throw_interval(self, keeper):
        #Check the placed time first
        fixed_time = self.clock - keeper.get_placed_time() - 1
        
        if fixed_time != 0 and fixed_time % keeper.get_throw_interval() == 0:
            if keeper.get_aim_dir() is not None:
                return True
        
        return False
    
    def get_gameboard_sizes(self):
        return (self.gameboard_width, self.gameboard_height)

################################################################################
################################################################################
#class Formation

class Formations:
    def __init__(self, loc, formation_type, width, height):
        self.texture = Constants.TEXTURES[formation_type]
        self.loc = loc
        self.type = formation_type
        self.width = width
        self.height = height
        
    def get_object_info(self):
        '''
        Returns a dictionary which contains various info about the given
        Formation object
        {'loc': Current location of the object as tuple of integers (x, y),
         'tecture': Texture of the object,
         'size': Size of the object as tuple of integers (width, height)}
        '''
        if self.type not in set(Constants.FORMATION_INFO) - set(('Demon', 'VHS')):
            info_dict = {'loc': self.loc,
                         'texture': self.texture,
                         'size': (self.width, self.height)}
            
        else:
            info_dict = {'loc': self.loc,
                         'texture': self.texture,
                         'size': (self.width, self.height),
                         'aim_dir': self.aim_dir}
            
        return info_dict
    
    def get_loc(self):
        return self.loc
    
    def set_loc(self, x, y):
        self.loc = (x, y)
        
    def get_sizes(self):
        return self.width, self.height
    
class Keeper(Formations):
    def __init__(self, loc, keeper_type, placed_time, aim_dir = None):
        '''
        Initializes the keeper with given loc and keeper_type
        '''
        Formations.__init__(self, loc, keeper_type, Constants.KEEPER_WIDTH, Constants.KEEPER_HEIGHT)
        self.price = Constants.FORMATION_INFO[keeper_type]['price']
        self.interval = Constants.FORMATION_INFO[keeper_type]['interval']
        self.throw_speed_mag = Constants.FORMATION_INFO[keeper_type]['throw_speed_mag']
        self.aim_dir = aim_dir
        self.placed_time = placed_time
        self.sight = None
        
        if keeper_type == 'TraineeZookeeper':
            self.training_threshold = Constants.TRAINEE_THRESHOLD
            
        if keeper_type == 'CrazyZookeeper':
            self.is_crazy_napping = False
            self.crazy_endurance = Constants.CRAZY_ENDURANCE
            self.nap_length = Constants.CRAZY_NAP_LENGTH
            
    def get_crazy_endurance(self):
        return self.crazy_endurance
    
    def get_training_threshold(self):
        return self.training_threshold
    
    def get_keeper_type(self):
        return self.type
    
    def update_training_threshold(self):
        self.training_threshold -= 1
        
        if self.training_threshold == 0:
            self.type = 'SpeedyZookeeper'
            self.texture = Constants.TEXTURES[self.type]
            self.interval = Constants.FORMATION_INFO[self.type]['interval']
            self.throw_speed_mag = Constants.FORMATION_INFO[self.type]['throw_speed_mag']
            
    
    def update_crazy_endurance(self):
        self.crazy_endurance -= 1
        
        if self.crazy_endurance == 0:
            self.is_crazy_napping = True
            self.texture = Constants.TEXTURES['SleepingZookeeper']
        
    def update_nap_length(self):
        self.nap_length -= 1
        
        if self.nap_length == 0:
            self.is_crazy_napping = False
            self.crazy_endurance = Constants.CRAZY_ENDURANCE
            self.nap_length = Constants.CRAZY_NAP_LENGTH
            self.texture = Constants.TEXTURES['CrazyZookeeper']
        
    def is_crazy_keeper_napping(self):
        return self.is_crazy_napping
    
    def get_angle_between_locs(self, unit_vector1, unit_vector2):
        
        ratio = unit_vector1[0]*unit_vector2[0] + unit_vector1[1]*unit_vector2[1]
        angle_between_vectors = acos(ratio)
        
        return angle_between_vectors
        
        
    def create_sight(self, path):
        '''
        By using aim direction of the keeper, creates line of sight for the keeper
        '''
        loc = self.get_loc()
        aim_dir = self.aim_dir
        min_angle = float('inf')
        
        for i in range(len(path) - 1):
            segment = path[i:i+2]
            del_x, del_y = get_dir(segment)
            
            #Path along x-direction
            if del_x != 0:
                
                y = segment[0][1]
                
                for x in range(segment[0][0], segment[1][0], del_x):
                    
                    unit_vector = get_unit_vector(loc, (x, y))
                    angle_between_vectors = self.get_angle_between_locs(unit_vector, aim_dir)
                    
                    if abs(angle_between_vectors) < min_angle:
                        min_angle = abs(angle_between_vectors)
                        self.sight = (x, y)
            
            #Path along y-direction
            if del_y != 0:
                
                x = segment[0][0]
                
                for y in range(segment[0][1], segment[1][1], del_y):
                    
                    unit_vector = get_unit_vector(loc, (x, y))
                    angle_between_vectors = self.get_angle_between_locs(unit_vector, aim_dir)
                    
                    if abs(angle_between_vectors) < min_angle:
                        min_angle = abs(angle_between_vectors)
                        self.sight = (x, y)
                        
    def get_aim_dir(self):
        return self.aim_dir
    
    def get_placed_time(self):
        return self.placed_time
    
    def get_throw_interval(self):
        return self.interval
    
    def get_throw_speed(self):
        return self.throw_speed_mag
    
    def get_line_of_sight(self):
        return self.sight
    
    def set_aim_dir(self, x, y):
        self.aim_dir = (x, y)
                
class Animal(Formations):
    def __init__(self, loc, speed, path, index):
        Formations.__init__(self, loc, 'animal', Constants.ANIMAL_WIDTH, Constants.ANIMAL_HEIGHT)
        self.speed = speed
        self.index = index
        self.path = path
        self.segment = (self.path[index], self.path[index + 1])
        self.hor, self.ver = get_dir(self.segment)
    
    def is_there_corner(self, remaining_speed = None):
        '''
        Checks whether the animal with given remaining_speed can turn the corner
        '''
        if remaining_speed is None:
            remaining_speed = self.speed
        return remaining_speed > (abs(self.loc[0] - self.segment[1][0]) + abs(self.loc[1]- self.segment[1][1]))
    
    def make_turn(self, remaining):
        '''
        Helper function for update_loc. This is actually a recursive function.
        Updates the location of the animal by considering turning locations.
        
        If it is detected that animal is out of the board, returns True
        '''
        self.index += 1
        
        try:
            delta_x = abs(self.segment[1][0] - self.loc[0])
            delta_y = abs(self.segment[1][1] - self.loc[1])
            
            remaining = remaining - (delta_x + delta_y)
            
            self.loc = self.segment[1]
            self.segment = (self.path[self.index], self.path[self.index + 1])
            self.hor, self.ver = get_dir(self.segment)
            if self.is_there_corner(remaining):
                self.make_turn(remaining)
            else:
                self.loc = (self.loc[0] + remaining*self.hor, self.loc[1] + remaining*self.ver)
        except:
            return True
    
    def update_loc(self):
        '''
        Updates the location of the animal
        '''
        if not self.is_there_corner():
            self.loc = (self.loc[0] + self.speed*self.hor, self.loc[1] + self.speed*self.ver)
            
        else:
            is_offboard = self.make_turn(self.speed)
            
            if is_offboard:
                return True
            
    def get_speed(self):
        return self.speed
    
    def set_speed(self, new_speed):
        self.speed = new_speed
        
class Food(Formations):
    def __init__(self, loc, speed, direction, thrown_by_trainee = False, thrower_of_the_food = None):
        Formations.__init__(self, loc, 'food', Constants.FOOD_WIDTH, Constants.FOOD_HEIGHT)
        self.speed = speed
        self.direction = direction
        self.thrown_by_trainee = thrown_by_trainee
        self.thrower_of_the_food = thrower_of_the_food
        
    def get_speed(self):
        return self.speed
    
    def get_direction(self):
        return self.direction
    
    def is_thrown_by_trainee(self):
        return self.thrown_by_trainee
    
    def get_thrower(self):
        return self.thrower_of_the_food
    
class Rock(Formations):
    def __init__(self, loc):
        Formations.__init__(self, loc, 'rock', Constants.ROCK_WIDTH, Constants.ROCK_HEIGHT)

class Artifact(Formations):
    def __init__(self, loc, artifact_type):
        Formations.__init__(self, loc, artifact_type, Constants.FORMATION_INFO[artifact_type]['width'], Constants.FORMATION_INFO[artifact_type]['height'])
        self.price = Constants.FORMATION_INFO[artifact_type]['price']
        self.radius = Constants.FORMATION_INFO[artifact_type]['radius']
        self.multiplier = Constants.FORMATION_INFO[artifact_type]['multiplier']
        
    def get_range(self):
        return self.radius
    
    def get_multiplier(self):
        return self.multiplier

################################################################################
################################################################################

### lab9 code here ###

if __name__ == '__main__':
    pass