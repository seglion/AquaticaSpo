/**
 * Parses a date string that is assumed to be in UTC into a Date object.
 * If the string does not have timezone information, it appends 'Z' to
 * force JS to parse it as UTC rather than local time.
 * @param dateString The date string, e.g., "2026-02-20 00:00:00" or "2026-02-20T00:00:00"
 * @returns Date object correctly instantiated from UTC
 */
export const parseUTCDate = (dateString: string): Date => {
    if (!dateString) return new Date();

    // Replace space with T to comply with ISO 8601
    let isoString = dateString.replace(' ', 'T');

    // If it doesn't end with 'Z' and doesn't contain a timezone offset like '+01:00'
    // append 'Z' to force it to be parsed as UTC
    if (!isoString.endsWith('Z') && !isoString.match(/[+-]\d{2}:\d{2}$/)) {
        isoString += 'Z';
    }

    return new Date(isoString);
};

/** Todos los datos (hindcast, previsión) llegan en UTC; se muestran en hora local de Madrid. */
export const MADRID_TIMEZONE = 'Europe/Madrid';

/**
 * Formatea una fecha UTC (string) a hora local de Madrid, independientemente
 * de la zona horaria del dispositivo del usuario.
 */
export const formatMadridDateTime = (
    dateString: string,
    options: Intl.DateTimeFormatOptions = {}
): string => {
    const date = parseUTCDate(dateString);
    return new Intl.DateTimeFormat('es-ES', {
        weekday: 'short',
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: MADRID_TIMEZONE,
        ...options,
    }).format(date);
};
