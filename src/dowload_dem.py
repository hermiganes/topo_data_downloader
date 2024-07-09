import requests
import json


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
                return result
            else:
                print(clave + "   Error en la solicitud. Código de estado:", response.status_code)
                return None
        except Exception as e:
            print(clave + "   Error:", str(e))
            return None

    def buscar_liga(self, json, tipo, ext):
        liga = {"liga": ""}
        if not json or not json['success']:
            return None
        
        for mapa in json['list']['mapas']:
            for formato in mapa["formatos"]:
                texto = formato['url']['valor'].lower()
                if tipo in texto and ext == 0 and "_b.zip" in texto:
                    liga["liga"] = formato['url']['valor']
                    return liga['liga']
                elif tipo in texto and ext == 1 and "_as.zip" in texto:
                    liga["liga"] = formato['url']['valor']
                    return liga['liga']
                elif tipo in texto and ext == 2 and "_gr.zip" in texto:
                    liga["liga"] = formato['url']['valor']
                    return liga['liga']
                elif tipo in texto and ext == 3 and "_t.zip" in texto:
                    liga["liga"] = formato['url']['valor']
                    return liga['liga']
                
        
        return None

    def download_dem(self, clave, tipo, ext, folder_output):
        #clave = datos_dem["clave"]
        #tipo = datos_dem["tipo"]
        #ext = datos_dem["ext"]
        #folder_output = datos_dem["folder"]

        salida = self.get_upc(clave)
        
        if salida:
            liga = self.buscar_liga(salida, tipo, ext)
            if liga:
                url = self.url_base + liga
                try:
                    response = requests.get(url, headers=self.headers)
                    if response.status_code == 200:
                        archivo_local = folder_output + clave + ".zip"
                        with open(archivo_local, 'wb') as archivo:
                            archivo.write(response.content)
                        print(clave + "   descargado y guardado")
                    else:
                        print(clave + "   Error en la solicitud. Código de estado:", response.status_code)
                except Exception as e:
                    print(clave + "   Error durante la descarga:", str(e))
            else:
                print(clave, "no tiene información")
        else:
            print(clave, "no se encontró en la base de datos")

