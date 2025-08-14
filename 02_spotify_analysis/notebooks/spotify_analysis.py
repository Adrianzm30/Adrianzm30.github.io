#Importar librerías necesarias
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

#Cargar dataset
df = pd.read_csv("SpotifyFeatures.csv")

#Exploración inicial
print("Columnas:", df.columns)
print("Filas y columnas:", df.shape)
print(df.head())

#Filtrar últimos 3 años (si existe columna 'year' o similar)
if "year" in df.columns:
    df = df[df["year"] >= df["year"].max() - 2]  # Últimos 3 años

#Scatterplot: Popularidad vs Energía
fig1 = px.scatter(
    df,
    x="energy",
    y="popularity",
    color="genre" if "genre" in df.columns else None,
    size="popularity",
    hover_data=["track_name", "artist_name"] if "track_name" in df.columns else None,
    title="Popularidad vs Energía de Canciones"
)
fig1.show()
fig1.write_html("scatter_popularity_energy.html")

#Histograma de duración de canciones
fig2 = px.histogram(
    df,
    x="duration_ms",
    nbins=40,
    color="genre" if "genre" in df.columns else None,
    title="Distribución de Duración de Canciones (ms)"
)
fig2.show()
fig2.write_html("histograma_duracion.html")

#Nube de palabras para géneros
if "genre" in df.columns:
    # Contar frecuencia de géneros
    genre_counts = df['genre'].value_counts()
    
    # Convertir a diccionario para WordCloud
    genre_dict = genre_counts.to_dict()
    
    # Configurar nube de palabras
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        colormap='viridis',  
        max_words=50,        
        prefer_horizontal=0.8,
        min_font_size=10,
        max_font_size=200    
    ).generate_from_frequencies(genre_dict)
    
    
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Distribución de Géneros Musicales en Spotify', fontsize=20, pad=20)
    
  
    plt.savefig('nube_generos_mejorada.png', dpi=300, bbox_inches='tight')
    plt.show()

#Guardar DataFrame limpio
df.to_csv("SpotifyFeatures_clean.csv", index=False)

print("✅ Análisis completado. Archivos HTML y PNG generados.")
