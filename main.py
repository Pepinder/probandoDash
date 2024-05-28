import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import os

# Leer los datos
df = pd.read_csv('raw_data/datosEncuestaGalleta.csv')
port = int(os.environ.get("PORT", 8050))

# Remover espacios en los nombres de las columnas
df.columns = df.columns.str.strip()

# Eliminar la columna "Marca temporal"
df = df.drop(columns=["Marca temporal"])

# Procesamiento adicional para columnas a separar por ';'
columns_to_split = [
    "Seleccione el rango etario al cual pertenece",
    "Seleccione nacionalidad a la que pertenece",
    "¿Cuántas veces a la semana realiza actividad física de al menos 30 minutos al día?",
    "¿Con cuánta frecuencia consume galletas?",
    "¿En qué tiempo de comida suele consumir galletas?",
    "¿Qué tipo de galletas consume?",
    "¿Cuántas unidades suele consumir de galletas?",
    "¿En qué se fija al momento de comprar una galleta?",
    "Considerando su respuesta anterior, ¿cuál es el factor más importante para usted al momento de comprar una galleta?",
    "¿Suele leer los ingredientes de estas galletas?",
    "¿Consume galletas con alguno de estos ingredientes que aportan fibra dietética, enfocados en mejorar la salud intestinal?",
    "¿Se siente satisfecho luego del consumo de galletas?",
    "¿Ha notado diferencias en la sensación de plenitud (sentirse satisfecho) cuando consume galletas azucaradas en comparación a las integrales?",
    "¿Cuánto dinero está dispuesto a pagar al momento de comprar un paquete de galletas?",
    "¿Estaría dispuesto a pagar más por una galleta de mejor composición nutricional que presente beneficios para su salud digestiva?",
    "¿Usted consumiría galletas preparadas con harina de cáscara de papa?",
    "¿Cuál de estos factores consideraría más importante al momento de comprar una galleta elaborada con cáscara de papa?",
    "¿Cuál de las siguientes afirmaciones refleja mejor su opinión sobre galletas con cáscara de papas?"
]

for column in columns_to_split:
    df[column] = df[column].astype(str).str.split(';')

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout de la aplicación
app.layout = html.Div(children=[
    html.H1(children='Análisis de Datos de Galletas'),

    # Contenedor para el menú desplegable del rango etario
    dcc.Dropdown(
        id='age-range-dropdown',
        options=[{'label': age, 'value': age}
                 for age in df["Seleccione el rango etario al cual pertenece"].explode().unique()],
        value=df["Seleccione el rango etario al cual pertenece"].explode().unique()[
            0],
        style={'margin-top': '10px'}
    ),

    # Contenedor para el menú desplegable de la columna
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns],
        value=df.columns[1],
        style={'margin-top': '10px'}
    ),

    # Contenedor para el total de datos
    html.Div(id='total-data', style={'margin': '20px 0',
             'font-size': '20px', 'font-weight': 'bold'}),

    # Contenedor para el gráfico
    dcc.Graph(id='bar-chart')
], style={'font-family': 'Arial, sans-serif', 'background-color': '#f8f5f2', 'color': '#333', 'padding': '20px'})

# Callback para actualizar el gráfico y el total de datos basado en los dropdowns seleccionados


@app.callback(
    [Output('total-data', 'children'),
     Output('bar-chart', 'figure')],
    [Input('age-range-dropdown', 'value'),
     Input('column-dropdown', 'value')]
)
def update_content(selected_age_range, selected_column):
    # Filtrar los datos para el rango etario seleccionado
    subset = df[df["Seleccione el rango etario al cual pertenece"].apply(
        lambda x: selected_age_range in x)]

    # Explode the selected column to handle multiple values in a list
    exploded_df = subset.explode(selected_column)

    # Calcular el número total de datos
    total_data = exploded_df[selected_column].notna().sum()

    # Calcular las frecuencias
    counts = exploded_df[selected_column].value_counts().reset_index()
    counts.columns = [selected_column, 'count']

    # Crear el gráfico de barras
    fig = px.bar(counts, x=selected_column, y='count', text='count',
                 title=f'Frecuencia de {selected_column} para {selected_age_range}')

    # Actualizar los colores del gráfico
    fig.update_layout(
        plot_bgcolor='#f8f5f2',
        paper_bgcolor='#f8f5f2',
        font=dict(color='#333'),
        title_font=dict(size=20, color='#663399', family='Arial, sans-serif')
    )
    fig.update_traces(marker_color='#663399', textfont_size=12,
                      textangle=0, textposition="outside", cliponaxis=False)

    # Texto para el número total de datos
    total_data_text = f'Total de datos: {total_data}'

    return total_data_text, fig


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True, port=port)
