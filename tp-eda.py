import requests as req
import json
import warnings
import pandas as pd

def get_config(file):
    with open(file, 'r') as f:
        return json.loads(f.read())

def reemplaza_vacios (x,leyenda):
    if not x:
        return leyenda
    else:
        return x

warnings.filterwarnings("ignore")

URL_AUTH = "https://auth.mercadolibre.com.ar"
URL_API = "https://api.mercadolibre.com"
APP_ID = "5160542056640612"
CLIENT_SECRET = "L2XERJAzNQKZOme3l4mc6jZyIr93eX6G"
YOUR_URL = "https://www.google.com"
ENDPOINT_AUTH = "authorization"
ENDPOINT_AUTH_TOKEN = "oauth/token"
CODE = "TG-64616dd5b4e0df000189eabc-224825607"

params = {
    "grant_type": "refresh_token",
    "client_id": APP_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": "TG-64616dfb6ea77500012b0274-224825607",
    "redirect_uri": YOUR_URL
}
headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded"
}
response = req.post(URL_API + "/" + ENDPOINT_AUTH_TOKEN, headers=headers, params=params, verify=False)

access_token = response.json().get('access_token')
refresh_token = response.json().get('refresh_token')
expires_in = response.json().get('expires_in')

# print(response.json())

# Obtenemos las categorías
URL = URL_API + "/sites/MLA/categories"
header = {
    "Authorization": f"Bearer {access_token}"
}
response = req.get(URL)
categories = response.json()


config = get_config("tp-eda_cfg.json")

columns = config.get('columns')


df = pd.DataFrame()
# Obtenemos las items
for categorie in categories:
    print("categoria: ", categorie.get('id'))
    URL = URL_API + "/sites/MLA/search"
    header = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "category": categorie.get('id'),
        "offset": 0
    }
    response = req.get(URL, params=params)
    paging = response.json().get('paging')
    items = response.json().get('results')
    df_aux = pd.DataFrame()
    df_aux = pd.concat([df_aux, pd.json_normalize(response.json().get('results'))], axis=0)
    while params.get('offset') < 4:
        params.update({'offset': params.get('offset') + 1})
        response = req.get(URL, params=params)
        items += response.json().get('results')
        df_aux = pd.concat([df_aux, pd.json_normalize(response.json().get('results'))], axis=0)
        # print("filas: ", len(df_aux.axes[0]), "  - columnas: ", len(df_aux.axes[1]))
    df_aux['categoria'] = categorie.get('id')
    print("filas: ", len(df_aux.axes[0]), "  - columnas: ", len(df_aux.axes[1]))
    print("-----------------------------------")
    df = pd.concat([df, df_aux], axis=0)
    # print("******* DF:  filas: ", len(df.axes[0]), "  - columnas: ", len(df.axes[1]))

print("Total de registros consultados: ",len(df))

# Selecciono y renombro columnas
column_selected = [column.get('name') for column in columns if column.get('selected') == 1]
df = df[column_selected]
column_rename = {column['name'] : column['rename'] for column in columns if column['selected'] == 1}
df.rename(columns= column_rename, inplace=True)

# Filtros
df['seller_level_id'] = df['seller_level_id'].map(lambda x: reemplaza_vacios(x,"No identificado"))
df['power_seller_status'] = df['power_seller_status'].map(lambda x: reemplaza_vacios(x,"sin_categoria"))
df = df[df['condition'] == "new"]
df = df[df['buying_mode'] == "buy_it_now"]

# Insert columnas calculadas:
df['flag_rating_positive'] = df['seller_trans_rating_positive'].map(lambda x: 1 if float(x)*100 >= 90 else 0)

print("Total de registros después de filtrar: ",len(df))
print(df.head())
df.to_csv(config.get('filename'), index=False, sep="|")

