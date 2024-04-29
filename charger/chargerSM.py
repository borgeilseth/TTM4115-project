
from stmpy import Machine, Driver
import random
import time
from config import *

max_charge = Charging_percent
global current_charge 
current_charge = random.randint(1, 80)


#Actions
class Charger:
    
    def check_user(self):
        "sjekker user her"
        return True 

    def check_user_transition(self):
        if Charger.check_user(self):
            self.stm.send("valid_user")
        else:
            self.stm.send("invalid_user")

    def charge(self):    
        global current_charge 

        while current_charge < max_charge:
            print("Ten electricity to you :)")
            current_charge += 10
            time.sleep(1)
            print(f"You are now at {current_charge}%") 

        if current_charge >= max_charge:
            print("You are currently at your preffered charge level.")
            self.stm.send("done_charging")
            

    def check_settings(self):
        print ('checking settings')

    def invalid_error(self):
        print ('not valid user')
    
    def stop_charging(self):
        print ('charging done')

    def on_idle(self):              
        print('Idling')

    def buildMessage(self):
        return ""
    
    def sendMessage(self):
        return ""
    

charger = Charger()

#Transitions:
#initial transition
t0 = {
    'trigger': '',
    'source': 'initial',
    'target': 'idle',
    'effect': 'on_idle; start_timer("t", 1000)'
}

#validate
t1 = {
    'trigger': 't',
    'source': 'idle',
    'target': 'validating',
    'effect': 'check_user_transition'
}

#start charging
t2 = {
    'trigger': 'valid_user',
    'source': 'validating',
    'target': 'charging',
    'effect': 'check_settings; charge'
}

#error
t3 = {
    'trigger': 'invalid_user',
    'source': 'validating',
    'target': 'idle',
    'effect': 'invalid_error'
}

#done charging
t4 = {
    'trigger': 'done_charging',
    'source': 'charging',
    'target': 'idle',
    'effect': 'stop_charging'
}
 

machine = Machine(name='charger', transitions=[t0, t1, t2, t3, t4], obj=charger)
charger.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()
