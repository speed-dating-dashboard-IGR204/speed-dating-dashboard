"""Functions to produce the sankey diagrams in the app"""

import numpy as np
import plotly.graph_objects as go

from meta_data import id2race, id2study, id2gender


def generate_sankey(df):

    dfGroupByAge = df.groupby(['age', 'gender'])
    dfTraget = dfGroupByAge.get_group((27, 0))  # groupé par femme de 27ans

    targetLabelStudy = [id2study[i] for i in dfTraget.groupby('field_cd').size().index]
    targetLabelRace = [id2race[i] for i in dfTraget.groupby('race').size().index]

    labelIndice = targetLabelStudy + targetLabelRace
    labelIndice.insert(0, 'Cible')

    sourceSankey = list(np.zeros(len(targetLabelStudy), dtype=int))
    targetSankey = [labelIndice.index(i) for i in targetLabelStudy]

    for i, j in dfTraget.groupby(['field_cd', 'race']).size().index:
        sourceSankey.append(labelIndice.index(id2study[i]))
        targetSankey.append(labelIndice.index(id2race[j]))

    valueSankey = list(dfTraget.groupby('field_cd').size().values) + list(dfTraget.groupby(['field_cd', 'race']).size().values)

    return go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=15,
            line=dict(color="blue", width=0.5),
            label=labelIndice,
            color="green"
        ),
        link=dict(
            source=sourceSankey,
            target=targetSankey,
            value=valueSankey
        ))])
