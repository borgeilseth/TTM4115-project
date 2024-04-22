from stmpy import Machine, Driver
 
class Charger:
    
    def on_idle(self):
        print('Idling')
    
    def on_charging(self):
        print('Charging')
        
 
charger = Charger()
 
t0 = {'source': 'initial',
      'target': 'idle',
      'effect': 'start_timer("t", 1000)'
     }
 
# Turn on detector
t1 = {'source': 'idle',
      'trigger': 't',
      'target': 'charging',
      'effect': 'start_timer("t", 1000); on_charging',
     }
 
# Turn off detector
t2 = {'source': 'charging',
      'trigger': 't',
      'target': 'idle',
      'effect': 'start_timer("t", 1000); on_idle'
     }
 
 
machine = Machine(
    name='Charger',
    transitions=[t0, t1, t2],
    obj=charger,
)
charger.stm = machine
 
driver = Driver()
driver.add_machine(machine)
driver.start(max_transitions=10)