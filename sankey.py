"""Functions to produce the sankey diagrams in the app"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from functools import reduce


from meta_data import id2race, id2study, id2label_dict, id2id, id2age
import plotly.express as px

secondary_graph_height=400

def generate_sankey(df,age,gender,imprelig=None):
    if imprelig:
        dfGroupByAge = df.groupby(['age', 'gender','imprelig'])
        df_target = dfGroupByAge.get_group((age, gender,imprelig))  # groupé par femme de 27ans
    else:
        dfGroupByAge = df.groupby(['age', 'gender'])
        df_target = dfGroupByAge.get_group((age, gender))  # groupé par femme de 27ans
        
    target_label_study = [id2study[i] for i in df_target.groupby('field_cd').size().index]
    target_label_race = [id2race[i] for i in df_target.groupby('race').size().index]

    label_indice = target_label_study + target_label_race
    label_indice.insert(0, 'Cible')

    source_sankey = list(np.zeros(len(target_label_study), dtype=int))
    target_sankey = [label_indice.index(i) for i in target_label_study]

    for i, j in df_target.groupby(['field_cd', 'race']).size().index:
        source_sankey.append(label_indice.index(id2study[i]))
        target_sankey.append(label_indice.index(id2race[j]))

    value_sankey = list(df_target.groupby('field_cd').size().values) + list(df_target.groupby(['field_cd', 'race']).size().values)

    return (go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=15,
            line=dict(color="blue", width=0.5),
            label=label_indice,
            color="green"
        ),
        link=dict(
            source=source_sankey,
            target=target_sankey,
            value=value_sankey
        ))]),

        go.Figure(data=[go.Histogram(x=df_target['income'])])
    )


def make_target_label(target_dict):
    label = ""
    if "gender" in target_dict:
        label += "Femme\n" if target_dict["gender"] == 0 else "Homme\n"
    if "age_class" in target_dict:
        label += " " + id2age[target_dict["age_class"]] + "\n"
    if "race" in target_dict:
        label += " " + id2race[target_dict["race"]] + "\n"

    return label

def transform_df(df_dates, df_users, target_dict,criteria_cols):

    
    target_dict.update({"match": 1})  # select matches
    target_select = reduce(lambda x, y: x.__and__(y), [(df_dates[k] == v) for k, v in target_dict.items()])
    df_target = df_dates[target_select]

    return df_target

def generate_sankey_multi(df_dates, df_users, target_dict, criteria_cols):
    """
    Parameters
    ----------
    df_dates : pandas.DataFrame
        The speed dating data frame.
    df_users : pandas.DataFrame
        The data frame with one user per row. 
    target_dict : dict
        The dictionary describing the target user features. Each key, value pair of the dictionary must correspond to an
        existing column name, value pair of the speed dating dataframe.
    criteria_cols : list(str)
        The list of columns to use as criteria, in the order. They will produce a series of chaining sankey diagrams.

    Returns
    -------
    plotly.Graph : the sankey diagram.
    """
    df_target=transform_df(df_dates, df_users, target_dict, criteria_cols)
    target_label = make_target_label(target_dict)

    # Log the amount of data after each selection
    #print(target_dict, sum(target_select))
    # Join the target dates with the user df on the pid (partner id)
    #print(df_users.columns)
    df_join = df_target[["iid", "pid"]].merge(df_users[["iid"] + criteria_cols], left_on="pid", right_on="iid")
    #print(df_join.columns, criteria_cols)

    # Build the unique node ids
    node_label2id = {("target", "target"): 0}
    node_id = 1
    for col in criteria_cols:
        df_group = df_join.groupby([col]).size().to_frame().rename(columns={0: "n"}).sort_values(["n"], ascending=False)
        uniques = df_group.index.tolist()
        for val in uniques:
            node_label2id.update({(col, val): node_id})
            node_id += 1

    # Prepare the very first part of the diagram data
    col = criteria_cols[0]
    df_group = df_join.groupby([col]).size().to_frame().rename(columns={0: "n"}).sort_values(["n"], ascending=False)
    col_unique_values = df_group.index.tolist()  # df_target[col].dropna().unique()
    source_sankey = [0] * len(col_unique_values)
    target_sankey = [node_label2id[(col, val)] for val in col_unique_values]
    label_sankey = [target_label] + [id2label_dict.get(col, id2id)[val] for val in col_unique_values]
    value_sankey = [df_group.loc[c1, "n"] for c1 in col_unique_values]
    # print(label_sankey, value_sankey)
    # Continue the diagram data
    prev_col = col
    for col in criteria_cols[1:]:
        df_group = df_join.groupby([prev_col, col]).size().to_frame().rename(columns={0: "n"}).sort_values("n", ascending=False)
        # prev_col_unique_values = col_unique_values.copy()
        # col_unique_values = df_target[col].dropna().unique()
        for s, t in df_group.index.tolist():
            source_sankey.append(node_label2id[(prev_col, s)])
            if node_label2id[(col, t)] not in target_sankey:
                label_sankey.append(id2label_dict.get(col, id2id)[t])
                # print(label_sankey[-1])
            target_sankey.append(node_label2id[(col, t)])
            value_sankey.append(df_group.loc[(s, t), "n"])
            # print(id2label_dict.get(prev_col, id2id)[s], id2label_dict.get(col, id2id)[t], value_sankey[-1])
        prev_col = col
    couleurs = px.colors.qualitative.Plotly \
               + px.colors.qualitative.D3 \
               + px.colors.qualitative.Dark2 \
               + px.colors.qualitative.Safe \
               + px.colors.qualitative.Antique \
               + px.colors.qualitative.Pastel2 \
               + px.colors.qualitative.Set2 \
               + px.colors.qualitative.Prism

    colorNode = couleurs[:len(label_sankey)]

    return go.Figure(data=[
        go.Sankey(
            node=dict(
                pad=15,
                thickness=15,
                line=dict(color="blue", width=0.5),
                label=label_sankey,
                color=colorNode
            ),
            link=dict(
                source=source_sankey,
                target=target_sankey,
                value=value_sankey
            )
        ),
    ],
        layout={"plot_bgcolor": "rgba(0,0,0,0)", "title_text": target_label}
    ).update_layout(height=700, font_size=10)

def update_histogram(df_dates, df_users,target_dict,criteria_cols):
        df_target=transform_df(df_dates, df_users,target_dict,criteria_cols)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=df_target['income'].where(df_target['tuition_bin']==0),
                                name='No tuition fee',
                                opacity=0.8
        ))
        fig.add_trace(go.Histogram(x=df_target['income'].where(df_target['tuition_bin']==1),
                                name='Tuition fee',
                                opacity=0.8
        ))
        fig.update_layout(
            barmode='stack',
            title_text='Number of Student per Income class', # title of plot
            xaxis_title_text='Income Class', # xaxis label
            yaxis_title_text='Number of Student', # yaxis label
            height=secondary_graph_height
        )
        return fig


def update_map(df_dates, df_users, target_dict, criteria_cols):
    df_target = transform_df(df_dates, df_users, target_dict, criteria_cols)
    df_map = df_users.loc[df_users['iid'].isin(df_target['iid'].unique())]

    fig = px.scatter_mapbox(df_map, lat="lat", lon="lon",
                            # hover_name="City", hover_data=["State", "Population"],color_discrete_sequence=["fuchsia"],
                            zoom=3, height=secondary_graph_height)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


    #df_target = transform_df(df_dates, df_users, target_dict, criteria_cols)
    #fig = go.Figure()
    #fig.add_trace(go.Histogram(x=df_target['income'].where(df_target['tuition_bin'] == 0),
    #                           name='No tuition fee',
    #                           opacity=0.8
    #                           ))
    #fig.add_trace(go.Histogram(x=df_target['income'].where(df_target['tuition_bin'] == 1),
    #                           name='Tuition fee',
    #                           opacity=0.8
    #                           ))
    #fig.update_layout(
    #    barmode='stack',
    #    title_text='Number of Student per Income class',  # title of plot
    #    xaxis_title_text='Income Class',  # xaxis label
    #    yaxis_title_text='Number of Student',  # yaxis label
    #)
    return fig
        
        
            
""" go.Histogram(x=df_target['income'],
                                name='Money Distribution',
                                opacity=0.8)]) """