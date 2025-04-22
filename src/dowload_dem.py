import requests
import json
import pandas as pd

class INEGI_API:
    def __init__(self):
        self.url_base = "https://www.inegi.org.mx"
        self.headers = {
            'User-Agent': '####',
            'Accept-Language': '####',
            'Accept-Encoding': '####',
            'Connection': '####',
            'Accept-Encoding': 'identity'
        }

    
    def get_upc(self, clave):
        url = "https://www.inegi.org.mx/app/api/productos/interna_v2/componente/mapas/lista/resultados/"
        payload = {
            "muni": "",
            "loca": "",
            "tema": "193",
            "titg": "",
            "esca": 8,
            "form": "",
            "edic": "",
            "seri": "",
            "clave": clave,
            "rango": "",
            "busc": "",
            "tipoB": 2,
            "adv": False,
            "wordag": "",
            "mkeys": "",
            "mageo": "",
            "formIncl": "",
            "formExcl": "",
            "orden": 4,
            "desc": True,
            "pag": 0,
            "tam": 10
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)         
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result
                else:
                    raise Exception(f"Carta {clave} - {result.get('message', 'Error')}")
            else:
                raise Exception(f"Carta {clave} - Problema en la solicitud - Código de estado: {response.status_code}")
        except Exception as e:
            print( f"Error: {e}" )

    def buscar_liga(self, json, terreno=True, ext='ascii'):
        """
        Busca y devuelve un enlace de descarga para el primer DEM encontrado
        con los parámetros tipo y ext dentro del objeto JSON proporcionado.

        Args:
        - json (dict): Objeto JSON que contiene información del DEM.
        - terreno (Bool): Booleano para filtrar por tipo 'Terreno' (True) o 'Superficie' (False). 
        - ext (str): Extensión ('ascii', 'bil', 'grid', 'tif') del archivo DEM a buscar .

        Returns:
        - str or None: Enlace de descarga del documento encontrado, o None si no se encontró coincidencia.

        Example:
        >>> INEGI_API.buscar_liga(json, True, 'tif')
        """
        try:
            if json is not None:
                
                if json['success']:
                    
                    if terreno:
                        tipo="terreno"
                    else:
                        tipo="superficie"
                    liga = {"liga": ""}
                    for mapa in json['list']['mapas']:
                        for formato in mapa["formatos"]:
                            texto = formato['url']['valor'].lower()
                            if tipo in texto and ext.lower() == 'bil' and "_b.zip" in texto:
                                liga["liga"] = formato['url']['valor']
                                return liga['liga']
                            elif tipo in texto and ext.lower() == 'ascii' and "_as.zip" in texto:
                                liga["liga"] = formato['url']['valor']
                                return liga['liga']
                            elif tipo in texto and ext.lower() == 'grid' and "_gr.zip" in texto:
                                liga["liga"] = formato['url']['valor']
                                return liga['liga']
                            elif tipo in texto and ext.lower() == 'tif' and "_t.zip" in texto:
                                liga["liga"] = formato['url']['valor']
                                return liga['liga']   
                    raise ValueError(f"no tiene el DEM solicitado")   

                else:
                    message = json['message'].replace("para el listado de cartas", "")
                    #clave= json['list']['mapas'][0]['clave_carta']
                    raise Exception(f" {message}")
            else:
                raise Exception(f"sin Json")
            
        except Exception as e:
            print( f"Error: Carta {clave} - {e}" )



    def download_dem(self, clave=None, terreno=True, ext='ascii', folder_output='output/', liga=None):
        """
        Descarga un DEM por su clave, tipo y extensión o por su url, en la carpeta especificada.

        Args:
        - clave (str): Clave única que identifica el documento a descargar.
        - terreno (Bool): Booleano para filtrar por tipo 'Terreno' (True) o 'Superficie' (False). 
        - ext (str): Extensión ('ascii', 'bil', 'grid', 'tif') del archivo DEM a buscar .
        - folder_output (str): Ruta de la carpeta donde se guardarán los documentos descargados.
        - liga (str): Liga de descargar del DEM, si de proporciona se usará en lugar buscar por clave. 

        Returns:
        - None

        Example:
        >>> INEGI_API.download_dem('e14b31d1', 'True, 'tif', 'output/')
        """

        try:
            if clave is None and liga is None:
                raise ValueError("Debe proporcionar  'clave' o 'liga' para descargar el DEM.")
            if (liga is not None):
                
                url = self.url_base + liga
                clave = f"{liga.split('/')[-1].split('_')[0]}" if clave is None else clave

            else:
                salida = self.get_upc(clave)        
                liga = self.buscar_liga(salida, terreno, ext)
                if liga:
                    url = self.url_base + liga
                else:
                    return None        
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                archivo_local = folder_output + clave + ".zip"
                with open(archivo_local, 'wb') as archivo:
                    archivo.write(response.content)
                print(f"{clave} descargado y guardado")

            else:
                raise Exception(f"Problema en la solicitud o descarga - Código de estado: {response.status_code}")
        except Exception as e:
            print( f"Error: Carta {clave} - {e}" )
    



class ProcesadorCartas ():

    def __init__(self, api, cartas):
        self.api = api
        self.cartas = cartas
    
    def crear_df(self):
        """
        Crea un DataFrame de todos los DEM disponibles para la lista de cartas (clave)

        Returns:
        - DataFrame con información de DEM disponibles
        """
        df_ = pd.DataFrame()
        for clave in self.cartas:
            respuesta = self.api.get_upc(clave)
            if respuesta == None:
                continue
            df = pd.json_normalize(respuesta['list']['mapas'], record_path='formatos', meta=['key', 'titulo', 'entidad', 'url', 'edicion', 'escala', 'clave_carta', 'datum', 'iin', 'af'])
            column_order = [
                'key', 'titulo', 'entidad', 'url', 'edicion', 'af', 'escala', 'clave_carta', 'datum', 'iin', 
                'upc', 'imagen', 'siglas', 'absoluto', 'dominio', 'folder', 'extension', 'datos_abiertos',
                'clave', 'peso', 'origen', 'web', 'control', 'url.valor', 'url.target', 'url.estilo', 'adicional.estilo'
            ]

            df = df[column_order]
            df_ = pd.concat([df_, df], ignore_index=True)
            df_['tipo'] = "Terreno"
            df_['tipo'] = df_['titulo'].apply(lambda x: 'Terreno' if 'terreno' in x.lower() else 'Superficie')
            df_['clave_carta'] = df_['clave_carta'].str.lower()
            df_["extension"] = df_["extension"].str.lower()
            df_['id'] = df_['upc'].astype(str) + '_' + df_.index.astype(str)
        return df_
    
    def filtrar_cartas(self, df=None, terreno=True, formatos=['ascii', 'bil', 'grid', 'tif'], year=None, quick=False):
        """
        Filtra y ordena los DEM según criterios especificados.

        Args:
        - df (DataFrame): DataFrame de cartas. Opcional.
        - terreno (Bool): Booleano para filtrar por tipo 'Terreno' (True) o 'Superficie' (False).
        - formatos (list): Lista de formatos de extensión en orden de preferencia, por default ['ascci', 'bil', 'grid', 'tif'] .
        - year (Int): Año mínimo de edición, opcional.
        - quick (Bool): Para regresar un DataFrame con los DEM más recientes de cada carta.

        Returns:
        - DataFrame filtrado, ordenado y agrupado con el DEM más reciente para cada carta.
        """
        if df is None :
            df = self.crear_df()
        
        if terreno:
            df = df[df['tipo'] == 'Terreno'].copy()
        else:
            df = df[df['tipo'] == 'Superficie'].copy()
        
        if year is not None:
            df = df[df['edicion'] >= year].copy()
        
        if quick:
            df = (df.sort_values(["edicion","peso"], ascending=[False,True])
                  .groupby(['clave_carta','tipo']).head(1))
        else:
            df['formato_orden'] = (df['extension']
                                   .apply(lambda x: formatos.index(x) if x in formatos else len(formatos)))
            df = (df.sort_values(by=['formato_orden', 'edicion'], ascending=[True, False]) 
                .groupby(['tipo', 'clave_carta']).head(1))

        return df
