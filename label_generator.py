"""
label_generator.py - Geração de imagens QR e PDFs de etiquetas
"""
import logging
from io import BytesIO
from functools import lru_cache

import qrcode
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

logger = logging.getLogger(__name__)

# Tamanho padrão da etiqueta pequena
ETIQUETA_W = 500
ETIQUETA_H = 620

# Tamanho da etiqueta larga (7 QR por folha)
LARGA_W = 3150
LARGA_H = 800


@lru_cache(maxsize=1)
def _carregar_fonte(tamanho: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Carrega a fonte uma vez e reutiliza (cache)."""
    for nome in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    logger.warning("Fonte TTF não encontrada, usando fonte padrão.")
    return ImageFont.load_default()


def _gerar_qr_image(texto: str, box_size: int = 12, border: int = 1) -> Image.Image:
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(str(texto))
    qr.make(fit=True)
    return qr.make_image().convert("RGB")


def gerar_etiqueta_pequena(codigo: str) -> Image.Image:
    """Gera imagem de etiqueta individual com QR code e codigo embaixo."""
    qr_img = _gerar_qr_image(codigo, box_size=12, border=1)
    qr_w, qr_h = qr_img.size

    canvas_w = qr_w + 300
    canvas_h = qr_h + 120
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    fonte = _carregar_fonte(60)
    try:
        tw = draw.textlength(codigo, font=fonte)
    except AttributeError:
        tw = len(codigo) * 36

    draw.text(((canvas_w - tw) / 2, 20), codigo, fill="black", font=fonte)
    canvas.paste(qr_img, (130, 100))
    return canvas


def gerar_etiqueta_larga(codigos: list[str]) -> Image.Image:
    """Gera etiqueta larga com ate 7 QR codes lado a lado.

    Celulas vazias ("") sao renderizadas como espaco em branco,
    sem QR code nem texto - usadas para separar locais diferentes.
    """
    canvas = Image.new("RGB", (LARGA_W, LARGA_H), "white")
    draw = ImageDraw.Draw(canvas)

    fonte_titulo = _carregar_fonte(80)
    fonte_codigo = _carregar_fonte(45)

    # Titulo baseado no primeiro codigo NAO vazio do grupo
    primeiro_valido = next((c for c in codigos if c and "." in str(c)), None)
    if primeiro_valido:
        partes = str(primeiro_valido).split(".")
        titulo = f"RUA {partes[0]} POSICAO {partes[1]}"
        try:
            tw = draw.textlength(titulo, font=fonte_titulo)
        except AttributeError:
            tw = len(titulo) * 48
        draw.text(((LARGA_W - tw) / 2, 25), titulo, fill="black", font=fonte_titulo)

    col_w = LARGA_W / 7

    # Linhas divisorias
    for i in range(1, 7):
        draw.line([(i * col_w, 120), (i * col_w, LARGA_H - 20)], fill="black", width=10)

    for i, codigo in enumerate(codigos[:7]):
        # Celula vazia: pula sem desenhar QR nem texto
        if not codigo or not codigo.strip():
            continue

        qr_img = _gerar_qr_image(str(codigo), box_size=13, border=2)
        qr_w, _ = qr_img.size

        x_centro = i * col_w + col_w / 2
        try:
            tw = draw.textlength(str(codigo), font=fonte_codigo)
        except AttributeError:
            tw = len(str(codigo)) * 27

        draw.text((x_centro - tw / 2, 160), str(codigo), fill="black", font=fonte_codigo)
        canvas.paste(qr_img, (int(x_centro - qr_w / 2), 250))

    return canvas


def _imagem_para_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def gerar_pdf_lote(codigos: list[str]) -> bytes:
    """Gera PDF com uma etiqueta por pagina (formato 65x100mm)."""
    pdf = FPDF("L", "mm", (65, 100))
    for codigo in codigos:
        img = gerar_etiqueta_pequena(codigo)
        img_bytes = _imagem_para_bytes(img)
        pdf.add_page()
        buf = BytesIO(img_bytes)
        pdf.image(buf, 5, 5, 90)
    return bytes(pdf.output())


def gerar_pdf_larga(grupos: list[list[str]]) -> bytes:
    """Gera PDF de etiquetas largas (315x80mm), um grupo por pagina."""
    pdf = FPDF("L", "mm", (80, 315))
    for grupo in grupos:
        img = gerar_etiqueta_larga(grupo)
        img_bytes = _imagem_para_bytes(img)
        pdf.add_page()
        buf = BytesIO(img_bytes)
        pdf.image(buf, 0, 0, 315, 80)
    return bytes(pdf.output())
