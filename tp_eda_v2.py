import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sbn

pd.options.display.max_columns = None
pd.options.display.max_rows = None

path = "dataset_meli.csv"

df = pd.read_csv(path, sep='|')

print(df.describe())
print(df.isnull().sum())
"""
Realizamos una agrupación por nivel de vendedor para analizar si es recomendable su análisis.
Observamos que existe un claro desbalance entre las diferentes clases, con lo cual no es recomendable realizar
alguna comparativa entre ellas
Lo mismo ocurre con el estatus de cada vendedor.
"""
print(df.groupby('seller_level_id')['seller_level_id'].count())
print(df.groupby('power_seller_status')['power_seller_status'].count())

renamed = {
    "seller_trans_canceled": "canceled",
    "seller_trans_completed": "completed",
    "seller_trans_rating_negative": "rat_negative",
    "seller_trans_rating_neutral": "rat_neutral",
    "seller_trans_rating_positive": "rat_positive",
    "seller_trans_total": "total",
    "seller_metric_sales_completed": "sales_completed",
    "seller_metrics_claims_rate": "claims_rate",
    "seller_metrics_claims_value": "claims_value",
    "seller_metrics_delayed_rate": "delayed_rate",
    "seller_metrics_delayed_value": "delayed_value",
    "seller_metrics_cancellations_rate": "cancellations_rate",
    "seller_metrics_cancellations_value": "cancellations_value"

}
df = df.rename(columns=renamed)

# Aplicamos transformaciones sobre los campos para lograr una mejor representación de los mismos y construimos
# nuevos atributos
df['canceled_rate_perc'] = df.apply(lambda x: (x['canceled'] / x['total']) * 100, axis=1)
df['claims_rate_perc'] = df.apply(lambda x: x['claims_rate'] * 100, axis=1)
df['rat_negative_perc'] = df.apply(lambda x: x['rat_negative'] * 100, axis=1)
df['total_formatted'] = df.apply(lambda x: x['total'] / 1000, axis=1)

# Análisis Exploratorio de Datos
"""
Realizamos un gráfico de barras horizontal para entender a proporción de transacciones realizadas por cada categoría,
de esa forma podremos seleccionar las mas significativas para el usuario.
"""
plt.figure(figsize=(25, 10))
axis = sbn.barplot(data=df, y='category_name', x="total_formatted", errorbar=('ci', False))
axis.set_title('Total de ventas por categoría')
axis.set(xlabel='Categoría', ylabel='Ventas Totales')
for i in axis.containers:
    axis.bar_label(i, fmt='%.1fK')
axis.set_xticklabels(axis.get_xticklabels(), horizontalalignment='center', rotation=0)
plt.show()

"""
Evaluamos la inferencia del envío gratis sobre la cantidad de ventas.
"""
plt.figure(figsize=(16, 10))
axis = sbn.kdeplot(data=df, x='total_formatted', hue='free_shipping', fill=True)
plt.title('Distribución de las transacciones en función del envío gratis')
plt.xlabel('Ventas Totales')
plt.show()
# Observamos una distribución prácticamente normal, con algunos puntos alejados de la media
# También se comprueba una distribución similar entre las ventas con o sin envío gratis

"""
El Mapa de calor nos muestra una representación general de la relación que existe entre las diferentes variables
cuantitativas involucradas.
"""
axis = sbn.heatmap(df[["price", "sold_quantity", "canceled", "completed",
                       "rat_negative", "rat_neutral", "rat_positive",
                       "total", "sales_completed",
                       "claims_value", "delayed_value",
                       "cancellations_value"]].corr(), annot=True)

axis.set_xticklabels(axis.get_xticklabels(), horizontalalignment='center', rotation=90)
plt.show()

# Notamos algunas relaciones obvias entre dos o mas variables, como ser los diferentes ratings
# Algunas relaciones llamativas como que la cantidad de reclamos incrementa tanto en transacciones canceladas como
# completadas.
# Un punto de interés resulta la relación del casi 50% entre las cancelaciones y la demora en el envío asi como también
# la alta correlación entre las transacciones canceladas y la cantidad de reclamos

q_low = df["claims_value"].quantile(0.05)
q_hi = df["claims_value"].quantile(0.95)
df = df[(df["claims_value"] < q_hi) & (df["claims_value"] > q_low)]

q_low = df["canceled"].quantile(0.05)
q_hi = df["canceled"].quantile(0.95)
df = df[(df["canceled"] < q_hi) & (df["canceled"] > q_low)]

q_low = df["delayed_value"].quantile(0.05)
q_hi = df["delayed_value"].quantile(0.95)
df = df[(df["delayed_value"] < q_hi) & (df["delayed_value"] > q_low)]

q_low = df["cancellations_value"].quantile(0.05)
q_hi = df["cancellations_value"].quantile(0.95)
df = df[(df["cancellations_value"] < q_hi) & (df["cancellations_value"] > q_low)]

sbn.jointplot(data=df, x='delayed_value', y='cancellations_value', dropna=True, hue='free_shipping')
# plt.title('Relación Demora - Cancelaciones Pedido')
plt.xlabel('Demora')
plt.ylabel('Cancelaciones')
plt.show()

# Luego del filtrado, notamos que disminuyó la relación entre las cancelaciones y aumentó considerablemente la relación
# con reclamos.
sbn.jointplot(data=df, x='canceled', y='claims_value', kind='reg', dropna=True)
# plt.title('Relación Cancelaciones Transaccionales - Reclamos')
plt.xlabel('Cancelaciones')
plt.ylabel('Reclamos')
plt.show()

"""
Veamos si existe alguna diferencia en cantidad de transacciones si segmentamos por las categorías principales
"""
categories = ["Electrónica, Audio y Video", "Electrodomésticos y Aires Ac.", "Herramientas", "Hogar, Muebles y Jardín"]
categories_out = ["Accesorios para Vehículos", "Animales y Mascotas", "Antigüedades y Colecciones",
                  "Consolas y Videojuegos", "Entradas para Eventos", "Juegos y Juguetes", "Música, Películas y Series",
                  "Ropa y Accesorios", "Souvenirs, Cotillón y Fiestas", "Otras Categorías",
                  "Computación", "Instrumentos Musicales", "Joyas y Relojes", "Agro", "Bebés", "Cámaras y Accesorios"]
df_filtered = df[~df['category_name'].isin(categories_out)]

axis = sbn.catplot(data=df_filtered, y='category_name', x='claims_value', kind='box')
axis.set(xlabel='Reclamos Totales', ylabel='Categorías')
axis.set_xticklabels(rotation=0)
plt.show()

axis = sbn.catplot(data=df_filtered, y='category_name', x='delayed_value', kind='box')
axis.set(xlabel='Demoras Totales', ylabel='Categorías')
axis.set_xticklabels(rotation=0)
plt.show()

axis = sbn.catplot(data=df_filtered, y='category_name', x='cancellations_value', kind='box')
axis.set(xlabel='Cancelaciones Totales', ylabel='Categorías')
axis.set_xticklabels(rotation=0)
plt.show()
# Observamos que las categorías "Alimentos y Bebidas" y "Hogar, Muebles y Jardín" presenta una mayor proporción de sus
# ventas con sin envío gratis en comparación a las otras dos categorías que muestran una distribución mas equitativa
# Seguimos observamos diferentes outliers, principalmente en la categoría "Hogar, Muebles y Jardín"

df_agg = df.groupby('category_name').agg(
    {
        "claims_value": "mean",
        "delayed_value": "mean",
        "canceled": "mean",
        "cancellations_value": "mean"
    }
).reset_index()
agg_fields = ['claims_value', 'delayed_value', 'cancellations_value']
df_agg = df_agg.sort_values(by=agg_fields, ascending=False, ignore_index=True).head(4)

df_agg['total_p'] = df_agg.apply(lambda x: x['claims_value'] + x['delayed_value'] + x['cancellations_value'], axis=1)
df_agg['claims_value_p'] = df_agg.apply(lambda x: x['claims_value'] / x['total_p'], axis=1)
df_agg['delayed_value_p'] = df_agg.apply(lambda x: x['delayed_value'] / x['total_p'], axis=1)
df_agg['cancellations_value_p'] = df_agg.apply(lambda x: x['cancellations_value'] / x['total_p'], axis=1)


ax = sbn.barplot(data=df_agg, x='category_name', y='claims_value_p', color='red', label='Reclamos')
ax = sbn.barplot(data=df_agg, x='category_name', y='delayed_value_p', color='green', label='Demoras')
ax = sbn.barplot(data=df_agg, x='category_name', y='cancellations_value_p', color='blue', label='Cancelaciones')

# Etiquetas
for bar in ax.patches:
    # x, y, s
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 1.6 + bar.get_y(),
            round(bar.get_height(), 2), ha='center',
            color='w', weight='bold', size=10)
plt.xlabel('Categorías')
plt.ylabel('Totales')
plt.legend()
plt.show()

sbn.scatterplot()