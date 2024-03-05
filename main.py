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
    
        for año, grupo in dta.groupby('Año'):
            total_items 0 len(grupo)
            juegos_gratis = len(grupo[grupo['price'] == 0.0])
            porcentaje_gratis = (juegos_gratis/total_items) *100 if total_items >0 else 0
    
            #devolvemos el resultado para el año dado
            yield {
                'Año': año,
                'Cantidad de items': total_items,
                'Porcentaje de juegos gratis': porcentaje_gratis
            }

    except Exception as e:
        #manejo de errores
        yield {'Error': str(e)}
        

#Devuelve la cantidad de dinero gastado para el usuario el porcentaje de recomendación
#en base a reviews recomend y la cantidad de items

