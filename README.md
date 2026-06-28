# energy-systems-toolkit
Open-source research toolkit for energy systems modelling and data validation. Contains automated scripts for image recognition and ANN-based surrogate modelling for energy demand analysis. 

**IMAGE RECOGNITION**

Tutorials are provided to facilitate navigation of the workflows.
Please note that the scripts have been designed to access sensitive data that is hidden in input and output files. Furthermore, they utilise username and password authentication to access APIs. Therefore, their purpose here is exclusively to explain and inspire, as well as to organise the workflow

**ELECTRICITY DEMAND MODELING**

This tool was developed to assess the impact of electric cooking on electricity demand and grid reliability.

The workflow consists of the following steps:

1. Collect survey data on current household electricity consumption in a rural area of Tanzania.
2. Model the introduction of induction cookers as part of a pilot project. Different deployment rates are used to define multiple adoption scenarios.
3. Use SESAM's open-source **RAMP** model to generate stochastic electricity load profiles for each scenario (`stochastic_load_simulation.py`).
4. Train an Artificial Neural Network (ANN) on the RAMP outputs (`ANN_train.py`) and use it to rapidly simulate a much larger set of scenarios.
5. Perform a statistical analysis to estimate the probability of grid overloading and assess the feasibility and optimal scale of a larger deployment (`stats_analysis.py`).

The tool is fully open source and reproducible. By combining RAMP with an AI-based surrogate model, it enables the rapid simulation of a wide range of scenarios while maintaining low computational costs. Although developed for electric cooking assessment, it can be applied to any use case supported by RAMP.


