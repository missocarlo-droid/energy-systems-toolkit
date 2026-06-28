# energy-systems-toolkit
Open-source research toolkit for energy systems modelling and data validation. Contains automated scripts for image recognition and ANN-based surrogate modelling for energy demand analysis. 

**IMAGE RECOGNITION**

Tutorials to navigate the workflows are provided.
Disclaimer: the scripts access sensitive data hidden in input/output files. Moreover they call APIs through username and password. Therefore their purpose here is only explicative and inspirational, besides organizational.

**ELECTRICITY DEMAND MODELING**

1. Collected survey data about current electricity consumption in a rural area in Tanzania.
2. Modelled introduction of new induction cookers in the system (pilot project). Different deployment rates correspond to  different scenarios)
3. Handled SESAM's RAMP Open Source model to simulate stochastically electricity load profiles in X scenarios  (stchastic load simulation.py)
4. Trained neural network (ANN_train.py) on RAMP outputs and simulated 5X scenarios.
5. Performed statistical analysis of the risk of tripping the grid and assessed feasibility and size of a scale-up project (stats_analysis.py)



