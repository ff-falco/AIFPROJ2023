import matplotlib.pyplot as plt
import IPython.display as display
import time
from pyswip import Prolog
from minihack import LevelGenerator
from minihack import RewardManager
from nle import nethack

from run import AVAIABLE_OBJECTS,AVAIABLE_ARROWS,AVAIABLE_WEAPONS,AVAIABLE_ARMORS

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

def perform_action(action, env,kb):

    name,args=parse_predicate(action)
    if action == 'eat': 
        action_id = 29
        # print(f'Action performed: {repr(env.actions[action_id])}')
        obs, _, _, _ = env.step(action_id)
        # Example message:
        # What do you want to eat?[g or *]
        message = bytes(obs['message']).decode('utf-8').rstrip('\x00')
        food_char = message.split('[')[1][0] # Because of the way the message in NetHack works
        action_id = env.actions.index(ord(food_char))
    elif action == 'pay': 
        action_id= 9
        kb.retractall('has_to_pay')
        kb.retractall('stepping_on(_,_,_)')
        kb.retractall('available_to_buy(_,_,_)')
    elif action == 'pick': 
        action_id = 8
        kb.asserta('has_to_pay')
    elif action == 'wield': action_id = 10
    elif name== 'buy_item':
        action_id = 8
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
    elif 'activate_portal' in action : action_id = 11
    #print(f'>> action from Prolog: {action} | Action performed: {repr(env.actions[action_id])}')
    obs, reward, done, info = env.step(action_id)
    return obs, reward, done, info

def process_state(obs: dict, kb: Prolog):
    kb.retractall("position(_,_,_,_)")

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
            elif obj_type=='^':
                kb.asserta(f"position(object,teleport,{i},{j})")
            elif obj_type=='>':
                kb.asserta(f"position(object,stairs,{i},{j})")
            elif 'shopkeeper' in objs:
                kb.asserta(f"position(enemy,shopkeeper,{i},{j})")
            elif 'closed door' in objs:
                kb.asserta(f"position(object,door,{i},{j})")
            elif 'open door' in objs or 'floor' in objs:
                kb.asserta(f"position(object,tile,{i},{j})")

    

    
    kb.retractall("wields_weapon(_,_)")
    kb.retractall("has(agent,_,_)")    
    for item in obs['inv_strs']:
        item = bytes(item).decode('utf-8').rstrip('\x00')
        inv_item=list(filter(lambda x:x in item,AVAIABLE_WEAPONS))
        if len(inv_item)!=0 :
            kb.asserta(f"has(agent,armor,\'{inv_item[0]}\')")
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


    # processa messaggio sullo schermo
    message = bytes(obs['message']).decode('utf-8').rstrip('\x00')
    if 'The door opens' in message:
        kb.asserta("shopping_done")
    if 'shopkeeper' in message:
        print("you stumbled upon the shopkeeper")
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

    if 'You activated a magic portal!' in message:
        kb.asserta("shopping_done")
        kb.asserta(f'stepping_on(agent,object,portal)')
        
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

