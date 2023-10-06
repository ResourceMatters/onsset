from CTkMessagebox import CTkMessagebox
from onsset.onsset import *
import onsset.onsset_gis as onsset_gis
from customtkinter import filedialog


def csv_File_dialog():
    filename = filedialog.askopenfilename(title="Select the csv file with GIS data")
    return filename


def load_csv_data():
    file_path = csv_File_dialog()
    try:
        csv_filename = r"{}".format(file_path)
        onsseter = SettlementProcessor(csv_filename)
        return onsseter
    except ValueError:
        CTkMessagebox(title='Error', message="Could not load file", icon="warning")
        return None
    except FileNotFoundError:
        CTkMessagebox(title='Error', message=f"Could not find the file {file_path}", icon="warning")
        return None


def calibrate(self):
    global calib_df
    CTkMessagebox(title='OnSSET', message='Open the file with extracted GIS data')
    onsseter = load_csv_data()

    start_year = int(self.e1.get())
    start_year_pop = float(self.e2.get())
    urban_ratio_start_year = float(self.e3.get())
    elec_rate = float(self.e4.get())
    elec_rate_urban = float(self.e5.get())
    elec_rate_rural = float(self.e6.get())
    min_night_light = float(self.e14.get())
    min_pop = float(self.e15.get())
    max_transformer_dist = float(self.e16.get())
    max_mv_dist = float(self.e17.get())
    max_hv_dist = float(self.e18.get())
    hh_size_urban = float(self.e19.get())
    hh_size_rural = float(self.e20.get())

    # RUN_PARAM: these are the annual household electricity targets
    tier_1 = 38.7  # 38.7 refers to kWh/household/year. It is the mean value between Tier 1 and Tier 2
    tier_2 = 219
    tier_3 = 803
    tier_4 = 2117
    tier_5 = 2993

    onsseter.prepare_wtf_tier_columns(hh_size_rural, hh_size_urban,
                                      tier_1, tier_2, tier_3, tier_4, tier_5)

    onsseter.condition_df()

    onsseter.df['GridPenalty'] = onsseter.grid_penalties(onsseter.df)

    onsseter.df['WindCF'] = onsseter.calc_wind_cfs()

    onsseter.calibrate_current_pop_and_urban(start_year_pop, urban_ratio_start_year)

    elec_modelled, rural_elec_ratio, urban_elec_ratio = \
        onsseter.elec_current_and_future(elec_rate, elec_rate_urban, elec_rate_rural, start_year,
                                         min_night_lights=min_night_light,
                                         min_pop=min_pop,
                                         max_transformer_dist=max_transformer_dist,
                                         max_mv_dist=max_mv_dist,
                                         max_hv_dist=max_hv_dist)
    self.button_save_calib.configure(state='normal')
    self.calib_df = onsseter.df

    CTkMessagebox(title='OnSSET', message='Calibration completed! The calibrated '
                                          'electrification rate was {}'.format(round(elec_modelled, 2)))

    return onsseter.df


def run_scenario(self, calibrated_csv_path):
    settlements_in_csv = calibrated_csv_path
    onsseter = SettlementProcessor(settlements_in_csv)

    rural_tier_text = self.rural_tier.get()
    urban_tier_text = self.urban_tier.get()
    start_year = int(self.start_year.get())
    intermediate_year = int(self.intermediate_year.get())
    end_year = int(self.end_year.get())
    intermediate_electrification_target = float(self.intermediate_elec_target.get())
    end_year_electrification_rate_target = float(self.elec_target.get())
    disc_rate = float(self.discount_rate.get())
    pop_future = float(self.pop_end_year.get())
    urban_future = float(self.urban_end_year.get())

    tier_dict = {'Tier 1': 1,
                 'Tier 2': 2,
                 'Tier 3': 3,
                 'Tier 4': 4,
                 'Tier 5': 5,
                 'Custom': 6}

    rural_tier = tier_dict[rural_tier_text]
    urban_tier = tier_dict[urban_tier_text]

    onsseter.df['HealthDemand'] = 0
    onsseter.df['EducationDemand'] = 0
    onsseter.df['AgriDemand'] = 0
    onsseter.df['CommercialDemand'] = 0
    onsseter.df['HeavyIndustryDemand'] = 0

    # ToDo
    gis_grid_extension = False
    social_productive_demand = 2
    industrial_demand = 2
    num_people_per_hh_rural = 5
    num_people_per_hh_urban = 5
    max_grid_extension_dist = 50
    # West grid specifications
    auto_intensification_ouest = 0
    annual_new_grid_connections_limit_ouest = {intermediate_year: 999999999,
                                               end_year: 999999999}
    annual_grid_cap_gen_limit_ouest = {intermediate_year: 999999999,
                                       end_year: 999999999}

    grid_generation_cost_ouest = 0.07
    grid_power_plants_capital_cost_ouest = 2000
    grid_losses_ouest = 0.08

    # South grid specifications
    auto_intensification_sud = 0
    annual_new_grid_connections_limit_sud = {intermediate_year: 999999999,
                                             end_year: 999999999}
    annual_grid_cap_gen_limit_sud = {intermediate_year: 999999999,
                                     end_year: 999999999}

    grid_generation_cost_sud = 0.07
    grid_power_plants_capital_cost_sud = 2000
    grid_losses_sud = 0.08

    # East grid specifications
    auto_intensification_est = 0
    annual_new_grid_connections_limit_est = {intermediate_year: 999999999,
                                             end_year: 999999999}
    annual_grid_cap_gen_limit_est = {intermediate_year: 999999999,
                                     end_year: 999999999}
    grid_generation_cost_est = 0.07
    grid_power_plants_capital_cost_est = 2000
    grid_losses_est = 0.08

    # Here the scenario run starts

    if social_productive_demand == 1:
        onsseter.df['HealthDemand'] = onsseter.df['health_dem_low']
        onsseter.df['EducationDemand'] = onsseter.df['edu_dem_low']
        onsseter.df['AgriDemand'] = onsseter.df['agri_dem_low']
        onsseter.df['CommercialDemand'] = onsseter.df['prod_dem_low']
    elif social_productive_demand == 2:
        onsseter.df['HealthDemand'] = onsseter.df['health_dem_mid']
        onsseter.df['EducationDemand'] = onsseter.df['edu_dem_mid']
        onsseter.df['AgriDemand'] = onsseter.df['agri_dem_mid']
        onsseter.df['CommercialDemand'] = onsseter.df['prod_dem_mid']
    elif social_productive_demand == 3:
        onsseter.df['HealthDemand'] = onsseter.df['health_dem_high']
        onsseter.df['EducationDemand'] = onsseter.df['edu_dem_high']
        onsseter.df['AgriDemand'] = onsseter.df['agri_dem_high']
        onsseter.df['CommercialDemand'] = onsseter.df['prod_dem_high']

    if industrial_demand == 1:
        onsseter.df['HeavyIndustryDemand'] = onsseter.df['ind_dem_low']
    elif industrial_demand == 2:
        onsseter.df['HeavyIndustryDemand'] = onsseter.df['ind_dem_mid']
    elif industrial_demand == 3:
        onsseter.df['HeavyIndustryDemand'] = onsseter.df['ind_dem_high']

    if rural_tier == 6:
        onsseter.df['ResidentialDemandTierCustom'] = onsseter.df['hh_dem_low']
    elif rural_tier == 7:
        onsseter.df['ResidentialDemandTierCustom'] = onsseter.df['hh_dem_mid']
    elif rural_tier == 8:
        onsseter.df['ResidentialDemandTierCustom'] = onsseter.df['hh_dem_high']

    onsseter.df.drop(['hh_dem_low', 'hh_dem_mid', 'hh_dem_high', 'health_dem_low', 'health_dem_mid',
                      'health_dem_high', 'edu_dem_low', 'edu_dem_mid', 'edu_dem_high', 'agri_dem_low',
                      'agri_dem_mid', 'agri_dem_high', 'prod_dem_low', 'prod_dem_mid', 'prod_dem_high',
                      'ind_dem_low', 'ind_dem_mid', 'ind_dem_high'], axis=1, inplace=True)

    Technology.set_default_values(base_year=start_year,
                                  start_year=start_year,
                                  end_year=end_year,
                                  discount_rate=disc_rate)

    grid_calc_ouest = Technology(om_of_td_lines=0.1,
                                 distribution_losses=grid_losses_ouest,
                                 connection_cost_per_hh=150,
                                 base_to_peak_load_ratio=0.8,
                                 capacity_factor=1,
                                 tech_life=30,
                                 grid_capacity_investment=grid_power_plants_capital_cost_ouest,
                                 grid_price=grid_generation_cost_ouest)

    grid_calc_sud = Technology(om_of_td_lines=0.1,
                               distribution_losses=grid_losses_sud,
                               connection_cost_per_hh=150,
                               base_to_peak_load_ratio=0.8,
                               capacity_factor=1,
                               tech_life=30,
                               grid_capacity_investment=grid_power_plants_capital_cost_sud,
                               grid_price=grid_generation_cost_sud)

    grid_calc_est = Technology(om_of_td_lines=0.1,
                               distribution_losses=grid_losses_est,
                               connection_cost_per_hh=150,
                               base_to_peak_load_ratio=0.8,
                               capacity_factor=1,
                               tech_life=30,
                               grid_capacity_investment=grid_power_plants_capital_cost_est,
                               grid_price=grid_generation_cost_est)

    mg_hydro_calc = Technology(om_of_td_lines=0.02,
                               distribution_losses=0.05,
                               connection_cost_per_hh=92,
                               base_to_peak_load_ratio=0.85,
                               capacity_factor=0.5,
                               tech_life=35,
                               capital_cost={float("inf"): 5000},
                               om_costs=0.03,
                               mini_grid=True)

    mg_wind_calc = Technology(om_of_td_lines=0.02,
                              distribution_losses=0.05,
                              connection_cost_per_hh=92,
                              base_to_peak_load_ratio=0.85,
                              capital_cost={float("inf"): 3750},
                              om_costs=0.02,
                              tech_life=20,
                              mini_grid=True)

    mg_pv_calc = Technology(om_of_td_lines=0.02,
                            distribution_losses=0.05,
                            connection_cost_per_hh=92,
                            base_to_peak_load_ratio=0.85,
                            tech_life=25,
                            om_costs=0.015,
                            capital_cost={float("inf"): 2950},
                            mini_grid=True)

    sa_pv_calc = Technology(base_to_peak_load_ratio=0.9,
                            tech_life=25,
                            om_costs=0.02,
                            capital_cost={float("inf"): 6950,
                                          1: 4470,
                                          0.100: 6380,
                                          0.050: 8780,
                                          0.020: 9620
                                          },
                            standalone=True)

    mg_diesel_calc = Technology(om_of_td_lines=0.02,
                                distribution_losses=0.05,
                                connection_cost_per_hh=92,
                                base_to_peak_load_ratio=0.85,
                                capacity_factor=0.7,
                                tech_life=20,
                                om_costs=0.1,
                                capital_cost={float("inf"): 672},
                                mini_grid=True)

    sa_diesel_calc = Technology(base_to_peak_load_ratio=0.9,
                                capacity_factor=0.5,
                                tech_life=20,
                                om_costs=0.1,
                                capital_cost={float("inf"): 814},
                                standalone=True)

    sa_diesel_cost = {'diesel_price': 0.8,
                      'efficiency': 0.28,
                      'diesel_truck_consumption': 14,
                      'diesel_truck_volume': 300}

    mg_diesel_cost = {'diesel_price': 0.8,
                      'efficiency': 0.33,
                      'diesel_truck_consumption': 33.7,
                      'diesel_truck_volume': 15000}

    annual_new_grid_connections_limit = {'Est': annual_new_grid_connections_limit_est,
                                         'Sud': annual_new_grid_connections_limit_sud,
                                         'Ouest': annual_new_grid_connections_limit_ouest}

    annual_grid_cap_gen_limit = {'Est': annual_grid_cap_gen_limit_est,
                                 'Sud': annual_grid_cap_gen_limit_sud,
                                 'Ouest': annual_grid_cap_gen_limit_ouest}

    grids = ['Est', 'Ouest', 'Sud']
    grid_calcs = [grid_calc_est, grid_calc_ouest, grid_calc_sud]
    auto_intensifications = [auto_intensification_est, auto_intensification_ouest, auto_intensification_sud]

    onsseter.df.loc[onsseter.df['Region'] == 'Haut-Katanga', 'ClosestGrid'] = 'Sud'
    onsseter.df.loc[onsseter.df['Region'] == 'Haut-Lomami', 'ClosestGrid'] = 'Sud'
    onsseter.df.loc[onsseter.df['Region'] == 'Lualaba', 'ClosestGrid'] = 'Sud'
    onsseter.df.loc[onsseter.df['Region'] == 'Tanganyka', 'ClosestGrid'] = 'Sud'
    onsseter.df.loc[onsseter.df['Region'] == 'Kasai-Central', 'ClosestGrid'] = 'Sud'
    onsseter.df.loc[onsseter.df['Region'] == 'Lomami', 'ClosestGrid'] = 'Sud'
    onsseter.df.loc[onsseter.df['Region'] == 'Kasai-Oriental', 'ClosestGrid'] = 'Sud'

    onsseter.df.loc[onsseter.df['Region'] == 'Kongo Central', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Kinshasa', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Kwango', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Kasai', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Kwilu', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Mai-Ndombe', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Tshuapa', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Equateur', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Mongala', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Sud-Ubangi', 'ClosestGrid'] = 'Ouest'
    onsseter.df.loc[onsseter.df['Region'] == 'Nord-Ubangi', 'ClosestGrid'] = 'Ouest'

    onsseter.df.loc[onsseter.df['Region'] == 'Sud-Kivu', 'ClosestGrid'] = 'Est'
    onsseter.df.loc[onsseter.df['Region'] == 'Nord-Kivu', 'ClosestGrid'] = 'Est'
    onsseter.df.loc[onsseter.df['Region'] == 'Maniema', 'ClosestGrid'] = 'Est'
    onsseter.df.loc[onsseter.df['Region'] == 'Sankuru', 'ClosestGrid'] = 'Est'
    onsseter.df.loc[onsseter.df['Region'] == 'Tshopo', 'ClosestGrid'] = 'Est'
    onsseter.df.loc[onsseter.df['Region'] == 'Ituri', 'ClosestGrid'] = 'Est'
    onsseter.df.loc[onsseter.df['Region'] == 'Bas-Uele', 'ClosestGrid'] = 'Est'
    onsseter.df.loc[onsseter.df['Region'] == 'Haut-Uele', 'ClosestGrid'] = 'Est'

    prioritization = 2

    # RUN_PARAM: One shall define here the years of analysis (excluding start year),
    # together with access targets per interval and timestep duration
    yearsofanalysis = [intermediate_year, end_year]
    eleclimits = {intermediate_year: intermediate_electrification_target,
                  end_year: end_year_electrification_rate_target}
    time_steps = {intermediate_year: intermediate_year - start_year, end_year: end_year - intermediate_year}

    onsseter.current_mv_line_dist()

    onsseter.project_pop_and_urban(pop_future, urban_future, start_year, end_year, intermediate_year)

    if gis_grid_extension:
        onsseter.df = onsset_gis.create_geodataframe(onsseter.df)

    for year in yearsofanalysis:
        eleclimit = eleclimits[year]
        time_step = time_steps[year]

        onsseter.set_scenario_variables(year, num_people_per_hh_rural, num_people_per_hh_urban, time_step,
                                        start_year, urban_tier, rural_tier, 1)

        onsseter.diesel_cost_columns(sa_diesel_cost, mg_diesel_cost, year)

        sa_diesel_investment, sa_pv_investment, mg_diesel_investment, mg_pv_investment, mg_wind_investment, \
            mg_hydro_investment = onsseter.calculate_off_grid_lcoes(mg_hydro_calc, mg_wind_calc, mg_pv_calc,
                                                                    sa_pv_calc, mg_diesel_calc,
                                                                    sa_diesel_calc, year, end_year, time_step)

        grid_investment = np.zeros(len(onsseter.df['X_deg']))
        grid_investment_combined = np.zeros(len(onsseter.df['X_deg']))
        onsseter.df[SET_LCOE_GRID + "{}".format(year)] = 99
        onsseter.df['grid_investment' + "{}".format(year)] = 0

        if gis_grid_extension:
            print('')
            onsseter.df['extension_distance_' + '{}'.format(year)] = 99

            onsseter.pre_screening(eleclimit, year, time_step, prioritization, auto_intensification_ouest,
                                   auto_intensification_sud, auto_intensification_est)

        for grid, grid_calc, auto_intensification in zip(grids, grid_calcs, auto_intensifications):
            grid_cap_gen_limit = time_step * annual_grid_cap_gen_limit[grid][year] * 1000
            grid_connect_limit = time_step * annual_new_grid_connections_limit[grid][year] * 1000

            grid_investment, grid_cap_gen_limit, grid_connect_limit = \
                onsseter.pre_electrification(grid_calc.grid_price, year, time_step, end_year, grid_calc,
                                             grid_cap_gen_limit, grid_connect_limit, grid_investment, grid)

            if gis_grid_extension:
                print('Running pathfinder for ' + grid + ' grid')

                grid_investment = np.zeros(len(onsseter.df['X_deg']))
                onsseter.max_extension_dist(year, time_step, end_year, start_year, grid_calc, grid)

                # ToDo
                # onsseter.df = onsset_gis.find_grid_path(onsseter.df, year, time_step, start_year, grid_connect_limit,
                #                                         grid_cap_gen_limit, gis_cost_folder, grid,
                #                                         max_grid_extension_dist,
                #                                         out_folder, save_shapefiles)

                onsseter.df[SET_LCOE_GRID + "{}".format(year)], onsseter.df[SET_MIN_GRID_DIST + "{}".format(year)], \
                    onsseter.df[SET_ELEC_ORDER + "{}".format(year)], onsseter.df[
                    SET_MV_CONNECT_DIST], grid_investment = onsseter.elec_extension_gis(grid_calc,
                                                                                        max_grid_extension_dist,
                                                                                        year,
                                                                                        start_year,
                                                                                        end_year,
                                                                                        time_step,
                                                                                        new_investment=grid_investment,
                                                                                        grid_name=grid)
                grid_investment_combined += np.nan_to_num(grid_investment[0])

            else:
                onsseter.df[SET_LCOE_GRID + "{}".format(year)], onsseter.df[SET_MIN_GRID_DIST + "{}".format(year)], \
                    onsseter.df[SET_ELEC_ORDER + "{}".format(year)], onsseter.df[
                    SET_MV_CONNECT_DIST], grid_investment = onsseter.elec_extension(grid_calc, max_grid_extension_dist,
                                                                                    year,
                                                                                    start_year, end_year,
                                                                                    time_step, grid_cap_gen_limit,
                                                                                    grid_connect_limit,
                                                                                    grid_investment,
                                                                                    auto_intensification,
                                                                                    prioritization, grid_name=grid)

        onsseter.df['grid_investment' + "{}".format(year)] = grid_investment_combined

        if gis_grid_extension:
            grid_investment = grid_investment_combined

        onsseter.results_columns(year, time_step, prioritization, auto_intensification_ouest,
                                 auto_intensification_sud, auto_intensification_est)

        grid_investment = pd.DataFrame(grid_investment)

        onsseter.calculate_investments(sa_diesel_investment, sa_pv_investment, mg_diesel_investment,
                                       mg_pv_investment, mg_wind_investment,
                                       mg_hydro_investment, grid_investment, year)

        if gis_grid_extension:
            print('')
            onsseter.apply_limitations_gis(year, time_step)
        else:
            onsseter.apply_limitations(eleclimit, year, time_step, prioritization, auto_intensification_ouest,
                                       auto_intensification_sud, auto_intensification_est)

        onsseter.calculate_new_capacity(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc,
                                        sa_diesel_calc, grid_calc_ouest, grid_calc_sud, grid_calc_est, year)

        onsseter.update_results_columns(year)

    for i in range(len(onsseter.df.columns)):
        if onsseter.df.iloc[:, i].dtype == 'float64':
            onsseter.df.iloc[:, i] = pd.to_numeric(onsseter.df.iloc[:, i], downcast='float')
        elif onsseter.df.iloc[:, i].dtype == 'int64':
            onsseter.df.iloc[:, i] = pd.to_numeric(onsseter.df.iloc[:, i], downcast='signed')

    self.df = onsseter.df


