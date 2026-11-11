"""Mini-generador: a partir de una lista de bloques crea el mismo documento en PDF (reportlab) y Markdown."""
import os
import re

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

FUENTES = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
for nombre, archivo in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"),
                        ("DV-I", "DejaVuSans-Oblique.ttf"), ("DV-BI", "DejaVuSans-BoldOblique.ttf"),
                        ("DV-M", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(nombre, os.path.join(FUENTES, archivo)))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

AZUL = colors.HexColor("#14365D")
GRIS = colors.HexColor("#EEF1F5")

E = {
    "title": ParagraphStyle("t", fontName="DV-B", fontSize=22, leading=27, textColor=AZUL, alignment=TA_CENTER, spaceAfter=10),
    "sub": ParagraphStyle("s", fontName="DV", fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=4),
    "h1": ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=AZUL, spaceBefore=14, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=12, leading=15, textColor=AZUL, spaceBefore=10, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="DV", fontSize=9.5, leading=13.5, spaceAfter=6),
    "li": ParagraphStyle("li", fontName="DV", fontSize=9.5, leading=13, leftIndent=14, bulletIndent=2, spaceAfter=2),
    "cell": ParagraphStyle("c", fontName="DV", fontSize=8, leading=10.5),
    "cellh": ParagraphStyle("ch", fontName="DV-B", fontSize=8, leading=10.5, textColor=colors.white),
    "formula": ParagraphStyle("f", fontName="DV-I", fontSize=10, leading=15, alignment=TA_CENTER, spaceBefore=3, spaceAfter=6,
                              backColor=GRIS, borderPadding=4),
    "cap": ParagraphStyle("cap", fontName="DV-I", fontSize=8, leading=10, alignment=TA_CENTER, spaceAfter=8),
    "nota": ParagraphStyle("n", fontName="DV", fontSize=9, leading=12.5, spaceAfter=6, backColor=colors.HexColor("#FFF6DB"),
                           borderPadding=5, borderColor=colors.HexColor("#E3B93C"), borderWidth=0.6),
}


def a_md(texto):
    t = re.sub(r"</?b>", "**", texto)
    t = re.sub(r"</?i>", "*", t)
    t = re.sub(r"<br/>", "  \n", t)
    t = re.sub(r"</?(sub|super|font[^>]*)>", "", t)
    return t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def generar(bloques, pdf, md=None, apaisado=False, encabezado="", ruta_base="."):
    tam = landscape(letter) if apaisado else letter
    margen = 0.6 * inch if apaisado else 0.8 * inch
    ancho_util = tam[0] - 2 * margen

    def pie(canvas, doc):
        canvas.saveState()
        canvas.setFont("DV", 7.5)
        canvas.setFillColor(colors.grey)
        canvas.drawString(margen, 0.4 * inch, encabezado)
        canvas.drawRightString(tam[0] - margen, 0.4 * inch, f"Pagina {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(pdf, pagesize=tam, leftMargin=margen, rightMargin=margen, topMargin=0.7 * inch,
                            bottomMargin=0.7 * inch, title=encabezado, author="Grupo 4 - ICCIA")
    hist, mdl = [], []
    for b in bloques:
        k = b[0]
        if k == "title":
            hist.append(Paragraph(b[1], E["title"])); mdl.append(f"# {a_md(b[1])}\n")
        elif k == "sub":
            hist.append(Paragraph(b[1], E["sub"])); mdl.append(f"{a_md(b[1])}  ")
        elif k == "space":
            hist.append(Spacer(1, b[1] * inch)); mdl.append("")
        elif k == "h1":
            hist.append(Paragraph(b[1], E["h1"])); mdl.append(f"\n## {a_md(b[1])}\n")
        elif k == "h2":
            hist.append(Paragraph(b[1], E["h2"])); mdl.append(f"\n### {a_md(b[1])}\n")
        elif k == "p":
            hist.append(Paragraph(b[1], E["p"])); mdl.append(f"{a_md(b[1])}\n")
        elif k == "nota":
            hist.append(Paragraph(b[1], E["nota"])); mdl.append(f"> {a_md(b[1])}\n")
        elif k == "formula":
            hist.append(Paragraph(b[1], E["formula"])); mdl.append(f"`{a_md(b[1])}`\n")
        elif k == "bullets":
            for item in b[1]:
                hist.append(Paragraph(item, E["li"], bulletText="•"))
                mdl.append(f"- {a_md(item)}")
            hist.append(Spacer(1, 4)); mdl.append("")
        elif k == "code":
            hist.append(Preformatted(b[1], ParagraphStyle("code", fontName="DV-M", fontSize=7.6, leading=9.6,
                                                            backColor=GRIS, borderPadding=4, spaceAfter=8)))
            mdl.append("```\n" + b[1] + "\n```\n")
        elif k == "table":
            _, cab, filas = b[:3]
            anchos = b[3] if len(b) > 3 else None
            datos = [[Paragraph(c, E["cellh"]) for c in cab]] + [[Paragraph(str(c), E["cell"]) for c in f] for f in filas]
            cw = [ancho_util * x for x in anchos] if anchos else None
            t = Table(datos, colWidths=cw, repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C0CC")),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS]), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
            hist.append(t); hist.append(Spacer(1, 8))
            mdl.append("| " + " | ".join(a_md(c) for c in cab) + " |")
            mdl.append("|" + "---|" * len(cab))
            for f in filas:
                mdl.append("| " + " | ".join(a_md(str(c)) for c in f) + " |")
            mdl.append("")
        elif k == "img":
            _, ruta, ancho_rel, leyenda = b
            ruta_abs = os.path.join(ruta_base, ruta)
            from PIL import Image as PI
            w, h = PI.open(ruta_abs).size
            aw = ancho_util * ancho_rel
            hist.append(KeepTogether([Image(ruta_abs, width=aw, height=aw * h / w), Paragraph(leyenda, E["cap"])]))
            mdl.append(f"![{a_md(leyenda)}]({ruta})\n\n*{a_md(leyenda)}*\n")
        elif k == "pagebreak":
            hist.append(PageBreak())
        else:
            raise ValueError(k)
    doc.build(hist, onFirstPage=pie, onLaterPages=pie)
    if md:
        with open(md, "w", encoding="utf-8") as f:
            f.write("\n".join(mdl) + "\n")
