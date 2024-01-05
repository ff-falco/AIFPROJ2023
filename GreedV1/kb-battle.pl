:- dynamic position/4.
:- dynamic wields_weapon/2.
:- dynamic has/3.

:- dynamic stepping_on/3.

:- dynamic health/1.
:- dynamic health_threshold/1.

:- dynamic arrows/1.
:- dynamic arrows_threshold/1.


:- dynamic unsafe_position/2.
:- dynamic onPlan/1.
:- dynamic plannedMove/1 .

:- dynamic money/1.
:- dynamic money_threshold/1.

:- dynamic battle_begin/0.
:- dynamic weapon_stats/2.

%attack an enemy
%if agent is near an enemy, attack it
%it is assumed the agent will always win against enemies, which is not true
%Requirements:
%   -agent at a given position
%   -enemy at a given position
%   -agent and enemy are near each other (the positions are close)
%after this action we need to replan

action(attack(Direction)) :- position(agent,_,R1,C1), position(enemy,_,R2,C2), is_close(R1,C1,R2,C2), next_step(R1,C1,R2,C2,Direction), battle_begin .

%pick up gold
%if agent is stepping on gold, he has to pick it up
%restricted to gold because other objects could be the ones from the shop
%requirements:
%   -agent is stepping on gold
%   -gold is pickable

action(pick) :- stepping_on(agent,gold,_), is_pickable(gold), battle_begin .

%default behaviour -> if you have a plan, follow it
%Requirements:
%   -agent has a plan and is following it
%   -the plan tells to go in direction Direction

action(followPlan(Direction)) :- onPlan(agent), plannedMove(Direction), battle_begin .

%default behavior -> create a plan if you don't have one and do its first action
%Requirements:
%   - agent has no plan to follow

action(plan) :- \+ onPlan(agent), battle_begin .


% -----------------------------------------------------------------------------------------------

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

% check if the selected direction is safe
safe_direction(R, C, D, Direction) :- resulting_position(R, C, NewR, NewC, D),
                                      ( safe_position(NewR, NewC) -> Direction = D;
                                      % else, get a new close direction
                                      % and check its safety
                                      close_direction(D, ND), safe_direction(R, C, ND, Direction)
                                      ).

% test the different condition for closeness
% two objects are close if they are at 1 cell distance, including diagonals
is_close(R1,C1,R2,C2) :- R1 == R2, (C1 is C2+1; C1 is C2-1).
is_close(R1,C1,R2,C2) :- C1 == C2, (R1 is R2+1; R1 is R2-1).
is_close(R1,C1,R2,C2) :- (R1 is R2+1; R1 is R2-1), (C1 is C2+1; C1 is C2-1).

% a square if unsafe if there is an enemy (there are no traps)
% possibly uncomment
unsafe_position(R, C) :- position(enemy, _, R, C).
%unsafe_position(R,C) :- position(enemy, _, ER, EC), is_close(ER, EC, R, C).

unsafe_position(_,_) :- fail.

safe_position(R,C) :- \+ unsafe_position(R,C).

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


is_pickable(gold).