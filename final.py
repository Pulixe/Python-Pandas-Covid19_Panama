#Adeel Gajia
#Francisco Pulice
#Holman Bonilla
#Daniel Díaz
#Miguel Li

import geopandas as gpd
import pandas as pd
import unidecode
import PIL
import io
    
# Lectura de archivo de casos por semana
corona_df = pd.read_csv(".\CASOSCOVID2019.csv")

# Lectura de shapefile de corregimientos de Panamá
corregimientos = gpd.read_file('.\pan_admbnda_2020_shp\pan_admbnda_adm3_2020.shp',encoding= 'utf-8')

# Renombrar columna de corregimiento en el mapa para que tengan el mismo nombre y facilitar la unión
corregimientos = corregimientos.rename(columns={'ADM3_ES': 'CORREGIMIENTO'})

# Rscribiendo todos los corregimientos en mayúscula en ambos dataframes
corona_df.CORREGIMIENTO= [c.upper() for c in corona_df.CORREGIMIENTO]
corregimientos.CORREGIMIENTO= [c.upper() for c in corregimientos.CORREGIMIENTO]

# Remover tildes en los nombres de los corregimientos
corregimientos.CORREGIMIENTO= [unidecode.unidecode(col) for col in corregimientos.CORREGIMIENTO]

# Unión por campo de nombre de corregimiento
joined_df = corona_df.merge(corregimientos, on='CORREGIMIENTO', how='right')
joined_df = joined_df.fillna(0)

# Transformación a GeoDataFrame para trabajar los mapas
joined_geo = gpd.GeoDataFrame(joined_df, geometry='geometry')

# Transposición de datos para realizar plots comparación por corregimientos si se desea
data_transposed = joined_df.set_index('CORREGIMIENTO').T
# de 3 a 17 ya que estas son las únicas filas con valores numéricos de semanas
casos_semana = data_transposed.iloc[3:21,]
casos_semana.plot(y=['ARRAIJAN','BETANIA','ANCON'], use_index = True, marker = '*')

# Lista para contener las imágenes del gif 
image_frames = []

# Para cada valor de fecha se dibuja un gráfico del mapa
for fechas in joined_geo.columns.to_list()[3:22]:
    ax = joined_geo.plot(column = fechas,
                      cmap = 'OrRd',
                      figsize = (14,14),
                      legend = True,
                      scheme = 'user_defined',
                      classification_kwds = {'bins': [10,20,50,100,500,1000]},
                      edgecolor = 'black',
                      linewidth = 0.4)
    
    # Título del Mapa
    ax.set_title('Casos de Coronavirus por Corregimiento '+fechas, fontdict = {'fontsize':20}, pad =12.5)
    
    # Quitar Ejes
    ax.set_axis_off()
    
    # Mover leyenda
    ax.get_legend().set_bbox_to_anchor((0.05,0.5))

    # Guardar imagen a la memoria temporal
    img = ax.get_figure()
    f = io.BytesIO()
    img.savefig(f, format='png', bbox_inches = 'tight')
    f.seek(0)
    image_frames.append(PIL.Image.open(f))

# Crear el GIF
image_frames[0].save('animacion_covid.gif',
                     format='GIF',
                     append_images = image_frames[1:],
                     save_all = True,
                     duration = 500,
                     loop = 3)

f.close()