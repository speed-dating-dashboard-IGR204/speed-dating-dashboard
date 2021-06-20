"""Functions to produce the sankey diagrams in the app"""

import numpy as np
import plotly.graph_objects as go
from functools import reduce

from meta_data import id2race, id2study, id2label_dict, id2id


def generate_sankey(df,**kwargs):
    if kwargs['imprelig']:
        dfGroupByAge = df.groupby(['age', 'gender','imprelig'])
        df_target = dfGroupByAge.get_group((kwargs['age'], kwargs['gender'],kwargs['imprelig']))  # groupé par femme de 27ans
    else:
        dfGroupByAge = df.groupby(['age', 'gender'])
        df_target = dfGroupByAge.get_group((kwargs['age'], kwargs['gender']))  # groupé par femme de 27ans
        
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


def generate_sankey_multi(df,target_dict,criteria_cols):
    """
    Parameters
    ----------
    df : pandas.DataFrame
        The speed dating data frame.
    target_dict : dict
        The dictionary describing the target user features. Each key, value pair of the dictionary must correspond to an
        existing column name, value pair of the speed dating dataframe.
    criteria_cols : list(str)
        The list of columns to use as criteria, in the order. They will produce a series of chaining sankey diagrams.

    Returns
    -------
    plotly.Graph : the sankey diagram.
    """

    target_select = reduce(lambda x, y: x.__and__(y), [(df[k] == v) for k, v in target_dict.items()])
    df_target = df[target_select]

    # Build the unique node ids
    node_label2id = {("target", "target"): 0}
    node_id = 1
    for col in criteria_cols:
        df_group = df_target.groupby([col]).size().to_frame().rename(columns={0: "n"}).sort_values(["n"], ascending=False)
        uniques = df_group.index.tolist()
        for val in uniques:
            node_label2id.update({(col, val): node_id})
            node_id += 1

    # Prepare the very first part of the diagram data
    col = criteria_cols[0]
    df_group = df_target.groupby([col]).size().to_frame().rename(columns={0: "n"}).sort_values(["n"], ascending=False)
    col_unique_values = df_group.index.tolist()  # df_target[col].dropna().unique()
    source_sankey = [0] * len(col_unique_values)
    target_sankey = [node_label2id[(col, val)] for val in col_unique_values]
    label_sankey = ["target"] + [id2label_dict.get(col, id2id)[val] for val in col_unique_values]
    value_sankey = [df_group.loc[c1, "n"] for c1 in col_unique_values]
    # print(label_sankey, value_sankey)
    # Continue the diagram data
    prev_col = col
    for col in criteria_cols[1:]:
        df_group = df_target.groupby([prev_col, col]).size().to_frame().rename(columns={0: "n"}).sort_values("n", ascending=False)
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

    return go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=15,
            line=dict(color="blue", width=0.5),
            label=label_sankey,
            color="green"
        ),
        link=dict(
            source=source_sankey,
            target=target_sankey,
            value=value_sankey
        ))])