#importamos las librerías necesarias
from fastapi import FastAPI
import pandas as pd
import scipy as sp
from sklearn.metrics.pairwise import cosine_similarity


app = FastAPI()

#http://127.0.0.1:8000

#abrimos los archivos en una variable para su manejo en las funciones
df_developer = pd.read_parquet('df_developer.parquet')

@app.get("/")
async def index():
    return {'Hola, alto ahí escribe /docs al final de la url'}

#Retorna la cantidad e items y el porcentaje de juegos gratis por año segun la desarrolladora
@app.get('/Developer/{desarrollador}')
async def developer(desarrollador:str):

    try:
   
        dta =df_developer[df_developer['developer'] == desarrollador]

        gruop_anio= dta.groupby('Año')['item_id'].count()
        free = dta[dta['price']==0.0].groupby('Año')['item_id'].count()
        free_porcentaje = (free/gruop_anio*100).fillna(0).astype(int)
        del free, dta
        retorno ={}
        for i in range(len(gruop_anio.index)):
            retorno['Año_'+ str(gruop_anio.index[i])] =(
                ' Cantidad de items por año:' + str(gruop_anio.values[i])+ 
                '- Porcentaje de juegos gratis:' + str(free_porcentaje.values[i])
                )

        return retorno
    except Exception as e:
        return{'Error': str(e)}
    
#Devuelve la cantidad de dinero gastado para el usuario el porcentaje de recomendación
#en base a reviews recomend y la cantidad de items

