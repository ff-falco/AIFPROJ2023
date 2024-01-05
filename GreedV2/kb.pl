:- dynamic position/4.
:- dynamic wields_weapon/2.
:- dynamic has/3.

:- dynamic stepping_on/3.
:- dynamic unsafe_position/2.

:- dynamic health/1.
:- dynamic health_threshold/1.

:- dynamic money/1.
:- dynamic money_threshold/1.

:- dynamic available_to_buy/3.
:- dynamic can_buy/3.
:- dynamic wants_to_buy/3.

:- dynamic corridors/0.

:- dynamic open_spaces/0.

:- dynamic shopping_done/0.
:- dynamic battlefield_start/2.
:- dynamic battle_begin/0.
:- dynamic weapon_stats/2.
:- dynamic level/2.

:- dynamic wears_armor/2.
:- dynamic armor_stats/2.

:- dynamic onPlan/1.
:- dynamic plannedMove/1 .
% SHOP PLANNING PREDICATES

% the agent feels healthy if the health is above the healthiness threshold (in percentage)
healthy :- health(H),health_threshold(T), H > T.

% the agent feels rich if the health is above the richness threhsold
rich :- money(M),money_threshold(T), M > T.

%the agent can buy the item if it has enough money and the item is available to buy 
can_buy(Type,Name,Cost) :- money(M), available_to_buy(Type,Name,Cost),M>=Cost.

%the best healing option is the one that has no other  available item with better healing
%Requirements:
% - the agent can buy the item
% - the item is the best one available to buy
% - there isn't any other item with better healing stats available
best_healing_option(Type,Name,Cost):- can_buy(Type,Name,Cost),
                                        healing_stats(Type,Name,Healing),
                                        \+ (
                                            can_buy(OtherType,OtherName,_),
                                            healing_stats(OtherType,OtherName,OtherHealing), 
                                            Healing < OtherHealing
                                        ).

%the agent will buy first health if it is not healthy and can afford the purchase
%Requirements:
% - the agent doesn't feels healthy
% - it can affor to buy the object
% - the object has healing properties and is the best healing item available
wants_to_buy(Type,Name,Cost) :- \+ healthy, 
                                can_buy(Type,Name,Cost), 
                                best_healing_option(Type,Name,Cost).

%buy equipment when the agent cannot beat the enemy
%Requirements:
% - the anget can buy the new weapon
% - the agent is wielding the current weapon
% - there is an enemy that is not beatable with the current weapon
% - but it beatable with the new weapon
% - the new weapon is best one available for purchase

wants_to_buy(EquipmentType,EquipmentName,EquipmentCost) :- can_buy(EquipmentType,EquipmentName,EquipmentCost),
                                              wields_weapon(agent,CurrentWeapon),
                                              wears_armor(agent,CurrentArmor),
                                              position(enemy,EnemyType,_,_),
                                              \+ is_beatable(EnemyType,CurrentWeapon,CurrentArmor),
                                              power_difference(EquipmentType,EquipmentName,Difference),
                                              Difference > 0, % i am improving the equipment
                                              best_equippable_buyable(EquipmentName).

%the agent stocks up on healing items
%Requirements:
%   -agent is rich
%   -agent can buy an item
%   -the item is the best healing item in the shop

wants_to_buy(Type,Name,Cost) :- rich, 
                                can_buy(Type,Name,Cost), 
                                best_healing_option(Type,Name,Cost).


%then the agent improves its equipment if he is still rich
%Requirements:
%   -agent is rich
%   -agent can buy a certain equipment for a certain price
%   -that equipment is better w.r.t. the respective type of equip. the agent is wearing
%   -the equipment considered is the best one available in the shop

wants_to_buy(EquipmentType,EquipmentName,EquipmentCost) :- rich,
                                              can_buy(EquipmentType,EquipmentName,EquipmentCost),
                                              power_difference(EquipmentType,EquipmentName,Difference),
                                              Difference > 0, % i am improving the equipment
                                              best_equippable_buyable(EquipmentName).


%best equipment is the one with highest power that i can buy
%Requirements:
%   -equipment has certain Power
%   -does not exists another equipments s.t.
%       -the agent can buy it
%       -its power is greater than the one of the original equipment

best_equippable_buyable(Name) :- can_buy(Type,Name,_),
                                power_difference(Type,Name,Difference),
                                \+ (
                                    can_buy(OtherType,OtherName,_),
                                    power_difference(OtherType,OtherName,OtherDifference),
                                    Difference < OtherDifference
                                ).



power_difference(weapon,NewWeapon,Difference) :- wields_weapon(agent,OldWeapon),
                                                    weapon_stats(OldWeapon,Damage),
                                                    weapon_stats(NewWeapon,NewDamage),
                                                    Difference is NewDamage - Damage.

power_difference(armor,NewArmor,Difference) :- wears_armor(agent,OldArmor),
                                                armor_stats(OldArmor,Defense),
                                                armor_stats(NewArmor,NewDefense),
                                                Difference is NewDefense - Defense.

%an enemy is beatable with a weapon if the weapon has more power than the enemy
%Requirements:
% - the weapon has a name and damage 
% - armor had name and defense
% - the enemy has a name and power
% - the total power of the equipment is higher than the enemy power
is_beatable(Enemy,Weapon,Armor) :- weapon_stats(Weapon,Damage),
                                    armor_stats(Armor,Defense),
                                    enemy_stats(Enemy,_,EnemyPower),
                                    Sum is Damage + Defense,
                                    Sum >= EnemyPower.




%drink a potion when not healthy
%Requirements:
% - the agent doesn't feel healthy
% - the agent has apotion in his inventory

action(quaff(Potion)) :- \+ healthy, has(agent,potion,Potion).
%eat food when no potion is available 
%Requirements:
% - the agent doesn't feel healthy
% - the agent has comestible food in the inventory and there isn't a potion available

action(eat(Food)) :- \+ healthy, has(agent,comestible,Food).
%wield the weapon in the inventory with the best damage
%Requirements:
% - the agent is wielding a weapon (Wold)
% - the weapon has a name and a damage power
% - the agent has another weapon (Wnew)
% - the other weapon has better damage power

action(wield(Wnew)) :-  wields_weapon(agent,Wold), 
                        weapon_stats(Wold,OldStats),
                        has(agent,weapon,Wnew), 
                        weapon_stats(Wnew,NewStats), 
                        NewStats > OldStats .

%wear the best armor in inventory
%Requirements:
% - the agent is wearing an armor
% - the armor has a name and armor power
% - the agent has another armor
% - the other armor has better armor power

action(wear(Aold,Anew)) :- wears_armor(agent,Aold),
                        armor_stats(Aold,OldStats),
                        has(agent,armor,Anew),
                        armor_stats(Anew,NewStats),
                        NewStats > OldStats .

%----------------------- BATTLE ONLY PREDICATES------------------------------

%attack an enemy
%if agent is near an enemy, attack it
%it is assumed the agent will always win against enemies, which is not true
%Requirements:
%   -agent at a given position
%   -enemy at a given position
%   -agent and enemy are near each other (the positions are close)
%   -agent is in the battle phase
%after this action we need to replan

action(attack(Direction)) :- position(agent,_,R1,C1), 
                             position(enemy,_,R2,C2), 
                             is_close(R1,C1,R2,C2), 
                             next_step(R1,C1,R2,C2,Direction), 
                             battle_begin .
%pick up gold
%if agent is stepping on gold, he has to pick it up
%restricted to gold because other objects could be the ones from the shop
%requirements:
%   -agent is healthy
%   -agent is stepping on gold
%   -gold is pickable
%   -agent is in battle phase
action(pick) :- healthy,
                stepping_on(agent,gold,_), 
                is_pickable(gold), 
                battle_begin.

%default behaviour -> if you have a plan, follow it
%Requirements:
% - agent has a plan and is following it
% - the plan tells to go in direction Direction
% - the agent is in the battle phase
action(followPlan(Direction)) :- onPlan(agent), 
                                 plannedMove(Direction), 
                                 battle_begin.

%not healty default behaviour -> create a plan to go towards the exit
%Requirements:
%   -agent is not healthy
%   -agent is not following a plan
%   -agent is in battle phase
action(plan_escape) :-  \+ healthy,
                        \+ onPlan(agent),
                        battle_begin.

%default behavior -> create a plan if you don't have one and do its first action
%Requirements:
% - agent has no plan to follow
action(plan) :- \+ onPlan(agent), 
                battle_begin .


%--------- SHOP ONLY PREDICATES ----------------------------
%if you step on a weapon and it is weapon you want to buy buy it
action(buy_item(ObjCost,ObjType,ObjName)):- stepping_on(agent,ObjType,ObjName),
                                            wants_to_buy(ObjType,ObjName,ObjCost).  
% go in the direction of the item you want to buy 
action(get_to_item(Direction)) :- wants_to_buy(ItemType,ItemName,_),
                                  position(ItemType,ItemName,IR,IC),
                                  position(agent,_,AR,AC),
                                  next_step(AR,AC,IR,IC,Direction),
                                  \+ shopping_done.

% pick a key when you stepped on it
action(pick_key) :- stepping_on(agent,tool,'skeleton key').

%when done with the shoping phase got to the key to unlock the door
action(get_key(Direction)) :- position(agent,_,R1,C1), 
                              position(tool,'skeleton key',R2,C2), 
                              next_step(R1,C1,R2,C2,Direction), 
                              \+ battle_begin.

%use the apply action in the chosen direction
action(apply(Direction)) :- position(agent,_,AR,AC), 
                            position(object,door,DR,DC), 
                            DC is AC+1, 
                            DR is AR, 
                            next_step(AR,AC,DR,DC,Direction).


% LEAVING THE SHOP
%exit the shop if it doesn't want to buy anything else
action(exit_shop(Direction)) :- position(agent,_,AR,AC),
                                position(object,door,DR,DC),
                                next_step(AR,AC,DR,DC,Direction),
                                resulting_position(AR, AC, NewR, NewC,Direction),
                                (position(object,door,NewR,NewC);position(object,tile,NewR,NewC)),
                                \+ (
                                    position(object,door,_,OtherDC),
                                    OtherDC<DC
                                ), 
                                \+ shopping_done,
                                \+ battle_begin.

% go right when you're done shopping and there is a tile or the battle field start on yout right, and the battle hasn't begun
action(get_into_battlefield(east)) :- shopping_done,position(agent,_,AR,AC),
                                      \+ battle_begin,
                                      (
                                        (position(object,tile,TR,TC),TC is AC+1,TR is AR);
                                        (battlefield_start(BR,_), BR is AR)
                                      ).
%go down when you can't go right and there is a tile below, and the battle hasn't begun
action(get_into_battlefield(south)) :- shopping_done,
                                       position(agent,_,AR,AC),\+ battle_begin,
                                       \+ (
                                            position(object,tile,TR,TC),
                                            TC is AC+1,
                                            TR is AR
                                        ).

% -----------------------------------------------------------------------------------------------

% test the different condition for closeness
% two objects are close if they are at 1 cell distance, including diagonals
is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+1; C1 is C2-1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+1; R1 is R2-1).
is_close(R1,C1,R2,C2) :- (R1 is R2+1; R1 is R2-1), (C1 is C2+1; C1 is C2-1).

%wheter a position is safe or not
unsafe_position(R, C) :- position(enemy, _, R, C).

unsafe_position(_,_) :- fail.

safe_position(R,C) :- \+ unsafe_position(R,C).

% compute the direction given the starting point and the target position
% check if the direction leads to a safe position
% D = temporary direction - may be unsafe
% Direction = the definitive direction 
next_step(R1,C1,R2,C2, D) :-
    ( R1 == R2 -> ( C1 > C2 -> D = west; D = east );
    ( C1 == C2 -> ( R1 > R2 -> D = north; D = south);
    ( R1 > R2 ->
        ( C1 > C2 -> D = northwest; D = northeast );
        ( C1 > C2 -> D = southwest; D = southeast )
    ))).

%%%% known facts %%%%
opposite(north, south).
opposite(south, north).
opposite(east, west).
opposite(west, east).
opposite(northeast, southwest).
opposite(southwest, northeast).
opposite(northwest, southeast).
opposite(southeast, northwest).

resulting_position(R, C, NewR, NewC, north) :-
    NewR is R-1, NewC = C.
resulting_position(R, C, NewR, NewC, south) :-
    NewR is R+1, NewC = C.
resulting_position(R, C, NewR, NewC, west) :-
    NewR = R, NewC is C-1.
resulting_position(R, C, NewR, NewC, east) :-
    NewR = R, NewC is C+1.
resulting_position(R, C, NewR, NewC, northeast) :-
    NewR is R-1, NewC is C+1.
resulting_position(R, C, NewR, NewC, northwest) :-
    NewR is R-1, NewC is C-1.
resulting_position(R, C, NewR, NewC, southeast) :-
    NewR is R+1, NewC is C+1.
resulting_position(R, C, NewR, NewC, southwest) :-
    NewR is R+1, NewC is C-1.

close_direction(north, northeast).
close_direction(northeast, east).
close_direction(east, southeast).
close_direction(southeast, south).
close_direction(south, southwest).
close_direction(southwest, west).
close_direction(west, northwest).
close_direction(northwest, north).

has(agent, _, _) :- fail.
/* 
unsafe_position(_,_) :- fail.
safe_position(R,C) :- \+ unsafe_position(R,C). */

healing_stats(comestible,apple,5).
healing_stats(comestible,orange,10).
healing_stats(comestible,banana,10).
healing_stats(potion,healing,20).


equip_stats(Equipment,Power) :- armor_stats(Equipment,Power).
equip_stats(Equipment,Power) :- weapon_stats(Equipment,Power).

equipment_type(Equipment,weapon) :- weapon_stats(Equipment,_).
equipment_type(Equipment,armor) :- armor_stats(Equipment,_).

armor_stats('red dragon scales',3).
armor_stats('scale mail',4).
armor_stats('elven mithril-coat',5).
armor_stats('dwarvish mithril-coat',6).
armor_stats('red dragon scale mail',7).


weapon_stats('spear',3).
weapon_stats('dwarvish spear',4).
weapon_stats('morning star',5).
weapon_stats('elven broadsword',6).
weapon_stats('trident',7).

enemy_stats('newt',melee,1).
enemy_stats('gecko',melee,2).
enemy_stats('manes',melee,4).
enemy_stats('lemure',melee,5).
enemy_stats('iguana',melee,3).
enemy_stats('dog',melee,5).
enemy_stats('lizard',melee,6).
enemy_stats('rock mole',melee,4).
enemy_stats('jellyfish',melee,5).
enemy_stats('giant beetle',melee,6).
enemy_stats('yeti',melee,7).

is_pickable(gold).
