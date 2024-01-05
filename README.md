
# AIFPROJ2023
This repository contains the project GreedMode done by the group money wizards.

Here you can see the repository is divided in to three directories:

* GreedV1 : contains all the files used by the first version of the agent
* GreedV2 : contains all the files used by the second version of the agent
* LEVELGENERATOR : contains the code for the generation of the levels

**To execute** GreedV1 and GreedV2 you can find in each of the two directories a file named `project.ipynb`. **However**, since those notebooks contain functions for the experiments, the output as it is is still suppressed.

**To output/print on terminal**: 
* put the debug flag of `vacuum_experiment`to `True`
* in the `utils.py` file of the interested directory, uncomment the interested `print`and `env.render` from the `perform_action` function.