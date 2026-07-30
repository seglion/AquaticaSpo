import alertThresholds from '../../../alert_thresholds.json'

type AlertLevel = 'light_green' | 'dark_green' | 'yellow' | 'orange' | 'red' | null

interface AlertTier {
    level: AlertLevel
    label: string
    color: string
    max: number | null
}

const LEVELS = alertThresholds.levels as AlertTier[]
const WIND_LEVELS = alertThresholds.wind_levels as AlertTier[]
const COTA_LEVELS = alertThresholds.cota_levels as AlertTier[]

const TAILWIND_CLASSES: Record<string, string> = {
    light_green: 'bg-emerald-300 text-emerald-900',
    dark_green: 'bg-emerald-700 text-emerald-100',
    none: 'bg-emerald-300 text-emerald-900',
    yellow: 'bg-yellow-300 text-yellow-900',
    orange: 'bg-orange-500 text-orange-200',
    red: 'bg-red-600 text-red-100',
}

const classifyHeight = (height: number): AlertTier => {
    for (const tier of LEVELS) {
        if (tier.max === null || height < tier.max) return tier
    }
    return LEVELS[LEVELS.length - 1]!
}

const classifyWind = (speed: number): AlertTier => {
    for (const tier of WIND_LEVELS) {
        if (tier.max === null || speed < tier.max) return tier
    }
    return WIND_LEVELS[WIND_LEVELS.length - 1]!
}

const classifyCota = (ratio: number): AlertTier => {
    for (const tier of COTA_LEVELS) {
        if (tier.max === null || ratio < tier.max) return tier
    }
    return COTA_LEVELS[COTA_LEVELS.length - 1]!
}

export const getWaveColor = (height: number | undefined): string => {
    if (height === undefined) return '#94a3b8'
    return classifyHeight(height).color
}

export const getWaveTailwindClass = (height: number | undefined): string => {
    if (height === undefined) return ''
    const level = classifyHeight(height).level
    return TAILWIND_CLASSES[level ?? 'none'] ?? ''
}

export const getWindTailwindClass = (speed: number | undefined): string => {
    if (speed === undefined) return ''
    const level = classifyWind(speed).level
    return TAILWIND_CLASSES[level ?? 'none'] ?? ''
}

export const getCotaTailwindClass = (ratio: number | undefined): string => {
    if (ratio === undefined) return ''
    const level = classifyCota(ratio).level
    return TAILWIND_CLASSES[level ?? 'none'] ?? ''
}
