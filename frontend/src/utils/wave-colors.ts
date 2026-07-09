import alertThresholds from '../../../alert_thresholds.json'

type AlertLevel = 'yellow' | 'orange' | 'red' | null

interface AlertTier {
    level: AlertLevel
    label: string
    color: string
    max: number | null
}

const LEVELS = alertThresholds.levels as AlertTier[]

const TAILWIND_CLASSES: Record<'none' | 'yellow' | 'orange' | 'red', string> = {
    none: 'bg-emerald-300 text-emerald-900',
    yellow: 'bg-yellow-300 text-yellow-900',
    orange: 'bg-orange-500 text-orange-200',
    red: 'bg-red-600 text-red-100',
}

const classifyHeight = (height: number): AlertTier => {
    for (const tier of LEVELS) {
        if (tier.max === null || height < tier.max) return tier
    }
    // Inalcanzable: el último tramo de alert_thresholds.json siempre tiene max=null.
    return LEVELS[LEVELS.length - 1]!
}

export const getWaveColor = (height: number | undefined): string => {
    if (height === undefined) return '#94a3b8' // slate-400 (gris para sin datos)
    return classifyHeight(height).color
}

export const getWaveTailwindClass = (height: number | undefined): string => {
    if (height === undefined) return ''
    const level = classifyHeight(height).level
    return TAILWIND_CLASSES[level ?? 'none']
}
