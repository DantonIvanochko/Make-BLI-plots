import time
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # a great speed enhancer!

### IDENTIFY FILE NAMES AND READ FILES

the_n_list = list(range(13))

for the_n in the_n_list:
    results_test = [f"A{the_n}Results",f"B{the_n}Results",f"C{the_n}Results",f"D{the_n}Results",f"E{the_n}Results",f"F{the_n}Results",f"G{the_n}Results",f"H{the_n}Results"]
    for result_test in results_test:
        if os.path.isfile(f'{result_test}.txt'):
            results = results_test

results_dict = {}
conc_dict = {}

for result in results:
    if os.stat(f'{result}.txt').st_size > 0:
        results_dict[result] = pd.read_csv(f'{result}.txt', sep='\t', skiprows=7)
        conc_dict[result] = pd.read_csv(f'{result}.txt', sep='\t', skiprows=0, nrows=1, header=None).iloc[0].tolist()[1:-1]
        conc_dict[result] = [np.float64(f"{num:.1e}") for num in conc_dict[result]]

### COUNT NUMBER OF PLOTS TO MAKE (ALSO CONFIRM ALL RESULTS FILES HAVE SAME NUMBER OF COLUMNS)

n_cols_list = [len(value.columns)-1 for key, value in results_dict.items()] 

#n_cols_list = [1,1,4] # TEST

for test_n_col in n_cols_list[1:]:
    if test_n_col != n_cols_list[0]:
        print("\n\nFATAL ERROR! # OF COLUMNS UNEQUAL IN Results.txt FILES\n\n")
        exit()

num_of_plots = int(n_cols_list[0]/3)
print(f"{num_of_plots=}")
list_of_plot_numbers = [x+1 for x in list(range(num_of_plots))]
print(f"{list_of_plot_numbers=}")

### ZERO ALL TIME COLUMNS

for key, value in results_dict.items():
    for plot_num in list_of_plot_numbers:
        value[f'Time{plot_num}'] -= value[f'Time{plot_num}'].iloc[0]

### CREATE DATAFRAMES FOR EACH PLOT

df_for_plots_dict = {}

for plot_num in list_of_plot_numbers:
    df_for_plots_dict[f"df_for_plot_{plot_num}"] = pd.DataFrame()
    n = 0
    for key, value in results_dict.items():
        n += 1
        df_for_plots_dict[f"df_for_plot_{plot_num}"]["Time"] = value[f"Time{plot_num}"]
        df_for_plots_dict[f"df_for_plot_{plot_num}"][str(conc_dict[key][plot_num-1])] = value[f"Data{plot_num}"]
        df_for_plots_dict[f"df_for_plot_{plot_num}"][f"Fit{n}"] = value[f"Fit{plot_num}"]

print(f"{df_for_plots_dict=}")

### GET MAX VALUE TO SET Y LIM

biggest_number_df_list = [df_for_plots_dict[f"df_for_plot_{plot_num}"].iloc[:, 1::2] for plot_num in list_of_plot_numbers ]

biggest_number = max([x.to_numpy().max() for x in biggest_number_df_list])

smallest_number = min([x.to_numpy().min() for x in biggest_number_df_list])

print(f'{biggest_number=}')
print(f'{smallest_number=}')

### GLOBAL PLOT VARIABLES

nature_style = {
    # General font settings
    "font.size": 7,               
    #"font.sans-serif": "Arial",  
    "axes.linewidth": 0.8,        
    "axes.labelsize": 7,          
    "axes.titlesize": 7,         
    'axes.spines.right' : False,
    'axes.spines.top'   : False,
    "legend.fontsize": 5,         
    "legend.frameon": False,      
    "savefig.dpi": 450,           

}

plt.style.use(nature_style)

### CREATE AND SAVE PLOTS 

for plot_num in list_of_plot_numbers:
    start = time.time()
    tmp_df = df_for_plots_dict[f"df_for_plot_{plot_num}"]
    ax = tmp_df.plot(x='Time', y=tmp_df.columns[1::2], lw=1.2) 
    tmp_df.plot(x='Time', y=tmp_df.columns[2::2],color="black",lw=0.6,ax=ax)
    
    # Customize legend to only include the first plot's labels
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles[:len(tmp_df.columns[1::2])],
        labels[:len(tmp_df.columns[1::2])],
        loc="center left",        # Position legend on the outside
        bbox_to_anchor=(1, 0.5) # Move it to the right of the plot
    )
    
    # x and y axes
    max_time = tmp_df['Time'].max()
    rounded_max_time = np.ceil(max_time / 10) * 10  # Round up to the nearest 10
    ax.set_xticks(np.linspace(0, rounded_max_time, 5))  # Generate 5 evenly spaced x-axis breaks
    ax.set_xlim(left=0, right=rounded_max_time) 
    y_top = np.ceil(biggest_number / 0.2) * 0.2
    ax.set_ylim(bottom=0, top=y_top)
    ax.set_yticks(np.linspace(0, y_top, 6))
    ax.set(xlabel="Time (s)", ylabel="Response (nm)")

    # make and save fig
    fig = ax.get_figure() 
    fig.set_size_inches(4.5 / 2.54, 3.5 / 2.54)
    fig.savefig(f'plot_{plot_num}.png', bbox_inches='tight')
    
    end = time.time()
    print(f"Time for plot {plot_num}: {end - start:.2f} seconds")

print("\nEND!\n")
