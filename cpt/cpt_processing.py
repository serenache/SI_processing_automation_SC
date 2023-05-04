###-----This is a module for the functions for processing CPT data-----  ###
import numpy as np
import pandas as pd

###-----Global variable-----  ###
# Atmospheric pressure
pa = 101.325


###-----Functions for Processing CPT data-----  ###
def calc_elev(depth, seabed_elev=0):
    elev = seabed_elev - depth
    return elev


def calc_Rf(fs, qc):
    """

    :param fs: in MPa
    :param qc: in MPa
    :return: Rf in %
    """
    Rf = 100 * fs / qc
    return Rf


def calc_qt_uncorr(qc, u2, a):
    qt = qc + u2 * (1 - a)
    return qt


def calc_qt_corr(qc, u2, a, u0b):
    qt_corr = qc + u2 * (1 - a) + u0b / 1000
    return qt_corr


def calc_u0(elev, elev_WT, gamma_w):
    """

    :param elev:
    :param elev_WT:
    :param gamma_w:
    :return: u0 in kPa
    """
    if elev > elev_WT:
        u0 = 0
    else:
        u0 = gamma_w * (elev_WT - elev)
    return u0


def calc_u0b(CPT_name, CPTname_shift, Push_no, Push_no_shift, u0):
    if CPT_name != CPTname_shift or Push_no != Push_no_shift:
        u0b = u0
    else:
        u0b = np.NaN
    return u0b


def calc_u2_corr(u2, u0b):
    u2_corr = u2 + u0b / 1000
    return u2_corr


# Calculate yeild stress based on qt (based on Mayne 2014)
def calc_eff_sig_y_UB(qt_corr, sig_v0,m=1):
    """

    :param qt_corr: in MPa
    :param sig_v0: in kPa
    :param m: Parameter m: 0.72 in clean quartz to silica sands. 0.8 in silty sands. 0.85 in silts. 0.9 in organic and sensitive fine grained soils. 1 in intact clays of low sensitivity. 1.1 for fissured clays.
     Can also be calculated by m=1-(0.28/(1+(Ic/2.65)^25)
    :return: in kPa
    """
    # if SOIL_CLASS == 'CLAY':
    #     m=1

    eff_sig_y_UB = 0.33 * ((qt_corr * 1000 - sig_v0) ** m) * (pa / 100) ** (1 - m)

    return eff_sig_y_UB


# Calculate yeild stress based on qt (based on Mayne 2014)
def calc_eff_sig_y_LB(qt_corr, sig_v0, m=0.72):
    """

    :param qt_corr: in MPa
    :param sig_v0: in kPa
    :param SOIL_CLASS: Parameter m: 0.72 in clean quartz to silica sands. 0.8 in silty sands. 0.85 in silts. 0.9 in organic and sensitive fine grained soils. 1 in intact clays of low sensitivity. 1.1 for fissured clays.
     Can also be calculated by m=1-(0.28/(1+(Ic/2.65)^25)
    :return: in kPa
    """
    # if SOIL_CLASS == 'SAND':
    #     m=0.72

    eff_sig_y_LB = 0.33 * ((qt_corr * 1000 - sig_v0) ** m) * (pa / 100) ** (1 - m)

    return eff_sig_y_LB




def calc_Fr(fs, qt_corr, sig_v0):
    """

    :param fs: in MPa
    :param qt: in MPa
    :param sig_v0: in kPa
    :return:
    """
    Fr = 100 * (1000 * fs) / (1000 * qt_corr - sig_v0)
    return Fr


def calc_Bq_uncorr(u2, u0, qt_uncorr, sig_v0):
    """

    :param u2: in MPa
    :param u0: in kPa
    :param qt: in MPa
    :param sig_v0: in kPa
    :return:
    """
    Bq_uncorr = (1000 * u2 - u0) / (1000 * qt_uncorr - sig_v0)
    return Bq_uncorr


def calc_Bq_corr(u2, u0, qt_corr, sig_v0, u0b):
    """

    :param u2: in MPa
    :param u0: in kPa
    :param qt: in MPa
    :param sig_v0: in kPa
    :return:
    """
    Bq_corr = (1000 * u2 + u0b - u0) / (1000 * qt_corr - sig_v0)
    return Bq_corr


def calc_Qtn(qt_corr, sig_v0, eff_sig_v0, n):
    """

    :param qt: in MPa
    :param sig_v0: in kPa
    :param eff_sig_v0: in kPa
    :param n:
    :return:
    """
    try:
        Qtn = ((1000 * qt_corr - sig_v0) / pa) * (pa / eff_sig_v0) ** n
    except:
        Qtn = np.NaN
    return Qtn


def calc_Ic(Fr, Qtn):
    """

    :param Fr:
    :param Qtn:
    :return:
    """
    if Fr > 0 and Qtn > 0:
        Ic = ((3.47 - np.log10(Qtn)) ** 2 + (np.log10(Fr) + 1.22) ** 2) ** 0.5
    else:
        Ic = np.NaN
    return Ic


def calc_n(Ic, eff_sig_v0):
    n = 0.381 * Ic + 0.05 * (eff_sig_v0 / pa) - 0.15
    return n


def loop_n(qt_corr, sig_v0, eff_sig_v0, Fr):
    # calculate n from iterations
    # initialise the parameters
    #n1 = 0
    Ic_prev = 100
    n = 1
    max_no_iteration=100
    iteration_no=0
    #Run one calculation of Qtn and Ic
    Qtn_1 = calc_Qtn(qt_corr, sig_v0, eff_sig_v0, n)
    Ic_1 = calc_Ic(Fr, Qtn_1)

    #while np.abs(n1 - n) > 0.0000000001:
    while np.abs(Ic_1 - Ic_prev) > 0.00000001:
        # Update n1
        #n1 = n
        #Update Ic_Prev
        Ic_prev = Ic_1
        # Update n
        n = calc_n(Ic_1, eff_sig_v0)
        # check n
        if n > 1:
            n = 1
        # Recalculate Qtn and Ic
        #Qtn_1 = calc_Qtn(qt_corr, sig_v0, eff_sig_v0, n1)
        Qtn_1 = calc_Qtn(qt_corr, sig_v0, eff_sig_v0, n)
        Ic_1 = calc_Ic(Fr, Qtn_1)

        # update iteration number
        iteration_no = iteration_no+1
        # Check iteration_no - get out after 100 to avoid infinite loop
        if iteration_no>100:
            n=100
            break

    n_looped = n
    return n_looped


# ICP equation to calculate G0 for sand
# only valid for qc/(sig'v0)^0.5= 200 to 3000
def calc_G0_ICP(SOIL_CLASS, check_value, n_value, qc):
    """

    :param SOIL_CLASS: either SAND, SILT or CLAY
    :param check_value:
    :param n_value:
    :param qc: in MPa
    :return: G0 in MPa
    """
    if SOIL_CLASS == 'SAND'or SOIL_CLASS == 'SILT' and 200 <= check_value <= 3000:
        G0 = qc * (0.0203 + 0.00125 * n_value - 0.000001216 * n_value ** 2) ** (-1)
    else:
        G0 = np.NaN
    return G0


# Rix and Stokoe (1992) equation to calculate G0 for sand
# only valid for qc/(sig'v0)^0.5= 200 to 10,000
def calc_G0_RS(SOIL_CLASS, check_value, qc):
    """

    :param SOIL_CLASS: either SAND, SILT or CLAY
    :param check_value:
    :param qc: in MPa
    :return: G0 in MPa
    """
    if SOIL_CLASS == 'SAND' or SOIL_CLASS == 'SILT' and 200 <= check_value <= 10000:
        G0 = 1634 * qc * check_value ** (-0.75)
    else:
        G0 = np.NaN
    return G0


# Baldi et al (1989) equation to calculate G0 for sand
def calc_G0_Baldi(SOIL_CLASS, qc, UNIT_WEIGHT, eff_sig_v0):
    """

    :param SOIL_CLASS: either SAND, SILT or CLAY
    :param qc: in MPa
    :param UNIT_WEIGHT:
    :param eff_sig_v0: in kPa
    :return: G0 in MPa
    """
    if SOIL_CLASS == 'SAND'or SOIL_CLASS == 'SILT':
        G0 = (UNIT_WEIGHT / 9.81) * (277 * (qc ** 0.13) * (eff_sig_v0 / 1000) ** 0.27) ** 2 / 1000
    else:
        G0 = np.NaN
    return G0


# Baldi et al (1986) Dr equation for sand
# valid for NC and OC sand for clean predominately silica sand
def calc_Dr_Baldi(SOIL_CLASS, qc, eff_p):
    """

    :param SOIL_CLASS: either SAND, SILT or CLAY
    :param qc: in kPa
    :param eff_p: in kPa
    :return: Dr in %
    """
    if SOIL_CLASS == 'SAND' or SOIL_CLASS == 'SILT':
        try:
            Dr = np.minimum(1 / 2.61 * (np.log((qc * 1000) / (181 * (eff_p) ** 0.55))) * 100, 100)
        except ZeroDivisionError:
            print('The qc and eff_p that give error = ',qc,eff_p)
            Dr = np.NaN
    else:
        Dr = np.NaN
    return Dr


# Jamiolkowski et al (2003) Dr equation for sand
# valid for NC and OC DRY sand for clean predominately silica sand
def calc_Dr_Jam_dry(SOIL_CLASS, qc, eff_p):
    """

    :param SOIL_CLASS: either SAND, SILT or CLAY
    :param qc: in kPa
    :param eff_p: in kPa
    :return: Dr in %
    """
    if SOIL_CLASS == 'SAND' or SOIL_CLASS == 'SILT':
        Dr = np.minimum(1 / 2.96 * (np.log((qc * 1000 / 98.1) / (24.94 * (eff_p / 98.1) ** 0.46))) * 100, 100)
    else:
        Dr = np.NaN
    return Dr


# Jamiolkowski et al (2003) Dr equation for sand
# valid for NC and OC SATURATED sand for clean predominately silica sand
# Note that this is not valid for qc/(sig'v0)^0.5<2.24
def calc_Dr_Jam_sat(SOIL_CLASS, check_value, qc, eff_sig_v0, Dr_dry):
    """

    :param SOIL_CLASS:either SAND, SILT or CLAY
    :param check_value:
    :param qc: in kPa
    :param eff_sig_v0: in kPa
    :param Dr_dry: in %
    :return:Dr in %
    """
    if SOIL_CLASS == 'SAND' or SOIL_CLASS == 'SILT' and check_value > 2.24:
        Dr = np.minimum((1 + (-1.87 + 2.32 * np.log(qc * 1000 / (eff_sig_v0 * pa) ** 0.5)) / 100) * Dr_dry, 100)
    else:
        Dr = np.NaN
    return Dr


# Schmertmann (1978) Peak phi' (upper bound)
# uniform gravel and well graded gravel-sand-silt
def calc_peak_phi_UB(SOIL_CLASS, Dr_Baldi):
    """

    :param SOIL_CLASS: either SAND, SILT, or CLAY
    :param Dr_Baldi: in %
    :return: in degree
    """
    if SOIL_CLASS == 'SAND'or SOIL_CLASS == 'SILT':
        peak_phi_UB = np.minimum(38 + 0.08 * Dr_Baldi, 38 + 8)
    else:
        peak_phi_UB = np.NaN
    return peak_phi_UB


# Schmertmann (1978) Peak phi' (lower bound)
# uniform fine sand
def calc_peak_phi_LB(SOIL_CLASS, Dr_Baldi):
    """

    :param SOIL_CLASS: either SAND, SILT or CLAY
    :param Dr_Baldi: in %
    :return: in degree
    """
    if SOIL_CLASS == 'SAND' or SOIL_CLASS == 'SILT':
        peak_phi_LB = 28 + 0.14 * Dr_Baldi
    else:
        peak_phi_LB = np.NaN
    return peak_phi_LB


# Lunne et al equation for calculating Su (upper bound)
# Note that Nkt_UB is specified in the gINT user input table
def calc_Su_UB(SOIL_CLASS, qt_corr, sig_v0, Nkt_UB):
    """

    :param SOIL_CLASS: either SAND, SILT or CLAY
    :param qt_corr: in Mpa
    :param sig_v0: in kPa
    :param Nkt_UB:
    :return: in kPa
    """
    if SOIL_CLASS == 'CLAY'or SOIL_CLASS == 'SILT':
        Su_UB = np.maximum((qt_corr*1000-sig_v0)/Nkt_UB,0)
    else:
        Su_UB = np.NaN
    return Su_UB

# Lunne et al equation for calculating Su (lower bound)
# Note that Nkt_LB is specified in the gINT user input table
def calc_Su_LB(SOIL_CLASS, qt_corr, sig_v0, Nkt_LB):
    """

    :param SOIL_CLASS: either SAND, SILT or CLAY
    :param qt_corr: in Mpa
    :param sig_v0: in kPa
    :param Nkt_LB:
    :return: in kPa
    """
    if SOIL_CLASS == 'CLAY' or SOIL_CLASS == 'SILT':
        Su_LB = np.maximum((qt_corr*1000-sig_v0)/Nkt_LB,0)
    else:
        Su_LB = np.NaN
    return Su_LB


# Plotting reference values of G0
def calc_G0_ref(A,na,eff_p):
    """

    :param A: constant from the global variable dictionary
    :param na: constant from the global variable dictionary
    :param eff_p: in kPa
    :return: in MPa
    """
    G0_ref=A*eff_p**na/1000
    return G0_ref

# Check if the push number is different
def check_push_no(CPT_name, CPTname_shift, Push_no, Push_no_shift):
    if CPT_name != CPTname_shift or Push_no != Push_no_shift:
        checker=True
    else:
        checker=False
    return checker



# main function to process CPT data
def process_CPT(df, gamma_w, G0_constants, Elev_WT=0):
    # processing
    depth = df.Depth
    qc = df.SCPT_RES
    u2 = df.SCPT_PWP2
    a = df.SCPG_CAR
    fs = df.SCPT_FRES
    K0 = df.K0
    df['Elev'] = calc_elev(depth)
    Elev = df.Elev
    df['Rf'] = calc_Rf(fs, qc)
    Rf = df.Rf
    df['qt_uncorr'] = calc_qt_uncorr(qc, u2, a)
    qt_uncorr = df.qt_uncorr

    # calculate sig_v0
    # df['d_Depth'] = df.Depth.diff().fillna(0)
    # df['d_sig_v0'] = df.d_Depth * df.UNIT_WEIGHT  # assuming that the first row is at 0m - amb I do not think we should assume that
    # df['sig_v0'] = df.d_sig_v0.cumsum()
    df['sig_v0'] = df.base_sigv0 + (df.Depth - df.DEPTH_BASE) * df.UNIT_WEIGHT
    sig_v0 = df.sig_v0

    # calculate u0 and eff_sig_v0
    df['u0'] = df.apply(lambda row: calc_u0(row['Elev'], Elev_WT, gamma_w), axis=1)
    u0 = df.u0
    df['eff_sig_v0'] = df.sig_v0 - df.u0
    eff_sig_v0 = df.eff_sig_v0

    # calculate u0b, u2_corr, qt_corr (correction for downhole test)
    df['CPT_name_shift'] = df.CPT_name.shift(1)
    df['Push_no_shift'] = df.Push_no.shift(1)
    df['u0b'] = df.apply(
        lambda row: calc_u0b(row['CPT_name'], row['CPT_name_shift'], row['Push_no'], row['Push_no_shift'], row['u0']),
        axis=1)
    df.u0b.fillna(method='ffill', inplace=True)
    u0b = df.u0b
    df['u2_corr'] = calc_u2_corr(u2, u0b)
    u2_corr = df.u2_corr
    df['qt_corr'] = calc_qt_corr(qc, u2, a, u0b)
    qt_corr = df.qt_corr

    # calculate yield stress and OCR (Mayne 2014)
    df['eff_sig_y_UB'] = df.apply(lambda row: calc_eff_sig_y_UB(row['qt_corr'], row['sig_v0']), axis=1)
    eff_sig_y_UB = df.eff_sig_y_UB

    df['eff_sig_y_LB'] = df.apply(lambda row: calc_eff_sig_y_LB(row['qt_corr'], row['sig_v0']), axis=1)
    eff_sig_y_LB = df.eff_sig_y_LB

    df['OCR_UB'] = eff_sig_y_UB / eff_sig_v0
    df['OCR_LB'] = eff_sig_y_LB/eff_sig_v0

    # calculate Fr
    df['Fr'] = calc_Fr(fs, qt_corr, sig_v0)
    Fr = df.Fr

    # calculate Bq
    df['Bq_uncorr'] = calc_Bq_uncorr(u2, u0, qt_uncorr, sig_v0)
    Bq_uncorr = df.Bq_uncorr
    df['Bq_corr'] = calc_Bq_corr(u2, u0, qt_corr, sig_v0, u0b)
    Bq_corr = df.Bq_corr

    # iterate to calculate n_IC:
    df['n_IC'] = df.apply(lambda row: loop_n(row['qt_corr'], row['sig_v0'], row['eff_sig_v0'], row['Fr']), axis=1)
    n_IC = df.n_IC


    # Then calculate Qtn and Ic
    df['Qtn'] = calc_Qtn(qt_corr, sig_v0, eff_sig_v0, n_IC)
    Qtn = df.Qtn

    df['Ic'] = df.apply(lambda row: calc_Ic(row['Fr'], row['Qtn']), axis=1)
    Ic = df.Ic

    # calculate p'
    df['eff_p'] = (eff_sig_v0 + 2 * K0 * eff_sig_v0) / 3
    eff_p = df.eff_p
    #print(df[['eff_sig_v0','eff_p']])

    # Calculate G0
    # Preliminary parameters fro checking
    df['qc/eff_sig_v0^0.5'] = 1000 * qc / (eff_sig_v0 ** 0.5)
    df['n_G0'] = 1000 * qc / ((eff_sig_v0 * 100) ** 0.5)
    # ICP G0 equation for sand
    df['G0_ICP'] = df.apply(
        lambda row: calc_G0_ICP(row['SOIL_CLASS'], row['qc/eff_sig_v0^0.5'], row['n_G0'], row['SCPT_RES']), axis=1)
    G0_ICP = df.G0_ICP
    # Rix and Stoke (1992) G0 equation for sand
    df['G0_RS'] = df.apply(lambda row: calc_G0_RS(row['SOIL_CLASS'], row['qc/eff_sig_v0^0.5'], row['SCPT_RES']), axis=1)
    G0_RS = df.G0_RS
    # Baldi et al (1989) G0 equation for sand
    df['G0_Baldi'] = df.apply(
        lambda row: calc_G0_Baldi(row['SOIL_CLASS'], row['SCPT_RES'], row['UNIT_WEIGHT'], row['eff_sig_v0']), axis=1)
    G0_Baldi = df.G0_Baldi

    # Calculate Dr in %
    # Baldi et al (1986) Dr equation for sand
    df['Dr_Baldi'] = df.apply(lambda row: calc_Dr_Baldi(row['SOIL_CLASS'], row['SCPT_RES'], row['eff_p']), axis=1)
    Dr_Baldi = df.Dr_Baldi
    # Jamiolkowski et al (2003) Dr equation for dry sand
    df['Dr_Jam_dry'] = df.apply(lambda row: calc_Dr_Jam_dry(row['SOIL_CLASS'], row['SCPT_RES'], row['eff_p']), axis=1)
    Dr_Jam_dry = df.Dr_Jam_dry
    # Jamiolkowski et al (2003) Dr equation for sat sand
    df['Dr_Jam_sat'] = df.apply(
        lambda row: calc_Dr_Jam_sat(row['SOIL_CLASS'], row['qc/eff_sig_v0^0.5'], row['SCPT_RES'], row['eff_sig_v0'],
                                    row['Dr_Jam_dry']), axis=1)
    Dr_Jam_sat = df.Dr_Jam_sat

    # Calculate Peak phi'
    # Schmertmann (1978) Peak phi' (upper bound)
    df['peak_phi_UB'] = df.apply(lambda row: calc_peak_phi_UB(row['SOIL_CLASS'], row['Dr_Baldi']), axis=1)
    peak_phi_UB = df.peak_phi_UB
    # Schmertmann (1978) Peak phi' (lower bound)
    df['peak_phi_LB'] = df.apply(lambda row: calc_peak_phi_LB(row['SOIL_CLASS'], row['Dr_Baldi']), axis=1)
    peak_phi_LB = df.peak_phi_LB

    # Calculate Su values
    # Lunne et al equation for calculating Su (lower bound)
    df['Su_UB'] = df.apply(lambda row: calc_Su_UB(row['SOIL_CLASS'], row['qt_corr'], row['sig_v0'], row['Nkt_UB']),
                           axis=1)
    Su_UB = df.Su_UB
    # Lunne et al equation for calculating Su (lower bound)
    df['Su_LB'] = df.apply(lambda row: calc_Su_LB(row['SOIL_CLASS'], row['qt_corr'], row['sig_v0'], row['Nkt_LB']),
                           axis=1)
    Su_LB = df.Su_LB

    # Calculate reference values of G0 for plotting
    df['G0_A'] = df.apply(lambda row: calc_G0_ref(G0_constants['A'][0], G0_constants['na'][0], row['eff_p']), axis=1)
    G0_A = df.G0_A
    df['G0_B'] = df.apply(lambda row: calc_G0_ref(G0_constants['A'][1], G0_constants['na'][1], row['eff_p']), axis=1)
    G0_B = df.G0_B
    df['G0_C'] = df.apply(lambda row: calc_G0_ref(G0_constants['A'][2], G0_constants['na'][2], row['eff_p']), axis=1)
    G0_C = df.G0_C
    df['G0_D'] = df.apply(lambda row: calc_G0_ref(G0_constants['A'][3], G0_constants['na'][3], row['eff_p']), axis=1)
    G0_D = df.G0_D
    df['G0_E'] = df.apply(lambda row: calc_G0_ref(G0_constants['A'][4], G0_constants['na'][4], row['eff_p']), axis=1)
    G0_E = df.G0_E



    # Add a row of NA to separate different push numbers
    df['Check_push_no'] = df.apply(
        lambda row: check_push_no(row['CPT_name'], row['CPT_name_shift'], row['Push_no'], row['Push_no_shift']),
        axis=1)

    row_index=df.index[df['Check_push_no']].tolist()
    column_no = len(df.columns)
    for i, index in enumerate(row_index):
        dfs = np.split(df, [index + i])
        df = pd.concat([dfs[0], pd.DataFrame(np.full((1,column_no),np.nan), columns=df.columns), dfs[1]],
                       ignore_index=True)
        # df.loc[index]=[np.NaN]
    processed_CPT=df
    return processed_CPT






# Get row index with True value

###----------------------------------------------------------------------------------  ###

###-----Merging dataframes from gINT database file ----  ###
# This is the workflow if we are starting from a gINT database file.

#function to merge SCPT and SCPG tables
def merge_SCPT_SCPG(SCPT, SCPG):
    first_merge = pd.merge(SCPT, SCPG, how="left", on=["PointID", "ItemKey"])
    first_merge_renamed = first_merge.rename(columns={'PointID': 'CPT_name', 'ItemKey': 'Push_no'})
    return first_merge_renamed

#Add location ID to SOIL_UNIT table
def assign_Location_ID(SOIL_UNIT_PointID, SCPG):
    for i, rows in SCPG.iterrows():
        row_SCPG = rows.to_frame().transpose()
        if row_SCPG['PointID'].values[0] == SOIL_UNIT_PointID:
            location_ID = row_SCPG['Location_ID'].values[0]
            return location_ID

def add_locationID(SCPG, SOIL_UNIT):
    SOIL_UNIT['Location_ID'] = SOIL_UNIT.apply(
        lambda row_SOIL_UNIT: assign_Location_ID(row_SOIL_UNIT['PointID'], SCPG), axis=1)
    return SOIL_UNIT

#merge soil unit with unit property
def merge_soil_profiles(SOIL_UNIT,SOIL_PROPERTY):
    '''
    Function to add the soil property of each layers to the
    soil profiles for each location point. Note that the function
    create a new 'UNIQUE_GEOL' feature that create a unique reference
    for each layer in the profile (even if they belong to the same identified unit
    :param SOIL_UNIT: dataframe that includes the soil profiles for different PointID
    :param SOIL_PROPERTY: dataframe the that includes the property for each soil unit
    :return: dataframe of the geological profilles with added soil properties
    '''
    #AMB - this is a general function that will need to be moved out of CPT later
    try:
        SOIL_UNIT_cleaned = SOIL_UNIT.drop(['GintRecID'], axis=1)
    except:
        SOIL_UNIT_cleaned= SOIL_UNIT
    SOIL_UNIT_renamed = SOIL_UNIT_cleaned.rename(columns={'ItemKey': 'GEOL_UNIT', 'Depth': 'DEPTH_TOP'})
    SOIL_PROPERTY_renamed = SOIL_PROPERTY.rename(columns={'ItemKey': 'GEOL_UNIT'})
    SOIL_UNIT_renamed['UNIQUE_GEOL'] = SOIL_UNIT_renamed.GEOL_UNIT+"_"+SOIL_UNIT_renamed.index.astype(str)
    merge_table = pd.merge(SOIL_UNIT_renamed,SOIL_PROPERTY_renamed, how="left", on=["GEOL_UNIT"])
    return merge_table.sort_values(by=['Location_ID','PointID','DEPTH_TOP'])

def calc_sigv0_base_layer(df):
    '''
    Calculate the total vertical stress at the base of a layer
    :param df: dataframe that includes the soil profiles with associated soil
               soil properties (i.e. merged of soil profiles and soil properties)
    :return: nothing - the function directly add a column to the input dataframe
    '''
    # AMB - this is a general function that will need to be moved out of CPT later
    df['inc_sigv0'] = ((df.DEPTH_BASE-df.DEPTH_TOP)*df.UNIT_WEIGHT)
    df['base_sigv0'] = np.nan
    for point in df.PointID.unique():
        min_depth = df[df['PointID'] == point]['DEPTH_TOP'].min()
        if  min_depth == 0:
            df.loc[df['PointID'] == point,['base_sigv0']] = df[df['PointID'] == point].inc_sigv0.cumsum()
        else: # for cases where the profile does not start from 0
            #AMB - probably not the smartest way to do this - need to think
            location = df[df['PointID'] == point]['Location_ID'].iloc[0]
            inter_df = df.loc[(df['Location_ID']==location) & (df['DEPTH_BASE'] < min_depth)]
            closest_depth= inter_df['DEPTH_BASE'].iloc[-1]
            closest_base_sigV = inter_df['base_sigv0'].iloc[-1]
            df.loc[(df['PointID'] == point) & (df['DEPTH_TOP'] == min_depth), ['inc_sigv0']] = (closest_base_sigV +
                                                                    (df[df['PointID'] == point]['DEPTH_BASE'].iloc[0]-closest_depth)*
                                                                    df[df['PointID'] == point]['UNIT_WEIGHT'].iloc[0])
            df.loc[df['PointID'] == point, ['base_sigv0']] = df[df['PointID'] == point].inc_sigv0.cumsum()

# Add soil unit to each row of data
# def assign_soil_unit(row_SCPT_depth, row_SCPT_LocationID, SOIL_UNIT):
#     for i, rows in SOIL_UNIT.iterrows():
#         row_soil = rows.to_frame().transpose()
#         if row_soil['Location_ID'].values[0] == row_SCPT_LocationID:
#             if row_soil.Depth.values < row_SCPT_depth < row_soil.DEPTH_BASE.values:
#                 geol_unit = row_soil.GEOL_UNIT.values[0]
#                 return geol_unit
#                 break

def assign_soil_unit(row_SCPT_depth, row_SCPT_LocationID, SOIL_UNIT):
    for i, rows in SOIL_UNIT.iterrows():
        row_soil = rows.to_frame().transpose()
        if row_soil['CPT_name'].values[0] == row_SCPT_LocationID:
            if row_soil.DEPTH_TOP.values < row_SCPT_depth < row_soil.DEPTH_BASE.values:
                geol_unit = row_soil.UNIQUE_GEOL.values[0]
                return geol_unit
                break

# def add_soil_unit(first_merge_SCPT, SOIL_UNIT):
#     first_merge_SCPT['GEOL_UNIT'] = first_merge_SCPT.apply(
#         lambda row_SCPT: assign_soil_unit(row_SCPT['Depth'], row_SCPT['Location_ID'], SOIL_UNIT), axis=1)
#     return first_merge_SCPT

def add_soil_unit(first_merge_SCPT, SOIL_UNIT):
    first_merge_SCPT['UNIQUE_GEOL'] = first_merge_SCPT.apply(
        lambda row_SCPT: assign_soil_unit(row_SCPT['Depth'], row_SCPT['CPT_name'], SOIL_UNIT), axis=1)
    return first_merge_SCPT

#function to Merge SCPT with soil unit and soil properties tables
# need to change column name of the three tables to ensure they all call GEOL_unit
# need to change the 'Depth' column in SOIL_UNIT to avoid conflict
# https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
# def third_merge(assigned_SCPT, SOIL_UNIT, SOIL_PROPERTY):
#     try:
#         SOIL_UNIT_cleaned = SOIL_UNIT.drop(['GintRecID'], axis=1)
#     except:
#         SOIL_UNIT_cleaned= SOIL_UNIT
#     SOIL_UNIT_renamed = SOIL_UNIT_cleaned.rename(columns={'ItemKey': 'GEOL_UNIT', 'Depth': 'DEPTH_TOP'})
#     SOIL_PROPERTY_renamed = SOIL_PROPERTY.rename(columns={'ItemKey': 'GEOL_UNIT'})
#     second_merge = pd.merge(assigned_SCPT, SOIL_UNIT_renamed, how="left", on=["GEOL_UNIT","Location_ID"])
#     merged_SCPT = pd.merge(second_merge, SOIL_PROPERTY_renamed, how="left", on="GEOL_UNIT")
#     return merged_SCPT

def third_merge(assigned_SCPT, SOIL_UNIT):
    merged_SCPT = pd.merge(assigned_SCPT, SOIL_UNIT, how="left", on=["UNIQUE_GEOL","Location_ID","CPT_name"])
    return merged_SCPT

# function to perform all merges#
# def merge_tables(SCPT, SCPG, SCPT_Location, SOIL_UNIT, SOIL_PROPERTY):
#     # merging of the table
#     first_merge_SCPT = merge_SCPT_SCPG(SCPT, SCPG)
#     SOIL_UNIT_with_LocationID = add_locationID(SCPG, SOIL_UNIT)
#     selected_SCPT = first_merge_SCPT[(first_merge_SCPT.Location_ID.isin(SCPT_Location))]
#     SCPT_sorted = selected_SCPT.sort_values(by=['Location_ID','Depth']) #AMB - may be it should be Location_ID, CPT_name, Depth - there may be some overlap in depth.
#     assigned_SCPT = add_soil_unit(SCPT_sorted, SOIL_UNIT_with_LocationID)
#     merged_SCPT = third_merge(assigned_SCPT, SOIL_UNIT_with_LocationID, SOIL_PROPERTY)
#     return merged_SCPT

def merge_tables(SCPT, SCPG, SCPT_Location, SOIL_UNIT, SOIL_PROPERTY):
    SOIL_UNIT_with_LocationID = add_locationID(SCPG, SOIL_UNIT)
    SOIL_UNIT_with_Property = merge_soil_profiles(SOIL_UNIT_with_LocationID,SOIL_PROPERTY)
    calc_sigv0_base_layer(SOIL_UNIT_with_Property)
    SOIL_UNIT_with_Property = SOIL_UNIT_with_Property.rename(columns={'PointID': 'CPT_name'})
    # merging of the table
    first_merge_SCPT = merge_SCPT_SCPG(SCPT, SCPG)
    selected_SCPT = first_merge_SCPT[(first_merge_SCPT.Location_ID.isin(SCPT_Location))]
    SCPT_sorted = selected_SCPT.sort_values(by=['Location_ID','CPT_name','Depth'])
    assigned_SCPT = add_soil_unit(SCPT_sorted, SOIL_UNIT_with_Property)
    merged_SCPT = third_merge(assigned_SCPT, SOIL_UNIT_with_Property)
    return merged_SCPT

###----------------------------------------------------------------------------------  ###
