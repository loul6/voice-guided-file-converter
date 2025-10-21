import io
import os
import tempfile
from PIL import Image
import docx
from pdfminer.high_level import extract_text
from pdf2docx import Converter
import pypandoc

CONVERSIONS = {
    'docx->pdf': (['docx'], 'application/pdf'),
    'pdf->docx': (['pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
    'pdf->txt': (['pdf'], 'text/plain'),
    'docx->txt': (['docx'], 'text/plain'),
    'img->png': (['jpg', 'jpeg', 'webp'], 'image/png'),
    'img->jpg': (['png', 'webp'], 'image/jpeg'),
    'img->webp': (['png', 'jpg', 'jpeg'], 'image/webp'),
}

def perform_conversion(input_stream, filename, target_format):
    base_name = filename.rsplit('.', 1)[0]
    input_ext = filename.rsplit('.', 1)[1].lower()

    allowed_exts = CONVERSIONS[target_format][0]
    if input_ext not in allowed_exts:
        raise ValueError(f"Extensión inválida. Esperado: {', '.join(allowed_exts)}")

    # --- DOCX -> PDF ---
    if target_format == 'docx->pdf':
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_in:
            temp_in.write(input_stream.getvalue())
            temp_in_path = temp_in.name
        temp_out_path = tempfile.mktemp(suffix=".pdf")
        pypandoc.convert_file(temp_in_path, 'pdf', outputfile=temp_out_path, extra_args=['--standalone'])
        with open(temp_out_path, 'rb') as f:
            data = f.read()
        os.remove(temp_in_path)
        os.remove(temp_out_path)
        return io.BytesIO(data), f"{base_name}.pdf"

    # --- PDF -> DOCX ---
    if target_format == 'pdf->docx':
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_in:
            temp_in.write(input_stream.getvalue())
            temp_in_path = temp_in.name
        temp_out_path = tempfile.mktemp(suffix=".docx")
        cv = Converter(temp_in_path)
        cv.convert(temp_out_path, start=0, end=None)
        cv.close()
        with open(temp_out_path, 'rb') as f:
            data = f.read()
        os.remove(temp_in_path)
        os.remove(temp_out_path)
        return io.BytesIO(data), f"{base_name}.docx"

    # --- PDF -> TXT ---
    if target_format == 'pdf->txt':
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(input_stream.getvalue())
            temp_pdf_path = temp_pdf.name
        text = extract_text(temp_pdf_path)
        os.remove(temp_pdf_path)
        return io.BytesIO(text.encode('utf-8')), f"{base_name}.txt"

    # --- DOCX -> TXT ---
    if target_format == 'docx->txt':
        doc = docx.Document(input_stream)
        text = "\n".join([p.text for p in doc.paragraphs])
        return io.BytesIO(text.encode('utf-8')), f"{base_name}.txt"

    # --- IMÁGENES ---
    if target_format.startswith('img->'):
        target_ext = target_format.split('->')[1]
        im = Image.open(input_stream)
        if target_ext in ('jpg', 'jpeg') and im.mode in ('RGBA', 'LA'):
            bg = Image.new('RGB', im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        elif target_ext in ('jpg', 'jpeg'):
            im = im.convert('RGB')
        output_stream = io.BytesIO()
        pil_format = 'JPEG' if target_ext == 'jpg' else target_ext.upper()
        im.save(output_stream, format=pil_format)
        output_stream.seek(0)
        return output_stream, f"{base_name}.{target_ext}"

    raise ValueError("Conversión no soportada.")
