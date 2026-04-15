"""Render QBR markdown into a styled PDF document."""

from datetime import datetime
from html import escape
from io import StringIO
import textwrap

from markdown import markdown


def markdown_to_pdf(markdown_content: str, account_name: str) -> bytes:
    try:
        return _render_with_weasyprint(markdown_content, account_name)
    except Exception:
        return _render_fallback_pdf(markdown_content, account_name)


def _render_with_weasyprint(markdown_content: str, account_name: str) -> bytes:
    from weasyprint import HTML

    generated_on = datetime.now().strftime("%B %d, %Y")
    rendered_markdown = markdown(markdown_content, extensions=["tables", "fenced_code"])

    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <style>
          @page {{
            size: A4;
            margin: 20mm 16mm 18mm;

            @top-left {{
              content: "monday.com QBR Co-Pilot";
              color: #5b6cff;
              font-size: 9pt;
              font-weight: 700;
            }}

            @top-right {{
              content: "{escape(account_name)}";
              color: #6b738f;
              font-size: 9pt;
            }}

            @bottom-right {{
              content: "Generated {generated_on} | Page " counter(page);
              color: #8c94ad;
              font-size: 8pt;
            }}
          }}

          :root {{
            color-scheme: light;
          }}

          body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: #1f2747;
            font-size: 11pt;
            line-height: 1.65;
            margin: 0;
          }}

          .cover {{
            border-bottom: 2px solid #dfe4ff;
            margin-bottom: 24px;
            padding-bottom: 18px;
          }}

          .eyebrow {{
            color: #5b6cff;
            font-size: 9pt;
            font-weight: 700;
            letter-spacing: 0.16em;
            margin: 0 0 10px;
            text-transform: uppercase;
          }}

          h1 {{
            color: #1f2747;
            font-size: 25pt;
            line-height: 1.15;
            margin: 0 0 8px;
          }}

          h2 {{
            color: #5b6cff;
            font-size: 16pt;
            line-height: 1.25;
            margin: 28px 0 10px;
          }}

          h3 {{
            color: #33246d;
            font-size: 12.5pt;
            margin: 22px 0 8px;
          }}

          p, li {{
            color: #334064;
          }}

          ul, ol {{
            padding-left: 20px;
          }}

          strong {{
            color: #1f2747;
          }}

          blockquote {{
            border-left: 4px solid #5b6cff;
            color: #465171;
            margin: 18px 0;
            padding: 6px 0 6px 14px;
          }}

          table {{
            border-collapse: collapse;
            margin: 18px 0;
            width: 100%;
          }}

          th {{
            background: #eef1ff;
            color: #33246d;
            font-size: 9.5pt;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-align: left;
          }}

          th, td {{
            border: 1px solid #dfe4ff;
            padding: 10px 12px;
            vertical-align: top;
          }}

          code {{
            background: #f4f6ff;
            border-radius: 6px;
            color: #33246d;
            font-size: 9.5pt;
            padding: 2px 5px;
          }}

          pre {{
            background: #f4f6ff;
            border-radius: 12px;
            overflow-wrap: anywhere;
            padding: 14px;
            white-space: pre-wrap;
          }}
        </style>
      </head>
      <body>
        <section class="cover">
          <p class="eyebrow">QBR Draft</p>
          <h1>{escape(account_name)}</h1>
          <p>Prepared for Customer Success review on {generated_on}.</p>
        </section>
        {rendered_markdown}
      </body>
    </html>
    """

    return HTML(string=html).write_pdf()


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_line(text: str, width: int) -> list[str]:
    if not text:
        return [""]
    return textwrap.wrap(
        text,
        width=width,
        replace_whitespace=False,
        drop_whitespace=False,
        break_long_words=False,
    ) or [text]


def _build_content_stream(lines: list[tuple[str, int, str, float, bool]]) -> str:
    stream = StringIO()
    for text, font_size, color, y_position, bold in lines:
        stream.write("BT\n")
        stream.write(f"/{'F2' if bold else 'F1'} {font_size} Tf\n")
        if color == "brand":
            stream.write("0.36 0.42 1 rg\n")
        elif color == "ink":
            stream.write("0.12 0.15 0.28 rg\n")
        else:
            stream.write("0.31 0.36 0.49 rg\n")
        stream.write(f"1 0 0 1 48 {y_position:.2f} Tm\n")
        stream.write(f"({_escape_pdf_text(text)}) Tj\n")
        stream.write("ET\n")
    return stream.getvalue()


def _serialize_pdf(objects: list[str]) -> bytes:
    buffer = StringIO()
    buffer.write("%PDF-1.4\n")
    offsets = [0]

    for index, obj in enumerate(objects, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{index} 0 obj\n{obj}\nendobj\n")

    xref_start = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n")
    buffer.write("0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n")
    buffer.write(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF"
    )
    return buffer.getvalue().encode("latin-1", errors="replace")


def _render_fallback_pdf(markdown_content: str, account_name: str) -> bytes:
    generated_on = datetime.now().strftime("%B %d, %Y")
    pages: list[list[tuple[str, int, str, float, bool]]] = [[]]
    y_position = 806.0

    def push_line(text: str, font_size: int, color: str, bold: bool = False) -> None:
        nonlocal y_position
        line_height = font_size + 6
        if y_position - line_height < 64:
            pages.append([])
            y_position = 780.0
        pages[-1].append((text, font_size, color, y_position, bold))
        y_position -= line_height

    push_line("monday.com QBR Co-Pilot", 10, "brand", True)
    push_line(generated_on, 9, "muted")
    y_position -= 14
    push_line(account_name, 24, "ink", True)
    y_position -= 12

    for raw_line in markdown_content.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            y_position -= 10
            continue

        font_size = 11
        color = "muted"
        bold = False
        wrap_width = 84
        prefix = ""

        if stripped.startswith("# "):
            stripped = stripped[2:].strip()
            font_size = 18
            color = "brand"
            bold = True
            wrap_width = 52
        elif stripped.startswith("## "):
            stripped = stripped[3:].strip()
            font_size = 15
            color = "brand"
            bold = True
            wrap_width = 58
        elif stripped.startswith("### "):
            stripped = stripped[4:].strip()
            font_size = 13
            color = "ink"
            bold = True
            wrap_width = 64
        elif stripped.startswith(("- ", "* ")):
            stripped = stripped[2:].strip()
            prefix = "• "
            color = "ink"
            wrap_width = 76
        else:
            color = "ink"

        for index, segment in enumerate(_wrap_line(stripped, wrap_width)):
            text = f"{prefix if index == 0 else '  '}{segment.strip()}"
            push_line(text, font_size, color, bold)

        y_position -= 4

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [" + " ".join(f"{3 + index * 2} 0 R" for index in range(len(pages))) + f"] /Count {len(pages)} >>",
    ]

    font_regular_object = 3 + len(pages) * 2
    font_bold_object = font_regular_object + 1

    for index, page in enumerate(pages):
        page_object_number = 3 + index * 2
        content_object_number = page_object_number + 1
        content_stream = _build_content_stream(page)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_regular_object} 0 R /F2 {font_bold_object} 0 R >> >> "
            f"/Contents {content_object_number} 0 R >>"
        )
        objects.append(
            f"<< /Length {len(content_stream.encode('latin-1', errors='replace'))} >>\nstream\n"
            f"{content_stream}endstream"
        )

    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    return _serialize_pdf(objects)
