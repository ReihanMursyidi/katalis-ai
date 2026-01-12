from fpdf import FPDF
import re
import io

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 116, 139)

        self.set_draw_color(59, 130, 246) # Blue Accent
        self.set_line_width(0.5)
        self.line(10, 18, 200, 18)
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Halaman {self.page_no()}/{{nb}}', 0, 0, 'C')

def create_pdf_bytes(title: str, content: str) -> bytes:
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(0)
    pdf.multi_cell(0, 10, title.upper(), align='C')
    pdf.ln(5)

    pdf.set_draw_color(203, 213, 225)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(0)

    lines = content.split('\n')

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith('#'):
            level = stripped.count('#')
            clean_text = stripped.lstrip('#').strip()
            
            pdf.ln(6)

            if level == 1:
                pdf.set_font('Helvetica', 'B', 14)
                pdf.set_text_color(0)
            elif level == 2:
                pdf.set_font('Helvetica', 'B', 12)
                pdf.set_text_color(0)
            else:
                pdf.set_font('Helvetica', 'B', 11)

            pdf.multi_cell(0, 8, clean_text)

            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(0)

        elif stripped.startswith('- ') or (len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == '.'):
            pdf.ln(2)
            pdf.set_x(20)

            try:
                pdf.multi_cell(0, 6, stripped, markdown=True)
            except:
                pdf.multi_cell(0, 6, stripped)

        else:
            pdf.set_x(10)

            if stripped.startswith('**') and stripped.endswith('**') and len(stripped) < 60:
                pdf.ln(4)

            try:
                pdf.multi_cell(0, 6, stripped, markdown=True)
            except:
                pdf.multi_cell(0, 6, stripped)

    return bytes(pdf.output(dest='S'))