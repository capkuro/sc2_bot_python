from pysc2.agents import base_agent
from pysc2.lib import actions
import time


# Running an agent that does nothing.


class SimpleAgent(base_agent.BaseAgent):

    def initialize(self):
        # TODO: Implement this function
        pass


    def step(self, obs):
        super(SimpleAgent, self).step(obs)
        #time.sleep(0.25)
        return actions.FunctionCall(actions.FUNCTIONS.no_op.id, [])

    def reset(self):
        #TODO: Implement this function
        pass

    def update(self,*kargs):
        # TODO: Implement this function
        pass

    def save_model(self,*kargs):
        # TODO: Implement this function
        pass