import pandas as pd
import numpy as np


def var_binaire(note):
    if note > 5:
        return 1
    else:
        return 0


def income_cat(income):
    incomeF = float(str(income).replace(',', ''))
    if incomeF < 50000.00:
        return 'medium'
    elif incomeF < 110000.00:
        return 'rich'
    else:
        return 'very rich'


def discretize_age(age):
    """ 4 classe d'age pour echantillon homogène"""
    if age < 23 :
        return 0
    elif age < 26 :
        return 1
    elif age < 29 :
        return 2
    else :
        return 3


def cleanDF(df_Speedating):
    #df_Speedating['imprelig']=df_Speedating['imprelig'].apply(lambda x : var_binaire(x))
    df_Speedating['sports']=df_Speedating['sports'].apply(lambda x : var_binaire(x))
    df_Speedating['tvsports']=df_Speedating['tvsports'].apply(lambda x : var_binaire(x))
    df_Speedating['exercise']=df_Speedating['exercise'].apply(lambda x : var_binaire(x))
    df_Speedating['dining']=df_Speedating['dining'].apply(lambda x : var_binaire(x))
    df_Speedating['museums']=df_Speedating['museums'].apply(lambda x : var_binaire(x))
    df_Speedating['hiking']=df_Speedating['hiking'].apply(lambda x : var_binaire(x))
    df_Speedating['clubbing']=df_Speedating['clubbing'].apply(lambda x : var_binaire(x))
    df_Speedating['tv']=df_Speedating['tv'].apply(lambda x : var_binaire(x))
    df_Speedating['theater']=df_Speedating['theater'].apply(lambda x : var_binaire(x))
    df_Speedating['movies']=df_Speedating['movies'].apply(lambda x : var_binaire(x))
    df_Speedating['concerts']=df_Speedating['concerts'].apply(lambda x : var_binaire(x))
    df_Speedating['shopping']=df_Speedating['shopping'].apply(lambda x : var_binaire(x))
    df_Speedating['yoga']=df_Speedating['yoga'].apply(lambda x : var_binaire(x))
    df_Speedating['income']=df_Speedating['income'].apply(lambda x : income_cat(x))
    df_Speedating['age_class'] = df_Speedating['age'].apply(lambda x: discretize_age(x))

    return df_Speedating


def get_df_users(df_Speedating):
    df_user = (
        df_Speedating[["iid", "age", "field_cd", "race", "goal", "date", "go_out", "career"]]
        .groupby("iid")
        .first()
        .reset_index()
    )

    return df_user

def df_hobbies_creation(df_sous_Speed):
    df_hobbies = df_sous_Speed.drop_duplicates(subset='iid').reset_index(drop=True)[
        ['sports', 'tvsports', 'exercise', 'dining', 'museums', 'hiking', 'clubbing', 'tv', 'theater', 'movies', 'concerts', 'shopping',
         'yoga']]
    return df_hobbies