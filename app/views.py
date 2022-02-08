from django.shortcuts import render,HttpResponse,redirect


#new import 

from django.http import HttpResponse, HttpResponseNotFound
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import pathlib
from os import path
from os import listdir
from os.path import isfile, join
from django.contrib import messages

### for verufy data
import pandas as pd
import numpy as np
from pandas import ExcelWriter
from openpyxl import Workbook
from openpyxl.styles import PatternFill

# Create your views here.

class Beginning():

    def index(request):

        uno = 1

        #upload files

        ################################ 
        ############# upload base

        folder = 'media/dirt' 

        filename = 'media/dirt/dirt.xlsx' 
        try:
            if request.method == 'POST' and request.FILES['upload']:
                upload = request.FILES['upload']
                fss = FileSystemStorage(location=folder)
                if os.path.isfile(filename):
                        os.remove(filename)
                #file = fss.save(upload.name, upload)
                file = fss.save("dirt.xlsx", upload)
                file_url = fss.url(file)


                
            ################################ 
            ############# Clean data
                df1 = pd.read_excel(filename)

                ### Changes name columns
                dfnuevo = df1.rename(columns={'Fecha de llegada a Colombia (Día/Mes/Año)':'Fecha de llegada a Colombia',
                            'Sexo biológico':'Sexo', 
                            'Lugar de procedencia\n':'Lugar de procedencia', 
                            'Edad':'Edad (especifiquela en años)',
                            'Fecha diligenciamiento (Día/Mes/Año) ':'Fecha diligenciamiento ',
                            'Canal para el reporte':'Canal o medio de reporte ',
                            'Razón por la cual no entra a la ruta de ICBF':'Razón por la cual NO ingresa a la ruta de ICBF',
                            'lugar de destino':'Pais de destino',
                            'motivo de ingreso a Colombia ':'Motivo de ingreso a Colombia ',
                            'motivo de la salida de su país de origen ':'Motivo de la salida de su país de origen ',
                            'Otra condición':'Comentarios adicionales',
                            'Otra Condición':'Comentarios adicionales',
                            'Lactantes':'Lactante','Perfíl migratorio':'Perfil migratorio',
                            'Indígena':'Indígena'})


                ### Create columns
                if 'Canal o medio de reporte ' not in dfnuevo:
                    dfnuevo['Canal o medio de reporte '] = np.nan
                    
                if 'Étnia' not in dfnuevo:
                    dfnuevo['Étnia'] = np.nan
                    
                # if 'Indígena' not in dfnuevo:
                #     dfnuevo['Indígena'] = np.nan

                ### Count row
                contar = len(dfnuevo.index)

                ### Delete blank space date
                def fechasLlegada():
                    for i in range(contar):
                        try:
                            dfnuevo['Fecha de llegada a Colombia'][i] = pd.to_datetime(dfnuevo['Fecha de llegada a Colombia'][i], dayfirst=True)
                        except:
                            dfnuevo['Fecha de llegada a Colombia'][i] = dfnuevo['Fecha de llegada a Colombia'][i]
                fechasLlegada()

                def fechasDiligenciamiento():
                    for i in range (contar):
                        try:
                            dfnuevo['Fecha diligenciamiento '][i] = pd.to_datetime(dfnuevo['Fecha diligenciamiento '][i], dayfirst=True)
                        except:
                            dfnuevo['Fecha diligenciamiento '][i] = dfnuevo['Fecha diligenciamiento '][i]
                fechasDiligenciamiento()

                ### Correccion tipo
                def tipo():
                    dfnuevo['Tipo'].replace(
                        to_replace=['No acompañado'],
                        value='No acompañado/a',
                        inplace=True
                    )

                    dfnuevo['Tipo'].replace(
                        to_replace=['Separado'],
                        value='Separado/a',
                        inplace=True
                    )
                tipo()

                ### Correccion sexo
                def sexo ():
                    dfnuevo['Sexo'].replace(
                        to_replace=['Mujer'],
                        value='Femenino',
                        inplace=True
                    )
                    dfnuevo['Sexo'].replace(
                        to_replace=['mujer'],
                        value='Femenino',
                        inplace=True
                    )
                    dfnuevo['Sexo'].replace(
                        to_replace=['Mujer '],
                        value='Femenino',
                        inplace=True
                    )
                    dfnuevo['Sexo'].replace(
                        to_replace=['mujer '],
                        value='Femenino',
                        inplace=True
                    )
                    dfnuevo['Sexo'].replace(
                        to_replace=['Hombre'],
                        value='Masculino',
                        inplace=True
                    )
                    dfnuevo['Sexo'].replace(
                        to_replace=['hombre'],
                        value='Masculino',
                        inplace=True
                    )
                    dfnuevo['Sexo'].replace(
                        to_replace=['hombre '],
                        value='Masculino',
                        inplace=True
                    )
                    dfnuevo['Sexo'].replace(
                        to_replace=['Hombre '],
                        value='Masculino',
                        inplace=True
                    )                       
                sexo ()

                ### Verify days and months

                def VerificacionDiasMeses(dfnuevo):
        
                    global lista_dia, lista_meses

                    lista_dia = []
                    lista_meses = []
                    
                    for i in range(contar):
                    
                        try:
                            Dias = dfnuevo['Fecha diligenciamiento '][i] - dfnuevo['Fecha de llegada a Colombia'][i]
                            lista_dia.append(Dias.days)
                            lista_meses.append(Dias.days/30)
                            
                        except:
                            Dias = ''
                            lista_dia.append(Dias)
                            lista_meses.append(np.nan)
                            
                VerificacionDiasMeses(dfnuevo)

                dfnuevo['Días entre llegada e identificación'] = lista_dia
                dfnuevo['Tiempo en meses'] = lista_meses

                ### Correct dates 

                def CompararFechasIngresoDiligenciamiento(dfnuevo):
        
                    number = dfnuevo['Días entre llegada e identificación']
                    if not isinstance(number,int): 
                        css = 'background-color: yellow'
                        #return None
                    elif  int(number) < 0:
                        css = 'background-color: yellow'
                    else:
                        css = 'background-color: none'
                    return [css] * len(dfnuevo)

                # Verificación gestantes

                def verificaciónGestantes(dfnuevo):
                    Sexo = dfnuevo['Sexo']
                    Gestante = dfnuevo['Gestante']
                    if (Sexo == 'Masculino') and (Gestante == 'Si'):
                        css = 'background-color: darkturquoise'
                    elif (Sexo == 'Masculino') and (Gestante == 'si'):
                        css = 'background-color: darkturquoise'
                    else:
                        css = 'background-color: none'
                    return [css] * len(dfnuevo)

                def verificaciónLactantes(dfnuevo):
                    Sexo = dfnuevo['Sexo']
                    Lactantes = dfnuevo['Lactante']
                    if (Sexo == 'Masculino') and (Lactantes == 'Si'):
                        css = 'background-color: deepskyblue'
                    elif (Sexo == 'Masculino') and (Lactantes == 'si'):
                        css = 'background-color: deepskyblue'    
                    else:
                        css = 'background-color: none'
                    return [css] * len(dfnuevo)

                ### Reorganizar columnas

                # dfnuevo = dfnuevo.reindex(columns=['Tipo','Mes','Fecha de llegada a Colombia','Edad','Sexo','OSIGD','Nombres ',
                #                                 'Apellidos','Documento de Identidad','Lugar de procedencia','Lugar de Identificación ',
                #                                 'Municipio','Organización/agencia que identifica','Fecha diligenciamiento ','Días entre llegada e identificación',
                #                                 'Tiempo en meses','Observaciones de contacto','Acciones adelantadas','Remitido a ICBF ','Canal o medio de reporte ',
                #                                 'Ingresó a la ruta ICBF','Razón por la cual NO ingresa a la ruta de ICBF','Lugar de destino','Motivo de ingreso a Colombia ',
                #                                 'Motivo de la salida de su país de origen ','Discapacidad física o cognitiva','Gestante','Lactante',
                #                                 'Inasistencia alimentaria','Desescolarizado','Trabajo Infantil ','Étnia','Perfil migratorio','Indígena','Otra Condición'])


                dfnuevo.style.\
                    apply(CompararFechasIngresoDiligenciamiento, subset=['Fecha de llegada a Colombia', 'Fecha diligenciamiento ', 'Días entre llegada e identificación', 'Tiempo en meses'], axis=1).\
                    apply(verificaciónGestantes, subset=['Sexo', 'Gestante'], axis=1).\
                    apply(verificaciónLactantes, subset=['Sexo', 'Lactante'], axis=1).\
                    highlight_null(null_color='orange').\
                    to_excel('media/clean/clean.xlsx', engine='openpyxl')
                    # highlight_null(null_color='orange').\
                    #hide_index()
                    #to_excel('media/clean/clean.xlsx', engine='openpyxl')                

            ################################ 
            ############# upload multiple files

            context = { 

                'uno':uno,
                'file_url': file_url,

            }

            return render(request, 'index.html', context) 
        
        # Si no carga nada, devuelve a la misma pagina
        except:
            return render(request, 'index.html',) 


class loadFiles():

    def load(request):

        uno = 1

        folder = 'media/loadFiles' 
        folderfiles = 'media/loadFiles' 
            #folderLista = 'media/lista' 
        folderUnion = 'media/UnionData' 

        try:

        
            if request.method == 'POST' and request.FILES['upload']:
                #upload = request.FILES['upload']
                upload = request.FILES.getlist("upload")
                fss = FileSystemStorage(location=folder)
                name = 'base'
                contar = len(upload)
                for i in upload:
                    fss.save(str(i), i)

                arr = os.listdir(folderfiles)

                contar = len(arr)
                        
                for i in range(contar):

                    name = str(arr[i])
                    finalPath = str(folderfiles+'/'+name)

                    globals()[f'df_{i}'] = pd.read_excel(finalPath, index_col=None)
                        #globals()[f'df_{i}'] = pd.DataFrame(os.path.join(folder,name))
            
                if contar == 1:
                    frames = [df_0]
                elif contar == 2:
                    frames = [df_0, df_1]
                elif contar == 3:
                    frames = [df_0, df_1, df_2]
                elif contar == 4:
                    frames = [df_0, df_1, df_2, df_3]
                elif contar == 5:
                    frames = [df_0, df_1, df_2, df_3, df_4]
                elif contar == 6:
                    frames = [df_0, df_1, df_2, df_3, df_4, df_5]
                elif contar == 7:
                    frames = [df_0, df_1, df_2, df_3, df_4, df_5, df_6]
                elif contar == 8:
                    frames = [df_0, df_1, df_2, df_3, df_4, df_5, df_6, df_7]
                elif contar == 9:
                    frames = [df_0, df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_8]
                else:
                    frames = [df_0, df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_8] 


                UnionDf = pd.concat(frames)

                print(UnionDf)

                print(arr)


                def CompararFechasIngresoDiligenciamiento(UnionDf):
            
                    number = UnionDf['Días entre llegada e identificación']
                    if not isinstance(number,int): 
                        css = 'background-color: yellow'
                        #return None
                            
                    elif  int(number) < 0:
                        css = 'background-color: yellow'
                    else:
                        css = 'background-color: none'

                    return [css] * len(UnionDf)

                def verificaciónGestantes(UnionDf):
                    Sexo = UnionDf['Sexo']
                    Gestante = UnionDf['Gestante']
                    if (Sexo == 'Masculino') and (Gestante == 'Si'):
                        css = 'background-color: darkturquoise'
                    else:
                        css = 'background-color: none'
                    return [css] * len(UnionDf)

                def verificaciónLactantes(UnionDf):
                    Sexo = UnionDf['Sexo']
                    Lactantes = UnionDf['Lactante']
                    if (Sexo == 'Masculino') and (Lactantes == 'Si'):
                        css = 'background-color: deepskyblue'
                    else:
                        css = 'background-color: none'
                    return [css] * len(UnionDf)


                # UnionDf = UnionDf.reindex(columns=['Tipo','Mes','Fecha de llegada a Colombia','Edad','Sexo','OSIGD','Nombres ',
                #                                 'Apellidos','Documento de Identidad','Lugar de procedencia','Lugar de Identificación ',
                #                                 'Municipio','Organización/agencia que identifica','Fecha diligenciamiento ','Días entre llegada e identificación',
                #                                 'Tiempo en meses','Observaciones de contacto','Acciones adelantadas','Remitido a ICBF ','Canal o medio de reporte ',
                #                                 'Ingresó a la ruta ICBF','Razón por la cual NO ingresa a la ruta de ICBF','Lugar de destino','Motivo de ingreso a Colombia ',
                #                                 'Motivo de la salida de su país de origen ','Discapacidad física o cognitiva','Gestante','Lactante',
                #                                 'Inasistencia alimentaria','Desescolarizado','Trabajo Infantil ','Étnia','Perfil migratorio','Indígena','Otra Condición'])

                UnionDf.reset_index(drop=True).style.\
                    apply(CompararFechasIngresoDiligenciamiento, subset=['Fecha de llegada a Colombia', 'Fecha diligenciamiento ', 'Días entre llegada e identificación', 'Tiempo en meses'], axis=1).\
                    apply(verificaciónGestantes, subset=['Sexo', 'Gestante'], axis=1).\
                    apply(verificaciónLactantes, subset=['Sexo', 'Lactante'], axis=1).\
                    highlight_null(null_color='orange').\
                    to_excel('media/UnionData/union.xlsx', engine='openpyxl')

                fss = FileSystemStorage(location=folderUnion)

                for i in range(contar):
                    name = str(arr[i])
                    finalPath = str(folderfiles+'/'+name)
                    if os.path.isfile(finalPath):
                            os.remove(finalPath)


            # return redirect("app:cargar")
            return render(request, 'union.html') 
 
        # else:

        except:

            return render(request, 'union.html') 

