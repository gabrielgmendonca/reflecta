import io
import csv
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.models import Board


class ExportService:
    @staticmethod
    def export_json(board: Board) -> str:
        data = {
            "title": board.title,
            "slug": board.slug,
            "created_at": board.created_at.isoformat(),
            "columns": [],
        }

        for column in board.columns:
            col_data = {
                "title": column.title,
                "color": column.color,
                "cards": [],
            }
            for card in column.cards:
                card_data = {
                    "content": card.content,
                    "votes": len(card.votes),
                    "color": card.color,
                }
                col_data["cards"].append(card_data)
            data["columns"].append(col_data)

        return json.dumps(data, indent=2)

    @staticmethod
    def export_csv(board: Board) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Column", "Card Content", "Votes"])

        for column in board.columns:
            for card in column.cards:
                writer.writerow([column.title, card.content, len(card.votes)])

        return output.getvalue()

    @staticmethod
    def export_pdf(board: Board) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=20,
        )
        elements.append(Paragraph(board.title, title_style))
        elements.append(Spacer(1, 12))

        # Build table data
        for column in board.columns:
            # Column header
            col_header_style = ParagraphStyle(
                "ColHeader",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor(column.color),
            )
            elements.append(Paragraph(column.title, col_header_style))
            elements.append(Spacer(1, 6))

            if column.cards:
                table_data = [["Content", "Votes"]]
                for card in column.cards:
                    table_data.append([card.content, str(len(card.votes))])

                table = Table(table_data, colWidths=[5 * inch, 1 * inch])
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("ALIGN", (1, 0), (1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 12),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ]
                    )
                )
                elements.append(table)
            else:
                elements.append(Paragraph("No cards", styles["Normal"]))

            elements.append(Spacer(1, 20))

        doc.build(elements)
        return buffer.getvalue()
