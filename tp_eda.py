import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sbn

path = "dataset_meli.csv"

df = pd.read_csv(path, sep='|')

# Aplicamos transformaciones sobre los campos para lograr una mejor representación de los mismos
df['seller_trans_canceled_rate_perc'] = df.apply(lambda x: (x['seller_trans_canceled'] / x['seller_trans_total'])*100, axis=1)
df['seller_metrics_claims_rate_perc'] = df.apply(lambda x: x['seller_metrics_claims_rate']*100, axis=1)
df['seller_trans_rating_negative_perc'] = df.apply(lambda x: x['seller_trans_rating_negative']*100, axis=1)
df['seller_trans_total_formatted'] = df.apply(lambda x: x['seller_trans_total']/1000, axis=1)
df['flag_rating_negative'] = df.apply(lambda x: 'Con rating Negativo' if x['seller_trans_rating_negative'] >= 0.05 else 'Sin rating Negativo', axis=1)

plt.figure(figsize=(25, 10))
axis = sbn.barplot(data=df, y='categoria_nombre', x="seller_trans_total_formatted", errorbar=('ci', False))
axis.set_title('Total de ventas por categoría')
axis.set(xlabel='Categoría', ylabel='Ventas Totales')
for i in axis.containers:
    axis.bar_label(i, fmt='%.1fK')
axis.set_xticklabels(axis.get_xticklabels(), horizontalalignment='center', rotation=0)
plt.show()

# seller_trans_canceled, seller_metrics_claims_rate, seller_trans_rating_negative
# Analizamos outliers en el dataset para cada una de las variables en cuestión
# Observamos algunos outliers que "ensucian" de alguna forma la representación de la relación. Por ende, se deciden
# eliminar utilizando un intervalo del 99%
q_low = df["seller_metrics_claims_rate_perc"].quantile(0.01)
q_hi = df["seller_metrics_claims_rate_perc"].quantile(0.99)
df_f = df[(df["seller_metrics_claims_rate_perc"] < q_hi) & (df["seller_metrics_claims_rate_perc"] > q_low)]

q_low = df_f["seller_trans_canceled_rate_perc"].quantile(0.01)
q_hi = df_f["seller_trans_canceled_rate_perc"].quantile(0.99)
df_f = df_f[(df_f["seller_trans_canceled_rate_perc"] < q_hi) & (df_f["seller_trans_canceled_rate_perc"] > q_low)]

# Observamos que no existe relación directa entre calificaciones negativas y cancelaciones de transacciones
figa, axa = plt.subplots(1, 2, figsize=(8, 8))
axis = sbn.scatterplot(data=df, x="seller_metrics_claims_rate_perc", y="seller_trans_canceled_rate_perc", hue='flag_rating_negative', ax=axa[0])
axis.set_title('Relación Reclamos - Cancelaciones (Con Outliers)')
axis.set(xlabel='Reclamos', ylabel='Cancelaciones')
axis.legend(title='Rating')

axis = sbn.scatterplot(data=df_f, x="seller_metrics_claims_rate_perc", y="seller_trans_canceled_rate_perc", hue='flag_rating_negative', ax=axa[1])
axis.set_title('Relación Reclamos - Cancelaciones (Sin Outliers)')
axis.set(xlabel='Reclamos', ylabel='Cancelaciones')
axis.legend(title='Rating')
plt.show()


# Se decide continuar el análisis con las categorías de mayor venta ya que se asume que son las de mayor
# interés para el usuario
# Alimentos y Bebidas, Belleza y Cuidado Personal, Celulares y Teléfonos, Hogar, Muebles y Jardín
categories = ["Alimentos y Bebidas", "Belleza y Cuidado Personal", "Celulares y Teléfonos", "Hogar, Muebles y Jardín"]
df_filtered = df_f[df_f['categoria_nombre'].isin(categories)]
fig, ax = plt.subplots(1, 2, figsize=(8, 8))
axis = sbn.barplot(data=df_filtered, x='categoria_nombre', y="seller_trans_canceled_rate_perc", errorbar=('ci', False), ax=ax[0], hue='flag_rating_negative')
axis.set_title('Proporción de ventas canceladas por categoría')
axis.set(xlabel='Categoría', ylabel='Porcentaje Cancelaciones')
for i in axis.containers:
    axis.bar_label(i, fmt='%.2f%%')
axis.set_xticklabels(axis.get_xticklabels(), horizontalalignment='center', rotation=30)
axis.legend(title='Rating')

axis = sbn.barplot(data=df_filtered, x='categoria_nombre', y="seller_metrics_claims_rate_perc", errorbar=('ci', False), ax=ax[1], hue='flag_rating_negative')
axis.set_title('Proporción de reclamos por categoría')
axis.set(xlabel='Categoría', ylabel='Porcentaje reclamos')
for i in axis.containers:
    axis.bar_label(i, fmt='%.2f%%')
axis.set_xticklabels(axis.get_xticklabels(), horizontalalignment='center', rotation=30)
axis.legend(title='Rating')
plt.show()