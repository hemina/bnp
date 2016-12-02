
# coding: utf-8

# In[68]:

import pandas as pd
import numpy as np


# In[69]:

# definition of modifiable parameters
PARAM = 20
PARAM_diff = 20

PARAM_abs_v = 4
PARAM_sq_v = PARAM_abs_v**2

PARAM_abs = 4
PARAM_sq = PARAM_abs**2

# definition of work path
PATH = "/Users/hemina/detect_irr/"


# In[70]:

# function in order to find outliers for a unique product_currency
def detectOutliers( df ):
    # set a temporary array for the column that we use often in order to save computational time
    tmp_value_array = df.loc[:,'value']
    diff = np.diff(tmp_value_array)
    
    tmp_diff_value_array = np.append([0],diff)
    df.loc[:,'diff_value'] = tmp_diff_value_array

    # generate a dataframe of outlier as the return object of this function
    outlier = pd.DataFrame(columns=df.columns)
    
    # referring the definition of outliers in boxplot, we regard the values outside mini-maxi range as outliers
    q75, q25 = np.percentile(tmp_value_array, [75 ,25])
    iqr = q75 - q25 # Inner Quartile Range
    mini = q25 - PARAM*iqr
    maxi = q75 + PARAM*iqr
    
    # for those tiny Inner Quartile Range (near zero), we shift the mini/maxi into a more significant value 
    if(mini**2 - PARAM_sq_v)<0:
        mini = mini - PARAM_abs
    if(maxi**2 - PARAM_sq_v)<0:
        maxi = maxi + PARAM_abs_v
    
    # anonymous function to decide if each value in an array is inside or outside the mini-maxi range
    cmpr = lambda val: True if (val<mini or val>maxi) else False
    # ind contains a list ot True/False indicating if the value is an outlier
    ind = map(cmpr, tmp_value_array)
    # if sum(ind)!=0:
    #     print("sum of ind for original value is %lf" %sum(ind))
    #     print("iqr is %lf , q1 is %lf, q3 is %lf, mini is %lf, maxi is %lf \n" %(iqr, q25, q75, mini, maxi))
    
    # repeat the same procedure with diff values
    q75_diff, q25_diff = np.percentile(tmp_diff_value_array, [75 ,25])
    iqr_diff = q75_diff - q25_diff
    mini_diff = q25_diff - PARAM_diff*iqr_diff
    maxi_diff = q75_diff + PARAM_diff*iqr_diff
    
    if(mini_diff**2 - PARAM_sq)<0:
        mini_diff = mini_diff - PARAM_abs
    if(maxi_diff**2 - PARAM_sq)<0:
        maxi_diff = maxi_diff + PARAM_abs
        
    cmpr_diff = lambda val: True if (val<mini_diff or val>maxi_diff) else False
    ind_diff = map(cmpr_diff, tmp_diff_value_array)
    # if sum(ind_diff) !=0:
    #     print("sum of ind for diff value is %lf" %sum(ind_diff))
    #     print("iqr_diff is %lf , q1_diff is %lf, q3_diff is %lf, mini_diff is %lf, maxi_diff is %lf \n" %(iqr_diff, q25_diff, q75_diff, mini_diff, maxi_diff))

    # logical calculate to integrate ind and ind_diff
    ind_final = np.logical_or(ind, ind_diff)
    if sum(ind_final) !=0:
        print("sum of ind for all is %lf \n" %sum(ind_final))
    
    # accomplish the outlier dataframe the combination outliers from original values and diff values
    outlier = outlier.append(df.iloc[ind_final,])   
    
    return outlier


# In[71]:

# function in order to generate all_outliers.csv and product_outlier.csv by giving the name of input data
def gen_output( str_name ):
    # load data
    df = pd.read_csv(PATH + 'data/'+ str_name + '.csv', encoding='utf-8')
    
    # redefine the column names to avoid encoding problems
    df.columns = ["product_id", "type", "value", "currency", "as_of"]
    
    # convert the product_id into string to facilitate the following concatenation
    df['product_id'] = df['product_id'].astype(str)
    
    # create all_outliers dataframe as a container of outliers for all product_id+currency groups
    all_outliers = pd.DataFrame(columns=df.columns)
    
    # create a new column which concatenate product_id and currency 
    df['id_currency'] = df['product_id'] + " " + df['currency']

    # split the whole dataframe into small ones by product_id+currency
    grouped = df.groupby(['id_currency'], sort = False)

    # for each small group of product_id+currency, we calculate the outliers, and we integrate outliers from different groups into all_outliers
    for name, group in grouped:
        #print name
        dftmp = df[df['id_currency']==name]
        outlier = detectOutliers(dftmp)
        all_outliers = all_outliers.append(outlier)

    #all_outliers.size #127788 when 1000, 142110 when 5000, 159600 when 200,174084 when 500/800
    #202896 when 1200, 14322 when 5000,14322 when 50000

    # 16452 when 50, 
    # 11562 when 50
    # 11550 when 50
    # 14292 when 30
    # 20340 when 10

    #all_outliers.head

    #len(np.unique(all_outliers['product_id']))
    #56 when 50, 95 when 30, 300 when 10

    # save all_outliers file 
    all_outliers.to_csv(PATH+ 'all_outliers/'+ str_name + '.csv', sep=';', index=True, encoding='utf-8')

    # show the product id which contains outliers
    product_out = np.unique(all_outliers['product_id'])
    product_out = pd.DataFrame(product_out)
    product_out.columns = ["product_id"]
    # save product_outlier file
    product_out.to_csv(PATH + 'product_outlier/'+ str_name + '.csv', sep=';', index=True, encoding='utf-8')
    return


# In[ ]:

# generate outlier files for the perf type
gen_output('perf')

# generate outlier files for the bench type
gen_output('bench')


# In[ ]:



