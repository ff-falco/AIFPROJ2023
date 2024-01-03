:- dynamic position/4.% an has a type, a name , a row and a column it is
:- dynamic wields_weapon/2. % an entity wields a certain weapon
:- dynamic has/3. % an entity has a certain type of item with his name

:- dynamic stepping_on/3.
:- dynamic unsafe_position/2.

:- dynamic health/1.
:- dynamic health_threshold/1.

:- dynamic arrows/1.
:- dynamic arrows_threshold/1.

:- dynamic money/1.
:- dynamic money_threshold/1.
:- dynamic available_to_buy/3. % an item is available to buy, it has a type,a name and a cost
:- dynamic can_buy/3.
:- dynamic wants_to_buy/3.
:- dynamic has_to_pay/0.
:- dynamic corridors/0.
:- dynamic open_spaces/0.
:- dynamic shopping_done/0.
:- dynamic battlefield_start/2.
:- dynamic battle_begin/0.

% SHOP PLANNING PREDICATES
healthy :- health(H),health_threshold(T), H > T.

rich :- money(M),money_threshold(T), M > T.

can_buy(Type,Name,Cost) :- money(M), available_to_buy(Type,Name,Cost),M>=Cost.
%the agent will buy first health if it is not healthy
wants_to_buy(Type,Name,Cost) :- \+ healthy , can_buy(Type,Name,Cost), best_healing_option(Type,Name,Cost).



best_healing_option(Type,Name,Cost):- can_buy(Type,Name,Cost),
                                        healing_stats(Type,Name,Healing),
                                        \+ (
                                            can_buy(OtherType,OtherName,_),
                                            healing_stats(OtherType,OtherName,OtherHealing), 
                                            Healing < OtherHealing
                                        ).

is_beatable(Enemy,Weapon) :- weapon_stats(Weapon,Damage),enemy_stats(Enemy,_,EnemyPower),Damage >= EnemyPower.

wants_to_buy(weapon,WeaponName,WeaponCost):- healthy,can_buy(weapon,WeaponName,WeaponCost),wields_weapon(agent,CurrentWeapon),
                                            (\+ is_beatable(EnemyType,CurrentWeapon)),is_beatable(EnemyType,WeaponName),position(enemy,EnemyName,_,_).

                                            wants_to_buy(weapon,WeaponName,WeaponCost):- healthy,rich,can_buy(weapon,WeaponName,WeaponCost),
                                            \+ (
                                                position(enemy,EnemyName,_,_),
                                            enemy_stats(EnemyName,ranged,_)
                                            ).
wants_to_buy(arrow,ArrowType,Cost):- healthy,(\+ rich),can_buy(arrow,ArrowType,Cost),position(enemy,EnemyName,_,_),
                                     %checks if there is a ranged enemy and the map as corridors
                                     enemy_stats(EnemyName,ranged,_),corridors,
                                     %checks if it has enough arrows
                                     arrows(Arrows),arrows_threshold(ArrowsThreshold),Arrows < ArrowsThreshold,
                                     % it doesn't want to buy another weapon
                                     \+ wants_to_buy(weapon,_,_).

wants_to_buy(armor,ArmorName,ArmorCost) :- healthy,rich, 
                                            \+ wants_to_buy(weapon,_,_),
                                            can_buy(armor,ArmorName,ArmorCost),
                                            position(enemy,EnemyName,_,_),enemy_stats(EnemyName,ranged,_),
                                            \+ (% there isn't any another armor that has better protection
                                            can_buy(armor,OtherArmorName,ArmorCost),
                                            armor_stats(OtherArmorName,OtherProtection),
                                            armor_stats(ArmorName,Protection),
                                            Protection < OtherProtection
                                            ).
                                        % if there is a shopkeeper get away from it
action(avoid_shopkeeper(Direction)) :- position(enemy,'shopkeeper',SKR,SKC),
                                        position(agent,_,AR,AC),
                                        is_close(SKR,SKC,AR,AC),
                                        next_step(AR,AC,SKR,SKC, SD),
                                        close_direction(SD,Direction),
                                        resulting_position(AR,AC, NewR, NewC,Direction),
                                        (position(object,tile,NewR,NewC);position(object,door,NewR,NewC)).
%action(activate_portal):- stepping_on(agent,object,portal).
%action(pick):- stepping_on(agent,ObjType,ObjName),wants_to_buy(ObjType,ObjName,_).


action(buy_item(ObjCost,ObjType,ObjName)):-stepping_on(agent,ObjType,ObjName),wants_to_buy(ObjType,ObjName,ObjCost).  
action(get_to_item(Direction)) :- wants_to_buy(ItemType,ItemName,_),
                                    position(ItemType,ItemName,IR,IC),
                                    position(agent,_,AR,AC),
                                    next_step(AR,AC,IR,IC,Direction),
                                    \+ stepping_on(agent,ItemType,ItemName),
                                    \+ shopping_done.


action(sit) :- battle_begin.


action(get_into_battlefield(east)) :- shopping_done,position(agent,_,AR,AC),\+ battle_begin,
                                      ((position(object,tile,TR,TC),TC is AC+1,TR is AR);(battlefield_start(BR,BC), BR is AR)).

action(get_into_battlefield(south)) :- shopping_done,position(agent,_,AR,AC),\+ battle_begin,
                                        \+ (position(object,tile,TR,TC),TC is AC+1,TR is AR).
can_move(R,C,D) :- position(agent,_,R,C),resulting_position(R, C, NewR, NewC, D),position(Type,_,NewR,NewC),Type \= enemy.
%exit the shop if it doesn't want to buy anything else
action(exit_shop(Direction)) :- position(agent,_,AR,AC),
                                position(object,door,DR,DC),
                                next_step(AR,AC,DR,DC,Direction),
                                resulting_position(AR, AC, NewR, NewC,Direction),
                                (position(object,door,NewR,NewC);position(object,tile,NewR,NewC)),
                                %can_move(AR,AC,Direction),
                                \+ (
                                    position(object,door,OtherDR,OtherDC),
                                    OtherDC<DC
                                ), 
                                %avoid_shopkeeper(AR,AC,Direction,ActualDirection),
                                \+ wants_to_buy(_,_,_),
                                \+ shopping_done,
                                \+ battle_begin.
%if no other action is avaialable sit to make a turn pass
action(sit) :- true.
% -----------------------------------------------------------------------------------------------

% test the different condition for closeness
% two objects are close if they are at 1 cell distance, including diagonals
is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+1; C1 is C2-1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+1; R1 is R2-1).
is_close(R1,C1,R2,C2) :- (R1 is R2+1; R1 is R2-1), (C1 is C2+1; C1 is C2-1).

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

/* % check if the selected direction is safe
safe_direction(R, C, D, Direction) :- resulting_position(R, C, NewR, NewC, D),
                                      ( safe_position(NewR, NewC) -> Direction = D;
                                      % else, get a new close direction
                                      % and check its safety
                                      close_direction(D, ND), safe_direction(R, C, ND, Direction)
                                      ).

% a square if unsafe if there is a trap or an enemy
unsafe_position(R, C) :- position(trap, _, R, C).
unsafe_position(R, C) :- position(enemy, _, R, C).
unsafe_position(R,C) :- position(enemy, _, ER, EC), is_close(ER, EC, R, C). */

%


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
healing_stats(comestible,banana,15).
healing_stats(potion,healing,5).

armor_stats('chain mail',3).
armor_stats('bronze plate mail',4).
armor_stats('dwarvish mithril-coat',5).
armor_stats('elven mithril-coat',6).
armor_stats('chain mail',7).


weapon_stats('bullwhip',3).
weapon_stats('stiletto',4).
weapon_stats('long sword',5).
weapon_stats('morning star',6).
weapon_stats('katana',7).

enemy_stats('kobold',melee,1).
enemy_stats('stone giant',melee,4).