#importamos las librerías necesarias
from fastapi import FastAPI
import pandas as pd
import scipy as sp
from sklearn.metrics.pairwise import cosine_similarity


app = FastAPI()

#http://127.0.0.1:8000

#abrimos los archivos en una variable para su manejo en las funciones
df_final = pd.read_parquet('Df_final.parquet')
model = pd.read_parquet('model_render.parquet')

@app.get("/")
async def index():
    return {'Hola, alto ahí escribe /docs al final de la url'}

#Retorna la cantidad e items y el porcentaje de juegos gratis por año segun la desarrolladora
@app.get('/Developer/{desarrollador}')
async def developer(desarrollador:str):

    try:
   
        dta = df_final[df_final['developer'] == desarrollador]

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

@app.get('/UserID/{Usuario}')
async def userdata(user_id:str):

    try:

        data = df_final[df_final['user_id'] == user_id]

        if data.empty:
            return {'Error': f"No se encontraron datos para el usuario don id{user_id}"}
       
        gastado = data['price'].sum()
        #recomendacion = df_final[df_final['user_id'] ==user_id]['recommend'].sum()
        total_recom= len(df_final[df_final['user_id'] == user_id])
        porcentaje = (total_recom/len(df_final['user_id'].unique()))*100

        cont = data['items_count'].iloc[0]
        del data, total_recom
        return [
            {'Cantidad de dinero gastado por el usuario': float(gastado)},
            {'Porcentaje de recomendacion por el usuario': round(float(porcentaje),3)},
            {'Cantidad de items': int(cont)}

        ]
    except Exception as e:
        return{'Error': str(e)} 
    

#Devuelve el usuario que acumula más hrs jugadas para el genero dado y una lista de acummulacion 
#de horas jugadas por año
    
@app.get('/UserForGenre/{Genero}')
async def UserforGenre(genero:str):

    try:
        df_genero = df_final[['genres','user_id','Año', 'playtime_forever']]
        filtro = df_genero[df_genero['genres'] == genero]
        playtime_sum = filtro.groupby(['user_id','Año'])['playtime_forever'].sum()
        user_maxplay = playtime_sum.groupby('user_id').sum().idxmax()
        play_year= playtime_sum.loc[user_maxplay].to_dict()
        del df_genero,playtime_sum #liberamos espacio

        return{'Usuario con más horas jugadas por el género '+ genero+ ' es: '+ str(user_maxplay),
                ' Horas jugadas por año:' + str(play_year)}
    
    except Exception as e:
        return{'Error': str(e)}

#devuelve el top 3 de desarrolladores con más juegos recomendados por usuarios para el año dado
    
@app.get('/BestDeveloperYear/{Year}')

async def best_developer_year(año:int):

    reviesxgames = df_final[['developer','Año', 'recommend','sentiment_analysis']]

    filtro = reviesxgames[(reviesxgames['Año'] == año) & (reviesxgames['recommend'] == True) & (reviesxgames['sentiment_analysis'] == 2)]
    positive= filtro['developer'].value_counts()
    top3_pos_dev= positive.nlargest(3).index.tolist()
    del reviesxgames, filtro, positive

    return[{'Puesto 1': top3_pos_dev[0]},{'Puesto 2': top3_pos_dev[1]}, 
            {'Puesto 3': top3_pos_dev[2]}]


#devuelve un diccionario con el nombre del desarrollador  con los registros de reseñas de usuarios que se encuentren categorizados con un analisis como valor positivo o negaticvo o nuetro

@app.get('/Developer review analysis/{Desarrollador}')

async def developer_review_analysis(desarrolladora:str):

    reviewxgame = df_final[['developer','sentiment_analysis']]
    filtro = reviewxgame[reviewxgame['developer'] == desarrolladora]
    sentiment = filtro['sentiment_analysis'].value_counts().to_dict()
    resultado = {desarrolladora: ['Negative= ' + str(sentiment.get(0,0)), 'Neutral =' + str(sentiment.get(1,0)), 'Positive = ' +str(sentiment.get(2,0))]}
    del reviewxgame, filtro, sentiment

    return resultado

#devuelve una lista con 5 juegos recomendados similares al ingresado

@app.get('/Recomendación de juego/{iddelproducto}')

async def recomendacion_games(item_id:int):
    juego = model[model['item_id'] == item_id]

    if juego.empty:
        return('El juego' + item_id + ' no posee registros en la base de datos' )

    indice = juego.index[0]

    muestra = 2000 
    df_muestra = model.sample(n=muestra, random_state=42)
    
    sim_score = cosine_similarity([model.iloc[indice,3:]], df_muestra.iloc[:,3:])

    sim_score = sim_score[0]

    sim_juegos = [(i, sim_score[i]) for i in range(len(sim_score)) if i != indice]

    sim_juegos =sorted(sim_juegos, key= lambda x: x[1],reverse=True)

    #obtenemos los 5 juegos similares
    sim_gam_ind = [i[0] for i in sim_juegos[:5]]

    sim_game_name = df_muestra['app_name'].iloc[sim_gam_ind].tolist()
    del juego, indice, df_muestra, sim_score, sim_juegos
    return{'Similar games': sim_game_name}
