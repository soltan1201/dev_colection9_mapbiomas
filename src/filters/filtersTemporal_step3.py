#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
#SCRIPT DE CLASSIFICACAO POR BACIA
#Produzido por Geodatin - Dados e Geoinformacao
#DISTRIBUIDO COM GPLv2
# https://code.earthengine.google.com/0c432999045898bb6e40c1fb7238d32f
'''

import ee
import os 
import gee
import json
import csv
import copy
import sys
import math
import arqParametros as arqParams 
import collections
collections.Callable = collections.abc.Callable
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


class processo_filterTemporal(object):

    options = {
            'output_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV2/',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Frequency',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/merge/',
            # 'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/SpatialV2',
            'input_asset': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/TemporalV2',
            'asset_bacias_buffer' : 'projects/mapbiomas-workspace/AMOSTRAS/col7/CAATINGA/bacias_hidrograficaCaatbuffer5k',            
            'last_year' : 2023,
            'first_year': 1985,
            'janela' : 5
        }

    def __init__(self):
        # self.id_bacias = nameBacia
        self.versoutput = 15
        self.versionInput = 15
        self.geom_bacia = ee.FeatureCollection(self.options['asset_bacias_buffer'])#.filter(
                                                    # ee.Filter.eq('nunivotto3', nameBacia)).first().geometry()              
        self.years = [yy for yy in range(self.options['first_year'], self.options['last_year'] + 1)]  # ,  - 1, -1
        # self.years = [kk for kk in years.sort(reverse= False)]
        self.lstbandNames = ['classification_' + str(yy) for yy in range(self.options['last_year'], self.options['first_year'] - 1, -1)]
        
        print("lista de anos ", self.years)
        self.ordem_exec_first = [21,4,3,12] #
        self.ordem_exec_last = [21,4,3,12]  # 29
        self.ordem_exec_middle = [21,4,3,12] # ,33, 22,      

        colectAnos = [self.mapeiaAnos(
                                ano, self.options['janela'], self.years) for ano in self.years]

        # self.colectAnos = [self.mapeiaAnos(
        #                         ano, self.options['janela'], self.years) for ano in self.years]
        dictYY = {}
        for cc, lstYY in enumerate(colectAnos):
            # print(cc, " <==>  ", lstYY)
            dictYY[str(cc)] = lstYY
        self.colectAnos = []
        for cc in range(len(self.years)-1, -1, -1):
            print(cc, " <> ",dictYY[str(cc)])
            self.colectAnos.append(dictYY[str(cc)])


    ################### CONJUNTO DE REGRAS PARA CONSTRUIR A LISTA DE BANDAS ##############
    def regra_primeira(self, jan, delt, lstYears):
        return lstYears[1 : delt + 1] + [lstYears[0]] + lstYears[delt + 1 : jan]
    def regra_primeiraJ4(self, jan, delt, lstYears):
        return [lstYears[1]] + [lstYears[0]] + lstYears[delt : jan]
    def regra_ultima(self, jan, delt, lstYears):
        print(lstYears[-1 * jan : ])
        return lstYears[-1 * jan : -1 *(delt + 1)] + [lstYears[-1]] + lstYears[-1 * (delt + 1) : -1]    
    def regra_segundo_stepJ5(self, jan, delt, lstYears):
        return [lstYears[0]] + [lstYears[1]] + lstYears[delt : jan]
    def regra_antespenultimo_stepJ5(self, jan, delt, lstYears):
        return [lstYears[-5], lstYears[-3]] + [lstYears[-4]] + lstYears[-2:]
    def regra_penultimo_stepJ5(self, jan, delt, lstYears):
        return [lstYears[-5], lstYears[-2]] + lstYears[-4: -2] + [lstYears[-1]]
    def regra_ultimo_stepJ5(self, jan, delt, lstYears):
        return [lstYears[-5], lstYears[-1]] + lstYears[-4: -1]    
    def regra_penultimo_stepJ4(self, jan, delt, lstYears):
        return [lstYears[-1 * jan]] + [lstYears[-2]] + [lstYears[-3]]  + [lstYears[-1]] 
    # retorna uma lista com as strings referentes a janela dada, por exemplo em janela 5, no ano 1Nan999, o metodo retornaria
    # ['classification_1997', 'classification_1998', 'classification_1999', 'classification_2000', 'classification_2001']
    # desse jeito pode-se extrair as bandas referentes as janelas

    def mapeiaAnos(self, ano, janela, anos):
        lsBandAnos = ['classification_'+str(item) for item in anos]
        # print("ultimo ano ", anos[-1])
        indice = anos.index(ano)
        delta = int(janela / 2)
        resto = int(janela % 2)
        ######### LIST OF BANDS FOR WINDOWS 3 #######################
        if janela == 3:
            if ano == self.options['first_year']:
                return self.regra_primeira(janela, delta, lsBandAnos)
            elif ano == anos[-1]: # igual a ultimo ano 
                return self.regra_ultima(janela, delta, lsBandAnos)
            else:
                return lsBandAnos[indice - delta: indice + delta + resto]
        ######### LIST OF BANDS FOR WINDOWS 4 #######################
        elif janela == 4:
            if ano == self.options['first_year']:
                return self.regra_primeiraJ4(janela, delta, lsBandAnos)
            elif ano == anos[1]:
                return lsBandAnos[:janela]
            elif ano == anos[-2]:
                return self.regra_penultimo_stepJ4(janela, delta, lsBandAnos)
            elif ano == anos[-1]:
                return self.regra_ultima(janela, delta, lsBandAnos)
            else:
                return lsBandAnos[indice - 1: indice + delta + 1]
        ######### LIST OF BANDS FOR WINDOWS 3 #######################
        elif janela == 5:
            if ano == self.options['first_year']:
                return self.regra_primeiraJ4(janela, delta, lsBandAnos)
            elif ano == anos[1]:
                return self.regra_segundo_stepJ5(janela, delta, lsBandAnos)
            elif ano == anos[-3]:
                return self.regra_antespenultimo_stepJ5(janela, delta, lsBandAnos)
            elif ano == anos[-2]:
                return self.regra_penultimo_stepJ5(janela, delta, lsBandAnos)
            elif ano == anos[-1]:
                return self.regra_ultimo_stepJ5(janela, delta, lsBandAnos)  
            else:                  
                return lsBandAnos[indice - 1: indice + 2 * delta]    
           
    def mask_3_years (self, valor, imagem):
        #### https://code.earthengine.google.com/1f9dd3ab081d243fa9d7962e06348579
        imagem = ee.Image(imagem)
        mmask = imagem.select([0]).eq(valor).And(
                    imagem.select([1]).neq(valor)).And(
                        imagem.select([2]).eq(valor)).unmask(0)    
        muda_img = imagem.select([1]).mask(mmask.eq(1)).where(mmask.eq(1), valor)
        return imagem.select([1]).blend(muda_img)

    def mask_4_years (self, valor, imagem):
        imagem = ee.Image(imagem)        
        mmask = imagem.select([0]).eq(valor).And(
                    imagem.select([1]).neq(valor)).And(
                        imagem.select([2]).neq(valor)).And(
                            imagem.select([3]).eq(valor))
        
        muda_img = imagem.select([1]).mask(mmask.eq(1)).where(mmask.eq(1), valor) 
        muda_img_post = imagem.select([2]).mask(mmask.eq(1)).where(mmask.eq(1), valor) 
        img_out = imagem.select([1]).blend(muda_img).blend(muda_img_post)
        return img_out

    def mask_5_years (self, valor, imagem):
        imagem = ee.Image(imagem)
        mmask = imagem.select([0]).eq(valor).And(
                    imagem.select([1]).neq(valor)).And(
                        imagem.select([2]).neq(valor)).And(
                            imagem.select([3]).neq(valor)).And(
                                imagem.select([4]).eq(valor))
        
        
        muda_img = imagem.select([1]).mask(mmask.eq(1)).where(mmask.eq(1), valor) 
        muda_img_post = imagem.select([2]).mask(mmask.eq(1)).where(mmask.eq(1), valor) 
        muda_img_pospos = imagem.select([3]).mask(mmask.eq(1)).where(mmask.eq(1), valor)

        img_out = imagem.select([1]).blend(muda_img).blend(muda_img_post).blend(muda_img_pospos)
        return img_out

    def applyTemporalFilter(self, id_bacias): 
               
        # clase = {
        #         '21': "agro",
        #         '4': 'Florest',
        #         '12': "campo",
        #         '3': 'savana',
        #         '22': 'area naoVeg',
        #         '29': 'aflora'
        #     }
        # self.ordem_exec_first = [29,12,4,21,3,22]
        # self.ordem_exec_last = [29,21]
        if "Temporal" in self.options['input_asset']:
            name_imgClass = 'filterTP_BACIA_'+ str(id_bacias) + f"_GTB_J{self.options['janela'] - 1}_V" + str(self.versoutput)
        else:
            name_imgClass = 'filterSP_BACIA_'+ id_bacias  + "_GTB_V" + str(self.versionInput )
        # name_imgClass = 'filterFQ_BACIA_'+ str(id_bacias) + "_V" + str(self.versionTP)
        # 
        #  projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Frequency/filterFQ_BACIA_744_V13 
        # imgCol = ee.ImageCollection(self.options['input_asset'])
        # colId = imgCol.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
        # print(colId)
        # sys.exit()
        # name_imgClass = 'filterGF_BACIA_'+ id_bacias  + "_V" + self.versionFR 
        # name_imgClass = 'filterFC_BACIA_'+ id_bacias  + "_V" + self.versionFR 
        imgClass = ee.Image(self.options['input_asset'] + "/" + name_imgClass)#.select() 
        print(imgClass.bandNames().getInfo()) 
        # self.colectAnos = self.colectAnos[1:]
        # print(" --------- lista de bandas -------------\n", self.colectAnos)
        if self.options['janela'] == 3:
            for id_class in self.ordem_exec_middle:
                imgOutput = ee.Image().byte()
                print("processing class {} == janela {} ".format(id_class, self.options['janela'] )) 

                for lstyear in self.colectAnos:
                    # print("  => ", lstyear)
                    imgtmp = self.mask_3_years(id_class, imgClass.select(lstyear))
                    imgOutput = imgOutput.addBands(imgtmp)

                imgOutput = imgOutput.select(self.lstbandNames)
                imgClass = imgOutput
                # print("comprovando o número de bandas \n ====>", len(imgOutput.bandNames().getInfo()))
            
            for id_class in self.ordem_exec_last:
                print("processing last 3 years class = ", id_class)
                for lstyear in self.colectAnos:
                    # print("  => ", lstyear)
                    imgtmp = self.mask_3_years(id_class, imgClass.select(lstyear))
                    imgOutput = imgOutput.addBands(imgtmp)

                imgOutput = imgOutput.select(self.lstbandNames)
                imgClass = imgOutput
                # print("comprovando o número de bandas \n ====>", len(imgOutput.bandNames().getInfo()))
        elif self.options['janela'] == 4:
            self.colectAnos = [self.mapeiaAnos(
                                    ano, self.options['janela'], self.years) for ano in self.years]   
            for id_class in self.ordem_exec_middle:
                imgOutput = ee.Image().byte()
                print("processing class {} == janela {} ".format(id_class, self.options['janela']))            
                for lstyear in self.colectAnos:
                    print("  => ", lstyear)
                    imgtmp = self.mask_4_years(id_class, imgClass.select(lstyear))
                    imgOutput = imgOutput.addBands(imgtmp)

                imgOutput = imgOutput.select(self.lstbandNames)
                imgClass = imgOutput
                # print("comprovando o número de bandas \n ====>", len(imgOutput.bandNames().getInfo()))
                # if id_class ==  self.ordem_exec_middle[0]:
                #     print(imgOutput.bandNames().getInfo())
        
        elif self.options['janela'] == 5:
            self.colectAnos = [self.mapeiaAnos(
                                    ano, self.options['janela'], self.years) for ano in self.years]   

            for id_class in self.ordem_exec_middle:
                imgOutput = ee.Image().byte()
                print("processing class {} == janela {} ".format(id_class, self.options['janela']))            
                for lstyear in self.colectAnos:
                    # print("  => ", lstyear)
                    imgtmp = self.mask_5_years(id_class, imgClass.select(lstyear))
                    imgOutput = imgOutput.addBands(imgtmp)

                imgOutput = imgOutput.select(self.lstbandNames)
                imgClass = imgOutput
                print("comprovando o número de bandas \n ====>", len(imgOutput.bandNames().getInfo()))
                if id_class ==  self.ordem_exec_middle[0]:
                    print(imgOutput.bandNames().getInfo())


        
         
        # lst_band_conn = [bnd + '_conn' for bnd in self.lstbandNames]
        # # / add connected pixels bands
        # imageFilledConnected = imgClass.addBands(
        #                             imgClass.connectedPixelCount(10, True).rename(lst_band_conn))
        geom = self.geom_bacia.filter(ee.Filter.eq('nunivotto3', id_bacias)).first().geometry()

        imageFilledConnected = imgClass.set(
                            'version',  self.versoutput, 
                            'biome', 'CAATINGA',
                            'type_filter', 'temporal',
                            'collection', '8.0',
                            'id_bacia', id_bacias,
                            'janela', self.options['janela'],
                            'sensor', 'Landsat', 'model', 'GTB',
                            'system:footprint' , geom
                        )
        imageFilledConnected = ee.Image.cat(imageFilledConnected).clip(geom)
        
        name_toexport = 'filterTP_BACIA_'+ str(id_bacias) + f"_GTB_J{self.options['janela']}_V" + str(self.versoutput)
        self.processoExportar(imageFilledConnected, name_toexport, geom)    

    #exporta a imagem classificada para o asset
    def processoExportar(self, mapaRF,  nomeDesc, geom_bacia):
        
        idasset =  self.options['output_asset'] + nomeDesc
        optExp = {
            'image': mapaRF, 
            'description': nomeDesc, 
            'assetId':idasset, 
            'region': geom_bacia.getInfo()['coordinates'],
            'scale': 30, 
            'maxPixels': 1e13,
            "pyramidingPolicy":{".default": "mode"}
        }
        task = ee.batch.Export.image.toAsset(**optExp)
        task.start() 
        print("salvando ... " + nomeDesc + "..!")
        # print(task.status())
        for keys, vals in dict(task.status()).items():
            print ( "  {} : {}".format(keys, vals))


param = {      
    'numeroTask': 6,
    'numeroLimit': 42,
    'conta' : {
        '0': 'caatinga01',
        '2': 'caatinga02',
        '14': 'caatinga03',
        '21': 'caatinga04',
        '28': 'caatinga05',        
        '35': 'solkan1201',   
    }
}

#============================================================
#========================METODOS=============================
#============================================================
def gerenciador(cont):
    #0, 18, 36, 54]
    #=====================================#
    # gerenciador de contas para controlar# 
    # processos task no gee               #
    #=====================================#
    numberofChange = [kk for kk in param['conta'].keys()]    
    if str(cont) in numberofChange:
        print("conta ativa >> {} <<".format(param['conta'][str(cont)]))        
        gee.switch_user(param['conta'][str(cont)])
        gee.init()        
        gee.tasks(n= param['numeroTask'], return_list= True)        
    
    elif cont > param['numeroLimit']:
        cont = 0
    
    cont += 1    
    return cont


# listaNameBacias = [
#     '744','754','741','7421','7422','745','746','7492','751','752',
#     '753','755','758','759','7621','7622','764','765',
#     '766','767','771','772','7741','7742','773','775','776',
#     '777','778','76111','76116','7612','7614','7615','7616',
#     '7617','7618','7619', '7613',
#     '756','757','763'
# ]

listaNameBacias = [
    '754','756','757','758',
]

aplicando_TemporalFilter = processo_filterTemporal()
# for cc, lst in enumerate(aplicando_TemporalFilter.colectAnos):
#     print(1985 + cc, lst)
# sys.exit()
input_asset = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/POS-CLASS/Temporal/'
version = 15
cont = 0
listBacFalta = []
knowMapSaved = False
for cc, idbacia in enumerate(listaNameBacias[:]):   
    if knowMapSaved:
        try:
            # projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/POS-CLASS/Temporal/filterTP_BACIA_7612_V2
            nameMap = 'filterTP_BACIA_' + idbacia + "_V" + str(version)
            print(input_asset + nameMap)
            imgtmp = ee.Image(input_asset + nameMap)
            print(f" {cc} loading ", nameMap, " ", len(imgtmp.bandNames().getInfo()), "bandas ")
            if cc == 0:
                print('show bands \n ', imgtmp.bandNames().getInfo())
        except:
            listBacFalta.append(idbacia)
    else: 
        cont = gerenciador(cont)
        print("----- PROCESSING BACIA {} -------".format(idbacia))        
        aplicando_TemporalFilter.applyTemporalFilter(idbacia)


if knowMapSaved:
    print("lista de bacias que faltam \n ",listBacFalta)
    print("total ", len(listBacFalta))