"""Functions to produce the sankey diagrams in the app"""

import numpy as np
import plotly.graph_objects as go

from meta_data import id2race, id2study, id2gender


def generate_sankey(df, age, gender):

    df_group_by_age = df.groupby(['age', 'gender'])
    df_target = df_group_by_age.get_group((age, gender))  # groupé par femme de 27ans

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

    return go.Figure(data=[go.Sankey(
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
        ))])
