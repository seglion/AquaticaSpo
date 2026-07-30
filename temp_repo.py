import httpx
import json
import os
import scipy.io as scio
import scipy.interpolate as interpolate
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from app.users.domain.models import User
from app.forecastSystem.application.services import ForecastWorkerService
from app.forecastSystem.domain.models import DownloadedData, ForecastSystem,ForecastZone


def _datetime_to_datenum(dt):
    return dt.to_julian_date() + 1721058.5

def cart2pol_mv(x, y):
    r = np.sqrt(x**2+y**2)
    theta = np.degrees(np.arctan2(y, x))
    return r, theta


def pol2cart(r, theta):
    x = r * np.cos(np.radians(theta))
    y = r * np.sin(np.radians(theta))
    return (x, y)

class ForecastWorkerRepository(ForecastWorkerService):
    """Implementación del repositorio de Propagacion."""
    def _datetime_to_datenum(self,dt):
        return dt.to_julian_date() + 1721058.5

    def _create_api_client(self, requester: User) -> httpx.AsyncClient:
        """Método auxiliar para crear y configurar un cliente HTTP con autenticación."""
        if not requester.is_admin:
            raise PermissionError("Se requieren permisos de administrador para esta operación.")
        
        backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
        headers = {"Authorization": f"Bearer {requester.session_USER}"}
        return httpx.AsyncClient(base_url=backend_url, headers=headers)

    async def get_forecast_system(self, forecast_id: int, requester: User) -> ForecastSystem:
        async with self._create_api_client(requester) as client:
            try:
                response = await client.get(f"/forecast-systems/{forecast_id}")
                response.raise_for_status()
                system_data = response.json()
                return ForecastSystem(
                    id=system_data.get("id"),
                    hindcast_point_id=system_data.get("hindcast_point_id"),
                    contract_id=system_data.get("contract_id"),
                    port_id=system_data.get("port_id"),
                    name=system_data.get("name")
                )
            except httpx.HTTPStatusError as e:
                print(f"Error al obtener el sistema de Prevision: {e.response.text}")
                raise

    async def get_forecast_zones(self, forecast_id: int, requester: User) -> List[ForecastZone]:
        """Obtiene las zonas de pronóstico asociadas a un sistema."""
        async with self._create_api_client(requester) as client:
            try:
                response = await client.get(f"/forecast-zones/by-system/{forecast_id}")
                response.raise_for_status()
                zones_data = response.json()
                return [ForecastZone(**zone_data) for zone_data in zones_data]
            except httpx.HTTPStatusError as e:
                print(f"Error al obtener las zonas de pronóstico: {e.response.text}")
                raise

    async def get_hindcast_data(self, download_data_id: int, requester: User) -> DownloadedData:
        """Obtiene los datos de un único punto de hindcast descargado."""
        async with self._create_api_client(requester) as client:
            try:
                response = await client.get(f"/downloaded-data/{download_data_id}")
                response.raise_for_status()
                download_data = response.json()
                # El endpoint devuelve un único objeto, no una lista.
                return DownloadedData(**download_data)
            except httpx.HTTPStatusError as e:
                print(f"Error al obtener el pronóstico de partida: {e.response.text}")
                raise

    async def save_forecast_results(self, system_id: int, zones: List[ForecastZone], propagation_results_json: str, requester: User) -> None:
        """Guarda los resultados de la propagación en la base de datos a través de la API."""
        import json
        
        try:
            results_dict = json.loads(propagation_results_json)
        except json.JSONDecodeError as e:
            print(f"Error parseando los resultados JSON: {e}")
            return

        async with self._create_api_client(requester) as client:
            # results_dict is grouped by model:
            # { "ewam": { "timestamps": [...], "zones": { "Zone 1": { "Hs": [...], "Tp": [...], "PeakDirection": [...] } } } }
            
            # We want to store a combined record for each zone, keeping the models inside 'result_data',
            # similar to the hindcast 'hourly' format, so the frontend can easily read it.
            
            # 1. Structure the data per zone
            zone_payloads = {zone.id: {"hourly": {"time": []}} for zone in zones}
            zone_map = {zone.name: zone.id for zone in zones}
            
            first_model = list(results_dict.keys())[0] if results_dict else None
            if first_model:
                timestamps = results_dict[first_model].get('timestamps', [])
                for zone_id in zone_payloads:
                    zone_payloads[zone_id]["hourly"]["time"] = timestamps

            for model, model_data in results_dict.items():
                zones_data = model_data.get("zones", {})
                for zone_name, params in zones_data.items():
                    zone_id = zone_map.get(zone_name)
                    if zone_id:
                        # Append the prefixed parameters into hourly
                        zone_payloads[zone_id]["hourly"][f"wave_height_{model}"] = params.get("Hs", [])
                        zone_payloads[zone_id]["hourly"][f"wave_period_{model}"] = params.get("Tp", [])
                        zone_payloads[zone_id]["hourly"][f"wave_direction_{model}"] = params.get("PeakDirection", [])

            # 2. Send to API for each zone
            for zone_id, result_data in zone_payloads.items():
                payload = {
                    "forecast_zone_id": zone_id,
                    "result_data": result_data
                }
                try:
                    response = await client.post("/forecast-results/", json=payload)
                    response.raise_for_status()
                    print(f"✅ Resultados guardados exitosamente para la zona {zone_id}")
                except httpx.HTTPError as e:
                    print(f"❌ Error al guardar resultados para la zona {zone_id}: {e}")
                    if hasattr(e, 'response') and e.response:
                        print(f"Detalle: {e.response.text}")


    async def calibration_hindcast_data(self, download_data: DownloadedData,hinccast_point_id: int,requester :User) -> Any:
        """
        Realiza la calibración de los datos de hindcast.
        NOTA: Por ahora, solo extrae los datos horarios. La lógica de calibración real se añadirá aquí.
        """
        async with self._create_api_client(requester) as client:
            try:
                response = await client.get(f"/hindcast-points/{hinccast_point_id}")
                response.raise_for_status()
                hindcast_data = response.json()
                models = hindcast_data.get("models", [])
            except httpx.HTTPStatusError as e:
                print(f"Error al obtener el punto Hindcast: {e.response.text}")
                raise    
        
        
        
        
        
        
        
        # El parámetro 'requester' se incluye para cumplir con la interfaz,
        # aunque no se use en esta lógica de cálculo.

        # Accedemos a los atributos del objeto con notación de punto (.)
        # download_data.data contiene el JSON que es un diccionario.
        
        url = "https://marine-api.open-meteo.com/v1/marine"
        
        params = {
            "latitude": 44.12,
            "longitude": -7.68,
            "hourly": "wave_direction",
            "models": models,
            "timezone": "auto",
        }
        
        
        # Llamada a la API
        async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()  # Lanza una excepción si la respuesta es un error (4xx o 5xx)
                api_data = response.json()
        # Convertir timestamps a datetime UTC
        api_df = pd.DataFrame(api_data["hourly"])
        api_df['time'] = pd.to_datetime(api_df['time'])
        api_df.set_index('time', inplace=True)

        
        hindcast_data = download_data.data["hourly"]
       
        local_times=pd.to_datetime(hindcast_data ["time"])
        time = hindcast_data ["time"]
        
        
        
        modelos = params["models"][0].split(",") if "models" in params else []
        dataframes = {}
        
        
        for modelo in modelos:
            height_key = f"wave_height_{modelo}"
            direction_key = f"wave_direction_{modelo}"
            period_key = f"wave_period_{modelo}"
        
            if height_key in hindcast_data and direction_key in hindcast_data and period_key in hindcast_data:
                df = pd.DataFrame({
                    "height": hindcast_data[height_key],
                    "direction": hindcast_data[direction_key],
                    "period": hindcast_data[period_key]
                }, index=local_times)
                df.dropna(inplace=True)  # Eliminar filas con NaN
                df.index.name = "datetime_utc"
        # Eliminar filas si alguna columna tiene NaN
                dataframes[modelo] = df
        dataframes_calibrados = {}
        for modelo, df in dataframes.items():
            print(f"\nProcesando modelo: {modelo}")
            print(f"[{modelo}] Intentando cargar parámetros de calibración...")
            path_dataset = os.path.join("app", "assets", "calibration_params", modelo, "calibration[0][0].mat")
            tiene_calibracion = os.path.exists(path_dataset)
            
            if tiene_calibracion:
                try:
                    print(f"[{modelo}] Cargando parámetros de calibración desde {path_dataset}")
                    calibration_data = scio.loadmat(path_dataset)
                    aj = calibration_data['aj']
                    bj = calibration_data['bj']
                    parametros =np.concatenate( [aj,bj],axis=1)
                    aj = aj.flatten()
                    bj = bj.flatten()
                    direcciones = np.arange(0,361,22.5)
                    Aj_interp = interpolate.interp1d(direcciones, aj, bounds_error=False, fill_value="extrapolate")
                    Bj_interp = interpolate.interp1d(direcciones, bj, bounds_error=False, fill_value="extrapolate")
                    directions = api_df[f"wave_direction_{modelo}"].dropna()
                    
                    df =pd.merge(left=df, right=directions, left_index=True, right_index=True)
                    
                                        
                                        
                    Aj = Aj_interp(df[f"wave_direction_{modelo}"])
                    Bj = Bj_interp(df[f"wave_direction_{modelo}"])
                    df.pop(f"wave_direction_{modelo}")
                    
                    df ["height_calibrated"] = Aj * df["height"] ** Bj
                    dataframes_calibrados[modelo] = df
                
                except Exception as e:
                    print(f"[{modelo}] Error al aplicar calibración: {e}")
                    tiene_calibracion = False
        return dataframes_calibrados
       
    def create_hypercube(self, Hsig: List, Tp: List,Dir:List,Nivel:List) -> np.ndarray:
        n,d,t,h= np.meshgrid(Nivel,Dir,Tp,Hsig, indexing='ij')    
        return  np.stack([h.ravel(), t.ravel(), d.ravel(),n.ravel()] ,axis=1)
        
    def propagation(self,hindcast:Dict[str, pd.DataFrame], zones:List[ForecastZone], hypercube:np.ndarray,angle:float=11.25):        # Primero vamos a obtener los datos del hipercubo en los puntos donde queremos regenerar.
        
        forecast_results = {}

        path_dataset = os.path.join("app", "assets", "swan")
        
        Xp=np.load(os.path.join(path_dataset,"Xp.npz"))
        Xp = np.unique(Xp['arr_0'])
        
        Yp=np.load(os.path.join(path_dataset,"Yp.npz"))
        Yp = np.unique(Yp['arr_0'])
        
        Hsig = np.load(os.path.join(path_dataset,"matrices_redondeadas_mm_hsig.npz"))
        Dir = np.load(os.path.join(path_dataset,"matrices_redondeadas_mm_dir.npz"))
        
        
        
        
        
        if zones:
            puntos_zones = np.zeros((len(zones),2))    
            for x,zone in enumerate(zones):
                print(f"Procesando zona: {zone.name}")
                puntos_zones[x,0] = zone.geom['coordinates'][0]
                puntos_zones[x,1] = zone.geom['coordinates'][1]


        Matriz = np.empty((len(Hsig), len(puntos_zones)*2))
       
        for x,case in enumerate(Hsig):
           
            fv = interpolate.RegularGridInterpolator(
            (Xp, Yp), (Hsig[case].T)/1000)
            Hsiginterp = fv(puntos_zones)
           
            Dirx, Diry = pol2cart((Hsig[case].T)/1000, (Dir[case].T)/1000)
            fv.values = Dirx
            Dirxinterp = fv(puntos_zones)
            fv.values = Diry
            Diryinterp = fv(puntos_zones)
            Dirinterp = cart2pol_mv(Dirxinterp, Diryinterp)[1]
            Dirinterp[Dirinterp < 0] = Dirinterp[Dirinterp < 0]+360
            Caso = np.concatenate((Hsiginterp, Dirinterp), axis=0)
            Caso = np.reshape(Caso, (2, len(puntos_zones))).reshape(
            (Caso.size, 1), order='f')
            Matriz[x, :] = Caso[:, 0]
       
        Hs = hypercube[:, 0]
        Tp = hypercube[:, 1]
        Dir = hypercube[:, 2]
        marea = hypercube[:, 3]
        Dir[Dir > 180] -= 360
        
        
        U_hc, V_hc = pol2cart(Hs, Dir)

        
        
        
        
        Hii = np.unique(Hs)
        Tpii = np.unique(Tp)
        Dirii = np.unique(Dir)
        mareaii = np.unique(marea)
        
        Hmin, Hmax = np.min(Hii), np.max(Hii)
        Tpmin, Tpmax = np.min(Tpii), np.max(Tpii)
        
        Hpropa = Matriz[:, 0::2]
        n_ptos = Hpropa.shape[1]
        # Listar las matrices disponibles

        # Normalizar la altura de ola propagada para obtener un factor de propagación.
        Hpropa_factor = Hpropa / Hs[:, None]

        Dir_propa = Matriz[:, 1::2]

        # --- REFACTORIZACIÓN: Interpolar componentes cartesianas ---
        # Para evitar problemas con la naturaleza circular de la dirección (0-360 grados),
        # descomponemos el vector de ola (Hpropa_factor, Dir_propa) en componentes U y V,
        # interpolamos estas componentes lineales y luego reconstruimos el vector.
        U_propa_factor, V_propa_factor = pol2cart(Hpropa_factor, Dir_propa)

        # El espacio de interpolación debe ser 4D para incluir el nivel de marea.
        hypercube_points_4d = np.column_stack((U_hc, V_hc, Tp, marea))

        path_dataset_level = os.path.join("app", "assets", "levels","level.dat")
        df_levels = pd.read_csv(path_dataset_level, sep=",", header=0,index_col=0,parse_dates=True)

        # Preparar los datos de nivel de marea para la interpolación.
        # Asumimos que la columna con los datos de nivel se llama 'level'.
        if 'tide' not in df_levels.columns:
            raise ValueError("El archivo 'level.dat' no contiene la columna 'tide'.")
        
        source_times_numeric = df_levels.index.astype(np.int64)
        source_levels = df_levels['tide'].values

        for modelo, df in hindcast.items():
            forecast_results[modelo] = {}
            
            # Interpolar la serie de niveles de marea para que coincida con los timestamps del pronóstico.
            target_times_numeric = df.index.astype(np.int64)
            level_series = np.interp(target_times_numeric, source_times_numeric, source_levels)+1.95
            
            Hs_wave0 = df['height_calibrated'].values
            Dir_wave = df['direction'].values
            Dir_wave[Dir_wave > 180] -= 360
            Tp_wave0 = df['period'].values
        
            
        
            Hs_wave = np.clip(Hs_wave0, Hmin, Hmax)
            Tp_wave = np.clip(Tp_wave0, Tpmin, Tpmax)
            

            
            # Zonas de sombra
            Hs_wave[(Dir_wave < min(Dirii)) | (Dir_wave > max(Dirii))] = 0
            Hs_wave0[(Dir_wave < min(Dirii)) | (Dir_wave > max(Dirii))] = 0
            Tp_wave[(Dir_wave < min(Dirii)) | (Dir_wave > max(Dirii))] = Tpmin
            Dir_wave[(Dir_wave < min(Dirii)) | (Dir_wave > max(Dirii))] = 0
            
            for ind in range(n_ptos):
                pto = ind
                
                # 1. Combinar los valores de las componentes U y V en un único array 2D.
                u_values = np.ascontiguousarray(U_propa_factor[:, pto])
                v_values = np.ascontiguousarray(V_propa_factor[:, pto])
                combined_cartesian_values = np.column_stack((u_values, v_values))

                # 2. Crear el interpolador 4D una vez para ambas componentes.
                F = interpolate.LinearNDInterpolator(hypercube_points_4d, combined_cartesian_values)

                # 3. Evaluar la interpolación en los puntos deseados.
                U_wave, V_wave = pol2cart(Hs_wave, Dir_wave)
                # Los puntos a evaluar también deben ser 4D, incluyendo la serie de nivel interpolada.
                points_to_evaluate_4d = np.column_stack((U_wave, V_wave, Tp_wave, level_series))
                interpolated_cartesian_results = F(points_to_evaluate_4d)

                # 4. Reconstruir el vector de ola a partir de las componentes interpoladas.
                interp_u_factor = interpolated_cartesian_results[:, 0]
                interp_v_factor = interpolated_cartesian_results[:, 1]
                H_factor_reconstructed, D_wave = cart2pol_mv(interp_u_factor, interp_v_factor)

                # 5. Aplicar el factor de altura de ola reconstruido a la altura de ola original.
                H_wave = H_factor_reconstructed * Hs_wave0
                D_wave[D_wave < 0] += 360 # Normalizar dirección a 0-360

                # 6. Crear y almacenar el DataFrame de resultados para el punto y modelo actual.
                zone_name = zones[pto].name
                point_forecast_df = pd.DataFrame({
                    'Hs': H_wave,
                    'Tp': Tp_wave, # Tp_wave fue calculado antes del bucle de puntos
                    'Dir': D_wave
                }, index=df.index)

                forecast_results[modelo][zone_name] = point_forecast_df
                print(f"✔ Pronóstico generado para el modelo '{modelo}' en la zona '{zone_name}'.")
        
        # --- Reestructuración de resultados al formato final ---
        # El objetivo es crear un diccionario anidado agrupado por modelo,
        # con una única lista de timestamps por modelo para evitar redundancia.
        structured_output = {}

        for model, zone_data in forecast_results.items():
            # Inicializar la estructura para el modelo actual
            structured_output[model] = {
                "timestamps": [],
                "zones": {}
            }

            # Extraer los timestamps una vez por modelo, ya que son comunes a todas sus zonas.
            first_df = next(iter(zone_data.values()), None)
            if first_df is not None:
                structured_output[model]['timestamps'] = [ts.isoformat() for ts in first_df.index]

            for zone_name, df in zone_data.items():
                # Convertir el DataFrame a un diccionario de listas
                parameter_data = df.to_dict(orient='list')
                if 'Dir' in parameter_data:
                    parameter_data['PeakDirection'] = parameter_data.pop('Dir')
                structured_output[model]["zones"][zone_name] = parameter_data

        # Serializar la estructura final a un string JSON
        return json.dumps(structured_output, indent=4)


if __name__ == "__main__":
    import asyncio

    async def main_test():
        # Cargar variables de entorno desde .env para facilitar las pruebas locales
    # Esto es especialmente útil para que RABBITMQ_HOST se establezca en 'localhost'
        from dotenv import load_dotenv
        load_dotenv()

        os.system('cls' if os.name == 'nt' else 'clear')
        """Función principal para probar el ForecastRepository."""
        print("--- Iniciando prueba de ForecastRepository ---")

        # Paso 1: Iniciar sesión para obtener un objeto User con token y rol.
        # Reutilizamos la lógica de infraestructura del usuario.
        from app.users.infrastructure.repositories import UserRepository

        test_user = os.getenv("API_USER")
        test_password = os.getenv("API_PASSWORD")

        if not test_user or not test_password:
            print("\nERROR: Por favor, define las variables de entorno API_USER y API_PASSWORD.")
            return

        try:
            print(f"Intentando iniciar sesión como '{test_user}' para obtener la sesión...")
            user_repo = UserRepository()
            user_session = await user_repo.login(test_user, test_password)
            print(f"✅ Login exitoso. El usuario es admin: {user_session.is_admin}")
        except Exception as e:
            print(f"\n❌ Falló el login inicial: {e}")
            return
        
        # 2. Crear una instancia del repositorio
        repo = ForecastWorkerRepository()
        
        # 3. ID del sistema de pronóstico a consultar
        test_forecast_id = 1
        test_download_id = 11
        # --- Ejecución de la prueba ---
        try:
            # --- PRUEBA 1: OBTENER SISTEMA DE PRONÓSTICO ---
            print(f"\n[TEST 1] Intentando obtener el sistema de pronóstico con ID: {test_forecast_id}...")
            forecast_system = await repo.get_forecast_system(
                forecast_id=test_forecast_id,
                requester=user_session
            )
            print("\n--- ¡Éxito! Sistema de pronóstico obtenido: ---")
            print(forecast_system)

            # --- PRUEBA 2: OBTENER ZONAS DE PRONÓSTICO ---
            print(f"\n[TEST 2] Intentando obtener las zonas para el sistema ID: {test_forecast_id}...")
            forecast_zones = await repo.get_forecast_zones(
                forecast_id=test_forecast_id,
                requester=user_session
            )
            print("\n--- ¡Éxito! Zonas de pronóstico obtenidas: ---")
            if forecast_zones:
                for zone in forecast_zones:
                    print(f"- {zone}")
            else:
                print("No se encontraron zonas para este sistema.")
                
                
                
            # --- PRUEBA 3: OBTENER PRONÓSTICO ---
            print(f"\n[TEST 3] Intentando obtener pronostico: {test_forecast_id}...")
            download_data = await repo.get_hindcast_data(
                download_data_id=test_download_id,
                requester=user_session
            )
            print("\n--- ¡Éxito! Pronosticos de Partida Obtenidos: ---")
 
            # --- PRUEBA 4: Calibrar  ---
            print(f"\n[TEST 34] Intentando calibrar pronostico: {test_forecast_id}...")
            
            data = await repo.calibration_hindcast_data(
                download_data = download_data # Añadimos el requester para cumplir la firma
                ,hinccast_point_id = forecast_system.hindcast_point_id
                ,requester=user_session
            )
            print("\n--- ¡Éxito! Pronosticos calibrados: ---")
            
            # --- PRUEBA 5: Generar Hypercubo  ---
            
            print(f"\n[TEST 5] Creando Hypercubo para : {test_forecast_id}...")

            puntos = repo.create_hypercube( # Ya no necesita await
                Hsig = [0.1,1,2,3,5,7,9,11,14],
                Tp = [5,8,10,13,16,19,25],
                Dir = [270,292.5,315,337.5,0,22.5,45,67.5,90],
                Nivel = [0,4.5]
            )
        
            print("\n--- ¡Éxito! Hypercubo Generado: ---")
            print(puntos)
            
            
            # --- PRUEBA 6: Prpagacion  ---

            print(f"\n[TEST 6] Propagacion Sistema de Previsión : {test_forecast_id}...")
            
            propagation_json = repo.propagation(
                hindcast = data,
                zones = forecast_zones,
                hypercube = puntos
            )
            
            print("\n--- ¡Éxito! Propagación completada. Resultados en formato JSON ---")
            
            print(f"\n[TEST 7] Guardando resultados...")
            await repo.save_forecast_results(
                system_id=test_forecast_id,
                zones=forecast_zones,
                propagation_results_json=propagation_json,
                requester=user_session
            )

        except (httpx.HTTPStatusError, httpx.ConnectError, PermissionError) as e:
            print(f"\n--- Ha ocurrido un error durante la prueba ---")
            print(f"Tipo de Error: {type(e).__name__}")
            print(f"Detalle: {e}")
        except Exception as e:
            print(f"\n--- Ocurrió un error inesperado ---")
            print(e)


    # Ejecutar la función de prueba asíncrona
    asyncio.run(main_test())