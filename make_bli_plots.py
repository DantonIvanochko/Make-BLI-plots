import time
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # a great speed enhancer!
import argparse


def main(args):
    
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
        if os.path.isfile(f'{result}.txt') and os.stat(f'{result}.txt').st_size > 0:
            results_dict[result] = pd.read_csv(f'{result}.txt', sep='\t', skiprows=7)
            conc_dict[result] = pd.read_csv(f'{result}.txt', sep='\t', skiprows=0, nrows=1, header=None).iloc[0].tolist()[1:-1]
            raw_str_list = [f"{num:.1e}" for num in conc_dict[result]]
            print(raw_str_list)
            raw_str_list_scinot = []
            for raw_str in raw_str_list:
                raw_str_left = raw_str.split('e-')[0]
                raw_str_right = '-' + raw_str.split('e-')[1].lstrip('0')
                raw_str_list_scinot += [fr"${raw_str_left}×10^{{{raw_str_right}}}$"]
            conc_dict[result] = raw_str_list_scinot
            print(conc_dict[result])
    
    
    
    
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
    
    ### GLOBAL PLOT VARIABLES
    
    nature_style = {
        # General font settings
        "font.size": 6,               
        "font.sans-serif": "Arial",  
        "axes.linewidth": 0.8,        
        "axes.labelsize": 6,          
        "axes.titlesize": 6,         
        'axes.spines.right' : False,
        'axes.spines.top'   : False,
        "legend.fontsize": 5,         
        "legend.frameon": False,      
        "savefig.dpi": int(args.dpi),           
    
    }
    
    plt.style.use(nature_style)
    
    ### CREATE AND SAVE PLOTS 
    
    for plot_num in list_of_plot_numbers:
        start = time.time()
        tmp_df = df_for_plots_dict[f"df_for_plot_{plot_num}"]
        tmp_df.to_csv(f"df_for_plot_{plot_num}.csv", index=False)
        ax = tmp_df.plot(x='Time', y=tmp_df.columns[1::2], lw=1.2, zorder=0, clip_on=False) 
        tmp_df.plot(x='Time', y=tmp_df.columns[2::2],color="black",lw=0.6,zorder=20, clip_on=False, ax=ax)
        
        # Customize legend to only include the first plot's labels
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(
            handles[:len(tmp_df.columns[1::2])],
            labels[:len(tmp_df.columns[1::2])],
            handlelength = 0.7, handletextpad = 0.4, columnspacing = 1,
            loc="center left",        # Position legend on the outside
            bbox_to_anchor=(1, 0.5) # Move it to the right of the plot
        )
        
        # x and y axes
        max_time = tmp_df['Time'].max()
        rounded_max_time = np.ceil(max_time / 10) * 10  # Round up to the nearest 10
        ax.set_xticks(np.linspace(0, rounded_max_time, 5))  # Generate 5 evenly spaced x-axis breaks
        ax.set_xlim(left=0, right=rounded_max_time) 
        y_top = np.round(max((np.ceil(biggest_number / 0.2) * 0.2), 0.4), 1)
                
        if y_top in [1.4, 2.2, 2.6, 1.0, 3.0, 3.4, 3.8]:
            y_top += 0.2
            
        print(f"{y_top=}")
    
        ax.set_ylim(bottom=0, top=y_top)
        
        if np.round(y_top,1) in [0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0]:
            ax.set_yticks(np.linspace(0, y_top, 5))
        elif np.round(y_top,1) in [0.6, 1.8]:
            ax.set_yticks(np.linspace(0, y_top, 4))
        else:
            ax.set_yticks(np.linspace(0, y_top, 3))
        
        ax.set(xlabel="Time (s)", ylabel="Response (nm)")
        plt.locator_params(axis='x', nbins=3)
    
        # make and save fig
        fig = ax.get_figure() 
        
        length_width_list = args.length_width
        fig_length = float(length_width_list[0])
        fig_width  = float(length_width_list[1])
        
        fig.set_size_inches(fig_length / 2.54, fig_width / 2.54)
        fig.savefig(f'plot_{plot_num}.{args.file_type}', bbox_inches='tight', pad_inches = 0)
        
        end = time.time()
        print(f"Time for plot {plot_num}: {end - start:.2f} seconds")
    
    print("\nEND!\n")


if __name__ == "__main__":

    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--length_width", type=float, nargs=2, required=False, default=[4,3], help="Enter length and width as two numbers (units = cm). Default: 4 3 ")
    parser.add_argument("--dpi", type=int, required=False, default=450, help="Enter desired resolution. Default: 450 dpi")
    parser.add_argument("--file_type", type=str, required=False, default='png', help="Enter desired file type. (Options: ) Default: png")
    args = parser.parse_args()

    main(args)
