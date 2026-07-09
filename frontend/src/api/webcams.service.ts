import axios from 'axios';

// We use a local proxy to bypass potential CORS issues
const API_BASE_URL = '/api/meteogalicia/mgrss/observacion/jsonCamaras.action';

export interface MeteoGaliciaWebcam {
    concello: string;
    dataUltimaAct: string;
    idConcello: number;
    identificador: number;
    imaxeCamara: string;
    imaxeCamaraMini: string;
    lat: number;
    lon: number;
    nomeCamara: string;
    provincia: string;
}

export interface MeteoGaliciaResponse {
    listaCamaras: MeteoGaliciaWebcam[];
}

/**
 * Calculates the distance between two coordinates in kilometers using the Haversine formula
 */
function getDistanceFromLatLonInKm(lat1: number, lon1: number, lat2: number, lon2: number) {
    const R = 6371; // Radius of the earth in km
    const dLat = (lat2 - lat1) * (Math.PI / 180);
    const dLon = (lon2 - lon1) * (Math.PI / 180);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c; // Distance in km
    return d;
}

/**
 * Fetch webcams from MeteoGalicia and filter by proximity.
 * @param lat Latitude
 * @param lon Longitude
 * @param radius Radius in kilometers (default: 100)
 * @param limit Maximum number of webcams to return (default: 10)
 * @returns 
 */
export const fetchNearbyWebcams = async (
    lat: number,
    lon: number,
    radius: number = 100,
    limit: number = 10
): Promise<MeteoGaliciaWebcam[]> => {
    try {
        const response = await axios.get<MeteoGaliciaResponse>(API_BASE_URL);
        const allCameras = response.data.listaCamaras || [];

        // Calculate distance for each camera and filter
        const camerasWithDistance = allCameras.map(cam => ({
            ...cam,
            distance: getDistanceFromLatLonInKm(lat, lon, cam.lat, cam.lon)
        }));

        const nearbyCameras = camerasWithDistance
            .filter(cam => cam.distance <= radius)
            .sort((a, b) => a.distance - b.distance)
            .slice(0, limit);

        return nearbyCameras;
    } catch (error) {
        console.error('Error fetching webcams from MeteoGalicia API:', error);
        throw error;
    }
};
