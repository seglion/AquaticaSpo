// All heavy dependencies are loaded dynamically inside generateForecastPdf
// to avoid module-level side effects that conflict with Leaflet on startup.

import { parseUTCDate, MADRID_TIMEZONE } from './dateFormatter'

// ────────────────────────────────────────────────────────────────────────────
// Types
// ────────────────────────────────────────────────────────────────────────────

export interface ForecastRowData {
    time: string
    [model: string]: any
}

interface ChartDataset {
    label: string
    data: (number | null)[]
    color: string
}

// ────────────────────────────────────────────────────────────────────────────
// Constants
// ────────────────────────────────────────────────────────────────────────────

const MODEL_COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#f87171', '#a78bfa', '#fb923c']

function modelColor(index: number): string {
    return MODEL_COLORS[index % MODEL_COLORS.length] ?? MODEL_COLORS[0]!
}

type RGB = [number, number, number]

const COTA_GREEN: { fill: RGB; text: RGB } = { fill: [167, 243, 208], text: [6, 78, 59] }       // ratio < 0.6
const COTA_YELLOW: { fill: RGB; text: RGB } = { fill: [253, 224, 71], text: [113, 63, 18] }     // ratio < 0.8
const COTA_ORANGE: { fill: RGB; text: RGB } = { fill: [249, 115, 22], text: [255, 247, 237] }   // ratio < 1.0
const COTA_RED: { fill: RGB; text: RGB } = { fill: [220, 38, 38], text: [255, 241, 242] }       // ratio >= 1.0

// ────────────────────────────────────────────────────────────────────────────
// Helpers
// ────────────────────────────────────────────────────────────────────────────

function fmtFull(iso: string): string {
    const d = parseUTCDate(iso)
    return new Intl.DateTimeFormat('es-ES', {
        weekday: 'short', day: '2-digit', month: 'short',
        hour: '2-digit', minute: '2-digit', timeZone: MADRID_TIMEZONE,
    }).format(d)
}

function fmtShort(iso: string): string {
    const d = parseUTCDate(iso)
    return new Intl.DateTimeFormat('es-ES', {
        day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', timeZone: MADRID_TIMEZONE,
    }).format(d)
}

function cotaColor(val: number, dockElevation: number): { fill: RGB; text: RGB } {
    const ratio = val / dockElevation
    if (ratio < 0.6) return COTA_GREEN
    if (ratio < 0.8) return COTA_YELLOW
    if (ratio < 1.0) return COTA_ORANGE
    return COTA_RED
}

// ────────────────────────────────────────────────────────────────────────────
// Chart rendering (offscreen canvas → PNG data URL)
// ────────────────────────────────────────────────────────────────────────────

async function renderChart(
    labels: string[],
    datasets: ChartDataset[],
    yAxisLabel: string,
    canvasWidth = 900,
    canvasHeight = 320,
): Promise<string> {
    const { Chart, LineController, LineElement, PointElement, LinearScale, CategoryScale, Legend, Tooltip, Filler } =
        await import('chart.js')
    Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Legend, Tooltip, Filler)

    const canvas = document.createElement('canvas')
    canvas.width = canvasWidth
    canvas.height = canvasHeight
    canvas.style.cssText = 'position:fixed;top:-9999px;left:-9999px;'
    document.body.appendChild(canvas)

    const chart = new Chart(canvas, {
        type: 'line',
        data: {
            labels,
            datasets: datasets.map(ds => ({
                label: ds.label,
                data: ds.data,
                borderColor: ds.color,
                backgroundColor: ds.color + '20',
                borderWidth: 2.5,
                pointRadius: 0,
                tension: 0.35,
                fill: false,
                spanGaps: true,
            })),
        },
        options: {
            responsive: false,
            animation: { duration: 0 },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: { color: '#334155', font: { size: 12 }, boxWidth: 20 },
                },
                tooltip: { enabled: false },
            },
            scales: {
                x: {
                    ticks: { color: '#64748b', font: { size: 10 }, maxTicksLimit: 14, maxRotation: 45 },
                    grid: { color: '#e2e8f0' },
                },
                y: {
                    ticks: { color: '#64748b', font: { size: 11 } },
                    grid: { color: '#e2e8f0' },
                    title: { display: true, text: yAxisLabel, color: '#475569', font: { size: 12 } },
                },
            },
        },
    })

    await new Promise(r => setTimeout(r, 120))
    const dataUrl = canvas.toDataURL('image/png')
    chart.destroy()
    document.body.removeChild(canvas)
    return dataUrl
}

// ────────────────────────────────────────────────────────────────────────────
// Map image (IGN WMS orthophoto + marker)
// ────────────────────────────────────────────────────────────────────────────

const IGN_WMS_URL = 'https://www.ign.es/wms-inspire/pnoa-ma'
const MAP_BBOX_DELTA = 0.004
const MAP_WIDTH_PX = 600
const MAP_HEIGHT_PX = 340

async function fetchZoneMapImage(lon: number, lat: number): Promise<string | null> {
    try {
        const bbox = `${lon - MAP_BBOX_DELTA},${lat - MAP_BBOX_DELTA},${lon + MAP_BBOX_DELTA},${lat + MAP_BBOX_DELTA}`
        const url = `${IGN_WMS_URL}?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=OI.OrthoimageCoverage&STYLES=&SRS=EPSG:4326&BBOX=${bbox}&WIDTH=${MAP_WIDTH_PX}&HEIGHT=${MAP_HEIGHT_PX}&FORMAT=image/png`

        const resp = await fetch(url)
        if (!resp.ok) return null
        const blob = await resp.blob()
        const img = await createImageBitmap(blob)

        const canvas = document.createElement('canvas')
        canvas.width = MAP_WIDTH_PX
        canvas.height = MAP_HEIGHT_PX
        const ctx = canvas.getContext('2d')!

        // Draw orthophoto
        ctx.drawImage(img, 0, 0)

        // Draw red marker
        const cx = MAP_WIDTH_PX / 2
        const cy = MAP_HEIGHT_PX / 2
        const r = 9
        ctx.beginPath()
        ctx.arc(cx, cy, r, 0, 2 * Math.PI)
        ctx.fillStyle = '#dc2626'
        ctx.fill()
        ctx.strokeStyle = '#ffffff'
        ctx.lineWidth = 2
        ctx.stroke()

        return canvas.toDataURL('image/png')
    } catch {
        return null
    }
}

// ────────────────────────────────────────────────────────────────────────────
// Public entry point
// ────────────────────────────────────────────────────────────────────────────

export async function generateForecastPdf(
    hourlyData: ForecastRowData[],
    models: string[],
    zoneInfo: any | null,
    hindcastInfo: any | null,
    downloadedAt: string,
): Promise<void> {
    if (!hourlyData.length || !models.length) return

    // Solo modelo EWAM en el PDF
    models = models.filter(m => m.toLowerCase() === 'ewam')
    if (!models.length) return

    const dockElevation = zoneInfo?.dock_elevation ?? 0

    const { default: jsPDF } = await import('jspdf')
    const { default: autoTable } = await import('jspdf-autotable')

    const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
    const PW = pdf.internal.pageSize.getWidth()   // 297
    const PH = pdf.internal.pageSize.getHeight()  // 210
    const M = 14  // margin

    // ── Header bar ─────────────────────────────────────────────────────────
    pdf.setFillColor(15, 23, 42)
    pdf.rect(0, 0, PW, 24, 'F')

    pdf.setTextColor(248, 250, 252)
    pdf.setFont('helvetica', 'bold')
    pdf.setFontSize(15)
    pdf.text('Parte de Previsión de Oleaje', M, 11)

    pdf.setFont('helvetica', 'normal')
    pdf.setFontSize(8)

    const lon = zoneInfo?.geom?.coordinates[0] ?? hindcastInfo?.longitude
    const lat = zoneInfo?.geom?.coordinates[1] ?? hindcastInfo?.latitude

    const zoneLine = zoneInfo
        ? `Zona: ${zoneInfo.name}  |  Lat: ${lat?.toFixed(4)}, Lon: ${lon?.toFixed(4)}`
        : hindcastInfo
            ? `Punto ID: ${hindcastInfo.id}  |  Lat: ${lat?.toFixed(4)}, Lon: ${lon?.toFixed(4)}`
            : ''

    const metaLine = `${zoneLine}  |  Datos: ${fmtFull(downloadedAt)}  |  Generado: ${new Date().toLocaleString('es-ES')}`
    pdf.text(metaLine, M, 20)

    let y = 30

    // ── Charts + map ────────────────────────────────────────────────────────
    const gap = 4
    const itemW = (PW - M * 2 - gap * 2) / 3

    const labels = hourlyData.map(r => fmtShort(r.time))

    const [hsImg, tpImg, mapImg] = await Promise.all([
        renderChart(
            labels,
            models.map((m, i) => ({
                label: m.toUpperCase(),
                data: hourlyData.map(r => r[m]?.height ?? null),
                color: modelColor(i),
            })),
            'Hs (m)',
        ),
        renderChart(
            labels,
            models.map((m, i) => ({
                label: m.toUpperCase(),
                data: hourlyData.map(r => r[m]?.period ?? null),
                color: modelColor(i),
            })),
            'Tp (s)',
        ),
        (lon != null && lat != null) ? fetchZoneMapImage(lon, lat) : Promise.resolve(null),
    ])

    const chartH = 48

    pdf.setTextColor(51, 65, 85)
    pdf.setFont('helvetica', 'bold')
    pdf.setFontSize(8)

    const titles = ['Altura Significativa — Hs (m)', 'Periodo Pico — Tp (s)', 'Localización del Punto']
    const images = [hsImg, tpImg, mapImg]
    for (let i = 0; i < 3; i++) {
        const x = M + i * (itemW + gap)
        pdf.text(titles[i]!, x, y - 1)
        if (images[i]) {
            pdf.addImage(images[i]!, 'PNG', x, y, itemW, chartH)
        }
    }
    y += chartH + 6

    // ── Table ───────────────────────────────────────────────────────────────
    // Columnas comunes + por modelo: Hs, Tp, Dir, Cota, Q
    const COMMON_COLS = 5  // Fecha, Marea, Vel, Ráf, Dir
    const COLS_PER_MODEL = 5

    const head = [
        [
            'Fecha / Hora',
            'Marea (m)',
            'Viento\nVel (km/h)',
            'Viento\nRáf (km/h)',
            'Viento\nDir (°)',
            ...models.flatMap(() => [
                'Hs (m)',
                'Tp (s)',
                'Dir (°)',
                'Remonte\nCota (m)',
                'Rebase\nQ (l/m/s)',
            ]),
        ],
    ]

    const body = hourlyData.map(row => [
        fmtFull(row.time),
        row.tide != null ? Number(row.tide).toFixed(2) : '–',
        row.windSpeed != null ? Number(row.windSpeed).toFixed(1) : '–',
        row.windGusts != null ? Number(row.windGusts).toFixed(1) : '–',
        row.windDirection != null ? Number(row.windDirection).toFixed(0) + '°' : '–',
        ...models.flatMap(m => [
            row[m]?.height != null ? row[m].height.toFixed(2) : '–',
            row[m]?.period != null ? row[m].period.toFixed(1) : '–',
            row[m]?.direction != null ? row[m].direction.toFixed(0) + '°' : '–',
            row[m]?.cotaRu2p != null ? row[m].cotaRu2p.toFixed(2) : '–',
            row[m]?.caudalRebase != null ? row[m].caudalRebase.toFixed(2) : '–',
        ]),
    ])

    autoTable(pdf, {
        head,
        body,
        startY: y,
        margin: { left: M, right: M },
        styles: { fontSize: 7, cellPadding: 1.5, overflow: 'linebreak' },
        headStyles: {
            fillColor: [15, 23, 42],
            textColor: [248, 250, 252],
            fontStyle: 'bold',
            halign: 'center',
            valign: 'middle',
            cellPadding: 2,
        },
        columnStyles: { 0: { halign: 'left', minCellWidth: 24 } },
        alternateRowStyles: { fillColor: [248, 250, 252] },
        didParseCell(data) {
            if (data.section !== 'body') return

            const ci = data.column.index
            const raw = (data.cell.raw as string) ?? ''
            const val = parseFloat(raw)

            // Viento col 2 (Vel): rojo si > 50 km/h
            if (ci === 2 && !isNaN(val) && val > 50) {
                data.cell.styles.fillColor = [254, 202, 202]
                data.cell.styles.textColor = [153, 27, 27]
                data.cell.styles.fontStyle = 'bold'
                data.cell.styles.halign = 'center'
                return
            }

            if (ci < COMMON_COLS) {
                data.cell.styles.halign = 'center'
                return
            }

            const modelCol = ci - COMMON_COLS
            const relIdx = modelCol % COLS_PER_MODEL
            // Cota de remonte (relIdx 3): semáforo según cota/dock_elevation.
            if (relIdx === 3) {
                if (!isNaN(val) && dockElevation > 0) {
                    const { fill, text } = cotaColor(val, dockElevation)
                    data.cell.styles.fillColor = fill
                    data.cell.styles.textColor = text
                } else {
                    data.cell.styles.textColor = [124, 58, 237]
                }
                data.cell.styles.fontStyle = 'bold'
                data.cell.styles.halign = 'center'
            }
            // Q (relIdx 4): rojo si > 10 l/s/m, negro si no.
            if (relIdx === 4) {
                if (!isNaN(val) && val > 10) {
                    data.cell.styles.fillColor = [254, 202, 202]
                    data.cell.styles.textColor = [153, 27, 27]
                    data.cell.styles.fontStyle = 'bold'
                } else {
                    data.cell.styles.textColor = [0, 0, 0]
                }
                data.cell.styles.halign = 'center'
            }
        },
        willDrawCell(data) {
            if (data.section !== 'body') return
            const ci = data.column.index
            if (ci === 2) return // ya manejado en didParseCell
            if (ci >= COMMON_COLS) data.cell.styles.halign = 'center'
        },
    })

    // ── Footer on each page ─────────────────────────────────────────────────
    const totalPages: number = (pdf as any).internal.getNumberOfPages()
    for (let p = 1; p <= totalPages; p++) {
        pdf.setPage(p)
        pdf.setFont('helvetica', 'normal')
        pdf.setFontSize(7)
        pdf.setTextColor(148, 163, 184)
        pdf.text(
            `AquaticaSpo  —  Página ${p} de ${totalPages}`,
            PW / 2,
            PH - 4,
            { align: 'center' },
        )
    }

    const safeZoneName = zoneInfo?.name
        ? zoneInfo.name.replace(/[^a-zA-Z0-9_\-]/g, '_')
        : hindcastInfo
            ? `punto_${hindcastInfo.id}`
            : 'prevision'
    pdf.save(`prevision_oleaje_${safeZoneName}.pdf`)
}
