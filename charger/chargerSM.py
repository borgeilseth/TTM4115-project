
from stmpy import Machine, Driver


#Actions
class Charger:

    def check_user(self):
        return True

    # def compound(self):
    #     boolean = self.check_user()
    #     if boolean:
    #         return 'charging'
    #     else:
    #         return 'idle'

    # def compound_effects(self):
    #     if self.compound() == 'charging':
    #         return 'charge; check_settings'
    #     else:
    #         return 'invalid_error'

    def charging(self):
        print ('charging')

    def check_settings(self):
        print ('checking settings')

    def invalid_error(self):
        print ('not valid user')
    
    def stop_charging(self):
        print ('charging done')

    def on_idle(self):
        print('Idling')

    # def on_charge(self):
    #     print('Charging')



charger = Charger()

#Transitions:
#Initial transitions
t0 = {
    'source': 'initial',
    'target': 'idle',
}

#Compound transition
t1 = {
    'trigger': 't', #??
    'source': 'idle',
    'target': '-',
    'action': 'check_user()',
    'guard': "check_user() ? 'charge' : 'idle'",
    'effect': "check_user() ? 'charging' : 'invalid_error'"
}

#Done charging
t2 = {
    'trigger': 't1',
    'source': 'charge',
    'target': 'idle',
    'effect': 'stop_charging'
}

#States
idle = {
    'name': 'idle',
    'entry': 'on_idle; start_timer("t", 1000)'
}

charge = {
    'name': 'charge',
    'entry': 'charging; start_timer("t1", 1000)'
}
 

machine = Machine(
    name='charger', 
    transitions=[t0, t1, t2], 
    obj=charger, 
    states=[idle, charge]
)
charger.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()
