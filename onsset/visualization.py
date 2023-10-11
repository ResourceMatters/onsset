import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import seaborn as sns

techs = ["Grid", "SA_Diesel", "SA_PV", "MG_Diesel", "MG_PV", "MG_Wind", "MG_Hydro"]
colors = ['#73B2FF', '#EDD100', '#EDA800', '#1F6600', '#98E600', '#70A800', '#1FA800']
end_year = 2030
SET_X_DEG = 'X_deg'
SET_Y_DEG = 'Y_deg'
SET_ELEC_FINAL_CODE = 'FinalElecCode'
SET_NEW_CAPACITY = 'NewCapacity'  # Capacity in kW
SET_INVESTMENT_COST = 'InvestmentCost'  # The investment cost in USD
SET_MIN_OVERALL = 'MinimumOverall'  # Same as above, but including grid
SET_NEW_CONNECTIONS = 'NewConnections'  # Number of new people with electricity connections
SET_POP = 'Pop'

def init_vis_map(results_map):
    ### Map results visualization tab

    frame_results = tk.LabelFrame(results_map, text='GIS results')
    frame_results.place(relheight=0.9, relwidth=0.9, relx=0.05, rely=0.05)
    frame_results['bg'] = '#FFFFFF'

    # Load results button
    button_viz = tk.Button(results_map, text="Visualize results map", command=lambda: vis_map(frame_results))
    button_viz.place(relwidth=0.2, rely=0.95, relx=0.4)

def vis_map(frame_results, df):

    # filename = filedialog.askopenfilename(title="Open the results file")
    # df = pd.read_csv(filename)

    figure1 = plt.figure(figsize=(9, 9))
    figure1.add_subplot(111)

    # plt.figure(figsize=(9, 9))
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 3, SET_X_DEG],
             df.loc[df['FinalElecCode{}'.format(end_year)] == 3, SET_Y_DEG], color='#EDA800',
             marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 2, SET_X_DEG],
             df.loc[df['FinalElecCode{}'.format(end_year)] == 2, SET_Y_DEG], color='#EDD100',
             marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 4, SET_X_DEG],
             df.loc[df['FinalElecCode{}'.format(end_year)] == 4, SET_Y_DEG], color='#1F6600',
             marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 5, SET_X_DEG],
             df.loc[df['FinalElecCode{}'.format(end_year)] == 5, SET_Y_DEG], color='#98E600',
             marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 6, SET_X_DEG],
             df.loc[df['FinalElecCode{}'.format(end_year)] == 6, SET_Y_DEG], color='#70A800',
             marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 7, SET_X_DEG],
             df.loc[df['FinalElecCode{}'.format(end_year)] == 7, SET_Y_DEG], color='#1FA800',
             marker=',', linestyle='none')
    plt.plot(df.loc[df['FinalElecCode{}'.format(end_year)] == 1, SET_X_DEG],
             df.loc[df['FinalElecCode{}'.format(end_year)] == 1, SET_Y_DEG], color='#73B2FF',
             marker=',', linestyle='none')
    if df[SET_X_DEG].max() - df[SET_X_DEG].min() > df[SET_Y_DEG].max() - df[
        SET_Y_DEG].min():
        plt.xlim(df[SET_X_DEG].min() - 1, df[SET_X_DEG].max() + 1)
        plt.ylim((df[SET_Y_DEG].min() + df[SET_Y_DEG].max()) / 2 - 0.5 * abs(
            df[SET_X_DEG].max() - df[SET_X_DEG].min()) - 1,
                 (df[SET_Y_DEG].min() + df[SET_Y_DEG].max()) / 2 + 0.5 * abs(
                     df[SET_X_DEG].max() - df[SET_X_DEG].min()) + 1)
    else:
        plt.xlim((df[SET_X_DEG].min() + df[SET_X_DEG].max()) / 2 - 0.5 * abs(
            df[SET_Y_DEG].max() - df[SET_Y_DEG].min()) - 1,
                 (df[SET_X_DEG].min() + df[SET_X_DEG].max()) / 2 + 0.5 * abs(
                     df[SET_Y_DEG].max() - df[SET_Y_DEG].min()) + 1)
        plt.ylim(df[SET_Y_DEG].min() - 1, df[SET_Y_DEG].max() + 1)

    # plt.figure(figsize=(30, 30))

    canvas = FigureCanvasTkAgg(figure1, master=frame_results)
    canvas.get_tk_widget().pack()

def init_vis_charts(results_tables):
    ### Charts results visualization tab

    frame_charts = tk.LabelFrame(results_tables, text='Results charts')
    frame_charts.place(relheight=0.9, relwidth=0.9, relx=0.05, rely=0.05)
    frame_charts['bg'] = '#FFFFFF'

    # Load results button
    button_charts_viz = tk.Button(results_tables, text="Visualize result charts",
                                  command=lambda: vis_charts(frame_charts))
    button_charts_viz.place(relwidth=0.2, rely=0.95, relx=0.4)

def vis_charts(frame_charts, df, intermediate_year, end_year):

    yearsofanalysis = [intermediate_year, end_year]

    elements = []
    for year in yearsofanalysis:
        elements.append("Population{}".format(year))
        elements.append("NewConnections{}".format(year))
        elements.append("Capacity{}".format(year))
        elements.append("Investment{}".format(year))

    sumtechs = []
    for year in yearsofanalysis:
        sumtechs.extend(["Population{}".format(year) + t for t in techs])
        sumtechs.extend(["NewConnections{}".format(year) + t for t in techs])
        sumtechs.extend(["Capacity{}".format(year) + t for t in techs])
        sumtechs.extend(["Investment{}".format(year) + t for t in techs])

    summary = pd.Series(index=sumtechs, name='country')

    for year in yearsofanalysis:
        for t in techs:
            summary.loc["Population{}".format(year) + t] = df.loc[
                (df[SET_MIN_OVERALL + '{}'.format(year)] == t + '{}'.format(year)), SET_POP + '{}'.format(year)].sum()
            summary.loc["NewConnections{}".format(year) + t] = df.loc[
                (df[SET_MIN_OVERALL + '{}'.format(year)] == t + '{}'.format(year)) &
                (df[SET_ELEC_FINAL_CODE + '{}'.format(year)] < 99), SET_NEW_CONNECTIONS + '{}'.format(year)].sum()
            summary.loc["Capacity{}".format(year) + t] = df.loc[(df[SET_MIN_OVERALL + '{}'.format
                (year)] == t + '{}'.format(year)) &
                                                                (df[SET_ELEC_FINAL_CODE + '{}'.format
                                                                    (year)] < 99), SET_NEW_CAPACITY + '{}'.format
                (year)].sum() / 1000
            summary.loc["Investment{}".format(year) + t] = df.loc[(df[SET_MIN_OVERALL + '{}'.format(year)] == t + '{}'.format(year)) & (df[SET_ELEC_FINAL_CODE + '{}'.format
                                                                                              (year)] < 99), SET_INVESTMENT_COST + '{}'.format(year)].sum()

    index = techs + ['Total']
    columns = []
    for year in yearsofanalysis:
        columns.append("Population{}".format(year))
        columns.append("NewConnections{}".format(year))
        columns.append("Capacity{} (MW)".format(year))
        columns.append("Investment{} (million USD)".format(year))

    summary_table = pd.DataFrame(index=index, columns=columns)

    summary_table[columns[0]] = summary.iloc[0:7].astype(int).tolist() + [int(summary.iloc[0:7].sum())]
    summary_table[columns[1]] = summary.iloc[7:14].astype(int).tolist() + [int(summary.iloc[7:14].sum())]
    summary_table[columns[2]] = summary.iloc[14:21].astype(int).tolist() + [int(summary.iloc[14:21].sum())]
    summary_table[columns[3]] = [round(x / 1e4) / 1e2 for x in summary.iloc[21:28].astype(float).tolist()] + [
        round(summary.iloc[21:28].sum() / 1e4) / 1e2]
    summary_table[columns[4]] = summary.iloc[28:35].astype(int).tolist() + [int(summary.iloc[28:35].sum())]
    summary_table[columns[5]] = summary.iloc[35:42].astype(int).tolist() + [int(summary.iloc[35:42].sum())]
    summary_table[columns[6]] = summary.iloc[42:49].astype(int).tolist() + [int(summary.iloc[42:49].sum())]
    summary_table[columns[7]] = [round(x / 1e4) / 1e2 for x in summary.iloc[49:56].astype(float).tolist()] + [
        round(summary.iloc[49:56].sum() / 1e4) / 1e2]

    techs_colors = dict(zip(techs, colors))

    # figure1 = plt.figure(figsize=(9, 9))

    summary_plot = summary_table.drop(labels='Total', axis=0)
    fig_size = [15, 15]
    plt.rcParams["figure.figsize"] = fig_size
    f, axarr = plt.subplots(2, 2)
    fig_size = [15, 15]
    font_size = 5
    plt.rcParams["figure.figsize"] = fig_size

    sns.barplot(x=summary_plot.index.tolist(), y=columns[4], data=summary_plot, ax=axarr[0, 0], palette=colors)
    axarr[0, 0].set_ylabel(columns[4], fontsize=2 * font_size)
    axarr[0, 0].tick_params(labelsize=font_size)
    sns.barplot(x=summary_plot.index.tolist(), y=columns[5], data=summary_plot, ax=axarr[0, 1], palette=colors)
    axarr[0, 1].set_ylabel(columns[5], fontsize=2 * font_size)
    axarr[0, 1].tick_params(labelsize=font_size)
    sns.barplot(x=summary_plot.index.tolist(), y=columns[6], data=summary_plot, ax=axarr[1, 0], palette=colors)
    axarr[1, 0].set_ylabel(columns[6], fontsize=2 * font_size)
    axarr[1, 0].tick_params(labelsize=font_size)
    sns.barplot(x=summary_plot.index.tolist(), y=columns[7], data=summary_plot, ax=axarr[1, 1], palette=colors)
    axarr[1, 1].set_ylabel(columns[7], fontsize=2 * font_size)
    axarr[1, 1].tick_params(labelsize=font_size)

    canvas = FigureCanvasTkAgg(f, master=frame_charts)
    canvas.get_tk_widget().pack()
