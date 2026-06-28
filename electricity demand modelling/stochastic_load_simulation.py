import pandas as pd
import os
from ramp.core.core import User, UseCase
import numpy as np

def run_sensitivity_analysis():
    # 1. Setup Parameters
    start_val = 920
    stop_val = 1000
    step = 20
    num_days = 31  # Number of days to simulate for peak extraction
    
    # This DataFrame will store 100 rows (peaks) for each cooker count (columns)
    Ramp_peaks_df = pd.DataFrame()

    folder_name = "Simulation_Results"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # 2. Start the Loop
    for n_cookers in range(start_val, stop_val + 1, step):
        print(f"--- Simulating {n_cookers} induction cookers for {num_days} days ---")
        
        # Define User List inside the loop for a clean state each time
        User_list = []

        # Create new user classes
        IND = User(user_name="generic households", num_users=n_cookers, user_preference=3)
        User_list.append(IND)

        HI = User(user_name="high income", num_users=350, user_preference=3)
        User_list.append(HI)

        HMI = User("higher middle income", 1050, 3)
        User_list.append(HMI)

        LMI = User("lower middle income", 1750, 3)
        User_list.append(LMI)

        LI = User("low income", 2100, 3)
        User_list.append(LI)

        #Hospital = User("hospital", 1)
        #User_list.append(Hospital)

        School = User("school", 4)
        User_list.append(School)

        Public_lighting = User("public lighting", 1)
        User_list.append(Public_lighting)

        Church = User("church", 4) #
        User_list.append(Church)

        # Create new appliances

        # Church
        Ch_indoor_bulb = Church.add_appliance(
            number=10,
            power=26,
            num_windows=1,
            func_time=210,
            time_fraction_random_variability=0.2,
            func_cycle=60,
            fixed="yes",
            flat="yes",
            name="indoor_bulb",
        )
        Ch_indoor_bulb.windows(window_1=[1200, 1440], window_2=[0, 0], random_var_w=0.1)

        Ch_outdoor_bulb = Church.add_appliance(
            7, 26, 1, 150, 0.2, 60, "yes", flat="yes", name="outdoor_bulb"
        )
        Ch_outdoor_bulb.windows([1200, 1440], [0, 0], 0.1)

        Ch_speaker = Church.add_appliance(1, 100, 1, 150, 0.2, 60, name="speaker")
        Ch_speaker.windows([1200, 1350], [0, 0], 0.1)

        # Public lighting
        Pub_lights = Public_lighting.add_appliance(
            12, 40, 2, 310, 0.1, 300, "yes", flat="yes", name="lights"
        )
        Pub_lights.windows([0, 336], [1110, 1440], 0.2)

        Pub_lights_2 = Public_lighting.add_appliance(
            25, 150, 2, 310, 0.1, 300, "yes", flat="yes", name="lights2"
        )
        Pub_lights_2.windows([0, 336], [1110, 1440], 0.2)


        # Induction
        number_of_induction_cookers = IND.num_users

        IND_induction = IND.add_appliance(
            number=1,
            power=1200,
            num_windows=3,
            func_time=150,
            time_fraction_random_variability=0.4,
            func_cycle=15,
            thermal_p_var=0.6,
            name="induction cooker",
        )
        IND_induction.windows(window_1=[420, 540],
                          window_2=[720, 840],
                          window_3=[1140, 1320],
                          random_var_w=0.4)


        # High-Income
        HI_indoor_bulb = HI.add_appliance(8, 7, 1, 300, 0.2, 10, name="indoor_bulb")
        HI_indoor_bulb.windows([1080, 1440])

        HI_outdoor_bulb = HI.add_appliance(5, 13, 2, 600, 0.2, 30, name="outdoor_bulb")
        HI_outdoor_bulb.windows([0, 360], [1140, 1440], 0.35)

        HI_TV = HI.add_appliance(1, 60, 1, 120, 0.1, 10, name="TV")
        HI_TV.windows([1140, 1380])

        HI_Radio = HI.add_appliance(1, 36, 1, 240, 0.6, 20, name="radio")
        HI_Radio.windows([420, 1080])

        HI_Iron = HI.add_appliance(1, 750, 2, 60, 0.3, 10, occasional_use=0.33, name="iron")
        HI_Iron.windows([420, 600], [840,1020], 0.35)
        """
        HI_DVD = HI.add_appliance(1, 8, 3, 60, 0.1, 5, name="DVD")
        HI_DVD.windows([720, 900], [1170, 1440], 0.35, [0, 60])

        HI_Antenna = HI.add_appliance(1, 8, 3, 120, 0.1, 5, name="antenna")
        HI_Antenna.windows([720, 900], [1170, 1440], 0.35, [0, 60])
        """

        HI_Phone_charger = HI.add_appliance(4, 2, 2, 180, 0.2, 30, name="phone_charger")
        HI_Phone_charger.windows([1080, 1440], [0, 360], 0.35)

        HI_Kettle = HI.add_appliance(1, 800, 1, 30, 0.2, 5, occasional_use=0.33, name="kettle")
        HI_Kettle.windows([420, 480])

        HI_Freezer = HI.add_appliance(1, 200, 1, 1440, 0, 30, flat="yes", pref_index=3, name="freezer")
        HI_Freezer.windows([0, 1440], [0, 0])
        HI_Freezer.specific_cycle_1(200, 20, 5, 10)
        HI_Freezer.specific_cycle_2(200, 15, 5, 15)
        HI_Freezer.specific_cycle_3(200, 10, 5, 20)
        HI_Freezer.cycle_behaviour(
            [480, 1200], [0, 0], [300, 479], [0, 0], [0, 299], [1201, 1440]
        )

        """ not present
        HI_Freezer2 = HI.add_appliance(1, 200, 1, 1440, 0, 30, "yes", 3, name="freezer2")
        HI_Freezer2.windows([0, 1440], [0, 0])
        HI_Freezer2.specific_cycle_1(200, 20, 5, 10)
        HI_Freezer2.specific_cycle_2(200, 15, 5, 15)
        HI_Freezer2.specific_cycle_3(200, 10, 5, 20)
        HI_Freezer2.cycle_behaviour(
            [480, 1200], [0, 0], [300, 479], [0, 0], [0, 299], [1201, 1440]
        )
        """

        # Higher-Middle Income
        HMI_indoor_bulb = HMI.add_appliance(6, 7, 1, 300, 0.2, 10, name="indoor_bulb")
        HMI_indoor_bulb.windows([1080, 1440])

        HMI_outdoor_bulb = HMI.add_appliance(4, 13, 2, 600, 0.2, 30, name="outdoor_bulb")
        HMI_outdoor_bulb.windows([0, 360], [1140, 1440], 0.35)

        HMI_TV = HMI.add_appliance(1, 60, 1, 120, 0.1, 10, name="TV")
        HMI_TV.windows([1140, 1380])

        HMI_Radio = HMI.add_appliance(1, 36, 1, 240, 0.6, 20, name="radio")
        HMI_Radio.windows([420, 1080])

        HMI_Iron = HMI.add_appliance(1, 750, 1, 60, 0.3, 10, occasional_use=0.33, name="iron")
        HMI_Iron.windows([420, 600])

        HMI_Phone_charger = HMI.add_appliance(3, 2, 2, 180, 0.2, 30, name="phone_charger")
        HMI_Phone_charger.windows([1080, 1440], [0, 360], 0.35)

        """
        HMI_Freezer = HMI.add_appliance(1, 200, 1, 1440, 0, 30, "yes", 3, name="freezer")
        HMI_Freezer.windows([0, 1440], [0, 0])
        HMI_Freezer.specific_cycle_1(200, 20, 5, 10)
        HMI_Freezer.specific_cycle_2(200, 15, 5, 15)
        HMI_Freezer.specific_cycle_3(200, 10, 5, 20)
        HMI_Freezer.cycle_behaviour(
            [480, 1200], [0, 0], [300, 479], [0, 0], [0, 299], [1201, 1440]
        )
        """

        # Lower-Middle Income
        LMI_indoor_bulb = LMI.add_appliance(4, 7, 2, 180, 0.2, 10, name="indoor_bulb")
        LMI_indoor_bulb.windows([1080, 1440], [300, 420], 0.35)

        LMI_outdoor_bulb = LMI.add_appliance(3, 13, 2, 600, 0.2, 10, name="outdoor_bulb")
        LMI_outdoor_bulb.windows([0, 360], [1140, 1440], 0.35)

        LMI_TV = LMI.add_appliance(1, 60, 1, 120, 0.1, 10, name="TV")
        LMI_TV.windows([1140, 1380])

        LMI_Radio = LMI.add_appliance(1, 36, 1, 240, 0.6, 20, name="radio")
        LMI_Radio.windows([420, 1080])

        LMI_Iron = LMI.add_appliance(1, 750, 1, 30, 0.3, 5, occasional_use=0.33, name="iron")
        LMI_Iron.windows([420, 600])

        LMI_Phone_charger = LMI.add_appliance(2, 2, 2, 180, 0.2, 30, name="phone_charger")
        LMI_Phone_charger.windows([480, 660], [1080, 1440], 0.35)

        # Low Income
        LI_indoor_bulb = LI.add_appliance(2, 7, 2, 300, 0.2, 10, name="indoor_bulb")
        LI_indoor_bulb.windows([1080, 1440], [300, 420], 0.35)

        LI_outdoor_bulb = LI.add_appliance(2, 13, 2, 600, 0.2, 10, name="outdoor_bulb")
        LI_outdoor_bulb.windows([0, 360], [1140, 1440], 0.35)

        LI_Radio = LI.add_appliance(1, 36, 1, 300, 0.6, 15, name="radio")
        LI_Radio.windows([420, 1380])

        LI_Phone_charger = LI.add_appliance(1, 2, 1, 120, 0.2, 30, name="phone_charger")
        LI_Phone_charger.windows([1080, 1440])

        """ not present
        # Hospital
        Ho_indoor_bulb = Hospital.add_appliance(12, 7, 2, 690, 0.2, 10, name="indoor_bulb")
        Ho_indoor_bulb.windows([480, 720], [870, 1440], 0.35)

        Ho_outdoor_bulb = Hospital.add_appliance(1, 13, 2, 690, 0.2, 10, name="outdoor_bulb")
        Ho_outdoor_bulb.windows([0, 330], [1050, 1440], 0.35)

        Ho_Phone_charger = Hospital.add_appliance(8, 2, 2, 300, 0.2, 5, name="phone_charger")
        Ho_Phone_charger.windows([480, 720], [900, 1440], 0.35)

        Ho_Fridge = Hospital.add_appliance(1, 150, 1, 1440, 0, 30, "yes", 3, name="fridge")
        Ho_Fridge.windows([0, 1440], [0, 0])
        Ho_Fridge.specific_cycle_1(150, 20, 5, 10)
        Ho_Fridge.specific_cycle_2(150, 15, 5, 15)
        Ho_Fridge.specific_cycle_3(150, 10, 5, 20)
        Ho_Fridge.cycle_behaviour(
            [580, 1200], [0, 0], [420, 579], [0, 0], [0, 419], [1201, 1440]
        )

        Ho_Fridge2 = Hospital.add_appliance(1, 150, 1, 1440, 0, 30, "yes", 3, name="fridge2")
        Ho_Fridge2.windows([0, 1440], [0, 0])
        Ho_Fridge2.specific_cycle_1(150, 20, 5, 10)
        Ho_Fridge2.specific_cycle_2(150, 15, 5, 15)
        Ho_Fridge2.specific_cycle_3(150, 10, 5, 20)
        Ho_Fridge2.cycle_behaviour(
            [580, 1200], [0, 0], [420, 579], [0, 0], [0, 419], [1201, 1440]
        )

        Ho_Fridge3 = Hospital.add_appliance(1, 150, 1, 1440, 0.1, 30, "yes", 3, name="fridge3")
        Ho_Fridge3.windows([0, 1440], [0, 0])
        Ho_Fridge3.specific_cycle_1(150, 20, 5, 10)
        Ho_Fridge3.specific_cycle_2(150, 15, 5, 15)
        Ho_Fridge3.specific_cycle_3(150, 10, 5, 20)
        Ho_Fridge3.cycle_behaviour(
            [580, 1200], [0, 0], [420, 579], [0, 0], [0, 419], [1201, 1440]
        )

        Ho_PC = Hospital.add_appliance(2, 50, 2, 300, 0.1, 10, name="PC")
        Ho_PC.windows([480, 720], [1050, 1440], 0.35)

        Ho_Mixer = Hospital.add_appliance(
            1, 50, 2, 60, 0.1, 1, occasional_use=0.33, name="mixer"
        )
        Ho_Mixer.windows([480, 720], [1050, 1440], 0.35)
        """

        # School
        S_indoor_bulb = School.add_appliance(20, 7, 1, 60, 0.2, 10, name="indoor_bulb")
        S_indoor_bulb.windows([1020, 1080], [0, 0], 0.35)

        S_outdoor_bulb = School.add_appliance(20, 13, 1, 60, 0.2, 10, name="outdoor_bulb")
        S_outdoor_bulb.windows([1020, 1080], [0, 0], 0.35)

        S_Phone_charger = School.add_appliance(5, 2, 2, 180, 0.2, 5, name="phone_charger")
        S_Phone_charger.windows([510, 750], [810, 1080], 0.35)

        S_PC = School.add_appliance(18, 50, 2, 210, 0.1, 10, name="PC")
        S_PC.windows([510, 750], [810, 1080], 0.35)

        S_Printer = School.add_appliance(1, 20, 2, 30, 0.1, 5, name="printer")
        S_Printer.windows([510, 750], [810, 1080], 0.35)

        """ not present
        S_Freezer = School.add_appliance(1, 200, 1, 1440, 0, 30, "yes", 3, name="freezer")
        S_Freezer.windows([0, 1440])
        S_Freezer.specific_cycle_1(200, 20, 5, 10)
        S_Freezer.specific_cycle_2(200, 15, 5, 15)
        S_Freezer.specific_cycle_3(200, 10, 5, 20)
        S_Freezer.cycle_behaviour(
            [580, 1200], [0, 0], [510, 579], [0, 0], [0, 509], [1201, 1440]
        )
        """

        S_TV = School.add_appliance(1, 60, 2, 120, 0.1, 5, occasional_use=0.5, name="TV")
        S_TV.windows([510, 750], [810, 1080], 0.35)

        S_DVD = School.add_appliance(1, 8, 2, 120, 0.1, 5, occasional_use=0.5, name="DVD")
        S_DVD.windows([510, 750], [810, 1080], 0.35)

        S_Stereo = School.add_appliance(
            1, 150, 2, 90, 0.1, 5, occasional_use=0.33, name="stereo"
        )
        S_Stereo.windows([510, 750], [810, 1080], 0.35)

        # 3. Run RAMP UseCase
        uc = UseCase(
            users=User_list, 
            date_start="2026-01-01",
            parallel_processing=True)
        uc.initialize(num_days=num_days, peak_enlarge=0.15)

        # Generate 31 daily load profiles
        profiles_list = uc.generate_daily_load_profiles_parallel(days=num_days, flat=False)
        grid_losses = 0.083  # 8.3% grid losses

        # 4. Extract Peaks for the 31 days
        # profiles_list is a list of 31 arrays (each 1440 minutes long)
        df_iteration = pd.DataFrame(profiles_list) 
        
        # Calculate max of each row (each day's peak)
        daily_peaks = df_iteration.max(axis=1)*(1+grid_losses)
        
        # Add these 31 peaks as a new column named after the cooker count
        Ramp_peaks_df[f"{n_cookers}"] = daily_peaks.values

    # 5. Export results to match your CSV format
    output_path = os.path.join(folder_name, "RAMP_peaks_matrix.csv")
    Ramp_peaks_df.to_csv(output_path, index=False)
    
    print(f"\nSimulation complete. Dataframe shape: {Ramp_peaks_df.shape}")
    print(f"Results saved to: {output_path}")

    # post-processing
    from ramp.post_process import post_process as pp

    Profiles_avg, Profiles_list_kW, Profiles_series = pp.Profile_formatting(
        profiles_list
    )
    pp.Profile_series_plot(
        Profiles_series
    )  # by default, profiles are plotted as a series
    if (
        len(profiles_list) > 1
    ):  # if more than one daily profile is generated, also cloud plots are shown
        pp.Profile_cloud_plot(profiles_list, Profiles_avg)
    
    return Ramp_peaks_df

if __name__ == "__main__":
    final_peaks = run_sensitivity_analysis()
