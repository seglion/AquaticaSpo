"""Genera el PDF de previsión (parte de oleaje) para una zona, en formato y
contenido equivalentes al que el frontend genera bajo demanda con jsPDF/Chart.js
(ver frontend/src/utils/forecastPdfGenerator.ts). Solo se usa el modelo EWAM,
igual que en el frontend."""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.pdfgen.canvas import Canvas

from app.notifications.domain.models import ZoneAlert
from app.shared.alert_levels import classify_wind_alert

MODEL = "ewam"

MADRID_TZ = ZoneInfo("Europe/Madrid")
UTC_TZ = ZoneInfo("UTC")

_WEEKDAYS_SHORT = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
_MONTHS_SHORT = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

COTA_GREEN = (colors.Color(167 / 255, 243 / 255, 208 / 255), colors.Color(6 / 255, 78 / 255, 59 / 255))
COTA_YELLOW = (colors.Color(253 / 255, 224 / 255, 71 / 255), colors.Color(113 / 255, 63 / 255, 18 / 255))
COTA_ORANGE = (colors.Color(249 / 255, 115 / 255, 22 / 255), colors.Color(255 / 255, 247 / 255, 237 / 255))
COTA_RED = (colors.Color(220 / 255, 38 / 255, 38 / 255), colors.Color(255 / 255, 241 / 255, 242 / 255))

WARN_FILL = colors.Color(254 / 255, 202 / 255, 202 / 255)
WARN_TEXT = colors.Color(153 / 255, 27 / 255, 27 / 255)

# Mismo mapeo nivel → color que TAILWIND_CLASSES en frontend/src/utils/wave-colors.ts,
# usado para el semáforo de viento (Vel/Ráf), que ahí sí colorea todas las celdas
# (incluida la de "sin alerta") y no solo las que superan un umbral fijo.
WIND_ALERT_COLORS = {
    None: (colors.HexColor("#6ee7b7"), colors.HexColor("#064e3b")),  # "Sin alerta" -> nivel null
    "light_green": (colors.HexColor("#6ee7b7"), colors.HexColor("#064e3b")),
    "dark_green": (colors.HexColor("#047857"), colors.HexColor("#d1fae5")),
    "yellow": (colors.HexColor("#fde047"), colors.HexColor("#713f12")),
    "orange": (colors.HexColor("#f97316"), colors.HexColor("#fed7aa")),
    "red": (colors.HexColor("#dc2626"), colors.HexColor("#fee2e2")),
}

HEADER_BG = colors.Color(15 / 255, 23 / 255, 42 / 255)
HEADER_TEXT = colors.Color(248 / 255, 250 / 255, 252 / 255)
ALT_ROW = colors.Color(248 / 255, 250 / 255, 252 / 255)
BODY_TEXT = colors.Color(51 / 255, 65 / 255, 85 / 255)
FOOTER_TEXT = colors.Color(148 / 255, 163 / 255, 184 / 255)

PAGE_SIZE = landscape(A4)
MARGIN = 14 * mm
HEADER_H = 22 * mm


def _parse_madrid(iso: str) -> datetime:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    return dt.astimezone(MADRID_TZ)


def _fmt_full(iso: Optional[str]) -> str:
    if not iso:
        return "-"
    dt = _parse_madrid(iso)
    return f"{_WEEKDAYS_SHORT[dt.weekday()]}, {dt.day:02d} {_MONTHS_SHORT[dt.month - 1]} {dt.hour:02d}:{dt.minute:02d}"


def _fmt_short(iso: Optional[str]) -> str:
    if not iso:
        return "-"
    dt = _parse_madrid(iso)
    return f"{dt.day:02d}/{dt.month:02d} {dt.hour:02d}:{dt.minute:02d}"


def _cota_colors(value: float, dock_elevation: float):
    ratio = value / dock_elevation
    if ratio < 0.6:
        return COTA_GREEN
    if ratio < 0.8:
        return COTA_YELLOW
    if ratio < 1.0:
        return COTA_ORANGE
    return COTA_RED


def _num(value: Any, decimals: int) -> str:
    if value is None:
        return "–"
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return "–"


def _render_chart(labels: List[str], values: List[Optional[float]], y_label: str, color: str) -> bytes:
    fig, ax = plt.subplots(figsize=(4.3, 1.95), dpi=160)
    xs = list(range(len(values)))
    ax.plot(xs, values, color=color, linewidth=1.6)
    ax.set_ylabel(y_label, fontsize=8, color="#475569")
    step = max(1, len(labels) // 12)
    ticks = xs[::step]
    ax.set_xticks(ticks)
    ax.set_xticklabels([labels[i] for i in ticks], rotation=45, ha="right", fontsize=6, color="#64748b")
    ax.tick_params(axis="y", labelsize=7, colors="#64748b")
    ax.grid(color="#e2e8f0", linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_color("#e2e8f0")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


class _NumberedCanvas(Canvas):
    """Dibuja 'AquaticaSpo — Página X de Y' en cada página; requiere saber el
    total de páginas, que solo se conoce al terminar de generar el documento
    (patrón estándar de reportlab: guarda el estado por página y redibuja el
    pie al final)."""

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self._saved_states = []

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._draw_footer(total)
            Canvas.showPage(self)
        Canvas.save(self)

    def _draw_footer(self, total_pages: int):
        self.setFont("Helvetica", 7)
        self.setFillColor(FOOTER_TEXT)
        self.drawCentredString(
            PAGE_SIZE[0] / 2,
            4 * mm,
            f"AquaticaSpo  —  Página {self._pageNumber} de {total_pages}",
        )


def _draw_header(canvas_obj: Canvas, zone: ZoneAlert, execution_date: str):
    pw, _ = PAGE_SIZE
    canvas_obj.saveState()
    canvas_obj.setFillColor(HEADER_BG)
    canvas_obj.rect(0, PAGE_SIZE[1] - HEADER_H, pw, HEADER_H, fill=1, stroke=0)

    canvas_obj.setFillColor(HEADER_TEXT)
    canvas_obj.setFont("Helvetica-Bold", 15)
    canvas_obj.drawString(MARGIN, PAGE_SIZE[1] - 11 * mm, "Parte de Previsión de Oleaje")

    canvas_obj.setFont("Helvetica", 8)
    lat_lon = ""
    if zone.lat is not None and zone.lon is not None:
        lat_lon = f"  |  Lat: {zone.lat:.4f}, Lon: {zone.lon:.4f}"
    zone_line = f"Zona: {zone.zone_name or '-'}{lat_lon}"
    generated = datetime.now(MADRID_TZ).strftime("%d/%m/%Y %H:%M")
    meta_line = f"{zone_line}  |  Datos: {_fmt_full(execution_date)}  |  Generado: {generated}"
    canvas_obj.drawString(MARGIN, PAGE_SIZE[1] - 18 * mm, meta_line)
    canvas_obj.restoreState()


def generate_zone_pdf(
    zone: ZoneAlert,
    hourly: Dict[str, Any],
    execution_date: str,
    map_png_bytes: Optional[bytes] = None,
) -> Optional[bytes]:
    """Genera el PDF de previsión de una zona (solo modelo EWAM). Devuelve
    None si no hay datos horarios o del modelo EWAM para esa zona (nunca debe
    lanzar: el llamador ya trata cualquier fallo como 'sin adjunto')."""

    times = hourly.get("time") or []
    hs = hourly.get(f"wave_height_{MODEL}") or []
    if not times or not hs:
        return None

    dock_elevation = zone.dock_elevation or 0
    tp = hourly.get(f"wave_period_{MODEL}", [])
    direction = hourly.get(f"wave_direction_{MODEL}", [])
    cota = hourly.get(f"cota_ru2p_{MODEL}", [])
    q = hourly.get(f"caudal_rebase_{MODEL}", [])
    tide = hourly.get(f"tide_level_{MODEL}", [])
    wind_speed = hourly.get("wind_speed_10m", [])
    wind_gusts = hourly.get("wind_gusts_10m", [])
    wind_dir = hourly.get("wind_direction_10m", [])

    labels_short = [_fmt_short(t) for t in times]

    hs_png = _render_chart(labels_short, hs, "Hs (m)", "#0ea5e9")
    tp_png = _render_chart(labels_short, tp, "Tp (s)", "#10b981")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_H + 6 * mm,
        bottomMargin=10 * mm,
    )

    available_w = PAGE_SIZE[0] - 2 * MARGIN
    story = []

    # ── Gráficos + mapa, uno al lado del otro ──────────────────────────────
    title_style = ParagraphStyle("chart_title", fontName="Helvetica-Bold", fontSize=8, textColor=BODY_TEXT)
    item_w = available_w / 3
    chart_h = 40 * mm

    def _img_cell(png_bytes: Optional[bytes], title: str):
        if not png_bytes:
            return Paragraph(title, title_style)
        img = Image(io.BytesIO(png_bytes), width=item_w - 4, height=chart_h)
        return [Paragraph(title, title_style), img]

    images_row = [
        _img_cell(hs_png, "Altura Significativa — Hs (m)"),
        _img_cell(tp_png, "Periodo Pico — Tp (s)"),
        _img_cell(map_png_bytes, "Localización del Punto"),
    ]
    images_table = Table([images_row], colWidths=[item_w] * 3)
    images_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(images_table)
    story.append(Spacer(1, 5 * mm))

    # ── Tabla horaria ───────────────────────────────────────────────────────
    head = [
        "Fecha / Hora", "Marea (m)", "Viento\nVel (km/h)", "Viento\nRáf (km/h)", "Viento\nDir (°)",
        "Hs (m)", "Tp (s)", "Dir (°)", "Remonte\nCota (m)", "Rebase\nQ (l/m/s)",
    ]
    body = []
    n = len(times)
    for i in range(n):
        body.append([
            _fmt_full(times[i]),
            _num(tide[i] if i < len(tide) else None, 2),
            _num(wind_speed[i] if i < len(wind_speed) else None, 1),
            _num(wind_gusts[i] if i < len(wind_gusts) else None, 1),
            (f"{wind_dir[i]:.0f}°" if i < len(wind_dir) and wind_dir[i] is not None else "–"),
            _num(hs[i] if i < len(hs) else None, 2),
            _num(tp[i] if i < len(tp) else None, 1),
            (f"{direction[i]:.0f}°" if i < len(direction) and direction[i] is not None else "–"),
            _num(cota[i] if i < len(cota) else None, 2),
            _num(q[i] if i < len(q) else None, 2),
        ])

    table_data = [head] + body
    col_widths = [available_w * w for w in (0.14, 0.09, 0.09, 0.09, 0.08, 0.10, 0.09, 0.08, 0.12, 0.12)]

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), HEADER_TEXT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    for row_idx in range(1, len(table_data)):
        if row_idx % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), ALT_ROW))

        data_idx = row_idx - 1

        # Semáforo de viento (Vel/Ráf), igual que en el visor: cada celda con dato
        # se colorea según el nivel de 'wind_levels' en alert_thresholds.json
        # (incluida la celda "sin alerta", en verde claro), no solo cuando supera
        # un umbral fijo.
        wind_speed_val = wind_speed[data_idx] if data_idx < len(wind_speed) else None
        if wind_speed_val is not None:
            alert = classify_wind_alert(wind_speed_val)
            fill, text = WIND_ALERT_COLORS.get(alert["level"], WIND_ALERT_COLORS[None])
            style_cmds.append(("BACKGROUND", (2, row_idx), (2, row_idx), fill))
            style_cmds.append(("TEXTCOLOR", (2, row_idx), (2, row_idx), text))
            if alert["level"]:
                style_cmds.append(("FONTNAME", (2, row_idx), (2, row_idx), "Helvetica-Bold"))

        wind_gusts_val = wind_gusts[data_idx] if data_idx < len(wind_gusts) else None
        if wind_gusts_val is not None:
            alert = classify_wind_alert(wind_gusts_val)
            fill, text = WIND_ALERT_COLORS.get(alert["level"], WIND_ALERT_COLORS[None])
            style_cmds.append(("BACKGROUND", (3, row_idx), (3, row_idx), fill))
            style_cmds.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), text))
            if alert["level"]:
                style_cmds.append(("FONTNAME", (3, row_idx), (3, row_idx), "Helvetica-Bold"))

        cota_val = cota[data_idx] if data_idx < len(cota) else None
        if cota_val is not None and dock_elevation > 0:
            fill, text = _cota_colors(cota_val, dock_elevation)
            style_cmds.append(("BACKGROUND", (8, row_idx), (8, row_idx), fill))
            style_cmds.append(("TEXTCOLOR", (8, row_idx), (8, row_idx), text))
            style_cmds.append(("FONTNAME", (8, row_idx), (8, row_idx), "Helvetica-Bold"))

        q_val = q[data_idx] if data_idx < len(q) else None
        if q_val is not None and q_val > 10:
            style_cmds.append(("BACKGROUND", (9, row_idx), (9, row_idx), WARN_FILL))
            style_cmds.append(("TEXTCOLOR", (9, row_idx), (9, row_idx), WARN_TEXT))
            style_cmds.append(("FONTNAME", (9, row_idx), (9, row_idx), "Helvetica-Bold"))

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle(style_cmds))
    story.append(table)

    def _on_page(canvas_obj, _doc):
        _draw_header(canvas_obj, zone, execution_date)

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page, canvasmaker=_NumberedCanvas)

    return buf.getvalue()
