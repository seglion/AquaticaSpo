export interface ForecastSystem {
    id: number;
    name: string;
    description?: string;
    contract_id: number;
    port_id: number;
    hindcast_point_id: number;
}

export interface Contract {
    id: number;
    name?: string;
    start_date: string;
    end_date: string | null;
    active: boolean;
    // user_id might not be returned by backend based on curl output, making it optional
    user_id?: number;
}

export interface Port {
    id: number;
    name: string;
    country: string;
    latitude: number;
    longitude: number;
}

export interface HindcastPoint {
    id: number;
    latitude: number;
    longitude: number;
    url: string;
    models: string[];
}

export interface DownloadedData {
    id: number;
    point_id: number;
    downloaded_at: string;
    data: Record<string, any>;
}

export interface ForecastZone {
    id: number;
    name: string;
    description?: string;
    forecast_system_id: number;
    geom: {
        type: "Point";
        coordinates: [number, number]; // [longitude, latitude]
    };
}
