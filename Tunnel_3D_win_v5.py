"""
predict the characteristics of tunnel fire

@author: wu
"""

"""
delete all user defined variables before running the code
get_ipython: to input lines just like in the IPython console
-f: not to show 
"""



import keras
import keras.backend as K
from keras.layers.core import Activation
from keras.models import Sequential,load_model
from keras.layers import Dense, Dropout, LSTM
from keras.callbacks import TensorBoard
from keras.utils import to_categorical, plot_model

import os,glob

from sklearn.utils import shuffle
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import confusion_matrix
import seaborn as sns

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import sys
import numpy as np
import pandas as pd

import crt_folder
import xlsxwriter
import xlrd


# fix random seed
np.random.seed(1234)



"""
1. import the parameter values from fds file generator
"""

Bound = np.array([1.7, 0.14, 0.17])
FireHight = 0.5

T_END, DT_SLCF, DT_DEVC = 300.0, 1, 1

Sur_value = 10**(-2)
Fire_Size = np.array([0.03**2, 0.05**2, 0.06**2, 0.08**2, 0.11**2])
Fire_Loc = np.arange(1.0,17.0,1.0)
H_RR = np.array([0.674, 1.225, 1.545, 2.453, 4.412])
Wind_Spe = np.array([0.0,  -2.0, -4.0,  2.0, 4.0])

Devc_delta_fds = 1.0
seq_interval_fds = 1.0

"""
Variables for discussion
Devc_Height: the height of the sensor devices, this value should be selected from "DevcHeight_all"
Deve_region_loc: start point of device region, this value should be <= Bound[0] (160)
Deve_region_length: region length of device, this value should be <= Bound[0] (160)
Devc_delta: the distance between sensors, this value should be >=1.0

seq_length: duration of sensor data to be trained, such as 60s
seq_interval: time interval between sensor data, such as every 1s
"""

Devc_Height = 0.1

# create results folders

father_path = ('C:\\GoogleDrive\\Desktop\\Paper on small scale tunnel fire')
path_data =(father_path + '\\Tunnel_3D_Simulation')
output_dir = father_path + '\\Tunnel_3D_output'



# define metrics criterion of loc, hrr and wind
def r2_loc(y_true, y_pred):
    """Coefficient of Determination 
    """
    SS_res =  K.sum(K.square( y_true[:,0] - y_pred[:,0] ))
    SS_tot = K.sum(K.square( y_true[:,0] - K.mean(y_true[:,0]) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )

def r2_hrr(y_true, y_pred):
    """Coefficient of Determination 
    """
    SS_res =  K.sum(K.square( y_true[:,1] - y_pred[:,1] ))
    SS_tot = K.sum(K.square( y_true[:,1] - K.mean(y_true[:,1]) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )

def r2_wind(y_true, y_pred):
    """Coefficient of Determination 
    """
    SS_res =  K.sum(K.square( y_true[:,2] - y_pred[:,2] ))
    SS_tot = K.sum(K.square( y_true[:,2] - K.mean(y_true[:,2]) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )

def r2_total(y_true, y_pred):
    """Coefficient of Determination 
    """
    SS_res =  K.sum(K.square( y_true - y_pred ))
    SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )

def norm_array_column(array_raw):
    num_column = array_raw.shape[1]
    max_min_array = [[16.0, 4.412, 4.0],[1.0, 0.674, -4.0]]
    array_norm = []
    for col in np.arange(num_column):
        col_min = max_min_array[1][col]
        col_max = max_min_array[0][col]
        array_norm.append((array_raw[:,col] - col_min) / (col_max - col_min))
    return np.array(np.transpose(array_norm).tolist(), 'f')

def Inverse_norm_array_column(array_raw):
    num_column = array_raw.shape[1]
    max_min_array = [[16.0, 4.412, 4.0],[1.0, 0.674, -4.0]]
    array_norm = []
    for col in np.arange(num_column):
        col_min = max_min_array[1][col]
        col_max = max_min_array[0][col]
        array_norm.append((array_raw[:,col] * (col_max - col_min) +  col_min))
    return np.array(np.transpose(array_norm).tolist(), 'f')

# read the variable values of each factor cases
read_case_data = xlrd.open_workbook(output_dir + '\\benchmark.xlsx')
sheet_cases = read_case_data.sheets()[0]
nrows = sheet_cases.nrows
factor_values = []
for i in np.arange(nrows-1):
    factor_values.append(sheet_cases.row_values(i+1))

# write the data into sheet
workbook = xlsxwriter.Workbook(output_dir + '\\results.xlsx')
output_variables =['loss', 'r2_total', 'r2_loc', 'r2_hrr', 'r2_wind',\
                   'val_loss','val_r2_total', 'val_r2_loc', 'val_r2_hrr', 'val_r2_wind']
for var in output_variables:
    locals()['sheet_' + var] = workbook.add_worksheet(var)

for q in np.arange(0, int(np.round(np.array(factor_values).shape[0])), 1):
    
    print('Start the factor of ' + str(q+1))
    Deve_region_loc, Deve_region_length, Devc_delta, seq_start, seq_end, sample_len, seq_interval = factor_values[q]
    
    # calculated parameters
    if Deve_region_loc + Deve_region_length > Bound[0]:
        print('the start and/or the length of the sensor region is wrong')
        sys.exit()
    
    Dev_num_fds = np.floor((Deve_region_length - Devc_delta_fds)/Devc_delta_fds)+1
    Dev_num_start = np.ceil(Deve_region_loc/Devc_delta_fds)
    
    """
    2. import data and generate train dataset
    Flag_filesize: to mark whether the devc.csv file is corrent. if incorrent, stop to run the following lines.
    Train_df: training data
    Truth_df: label of the training data
    Loc_label: label for classification of the training data
    (1) import all the csv files
    (2) select the data of the current device height
    (3) normalize the training data and labels
    (4) shuffle the data for training
    """
    
    Train_df = list()
    Truth_df = list()
    Loc_label = list()
    
    # Num_case: used to show the cases read into the current dataset
    Num_case = 0
    
    for FireLoc in Fire_Loc:
        for HRR in H_RR:
            for WindSpe in Wind_Spe:
                
                # H_RR*3*6/1000: is due to the different definitions of HRR and H_RR
                # WindSpe*10: is due to the definition in fds file
                Filename = ('Loc_' + str(int(np.round(FireLoc))) +
                            '_HRR_' + str(int(np.round(HRR/(Fire_Size[list(H_RR).index(HRR)])))) + '_Wind_' + str(int(np.round(WindSpe*10))))
                Num_case = Num_case +1
                # check wheter the directory of csv file is correct
                file=os.path.join(path_data, Filename + '_devc.csv')
                
                # drop the line of name and convert the data format
                train_df_temp = pd.read_csv(file)
                train_df_temp.drop('s', axis=1, inplace=True)
                train_df_temp.drop([0], axis=0, inplace=True)
                
                train_df_temp = np.array(train_df_temp, dtype = np.float)
                
                # form the training dataset "Train_df", lable dataset "Truth_df" and classification dataset "Loc_label"
                for start, stop in zip(range(int(seq_start/seq_interval_fds), int(seq_end)-int(sample_len/seq_interval_fds), int(sample_len)), \
                                       range(int(seq_start/seq_interval_fds + sample_len/seq_interval_fds), int(seq_end), int(sample_len))):
                    # select the temporal training data
                    Train_df.append(list(train_df_temp[start:stop:int(seq_interval/seq_interval_fds), :]))
                    HRR_Total = HRR
                    Truth_df.append(list([FireLoc, HRR_Total, WindSpe]))
    
    Train_df = np.array(Train_df, dtype = np.float)
    Train_df = ((Train_df+270)**4 - 300.0**4) / (1100.0**4 - 300.0**4)
    # Train_df = (Train_df - 20) / (800 - 20)
    Truth_df_raw = np.array(Truth_df, dtype = np.float)
    Truth_df = norm_array_column(np.array(Truth_df, dtype = np.float))
    
    # shuffle data
    index = [i for i in range(len(Truth_df))]
    np.random.shuffle(index)
    Truth_df = Truth_df[index]
    Train_df = Train_df[index]
    Truth_df_raw_index = Truth_df_raw[index]
    
    # split the train data and test data
    # set the amount of test data as 0.1 times of the whole dataset
    # the names of *_test are the testing data, while the names without _test are training data
    batch = int(np.round(len(Train_df)*0.6/(40*10))*10)
    no_epochs = 200
    test_ratio = 0.2
    validation_split = 0.2
    verbosity = 1
    drop_ratio = 0.1
    
    Truth_df_test = Truth_df[:int(test_ratio*Truth_df.shape[0])]
    Train_df_test = Train_df[:int(test_ratio*Train_df.shape[0])]
    
    Truth_df = Truth_df[int(test_ratio*Truth_df.shape[0]):]
    Train_df = Train_df[int(test_ratio*Train_df.shape[0]):]
    
    """
    3. Train the model
    # The first layer is an LSTM layer with 100 units followed by another LSTM layer with 50 units. 
    # Dropout is also applied after each LSTM layer to control overfitting. 
    # Final layer is a Dense output layer with single unit and linear activation since this is a regression problem.
    (1) define the criteria of accuracy
    (2) build up the model, both regression and classification model
    (3) fit the models
    """

    
    # regression model
    nb_features = Train_df.shape[2]
    nb_out = Truth_df.shape[1]
    
    model1 = Sequential()
    model1.add(LSTM(
             input_shape=(Train_df.shape[1], nb_features),
             units=100,
             return_sequences=True))
    model1.add(Dropout(drop_ratio))
    
    model1.add(LSTM(
              units=10,
              return_sequences=False))
    model1.add(Dropout(drop_ratio))
     
    
    model1.add(Dense(units=nb_out))
    model1.add(Activation("tanh"))
    model1.add(Dense(units=nb_out))
    model1.add(Activation("tanh")) 
    model1.compile(loss='mean_squared_error', optimizer='adam',metrics=[r2_total, r2_loc, r2_hrr, r2_wind])
    
    # fit the network
    history1 = model1.fit(Train_df, Truth_df, epochs=no_epochs, batch_size=batch, validation_split=validation_split /(1 - test_ratio), verbose=verbosity)
    
    model1.save(output_dir + '/tunnel_3D.h5')
    # write the data into sheet
    for out_var in output_variables:
        locals()['sheet_' + out_var].write_row('A' + str(q+1), history1.history[out_var])
    
    
    #######################################################################################
    # check the fitted model
    # results_reg = Inverse_norm_array_column(model1.predict(Train_df))
    results_reg = Inverse_norm_array_column(model1.predict(Train_df_test))
    Truth_df = Truth_df_test
    
    # end of check
    
    
    results_reg_test = Inverse_norm_array_column(model1.predict(Train_df_test))

    # evaluate the model on test data
    loss_test, accuracy_test, mes_loc_test, mes_hrr_test, mse_wind_test = model1.evaluate(Train_df_test,Truth_df_test)
    
    """
    Set the properties of the figures
    """
    
    figure_size_width, figure_size_height = 15, 5
    dpi_figure = 600
    font_size = 11
    
    font1 = {'family':'DejaVu Sans',
              'weight': 'normal',
              'size': font_size,
            }
    
    # filling of column
    patterns_column = ('///','\\\\','---', '++', 'xx', '**', 'oo', 'OO', '..')
    color_column = ('light blue', 'dark red', 'grey')
    
    plot_factor = ['Fire_Loc', 'H_RR', 'Wind_Spe']
    plot_legend_name = ['Location', 'HRR', 'ventilation speed']
    plot_unit =['m', 'MW', 'm/s']
    
    tick_interval_num = 100
    
    # plot the comparison of Location on training data
    
    # data_fuse_interval: the interval of the axis label
    # data_fuse_label: axis label
    # data_fuse_count: count of corresponding to each axis label
    # svae the bar data
    Truth_df_inverse = Inverse_norm_array_column(Truth_df)
    locals()['sheet_' + 'bar_' + str(q)] = workbook.add_worksheet('bar' + str(q))
    locals()['sheet_' + 'bar_' + str(q+1)] = workbook.add_worksheet('bar' + str(q+1))
    i_export_bar_data = 1
    for i_factor in np.arange(len(plot_factor)):
        
        data_fuse_count = 0
        # calculate the interval of ticks
        data_fuse_interval = np.round( (max(Truth_df_inverse[:,i_factor])- min(Truth_df_inverse[:,i_factor])) / (tick_interval_num *2.0), \
                                            int(-1.0 * np.floor(np.log10(max(Truth_df_inverse[:,i_factor]) / tick_interval_num)))) *2.0
            
        # set the size of figure, tick label, and column width 
        data_fuse_label = np.arange(min(Truth_df_inverse[:,i_factor]) - data_fuse_interval,max(Truth_df_inverse[:,i_factor]) \
                                    + data_fuse_interval + Sur_value,data_fuse_interval)
    
        width_column = data_fuse_interval/2
        
        for i_pattern, i_fac_value in enumerate(locals()[plot_factor[i_factor]]):
            data_fuse_index = [i for i in range(Truth_df.shape[0]) if \
                                np.round(Inverse_norm_array_column(Truth_df[i].reshape(1,-1))[0,i_factor]*10,0) == np.round(i_fac_value*10,0)]
            
            data_fuse_count = np.array([0]*data_fuse_label.shape[0])
            for j in np.arange(np.array(data_fuse_index).shape[0]):
                data_fuse_count_index = np.round((results_reg[data_fuse_index[j],i_factor] - \
                                                  (min(Truth_df_inverse[:,i_factor]))) / data_fuse_interval + 1)
                data_fuse_count_index = max(data_fuse_count_index, 0.0)
                data_fuse_count[int(data_fuse_count_index)] += 1
            
            # show in percentage
            data_fuse_count = data_fuse_count/np.sum(data_fuse_count)*100
            
            # set the limitation of x-axis
            Flag_data_fuse_count = 0
            for m in np.arange(len(data_fuse_count)):
                if (Flag_data_fuse_count == 0) & (data_fuse_count[m] >1):
                    limit_min_xaxis_data = m
                    limit_min_xaxis = data_fuse_label[max(m -1,0)]
                    Flag_data_fuse_count = 1
                elif (Flag_data_fuse_count == 1) & (sum(data_fuse_count[:m]) >95) & (data_fuse_count[m] <1):
                    limit_max_xaxis_data = m
                    limit_max_xaxis = data_fuse_label[min(m+1, len(data_fuse_label)-1)]
                    break
            
            # plot the bar figures
            fig_acc = plt.figure(figsize=(figure_size_width, figure_size_height))       
    
            plt.bar(data_fuse_label[limit_min_xaxis_data: limit_max_xaxis_data], data_fuse_count[limit_min_xaxis_data: limit_max_xaxis_data], width=width_column, \
                label=plot_legend_name[i_factor] + '=' + str(int(np.round(locals()[plot_factor[i_factor]][i_pattern]))), hatch=patterns_column[0], \
                color='white', edgecolor='blue')
            
            data_fuse_mean = sum(data_fuse_label *data_fuse_count) / sum(data_fuse_count)
            data_fuse_var = sum((data_fuse_label - data_fuse_mean)**2 * data_fuse_count)/sum(data_fuse_count)
            data_fuse_std = data_fuse_var**(1/2.0)
            # set the properties of the figure
            # tick_params: tick value
            # xlabel: title value
            plt.tick_params(labelsize=font_size)
            plt.xlim((limit_min_xaxis, limit_max_xaxis))
            plt.xlabel('Distributed ' + plot_legend_name[i_factor] + ' (' + plot_unit[i_factor] + ')', font1)
            plt.ylabel('Percentage (%)', font1)
            plt.legend(prop = font1)
            # show and save figures
            fig_acc.savefig(output_dir + '/comparison of ' + plot_legend_name[i_factor] + ' at ' + \
                            str(int(np.round(locals()[plot_factor[i_factor]][i_pattern],2))) + '.png',dpi=dpi_figure)
            # svae the bar data
            print('print results to excel files')
            locals()['sheet_' + 'bar_' + str(q)].write('A' + str(i_export_bar_data), 'comparison of ' + plot_legend_name[i_factor] + ' at ' + \
                  str(int(np.round(locals()[plot_factor[i_factor]][i_pattern]))) + ' ' + plot_unit[i_factor])
            locals()['sheet_' + 'bar_' + str(q)].write_row('A' + str(i_export_bar_data +1), data_fuse_label)
            locals()['sheet_' + 'bar_' + str(q)].write_row('A' + str(i_export_bar_data +2), data_fuse_count)

            locals()['sheet_' + 'bar_' + str(q+1)].write('A' + str(i_export_bar_data), 'comparison of ' + plot_legend_name[i_factor] + ' at ' + \
                  str(int(np.round(locals()[plot_factor[i_factor]][i_pattern]))) + ' ' + plot_unit[i_factor])
            locals()['sheet_' + 'bar_' + str(q+1)].write_row('A' + str(i_export_bar_data +1), np.array([data_fuse_mean]))
            locals()['sheet_' + 'bar_' + str(q+1)].write_row('A' + str(i_export_bar_data +2), np.array([data_fuse_std]))
            
            i_export_bar_data = i_export_bar_data + 3
workbook.close()
