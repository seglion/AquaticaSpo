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
from app.shared.domain.remonte import calcular_remonte, calcular_caudal_rebase
from app.shared.domain.remonte_params import get_zone_remonte_params


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

    async def _relogin(self, requester: User) -> None:
        """Renueva el token de sesión (mutando 'requester' in-place) tras un 401.
        El worker corre indefinidamente consumiendo mensajes; sin esto, deja de
        poder llamar a la API pasado ACCESS_TOKEN_EXPIRE_MINUTES desde el arranque."""
        from app.users.infrastructure.repositories import UserRepository

        api_user = os.getenv("API_USER")
        api_password = os.getenv("API_PASSWORD")
        fresh = await UserRepository().login(api_user, api_password)
        requester.session_USER = fresh.session_USER
        requester.id = fresh.id
        requester.is_admin = fresh.is_admin
        print("🔄 Sesión del worker renovada tras token expirado")

    async def _request_authed(self, method: str, path: str, requester: User, **kwargs) -> httpx.Response:
        """Petición autenticada con un reintento automático si el token ha expirado (401)."""
        async with self._create_api_client(requester) as client:
            response = await client.request(method, path, **kwargs)
        if response.status_code == 401:
            await self._relogin(requester)
            async with self._create_api_client(requester) as client:
                response = await client.request(method, path, **kwargs)
        return response

    async def get_forecast_system(self, forecast_id: int, requester: User) -> ForecastSystem:
        try:
            response = await self._request_authed("GET", f"/forecast-systems/{forecast_id}", requester)
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
        try:
            response = await self._request_authed("GET", f"/forecast-zones/by-system/{forecast_id}", requester)
            response.raise_for_status()
            zones_data = response.json()
            return [ForecastZone(**zone_data) for zone_data in zones_data]
        except httpx.HTTPStatusError as e:
            print(f"Error al obtener las zonas de pronóstico: {e.response.text}")
            raise

    async def get_hindcast_data(self, download_data_id: int, requester: User) -> DownloadedData:
        """Obtiene los datos de un único punto de hindcast descargado."""
        try:
            response = await self._request_authed("GET", f"/downloaded-data/{download_data_id}", requester)
            response.raise_for_status()
            download_data = response.json()
            # El endpoint devuelve un único objeto, no una lista.
            return DownloadedData(**download_data)
        except httpx.HTTPStatusError as e:
            print(f"Error al obtener el pronóstico de partida: {e.response.text}")
            raise

    async def save_forecast_results(self, system_id: int, zones: List[ForecastZone], propagation_results_json: str, requester: User, wind_data: Optional[Dict[str, Any]] = None, wind_times: Optional[List[str]] = None) -> tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Guarda los resultados de la propagación en la base de datos a través de la API.

        Devuelve una tupla (zone_alerts, wind_alert):
        - zone_alerts: resumen de alertas de cota de remonte por zona.
        - wind_alert: alerta de viento global (None si no hay datos de viento).

        Si se proporciona wind_data (diccionario con claves 'wind_speed_10m',
        'wind_gusts_10m', 'wind_direction_10m'), se añade a los resultados de cada zona.
        """
        import json

        try:
            results_dict = json.loads(propagation_results_json)
        except json.JSONDecodeError as e:
            print(f"Error parseando los resultados JSON: {e}")
            return []

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
                    zone_payloads[zone_id]["hourly"][f"tide_level_{model}"] = params.get("Tide", [])
                    # Remonte (wave runup) EurOtop: cota de remonte y runup teórico por modelo.
                    zone_payloads[zone_id]["hourly"][f"cota_ru2p_{model}"] = params.get("CotaRu2p", [])
                    zone_payloads[zone_id]["hourly"][f"cota_ru1p_{model}"] = params.get("CotaRu1p", [])
                    zone_payloads[zone_id]["hourly"][f"runup_ru2p_{model}"] = params.get("Ru2p", [])
                    zone_payloads[zone_id]["hourly"][f"runup_ru1p_{model}"] = params.get("Ru1p", [])
                    zone_payloads[zone_id]["hourly"][f"caudal_rebase_{model}"] = params.get("CaudalRebase", [])

        # Añadir datos de viento a cada zona (es el mismo para todas, dato puntual)
        if wind_data:
            for zone_id in zone_payloads:
                for wind_key in ("wind_speed_10m", "wind_gusts_10m", "wind_direction_10m"):
                    if wind_key in wind_data:
                        zone_payloads[zone_id]["hourly"][wind_key] = wind_data[wind_key]

        # 2. Send to API for each zone
        for zone_id, result_data in zone_payloads.items():
            payload = {
                "forecast_zone_id": zone_id,
                "result_data": result_data
            }
            try:
                response = await self._request_authed("POST", "/forecast-results/", requester, json=payload)
                response.raise_for_status()
                print(f"✅ Resultados guardados exitosamente para la zona {zone_id}")
            except httpx.HTTPError as e:
                print(f"❌ Error al guardar resultados para la zona {zone_id}: {e}")
                if hasattr(e, 'response') and e.response:
                    print(f"Detalle: {e.response.text}")

        # 3. Calcular la evolución de la alerta por zona a lo largo del tiempo,
        # usando la cota de remonte (CotaRu2p) del modelo EWAM como referencia.
        # Se agrupan las horas consecutivas con el mismo nivel de alerta en
        # intervalos, según los thresholds de cota definidos en alert_thresholds.json.
        from app.shared.domain.alert_levels import classify_cota_alert, classify_wind_alert

        REFERENCE_MODEL = "ewam"
        zone_names = {zone.id: zone.name for zone in zones}
        zone_coords = {zone.id: zone.geom.get("coordinates") for zone in zones if zone.geom}
        zone_dock = {zone.id: zone.dock_elevation for zone in zones}
        zone_alerts: List[Dict[str, Any]] = []
        for zone_id, result_data in zone_payloads.items():
            hourly = result_data["hourly"]
            times = hourly.get("time", [])
            dock = zone_dock.get(zone_id)

            model_key = f"cota_ru2p_{REFERENCE_MODEL}"
            used_model = REFERENCE_MODEL
            if model_key not in hourly:
                fallback_key = next((k for k in hourly if k.startswith("cota_ru2p_")), None)
                model_key = fallback_key
                used_model = fallback_key[len("cota_ru2p_"):] if fallback_key else None

            values = hourly.get(model_key, []) if model_key else []

            # 3a. Agrupar horas consecutivas con el mismo nivel de alerta en intervalos.
            intervals: List[Dict[str, Any]] = []
            current: Optional[Dict[str, Any]] = None
            for idx, value in enumerate(values):
                alert = classify_cota_alert(value, dock) if dock else {"level": None, "label": "Sin alerta", "color": "#6ee7b7"}
                if current is None or alert["level"] != current["level"]:
                    if current is not None:
                        intervals.append({
                            "alert_level": current["level"],
                            "alert_label": current["label"],
                            "alert_color": current["color"],
                            "start_time": times[current["start_idx"]] if current["start_idx"] < len(times) else None,
                            "end_time": times[idx - 1] if 0 <= idx - 1 < len(times) else None,
                            "max_hs": current["max_hs"],
                        })
                    current = {
                        "level": alert["level"], "label": alert["label"], "color": alert["color"],
                        "start_idx": idx, "max_hs": value,
                    }
                elif value is not None and (current["max_hs"] is None or value > current["max_hs"]):
                    current["max_hs"] = value
            if current is not None:
                intervals.append({
                    "alert_level": current["level"],
                    "alert_label": current["label"],
                    "alert_color": current["color"],
                    "start_time": times[current["start_idx"]] if current["start_idx"] < len(times) else None,
                    "end_time": times[-1] if times else None,
                    "max_hs": current["max_hs"],
                })

            # 3b. Resumen de cabecera: valor máximo de cota de remonte en todo el horizonte.
            best_max = None
            best_time = None
            for idx, value in enumerate(values):
                if value is not None and (best_max is None or value > best_max):
                    best_max = value
                    best_time = times[idx] if idx < len(times) else None

            # 3c. Caudal de rebase máximo para este modelo de referencia
            q_key = f"caudal_rebase_{used_model}" if used_model else None
            q_values = hourly.get(q_key, []) if q_key else []
            max_q = None
            for qv in q_values:
                if qv is not None and (max_q is None or qv > max_q):
                    max_q = qv

            alert = classify_cota_alert(best_max, dock) if dock else {"level": None, "label": "Sin alerta", "color": "#6ee7b7"}
            # Sobreescribir a rojo si el caudal de rebase supera el umbral de peligro para peatones (10 l/s/m, Allsop/Franco 2005)
            if max_q is not None and max_q > 10:
                alert = {"level": "red", "label": "Roja", "color": "#dc2626"}

            coords = zone_coords.get(zone_id)
            zone_alerts.append({
                "zone_id": zone_id,
                "zone_name": zone_names.get(zone_id),
                "max_hs": best_max,
                "max_q": max_q,
                "alert_level": alert["level"],
                "alert_label": alert["label"],
                "alert_color": alert["color"],
                "model": used_model,
                "peak_time": best_time,
                "intervals": intervals,
                "lon": coords[0] if coords else None,
                "lat": coords[1] if coords else None,
            })

        # 3d. Alerta de viento global (común a todas las zonas)
        wind_alert = None
        wind_intervals = []
        if wind_data and wind_data.get("wind_speed_10m"):
            speeds = wind_data["wind_speed_10m"]
            best_wind = max(s for s in speeds if s is not None) if any(s is not None for s in speeds) else None
            wind_alert = classify_wind_alert(best_wind)
            if wind_times and len(wind_times) == len(speeds):
                current_iv = None
                for idx, s in enumerate(speeds):
                    over = s is not None and s > 50
                    if over and current_iv is None:
                        current_iv = {"start_idx": idx, "max_speed": s}
                    elif over and current_iv is not None and s > current_iv["max_speed"]:
                        current_iv["max_speed"] = s
                    elif not over and current_iv is not None:
                        current_iv["end_idx"] = idx
                        wind_intervals.append({
                            "start_time": wind_times[current_iv["start_idx"]],
                            "end_time": wind_times[current_iv["end_idx"]],
                            "max_wind_speed": current_iv["max_speed"],
                        })
                        current_iv = None
                if current_iv is not None:
                    wind_intervals.append({
                        "start_time": wind_times[current_iv["start_idx"]],
                        "end_time": wind_times[-1],
                        "max_wind_speed": current_iv["max_speed"],
                    })

        if wind_alert is None:
            wind_alert = {}
        wind_alert["intervals"] = wind_intervals

        return zone_alerts, wind_alert

    async def calibration_hindcast_data(self, download_data: DownloadedData,hinccast_point_id: int,requester :User) -> Any:
        """
        Realiza la calibración de los datos de hindcast.
        NOTA: Por ahora, solo extrae los datos horarios. La lógica de calibración real se añadirá aquí.
        """
        try:
            response = await self._request_authed("GET", f"/hindcast-points/{hinccast_point_id}", requester)
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

        # Coordenadas del punto cercano a la Boya de Estaca de Bares, usado para
        # obtener la dirección de oleaje de la boya y calibrar direccionalmente
        # el punto de inicio del sistema. Sin 'timezone' para que quede en GMT
        # (UTC+0), igual que el resto de datos con los que se hace merge por
        # timestamp (con 'auto' se resolvía a Etc/GMT+1, desalineando 1h el merge).
        params = {
            "latitude": 44.12,
            "longitude": -7.68,
            "hourly": "wave_direction",
            "models": models,
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

                # 6. Calcular el remonte (wave runup) EurOtop para este punto/modelo.
                # Todas las series necesarias ya están en scope y alineadas por df.index.
                # Los parámetros estructurales (talud, orientación, rugosidad, ...) se
                # resuelven por zona desde remonte_params.json.
                zona = zones[pto]
                rp = get_zone_remonte_params(zona.id, zona.name)
                remonte = calcular_remonte(
                    hs=H_wave,
                    tp=Tp_wave,
                    dir_oleaje=D_wave,
                    marea=level_series,
                    talud=rp["talud"],
                    angulo_perpendicular=rp["angulo_perpendicular"],
                    rugosidad=rp["rugosidad"],
                    berma=rp["berma"],
                    factor_seguridad=rp["factor_seguridad"],
                )

                caudal = calcular_caudal_rebase(
                    hs=H_wave,
                    tp=Tp_wave,
                    dir_oleaje=D_wave,
                    marea=level_series,
                    cota_coronacion=zona.dock_elevation or 15.70,
                    talud=rp["talud"],
                    angulo_perpendicular=rp["angulo_perpendicular"],
                    rugosidad=rp["rugosidad"],
                )

                # 7. Crear y almacenar el DataFrame de resultados para el punto y modelo actual.
                zone_name = zones[pto].name
                point_forecast_df = pd.DataFrame({
                    'Hs': H_wave,
                    'Tp': Tp_wave, # Tp_wave fue calculado antes del bucle de puntos
                    'Dir': D_wave,
                    'Tide': level_series,
                    'Ru2p': remonte['ru2p'],
                    'Ru1p': remonte['ru1p'],
                    'CotaRu2p': remonte['cota_ru2p'],
                    'CotaRu1p': remonte['cota_ru1p'],
                    'CaudalRebase': caudal,
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