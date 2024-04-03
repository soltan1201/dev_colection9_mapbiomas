
import sys
import os 
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
# import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go
# from plotly.validators.scatter.marker import SymbolValidator
# raw_symbols = SymbolValidator().values
# print("lista de markers ", raw_symbols)


def get_interval_to_plot(df_Cobert, lstColunas):
    pmtroDict = {}

    for cobert in lstColunas:
        # print("classe ", cobert)
        maxVal = df_Cobert[df_Cobert["classe"] == cobert]['area'].max()
        minVal = df_Cobert[df_Cobert["classe"] == cobert]['area'].min()
        if maxVal > minVal:
            amp = maxVal - minVal
            intervalo = int(amp / 5)
            ampDown = minVal * 0.3
            ampUp = maxVal * 0.20

            # print("cobertura=> ", cobert, " | Min ", minVal ,  ' | max ', maxVal, ' | Amp ', amp, " | interval ", intervalo)
            maxVal += ampUp
            if ampDown > 0:
                minVal -= ampDown
            else:
                minVal += ampDown
            amp = maxVal - minVal
            intervalo = int(amp / 5)
            # print(" ----> cobertura=> ", cobert, " | Min ", minVal ,  ' | max ', maxVal, ' | Amp ', amp, " | interval ", intervalo)
            dict_temp = {'range': [minVal, maxVal], 'dtick': intervalo,}
            pmtroDict[str(cobert)] = dict_temp
        else:
            dict_temp = {'range': [minVal, maxVal], 'dtick': 0,}
            pmtroDict[str(cobert)] = dict_temp

    return pmtroDict


def get_interval_geral_plot(df_Cobert, lstColunas):
    pmtroDict = {}
    
    maxVal = df_Cobert[df_Cobert["classe"].isin(lstColunas)]['area'].max()
    minVal = df_Cobert[df_Cobert["classe"].isin(lstColunas)]['area'].min()
    if maxVal > minVal:
        amp = maxVal - minVal
        intervalo = int(amp / 5)
        ampDown = minVal * 0.3
        ampUp = maxVal * 0.20

        # print("cobertura=> ", cobert, " | Min ", minVal ,  ' | max ', maxVal, ' | Amp ', amp, " | interval ", intervalo)
        maxVal += ampUp
        if ampDown > 0:
            minVal -= ampDown
        else:
            minVal += ampDown
        amp = maxVal - minVal
        intervalo = int(amp / 5)
        # print(" ----> cobertura=> ", cobert, " | Min ", minVal ,  ' | max ', maxVal, ' | Amp ', amp, " | interval ", intervalo)
        pmtroDict = {'range': [minVal, maxVal], 'dtick': intervalo,}
        
    else:
        pmtroDict = {'range': [minVal, maxVal], 'dtick': 0,}
        

    return pmtroDict


def buildingPlots_x_Class(df_class, lstclass, nameArea):
    coluna = 3
    nameArea = nameArea.replace('areasPrioritCSV/', '')
    # print("lista de classes ", lstclass)
    dictPmtrosPlot = get_interval_to_plot(df_class, lstclass)
    print("dictionario classe ")
    for kk, val in dictPmtrosPlot.items():
        print(kk, " ", val)
    dictPmtros = {
            'height': 800,
            'width': 800,
            'template':'plotly_white'
        }
    # sys.exit()
    nRowplot = int(len(lstclass) / coluna) + 1
    figPlotC = make_subplots(rows= nRowplot, cols= coluna)

    for cc, nclase in enumerate(lstclass): 
        kcol = cc % coluna
        krow = int(cc / coluna)
        print(cc, krow, kcol)
        print(colors[cc], nclase)
          
        figPlotC.add_trace(
                go.Scatter(
                    x= df_class[df_class['classe'] == nclase]['year'], 
                    y= df_class[df_class['classe'] == nclase]['area'], 
                    marker_color= colors[cc],
                    marker_symbol= 'star-open',
                    name= dict_class[str(nclase)] 
                ),
                row=krow + 1, col= kcol + 1
            )
        figPlotC.update_xaxes(title_text=dict_class[str(nclase)], row= krow + 1, col= kcol + 1)
        if cc < 1:
            mkey = 'yaxis'
        else:
            mkey = 'yaxis' + str(cc + 1)
        dictPmtros[mkey] = dictPmtrosPlot[str(nclase)]

    figPlotC.update_layout(dictPmtros)
    figPlotC.update_layout(height=800, width=1600, title_text="bacia " + nameArea, showlegend=False)
    figPlotC.update_layout(showlegend= True)
    # figPlot.show()
    print(f" saving plot Class {nameArea}.png ")
    figPlotC.write_image(f"graficosAreasPrior/{nameArea}.png")
    plt.clf()
    # export as static image
    # pio.write_image(fig, "op.pdf")


def buildingPlots_Cruzando_Class(df_class, lstclass, nameArea):
    coluna = 3
    nameArea = nameArea.replace('areasPrioritCSV/', '')
    # print("lista de classes ", lstclass)
    dictPmtrosPlot = get_interval_geral_plot(df_class, lstclass)
    print("dictionario classe ", dictPmtrosPlot)    
    dictPmtros = {
            'height': 600,
            'width': 800,
            'template':'plotly_white'
        }
    # sys.exit()
    
    figPlotCr = make_subplots(rows= 1, cols= 1)
    for cc, nclase in enumerate(lstclass):        
        # print(colors[cc], nclase)          
        figPlotCr.add_trace(
                go.Scatter(
                    x= df_class[df_class['classe'] == nclase]['year'], 
                    y= df_class[df_class['classe'] == nclase]['area'], 
                    marker_color= colors[cc],
                    marker_symbol= 'star-open',
                    name= dict_class[str(nclase)] 
                ),
                row= 1, col= 1
            )
        figPlotCr.update_xaxes(title_text= dict_class[str(nclase)], row= 1, col= 1)

        dictPmtros['yaxis'] = dictPmtrosPlot

    figPlotCr.update_layout(dictPmtros)
    figPlotCr.update_layout(height=600, width=800, title_text="cruzandoAreas_" + nameArea, showlegend=False)
    figPlotCr.update_layout(showlegend= True)
    # figPlot.show()
    print(" ", "cruzandoAreas_" + nameArea)
    figPlotCr.write_image("graficosAreasPrior/{}.png".format("cruzandoAreas_" + nameArea))
    # export as static image
    # pio.write_image(fig, "op.pdf")
    plt.clf()


def plotPie_extremosSerie(dfArea, nyear, nameArea, dict_colors):
    nameArea = nameArea.replace('areasPrioritCSV/', '')

    fig_pie = px.pie(
                values = dfArea[dfArea['year'] == nyear]['area'],
                names = dfArea[dfArea['year'] == nyear]['cobertura'],
                color = dfArea[dfArea['year'] == nyear]['cobertura'],
                color_discrete_map = dict_colors,
                hole= 0.45,
                width=1200,
                height=650
               )
    fig_pie.update_traces(
                textfont_size=18,
                textinfo=' percent'  # value +
                )
    fig_pie.update_layout(
                    title={
                        'text': '<i><b>Distribuição {} Caatinga {} <br />'.format(nameArea, nyear),
    #                             'y':0.7,
                                'x':0.45,
                                'xanchor': 'center',
                                'yanchor': 'top',
                                'font': dict(color= "black",size=25, family='Verdana')
                        },
    #                 margin = dict(l=350, r=200, pad=100),
    #                 title_pad_t = 380,
                )

    # fig_1985.show()
    print("plot areas plot pie ", nameArea)
    fig_pie.write_image("graficosAreasPrior/{}_{}.png".format("Pie_Areas_" + nameArea, str(nyear)))
    plt.clf()

def plot_Sankey_map_classCober(dfArea, nyearF, nyearS, nameArea, dict_colors):
    figSank = go.Figure(
                    data=[go.Sankey(
                            valueformat = ".0f",
                            valuesuffix = "TWh",
                            node = dict(
                            pad = 15,
                            thickness = 15,
                            line = dict(color = "black", width = 0.5),
                            label =  data['data'][0]['node']['label'],
                            color =  data['data'][0]['node']['color']
                            ),
                            link = dict(
                            source =  data['data'][0]['link']['source'],
                            target =  data['data'][0]['link']['target'],
                            value =  data['data'][0]['link']['value'],
                            label =  data['data'][0]['link']['label']
                        ))])

    figSank.update_layout(
            hovermode = 'x',
            title="Energy forecast for 2050<br>Source: Department of Energy & Climate Change, Tom Counsell via <a href='https://bost.ocks.org/mike/sankey/'>Mike Bostock</a>",
            font=dict(size = 10, color = 'white'),
            plot_bgcolor='black',
            paper_bgcolor='black'
    )
    figSank.write_image("graficosAreasPrior/{}_{}_{}.png".format("SankeyMap_Areas_" + nameArea, str(nyear)))
    figSank.show()

def set_columncobertura(nrow):
    nclasse = nrow['classe']
    nrow['cobertura'] = dict_class[str(nclasse)]
    return nrow

# 100 arvores
nameVetors = []

 # "#fff3bf",,"#45C2A5"
filesAreaCSV = glob.glob('areasPrioritCSV/*.csv')
classes = [3,4,12,15,18,21,22,29,33]
columnsInt = [
    'Forest Formation', 'Savanna Formation', 'Grassland', 'Pasture',
    'Agriculture', 'Mosaic of Uses', 'Non vegetated area', 'Rocky Outcrop', 
    'Water'
]
colors = [ 
    "#006400", "#32CD32", "#B8AF4F", "#FFD966", "#E974ED", 
    "#FFFFB2", "#EA9999", "#FF8C00", "#0000FF"
]
# bacia_sel = '741'

dict_class = {
    '3': 'Forest Formation', 
    '4': 'Savanna Formation', 
    '12': 'Grassland', 
    '15': 'Pasture', 
    '18': 'Agriculture', 
    '21': 'Mosaic of Uses', 
    '22': 'Non vegetated area', 
    '29': 'Rocky Outcrop', 
    '33': 'Water'
}

dict_colors = {}
for ii, cclass in enumerate(classes):
    dict_colors[dict_class[str(cclass)]] = colors[ii]
lst_df_conse = []
lst_df_semi = []
groupConserva = False
groupSemiarido = False

# for kk, vv in dict_color.items():
#     print(kk, " ", vv)
# sys.exit()
for cc, nfile in enumerate(filesAreaCSV):

    print(f"*** Loading {nfile} ****")
    if cc > -1:
        if 'prioridade-conservacao' in nfile:
            tmp_df_Area = pd.read_csv(nfile)
            tmp_df_Area = tmp_df_Area[tmp_df_Area['classe'] != 0]
            tmp_df_Area = tmp_df_Area.drop(['system:index', '.geo'], axis='columns')
            tmp_df_Area = tmp_df_Area.apply(set_columncobertura, axis= 1)
            print(tmp_df_Area.head(2))
            lst_df_conse.append(tmp_df_Area)
            if len(lst_df_conse) > 1:
                groupConserva = True

        elif 'class_semiarido' in nfile:
            tmp_df_Area = pd.read_csv(nfile)
            tmp_df_Area = tmp_df_Area[tmp_df_Area['classe'] != 0]
            tmp_df_Area = tmp_df_Area.drop(['system:index', '.geo'], axis='columns')
            tmp_df_Area = tmp_df_Area.apply(set_columncobertura, axis= 1)
            print(tmp_df_Area.head(2))
            lst_df_semi.append(tmp_df_Area)
            if len(lst_df_semi) > 1:
                groupSemiarido = True

        else:
            # pass
            df_Area = pd.read_csv(nfile)
            df_Area = df_Area[df_Area['classe'] != 0]
            print(df_Area.shape)
            print(df_Area.columns)
            df_Area = df_Area.drop(['system:index', '.geo'], axis='columns')
            df_Area = df_Area.apply(set_columncobertura, axis= 1)
            print(df_Area.head(2))
            # print(df_Area['classe'].unique())
            # print(df_tmp['year'].value_counts())
            df_Area = df_Area.sort_values(by='year')

            buildingPlots_x_Class(df_Area, classes,  nfile.replace("class_", ""))
            buildingPlots_Cruzando_Class(df_Area, [3,4,12,15,18,21],  nfile.replace("class_", ""))

            plotPie_extremosSerie(df_Area, 1985, nfile.replace("class_", "").replace(".csv", ""), dict_colors)
            plotPie_extremosSerie(df_Area, 2022, nfile.replace("class_", "").replace(".csv", ""), dict_colors)


if groupConserva:
    print()
    ndfAcc = pd.concat(lst_df_conse, ignore_index= True)
    print("columna ", ndfAcc.columns)
    # print(ndfAcc.head(1))
    print(" SMUDANDO ")
    lstInt = ['classe', 'cobertura', 'year']  # 'area', 
    lstAll = ['classe', 'cobertura', 'year', 'area']  # 
    groupDF = ndfAcc[lstAll].groupby(lstInt).agg('sum').reset_index();
    print(groupDF.head(2))
    groupDF = groupDF.sort_values(by='year')
    print(groupDF.shape)
    buildingPlots_x_Class(groupDF, classes,  nfile.replace("class_", ""))
    buildingPlots_Cruzando_Class(groupDF, [3,4,12,15,18,21],  nfile.replace("class_", ""))

    plotPie_extremosSerie(df_Area, 1985, 'areasPrioritCSV/prioridade-conservacao' , dict_colors)
    plotPie_extremosSerie(df_Area, 2022, 'areasPrioritCSV/prioridade-conservacao', dict_colors)


if groupSemiarido:
    print()
    ndfAcc = pd.concat(lst_df_semi, ignore_index= True)
    print("columna ", ndfAcc.columns)
    print(ndfAcc.head(1))
    print(" SMUDANDO ")
    lstInt = ['classe', 'cobertura', 'year']  # 'area', 
    lstAll = ['classe', 'cobertura', 'year', 'area']  # 
    groupDF = ndfAcc[lstAll].groupby(lstInt).agg('sum').reset_index();
    print(groupDF.head(2))
    print(groupDF.shape)
    groupDF = groupDF.sort_values(by='year')
    buildingPlots_x_Class(groupDF, classes,  nfile.replace("class_", ""))
    buildingPlots_Cruzando_Class(groupDF, [3,4,12,15,18,21],  nfile.replace("class_", ""))

    plotPie_extremosSerie(df_Area, 1985, 'areasPrioritCSV/Semiarido' , dict_colors)
    plotPie_extremosSerie(df_Area, 2022, 'areasPrioritCSV/Semiarido', dict_colors)