import matplotlib.pyplot as plt
import IPython.display as display
import time
from pyswip import Prolog
from minihack import LevelGenerator
from minihack import RewardManager
from nle import nethack
from algorithms import a_star
from utilsbattle import DIR_TO_NUM_MAP, NUM_TO_DIR_MAP, actions_from_path, chebyshev_distance, get_closest_gold

from run import AVAIABLE_OBJECTS,AVAIABLE_ARROWS,AVAIABLE_WEAPONS,AVAIABLE_ARMORS, BOSS, MINIBOSS, MOB

def create_level():
    lvl = LevelGenerator(w=21,h=21)
    shopkeeper_posx,shopkeeper_posy=(11,2)

    lvl.add_monster(name='shopkeeper',place=(shopkeeper_posx,shopkeeper_posy) )

    lvl.add_object(name='apple', symbol='%',place=(shopkeeper_posx,shopkeeper_posy+2))
    lvl.add_object(name='banana', symbol='%',place=(shopkeeper_posx-2,shopkeeper_posy+2))
    lvl.add_object(name='orange', symbol='%',place=(shopkeeper_posx+2,shopkeeper_posy+2))
    #lvl.add_object(name='ring mail', symbol='[',place=(shopkeeper_posx,shopkeeper_posy+2))
    #lvl.add_object(name='tsurugi', symbol=')',place=(shopkeeper_posx+2,shopkeeper_posy+2))
    return lvl.get_des()

def define_reward(monster: str = 'kobold'):
    reward_manager = RewardManager()

    reward_manager.add_eat_event(name='apple', reward=2, terminal_sufficient=True, terminal_required=True)
    reward_manager.add_kill_event(name=monster, reward=1, terminal_required=False)

    return reward_manager

def perform_action(action, env,kb,planned_actions,obs):

    name,args=parse_predicate(action)
    if name == 'eat': 
        action_id = 29
        # print(f'Action performed: {repr(env.actions[action_id])}')
        obs, _, _, _ = env.step(action_id)
        # Example message:
        # What do you want to eat?[g or *]
        message = bytes(obs['message']).decode('utf-8').rstrip('\x00')
        food_char = message.split('[')[1][0] # Because of the way the message in NetHack works
        action_id = env.actions.index(ord(food_char))

    elif name == 'attack' :
        #print(action)
        action_id = DIR_TO_NUM_MAP[args[0]]
        kb.retractall('onPlan(_)')

    elif 'followPlan' == name :
        action_id = DIR_TO_NUM_MAP[args[0]]
        kb.retractall('plannedMove(_)') #remove last planned move
        if len(planned_actions) > 0 :
            kb.asserta(f'plannedMove({NUM_TO_DIR_MAP[planned_actions.pop(0)]})')
        else : kb.retractall('onPlan(_)')

    elif 'plan' in action : #have to formulate plan
        kb.retractall('plannedMove(_)') #remove past planned move

        #get agent pos
        agent_pos = list(kb.query('position(agent,_,X,Y)'))[0]
        start = (agent_pos['X'],agent_pos['Y'])

        #get stairs pos
        stair_pos = list(kb.query('position(stairs,_,X,Y)'))[0]
        target = (stair_pos['X'],stair_pos['Y'])

        #get all gold pos
        gold_pos_list= list(kb.query('position(gold,_,X,Y)'))

        gold_pos_list = [(element['X'],element['Y'])for element in gold_pos_list]

        gold_pos = get_closest_gold(gold_pos_list,start)
        #print(f'Gold at:{gold_pos}')

        if gold_pos is None :
            gold_pos = target

        game_map = obs['chars']

        path,_ = a_star(game_map, start, gold_pos,chebyshev_distance)
        #print(f"PATH:{path}")
        planned_actions = actions_from_path(start, path[1:])

        action_id = planned_actions.pop(0) #retrieve action to execute


        #insert next planned move in kb
        if len(planned_actions) > 0 : #if plan made of one action (thus len == 0 here) we need to replan next
            kb.asserta(f'plannedMove({NUM_TO_DIR_MAP[planned_actions.pop(0)]})')
            kb.asserta('onPlan(agent)') #tell that new plan is available

    elif 'pick_key' == action :
        action_id = 49
    elif name == 'apply' :
        while True:
            action_id = 20
            obs, _, _, _ = env.step(action_id)
            env.render()

            #roba del tipo: What do you want to use or apply? [fg or ?*]
            message = bytes(obs['message']).decode('utf-8').rstrip('\x00')
            weapon_char = message.split('[')[1].split(' ')[0][-1]
            action_id = env.actions.index(ord(weapon_char))

            obs, _, _, _ = env.step(action_id)
            env.render()
            #appare messaggio: In what direction?
            obs, _, _, _ = env.step(DIR_TO_NUM_MAP[args[0]])
            env.render()

            #appare messaggio
            # Unlock it? [yn] (n)
            obs, _, _, _ = env.step(env.actions.index(ord('y')))
            env.render()

            # You succeed in unlocking the door.
            message = bytes(obs['message']).decode('utf-8').rstrip('\x00')
            if 'You succeed in unlocking the door.' in message :
                action_id = int(DIR_TO_NUM_MAP[args[0]]) #open the door
                break 

    elif 'pick' in action: #picking gold
        action_id = 49
        kb.retractall('stepping_on(agent,_,_)')
        agent_pos = list(kb.query('position(agent,_,X,Y)'))[0]
        agent_x = int(agent_pos['X'])
        agent_y = int(agent_pos['Y'])
        kb.retractall(f'position(gold,_,{agent_x},{agent_y})')

        #updating money
        #retrieve money before picking up gold
        game_money_old = int(obs['blstats'][13])
        curr_money = int(list(kb.query('money(X)'))[0]['X'])
        
        #perform action
        #print(f'>> Current action from Prolog: {action}')
        obs, reward, done, info = env.step(action_id)

        #obtain new game money
        game_money_new = int(obs['blstats'][13])
        #update kb
        kb.retractall('money(_)')
        kb.asserta(f'money({curr_money + game_money_new - game_money_old})')

        return obs, reward, done, info , planned_actions
    
    elif name == 'wield':
        action_id = 78
        obs, _, _, _ = env.step(action_id)
        env.render()

        # Example message:
        # What do you want to wield? [- abcdg or ?*]

        message = bytes(obs['message']).decode('utf-8').rstrip('\x00')

        weapon_char = message.split('[')[1].split(' ')[1][-1]

        action_id = env.actions.index(ord(weapon_char))

    elif name== 'buy_item':
        action_id = 49
        cost=int(args[0])
        item_type=args[1]
        item_name=args[2]
        kb.retractall('stepping_on(_,_,_)')
        kb.retractall('available_to_buy(_,_,_)')
        #refersh money after purchase
        old_money=int(list(kb.query('money(X)'))[0]['X'])
        kb.retractall("money(_)")
        kb.asserta(f"money({old_money-cost})")
        # if it's buying arrows it will update the number of arrows the agent has
        if ('armor' in item_type):
            healthiness=int(list(kb.query('money_threshold(X)'))[0]['X'])
            protection= int(list(kb.query(f"armor_stats({item_name},X)"))[0]['X'])
            kb.retractall("health_threshold(X)")
            kb.asserta(f"health_threshold({protection*0.25 + healthiness})")
        if('arrow' in item_type):
            old_arrows=int(list(kb.query('arrows(X)'))[0]['X'])
            kb.retractall("arrows(X)")
            kb.asserta(f"arrows({old_arrows+1})")
        kb.asserta(f"has(agent,\'{item_type}\',\'{item_name}\')")

    # Movement/Attack/Run/Get_To_Weapon actions
    # in the end, they all are movement in a direction
    elif 'northeast' in action: action_id = 4
    elif 'southeast' in action: action_id = 5
    elif 'southwest' in action: action_id = 6
    elif 'northwest' in action: action_id = 7
    elif 'north' in action: action_id = 0
    elif 'east' in action: action_id = 1
    elif 'south' in action: action_id = 2
    elif 'west' in action: action_id = 3
    elif 'sit' in action : action_id = 11
    print(f'>> action from Prolog: {action} | Action performed: {repr(env.actions[action_id])}')
    obs, reward, done, info = env.step(action_id)

    if name == 'apply' :
        message = bytes(obs['message']).decode('utf-8').rstrip('\x00')
        #the door resist
        while 'The door opens.' not in message :
            obs, reward, done, info = env.step(action_id)
            message = bytes(obs['message']).decode('utf-8').rstrip('\x00')


    return obs, reward, done, info , planned_actions


#TODO: add battle to process state
def process_state(obs: dict, kb: Prolog, in_battle:bool = False):

    #to mantain global information about gold positions
    if in_battle :
        print('QUAAAAAa')
        gold_pos_list= list(kb.query("position(gold,_,X,Y)"))
        print(gold_pos_list)
        stairs_pos = list(kb.query("position(stairs,_,X,Y)"))[0]
        print(stairs_pos)

    kb.retractall("position(_,_,_,_)")

    if in_battle :
        for gold_pos in gold_pos_list : #put the information about gold that you have eliminated
            gold_x = int(gold_pos['X'])
            gold_y = int(gold_pos['Y'])
            kb.asserta(f'position(gold,_,{gold_x},{gold_y})')

        kb.asserta(f'position(stairs,_,{int(stairs_pos["X"])},{int(stairs_pos["Y"])})') #putting information about stairs again, even if not in observation


    # elabora in base alle osservazioni presenti
    level_heigth=len(obs['screen_descriptions'])
    level_width=len(obs['screen_descriptions'][0])

    for i in range(level_heigth):
        for j in range(level_width):
            if (obs['screen_descriptions'][i][j] == 0).all(): continue
            objs = bytes(obs['screen_descriptions'][i][j]).decode('utf-8').rstrip('\x00') 
            obj_type=chr(obs['chars'][i][j]) # characters indicates the type of object
            if obj_type == '!':
                kb.asserta(f"position(potion,healing,{i},{j})")
                kb.asserta(f"available_to_buy(potion,healing,1)")
            elif obj_type == ')':
                arrow= list(filter(lambda x:x in objs,AVAIABLE_ARROWS))
                if len(arrow)!=0:# if the list isn't empty it's an arrow otherwise it's a weapon
                    arrow=arrow[0]
                    kb.asserta(f"position(arrow,\'{arrow}\',{i},{j})")
                    kb.asserta(f"available_to_buy(arrow,\'{arrow}\',1)")
                weapon= list(filter(lambda x:x in objs,AVAIABLE_WEAPONS))
                if len(weapon)!=0 :
                    weapon = weapon[0]
                    kb.asserta(f"position(weapon,\'{weapon}\',{i},{j})")
                    kb.asserta(f"available_to_buy(weapon,\'{weapon}\',10)")
                #special case: the katana appears as a samurai sword until it's stepped on
                if 'samurai sword' in objs:
                    kb.asserta(f"available_to_buy(weapon,\'katana\',10)")
                    kb.asserta(f"position(weapon,\'katana\',{i},{j})")
            elif obj_type == '[': 
                armor= list(filter(lambda x:x in objs,AVAIABLE_ARMORS))
                if len(armor)!=0:
                    armor=armor[0]
                    kb.asserta(f"position(armor,\'{armor}\',{i},{j})")
                    kb.asserta(f"available_to_buy(armor,\'{armor}\',5)")
            elif 'shopkeeper' in objs:
                kb.asserta(f"position(enemy,shopkeeper,{i},{j})")
            elif 'closed door' in objs:
                kb.asserta(f"position(object,door,{i},{j})")
            elif 'open door' in objs or 'floor' in objs:
                kb.asserta(f"position(object,tile,{i},{j})")
            elif objs in MOB or objs in MINIBOSS or objs in BOSS:
                #print(obj)
                kb.asserta(f'position(enemy,\'{objs}\',{i},{j})')
            elif 'key' in objs :
                kb.asserta(f"""position(tool,'skeleton key',{i},{j})""")

    

    
    kb.retractall("wields_weapon(_,_)")
    kb.retractall("has(agent,_,_)")

    display_inventory(obs['inv_strs'])

    for item in obs['inv_strs']:
        item = bytes(item).decode('utf-8').rstrip('\x00')
        if 'weapon in hand' in item:
            # the actual name of the weapon is in position 2
            # qualcosa nomearma (weapon in hand)
            wp = " ".join(item.split()[1:]).split('(')[0].rstrip()
            print(f'Arma: {wp}')
           
            kb.asserta(f"""wields_weapon(agent,'{wp}')""")
            if wp not in AVAIABLE_WEAPONS :
                kb.retractall(f"""weapon_stats('{wp}',_)""")
                kb.assertz(f"""weapon_stats('{wp}',0)""")
            continue


        inv_item=list(filter(lambda x:x in item,AVAIABLE_WEAPONS))
        if len(inv_item)!=0 :
            kb.asserta(f"has(agent,weapon,\'{inv_item[0]}\')")

        inv_item=list(filter(lambda x:x in item,AVAIABLE_ARMORS))
        if len(inv_item)!=0 :
            kb.asserta(f"has(agent,armor,\'{inv_item[0]}\')")

        inv_item=list(filter(lambda x:x in item,AVAIABLE_ARROWS))
        if len(inv_item)!=0 :
            kb.asserta(f"has(agent,arrow,\'{inv_item[0]}\')")

        inv_item=list(filter(lambda x:x in item,AVAIABLE_OBJECTS))
        if len(inv_item)!=0 :
            if 'potion' in inv_item[0]:
                kb.asserta(f"has(agent,potion,\'healing\')")
        if 'potion' in item:
            kb.asserta(f"has(agent,potion,\'healing\')")
        

    # processa in base allo stato dell'agente

    # aggiornamento posizione agente e vita
    kb.retractall("health(_)")
    kb.asserta(f"position(agent, _, {obs['blstats'][1]}, {obs['blstats'][0]})")
    kb.asserta(f"health({int(obs['blstats'][10]/obs['blstats'][11]*100)})")
    agent_r=obs['blstats'][1]
    agent_c=obs['blstats'][0]

    bs=list(kb.query("battlefield_start(R,C)"))[0]

    if agent_r == bs['R'] and agent_c == bs['C']+1: #even if it goes on this specific cell multiple times, it doesn't change anythign
        kb.asserta("battle_begin")

    kb.retractall('stepping_on(agent,_,_)')

    # processa messaggio sullo schermo
    message = bytes(obs['message']).decode('utf-8').rstrip('\x00')
    if 'The door opens' in message:
        kb.asserta("shopping_done")
    if 'You see here' in message:
        armor=list(filter(lambda x:x in message,AVAIABLE_ARMORS))
        if len(armor) !=0:
            kb.asserta(f'stepping_on(agent, armor, \'{armor[0]}\')')
        weapon=list(filter(lambda x:x in message,AVAIABLE_WEAPONS))
        if len(weapon) !=0:
            kb.asserta(f'stepping_on(agent, weapon, \'{weapon[0]}\')')
        arrow=list(filter(lambda x:x in message,AVAIABLE_ARROWS))
        if len(arrow) !=0:
            kb.asserta(f'stepping_on(agent, arrow, \'{arrow[0]}\')')
        objs=list(filter(lambda x:x in message,AVAIABLE_OBJECTS))
        if len(objs) !=0:
            kb.asserta(f'stepping_on(agent,potion,healing)')
        if 'potion' in message:
            kb.asserta(f'stepping_on(agent,potion,healing)')
        if 'key' in message:
            kb.asserta("""stepping_on(agent,tool,'skeleton key')""")

        #model stepping_on gold
    if in_battle :
        for gold_pos in gold_pos_list : #put the information about gold that you have eliminated
            gold_x = int(gold_pos['X'])
            gold_y = int(gold_pos['Y'])
            if gold_x == obs['blstats'][1] and gold_y == obs['blstats'][0] :
                kb.asserta('stepping_on(agent,gold,_)')
        
# indexes for showing the image are hard-coded
def show_match(states: list):
    image = plt.imshow(states[0])
    for state in states[1:]:
        time.sleep(0.25)
        display.display(plt.gcf())
        display.clear_output(wait=True)
        image.set_data(state)
    time.sleep(10)
    display.display(plt.gcf())
    display.clear_output(wait=True)

#return a tuple where the first element is the name of the predicate and the econd contains it's arguments
def parse_predicate(predicate):
    try:
        start=predicate.index('(')
        return predicate[0:start],tuple(predicate[start+1:-1].split(','))
    except:#il predicato ha arietà 0
        return predicate,()

def display_inventory(inv_obs):
    for item in inv_obs:
        item_str=bytes(item).decode('utf-8').rstrip('\x00')
        if(item_str!=""): print(item_str)
def extract_monsters(des_file:str):
    monsters=  list(filter(lambda x: "MONSTER" in x and "shopkeeper" not in x,des_file.split('\n')))
    monsters_data=[]
    for monster in monsters:
        name_start=monster.index('\"')+1
        name_end=monster.index('\"',9)
        name=monster[9:name_end]
        pos_start=monster.index('(')
        pos_x,pos_y= map(int,monster[pos_start+1:-1].split(','))
        monsters_data.append((name,pos_x,pos_y))
    return monsters_data

