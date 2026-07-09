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

const HS_GREEN: { fill: RGB; text: RGB } = { fill: [167, 243, 208], text: [6, 78, 59] }     // < 1 m  → verde
const HS_YELLOW: { fill: RGB; text: RGB } = { fill: [253, 224, 71], text: [113, 63, 18] }   // < 2 m  → amarillo
const HS_ORANGE: { fill: RGB; text: RGB } = { fill: [249, 115, 22], text: [255, 247, 237] } // < 4 m → naranja
const HS_RED: { fill: RGB; text: RGB } = { fill: [220, 38, 38], text: [255, 241, 242] }     // ≥ 4 m  → rojo

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

function hsColor(val: number): { fill: RGB; text: RGB } {
    if (val < 1) return HS_GREEN
    if (val < 2) return HS_YELLOW
    if (val < 4) return HS_ORANGE
    return HS_RED
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

    const zoneLine = zoneInfo
        ? `Zona: ${zoneInfo.name}  |  Lat: ${zoneInfo.geom?.coordinates[1]?.toFixed(4)}, Lon: ${zoneInfo.geom?.coordinates[0]?.toFixed(4)}`
        : hindcastInfo
            ? `Punto ID: ${hindcastInfo.id}  |  Lat: ${hindcastInfo.latitude?.toFixed(4)}, Lon: ${hindcastInfo.longitude?.toFixed(4)}`
            : ''

    const metaLine = `${zoneLine}  |  Datos: ${fmtFull(downloadedAt)}  |  Generado: ${new Date().toLocaleString('es-ES')}`
    pdf.text(metaLine, M, 20)

    let y = 30

    // ── Charts ──────────────────────────────────────────────────────────────
    const labels = hourlyData.map(r => fmtShort(r.time))

    const hsImg = await renderChart(
        labels,
        models.map((m, i) => ({
            label: m.toUpperCase(),
            data: hourlyData.map(r => r[m]?.height ?? null),
            color: modelColor(i),
        })),
        'Hs (m)',
    )

    const tpImg = await renderChart(
        labels,
        models.map((m, i) => ({
            label: m.toUpperCase(),
            data: hourlyData.map(r => r[m]?.period ?? null),
            color: modelColor(i),
        })),
        'Tp (s)',
    )

    const chartW = (PW - M * 2 - 6) / 2
    const chartH = 56

    // Chart titles
    pdf.setTextColor(51, 65, 85)
    pdf.setFont('helvetica', 'bold')
    pdf.setFontSize(9)
    pdf.text('Altura Significativa — Hs (m)', M, y - 1)
    pdf.text('Periodo Pico — Tp (s)', M + chartW + 6, y - 1)

    pdf.addImage(hsImg, 'PNG', M, y, chartW, chartH)
    pdf.addImage(tpImg, 'PNG', M + chartW + 6, y, chartW, chartH)
    y += chartH + 6

    // ── Table ───────────────────────────────────────────────────────────────
    // Nº de columnas por modelo: Hs, Tp, Dir, Cota Ru2%, Cota Ru1%.
    const COLS_PER_MODEL = 5

    const head = [
        [
            'Fecha / Hora',
            'Marea (m)',
            ...models.flatMap(m => [
                `${m.toUpperCase()}\nHs (m)`,
                `${m.toUpperCase()}\nTp (s)`,
                `${m.toUpperCase()}\nDir (°)`,
                `${m.toUpperCase()}\nCota Ru2% (m)`,
                `${m.toUpperCase()}\nCota Ru1% (m)`,
            ]),
        ],
    ]

    const body = hourlyData.map(row => [
        fmtFull(row.time),
        row.tide != null ? Number(row.tide).toFixed(2) : '–',
        ...models.flatMap(m => [
            row[m]?.height != null ? row[m].height.toFixed(2) : '–',
            row[m]?.period != null ? row[m].period.toFixed(1) : '–',
            row[m]?.direction != null ? row[m].direction.toFixed(0) + '°' : '–',
            row[m]?.cotaRu2p != null ? row[m].cotaRu2p.toFixed(2) : '–',
            row[m]?.cotaRu1p != null ? row[m].cotaRu1p.toFixed(2) : '–',
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
        columnStyles: { 0: { halign: 'left', minCellWidth: 28 }, 1: { halign: 'center' } },
        alternateRowStyles: { fillColor: [248, 250, 252] },
        didParseCell(data) {
            if (data.section !== 'body' || data.column.index <= 1) return
            const relIdx = (data.column.index - 2) % COLS_PER_MODEL
            // Hs es la primera columna de cada bloque de modelo (relIdx 0) -> semáforo.
            if (relIdx === 0) {
                const val = parseFloat(data.cell.raw as string)
                if (isNaN(val)) return
                const { fill, text } = hsColor(val)
                data.cell.styles.fillColor = fill
                data.cell.styles.textColor = text
                data.cell.styles.fontStyle = 'bold'
                data.cell.styles.halign = 'center'
                return
            }
            // Cotas de remonte (relIdx 3 y 4): acento violeta, sin semáforo de Hs.
            if (relIdx === 3 || relIdx === 4) {
                data.cell.styles.textColor = [124, 58, 237]
                data.cell.styles.fontStyle = 'bold'
                data.cell.styles.halign = 'center'
            }
        },
        willDrawCell(data) {
            if (data.section !== 'body' || data.column.index <= 1) return
            const relIdx = (data.column.index - 2) % COLS_PER_MODEL
            if (relIdx !== 0) {
                data.cell.styles.halign = 'center'
            }
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
