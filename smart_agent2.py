import random
import math
import time

import numpy as np
import pandas as pd

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

_NO_OP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_BUILD_SUPPLY_DEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id

_SELECT_CONTROL_GROUP = actions.FUNCTIONS.select_control_group.id

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index
_PLAYER_ID = features.SCREEN_FEATURES.player_id.index

_PLAYER_SELF = 1

_TERRAN_COMMANDCENTER = 18
_TERRAN_SCV = 45 
_TERRAN_SUPPLY_DEPOT = 19
_TERRAN_BARRACKS = 21

_NOT_QUEUED = [0]
_QUEUED = [1]

ACTION_DO_NOTHING = 'donothing'
ACTION_SELECT_SCV = 'selectscv'
ACTION_BUILD_SUPPLY_DEPOT = 'buildsupplydepot'
ACTION_BUILD_BARRACKS = 'buildbarracks'
ACTION_SELECT_BARRACKS = 'selectbarracks'
ACTION_BUILD_MARINE = 'buildmarine'
ACTION_SELECT_ARMY = 'selectarmy'
ACTION_ATTACK = 'attack'

smart_actions = [
    ACTION_DO_NOTHING,
    ACTION_SELECT_SCV,
    ACTION_BUILD_SUPPLY_DEPOT,
    ACTION_BUILD_BARRACKS,
    ACTION_SELECT_BARRACKS,
    ACTION_BUILD_MARINE,
    ACTION_SELECT_ARMY,
    ACTION_ATTACK,
]

KILL_UNIT_REWARD = 0.3
BUILD_UNIT_REWARD = 0.02
KILL_BUILDING_REWARD = 0.6
KILLED_SELF_UNIT_punishment = -0.02

# Stolen from https://github.com/MorvanZhou/Reinforcement-learning-with-tensorflow
class QLearningTable:
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)

    def choose_action(self, observation):
        self.check_state_exist(observation)
        
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.ix[observation, :]
            
            # some actions have the same value
            state_action = state_action.reindex(np.random.permutation(state_action.index))
            
            action = state_action.idxmax()
        else:
            # choose random action
            action = np.random.choice(self.actions)
            
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        self.check_state_exist(s)
        
        q_predict = self.q_table.ix[s, a]
        q_target = r + self.gamma * self.q_table.ix[s_, :].max()
        
        # update
        self.q_table.ix[s, a] += self.lr * (q_target - q_predict)

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(pd.Series([0] * len(self.actions), index=self.q_table.columns, name=state))

class SmartAgent(base_agent.BaseAgent):
    def __init__(self):
        super(SmartAgent, self).__init__()
        
        self.qlearn = QLearningTable(actions=list(range(len(smart_actions))))
        
        self.previous_killed_unit_score = 0
        self.previous_killed_building_score = 0

        #time.sleep(0.2)
        self.previous_action = None
        self.previous_state = None
        self.supply_depot_count = 0
        self.barracks_count = 0
        self.army_supply = 0
        self.barracks = []
        self.supplies = []

        self.control_groups = np.zeros(10).astype(bool)
        self.create_control = False
        print(self.control_groups)


        ####
        # Macros
        ####
        self.macro = None
        self.m_step = 0


    def initialize(self):
        print("TODO: Implementar esto")
        pass

    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]
        
        return [x + x_distance, y + y_distance]

    def performMacro(self,obs):
        return self.macro(obs)

        pass

    def endMacro(self):
        print("Macro Ended")
        self.m_step = 0
        self.macro = None


    def macro1(self,obs):

        if self.m_step == 0:
            self.m_step += 1
            if not(self.control_groups[5]):
                unit_type = obs.observation['screen'][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
                if unit_y.any():
                    i = random.randint(0, len(unit_y) - 1)
                    target = [unit_x[i], unit_y[i]]
                    action = actions.FunctionCall(_SELECT_POINT, [ _NOT_QUEUED, target])
                    self.control_groups[5] = True
                    self.create_control = True
                    print("Step 0 Done Correctly")
                    return action
                else:
                    print("Something failed on macro1 / step 0")
                    return actions.FunctionCall(_NO_OP, [])
        elif self.m_step == 1:
            if self.create_control:
                target = [5]
                action = actions.FunctionCall(_SELECT_CONTROL_GROUP, [[1], target])
                self.create_control = False
                print("Step 1 Done Correctly")
                self.endMacro()
                return action
            else:
                print("Something failed on macro1 / step 0")
                return actions.FunctionCall(_NO_OP, [])
        else:
            print("Wrong Step for this Macro")
            return actions.FunctionCall(_NO_OP, [])

    def macro2(self, obs):
        if self.m_step == 0:
            self.m_step += 1
            if self.control_groups[5]:
                unit_type = obs.observation['screen'][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
                if unit_y.any():
                    i = random.randint(0, len(unit_y) - 1)
                    target = [unit_x[i], unit_y[i]]
                    action = actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
                    print("Step 0 Done Correctly")
                    return action
                else:
                    print("Something failed on macro1 / step 0")
                    return actions.FunctionCall(_NO_OP, [])
        elif self.m_step == 1:
            target = [5]
            action = actions.FunctionCall(_SELECT_CONTROL_GROUP, [[0], target])
            self.create_control = False
            print("Step 1 Done Correctly")
            self.endMacro()
            return action
        else:
            print("Wrong Step for this Macro")
            return actions.FunctionCall(_NO_OP, [])

        
    def step(self, obs):
        super(SmartAgent, self).step(obs)
        time.sleep(0.2)
        #print(obs)

        player_y, player_x = (obs.observation['minimap'][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
        self.base_top_left = 1 if player_y.any() and player_y.mean() <= 31 else 0

        if not(self.macro is None):
            return self.macro(obs)
        elif self.control_groups[5]:
            self.macro = self.macro2

        elif not(self.control_groups[5]):
            self.macro = self.macro1





        """
        unit_type = obs.observation['screen'][_UNIT_TYPE]

        depot_y, depot_x = (unit_type == _TERRAN_SUPPLY_DEPOT).nonzero()
        supply_depot_count = self.supply_depot_count

        barracks_y, barracks_x = (unit_type == _TERRAN_BARRACKS).nonzero()
        barracks_count = self.barracks_count
            
        supply_limit = obs.observation['player'][4]
        army_supply = obs.observation['player'][5]
        
        killed_unit_score = obs.observation['score_cumulative'][5]
        killed_building_score = obs.observation['score_cumulative'][6]
        
        current_state = [
            supply_depot_count,
            barracks_count,
            supply_limit,
            army_supply,
        ]
        
        if self.previous_action is not None:
            reward = 0
                
            if killed_unit_score > self.previous_killed_unit_score:
                reward += KILL_UNIT_REWARD
            if killed_building_score > self.previous_killed_building_score:
                reward += KILL_BUILDING_REWARD
            if army_supply > self.army_supply:
                reward += BUILD_UNIT_REWARD
            #if army_supply < self.army_supply:
            #    reward += KILLED_SELF_UNIT_punishment    
                
            self.qlearn.learn(str(self.previous_state), self.previous_action, reward, str(current_state))
            #print(reward,current_state)
        rl_action = self.qlearn.choose_action(str(current_state))
        smart_action = smart_actions[rl_action]
        
        self.previous_killed_unit_score = killed_unit_score
        self.previous_killed_building_score = killed_building_score
        self.army_supply = army_supply
        self.previous_state = current_state
        self.previous_action = rl_action
        
        if smart_action == ACTION_DO_NOTHING:
            return actions.FunctionCall(_NO_OP, [])

        elif smart_action == ACTION_SELECT_SCV:
            unit_type = obs.observation['screen'][_UNIT_TYPE]
            unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()
                
            if unit_y.any():
                i = random.randint(0, len(unit_y) - 1)
                target = [unit_x[i], unit_y[i]]
                action = actions.FunctionCall(_SELECT_POINT, [_QUEUED, target])
                return action
        
        elif smart_action == ACTION_BUILD_SUPPLY_DEPOT:
            if _BUILD_SUPPLY_DEPOT in obs.observation['available_actions']:
                unit_type = obs.observation['screen'][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
                
                if unit_y.any():
                    target = self.transformLocation(int(unit_x.mean()), 0, int(unit_y.mean()), 20)
                    self.supply_depot_count +=1
                
                    return actions.FunctionCall(_BUILD_SUPPLY_DEPOT, [_NOT_QUEUED, target])
        
        elif smart_action == ACTION_BUILD_BARRACKS:
            if _BUILD_BARRACKS in obs.observation['available_actions']:
                unit_type = obs.observation['screen'][_UNIT_TYPE]
                holi = (unit_type == _TERRAN_COMMANDCENTER)
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()
                #print((unit_type == _TERRAN_COMMANDCENTER).shape)
                if self.barracks_count == 0:
                    print("Holi")
                    target = self.transformLocation(int(unit_x.mean()), 20, int(unit_y.mean()), 0)
                    print(target)
                    self.barracks_count += 1
                    self.barracks.append((target[0], target[1]))

                    return actions.FunctionCall(_BUILD_BARRACKS, [_NOT_QUEUED, target])
                else:
                    print("Hola")
                    barr = random.choice(self.barracks)
                    target = self.transformLocation(int(unit_x.mean()),barr[0] + self.barracks_count*5, barr[1],0)
                    print(target)
                    #target = self.transformLocation(int(unit_x.mean()), random.randint(1, 10)*20, int(unit_y.mean()), random.randint(1, 10)*20)
                    if target[0] > 0 and target[1] > 0 and target[0] < 84 and target[1] < 84:
                        self.barracks_count +=1
                        self.barracks.append((target[0],target[1]))
                        return actions.FunctionCall(_BUILD_BARRACKS, [_NOT_QUEUED, target])
    
        elif smart_action == ACTION_SELECT_BARRACKS:
            #print(self.barracks_count,self.barracks)
            if self.barracks_count >= 1:
                barr = random.choice(self.barracks)
                target = [barr[0], barr[1]]
                #print(target)
                return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
        
        elif smart_action == ACTION_BUILD_MARINE:
            if _TRAIN_MARINE in obs.observation['available_actions']:
                return actions.FunctionCall(_TRAIN_MARINE, [_QUEUED])
        
        elif smart_action == ACTION_SELECT_ARMY:
            if _SELECT_ARMY in obs.observation['available_actions']:
                return actions.FunctionCall(_SELECT_ARMY, [_NOT_QUEUED])
        
        elif smart_action == ACTION_ATTACK:
            if self.previous_action == 6:
                print(self.previous_action)
            if _ATTACK_MINIMAP in obs.observation["available_actions"] :
                if self.base_top_left:
                    return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [39, 45]])
            
                return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, [21, 24]])
        """
        return actions.FunctionCall(_NO_OP, [])

    def reset(self):
        self.supply_depot_count = 0
        self.barracks_count = 0
        self.army_supply = 0
        self.barracks = []
        self.supplies = []
        self.control_groups = np.zeros(10).astype(bool)
        self.episodes += 1
        self.control_groups = np.zeros(10).astype(bool)
        self.create_control = False

        ####
        # Macros
        ####
        self.macro = None
        self.m_step = 0


    def update(self,*kargs):
        #TODO: ASDJKLFA
        pass

    def save_model(self,*kargs):
        #Todo : ASDAF
        pass


