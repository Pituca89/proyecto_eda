import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sbn

path = "dataset_meli.csv"
df = pd.read_csv(path, sep='|')
df['porcent_canceladas'] = df.apply(lambda x: x['seller_trans_canceled'] / x['seller_trans_total'], axis=1)

plt.figure(figsize=(25, 10))
plt.xticks(rotation=90)
axis = sbn.barplot(data=df, y='categoria_nombre', x="seller_trans_total", errorbar=('ci', False))
for i in axis.containers:
    axis.bar_label(i, )
plt.legend(loc='upper left', bbox_to_anchor=(1, 0.95))
axis.set_xticklabels(axis.get_xticklabels(), horizontalalignment='center', rotation=0)
plt.show()

plt.figure(figsize=(25, 10))
plt.xticks(rotation=90)
axis = sbn.barplot(data=df, y='categoria_nombre', x="porcent_canceladas", errorbar=('ci', False))
for i in axis.containers:
    axis.bar_label(i, )
plt.legend(loc='upper left', bbox_to_anchor=(1, 0.95))
axis.set_xticklabels(axis.get_xticklabels(), horizontalalignment='center', rotation=0)
plt.show()

# Arriba de 0.068
categories = ['Consolas y Videojuegos', 'Ropa y Accesorios', 'Otras Categorías', 'Electrónica, Audio y Video', 'Joyas y Relojes']
df_filtered = df[df.categoria_nombre.isin(categories)]

_, ax = plt.subplots(1, 2, figsize=(25, 10))

sbn.catplot(data=df_filtered, x='categoria_nombre', y='seller_trans_total', kind='box', ax=ax[0])
q_low = df_filtered["seller_trans_total"].quantile(0.01)
q_hi = df_filtered["seller_trans_total"].quantile(0.99)
df_filtered = df_filtered[(df_filtered["seller_trans_total"] < q_hi) & (df_filtered["seller_trans_total"] > q_low)]
sbn.catplot(data=df_filtered, x='categoria_nombre', y='seller_trans_total', kind='box', ax=ax[1])
plt.show()

sbn.jointplot(data=df_filtered, x="porcent_canceladas", y="seller_metrics_claims_rate", kind='hex')
plt.show()
sbn.scatterplot(data=df_filtered, x="porcent_canceladas", y="seller_metrics_claims_rate", hue='categoria_nombre')
plt.show()


_, ax = plt.subplots(1, 2, figsize=(25, 10))
# sbn.set_palette(palette=sbn.color_palette(['green', 'blue', 'red', 'orange']))
axisa = sbn.kdeplot(data=df_filtered, x='porcent_canceladas', hue='categoria_nombre', ax=ax[0], multiple="stack")
axisa.set(title="Distribución de cancelaciones")
axisb = sbn.kdeplot(data=df_filtered, x='seller_metrics_claims_rate', hue='categoria_nombre', ax=ax[1], multiple="stack")
axisb.set(title="Distribución de rating negativos")
plt.show()
