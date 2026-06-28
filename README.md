# energy-systems-toolkit
Open-source research toolkit for energy systems modelling and data validation. Contains automated scripts for image recognition and ANN-based surrogate modelling for energy demand analysis. 

**IMAGE RECOGNITION**

Tutorial notebooks are provided to illustrate the workflow and facilitate navigation through the project.

DISCLAIMER

The scripts included in this repository have been adapted for public release. The original implementation accesses sensitive input and output data and relies on authenticated APIs requiring user credentials. For privacy and security reasons, these components have been removed or replaced with placeholders.
Consequently, the scripts are intended to document the methodology, demonstrate the workflow, and serve as a starting point for similar implementations, rather than being directly executable without modification.


**ELECTRICITY DEMAND MODELING**

This tool was developed to assess the impact of electric cooking on electricity demand and grid reliability.

The workflow consists of the following steps:

1. Collect survey data on current household electricity consumption in a rural area of Tanzania.
2. Model the introduction of induction cookers as part of a pilot project. Different deployment rates are used to define multiple adoption scenarios.
3. Use SESAM's open-source **RAMP** model to generate stochastic electricity load profiles for each scenario (`stochastic_load_simulation.py`).
4. Train an Artificial Neural Network (ANN) on the RAMP outputs (`ANN_train.py`) and use it to rapidly simulate a much larger set of scenarios.
5. Perform a statistical analysis to estimate the probability of grid overloading and assess the feasibility and optimal scale of a larger deployment (`stats_analysis.py`).

The tool is fully open source and reproducible. By combining RAMP with an AI-based surrogate model, it enables the rapid simulation of a wide range of scenarios while maintaining low computational costs. Although developed for electric cooking assessment, it can be applied to any use case supported by RAMP.


