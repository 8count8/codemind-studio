"""Ability diagnostic report PDF generation."""

from datetime import datetime
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class AbilityReportService:
    """Build a compact, printable Chinese ability diagnostic report."""

    FONT_NAME = "STSong-Light"
    DIMENSIONS = (
        ("syntax_score", "语法基础"),
        ("algorithm_score", "算法思维"),
        ("project_score", "项目实践"),
        ("debug_score", "调试能力"),
        ("security_score", "安全意识"),
    )

    @classmethod
    def _register_font(cls):
        if cls.FONT_NAME not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(UnicodeCIDFont(cls.FONT_NAME))

    @staticmethod
    def _score_level(score):
        if score >= 85:
            return "优秀"
        if score >= 70:
            return "熟练"
        if score >= 60:
            return "入门"
        return "待提升"

    @classmethod
    def build_pdf(cls, matrix_result, recommendations_result=None, username=None, generated_at=None):
        """Return a BytesIO containing a complete PDF report."""
        cls._register_font()
        generated_at = generated_at or datetime.now()
        matrix_result = matrix_result or {}
        matrix = matrix_result.get("matrix") or {}
        recommendations_result = recommendations_result or {}
        recommendations = recommendations_result.get("recommendations") or []
        weak_dimensions = matrix_result.get("weak_dimensions") or []

        scores = [float(matrix.get(key) or 0) for key, _ in cls.DIMENSIONS]
        average_score = matrix_result.get("average_score")
        if average_score is None or (not average_score and any(scores)):
            average_score = sum(scores) / len(scores)

        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=14 * mm,
            bottomMargin=15 * mm,
            title="CodeMind Studio 能力诊断报告",
            author="CodeMind Studio",
            subject="编程能力矩阵与个性化学习建议",
        )

        navy = colors.HexColor("#183B56")
        blue = colors.HexColor("#2563EB")
        pale_blue = colors.HexColor("#EFF6FF")
        light = colors.HexColor("#F8FAFC")
        muted = colors.HexColor("#64748B")
        border = colors.HexColor("#CBD5E1")
        red = colors.HexColor("#DC2626")

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"], fontName=cls.FONT_NAME,
            fontSize=23, leading=30, textColor=navy, alignment=TA_CENTER,
            spaceAfter=2 * mm,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle", parent=styles["Normal"], fontName=cls.FONT_NAME,
            fontSize=10, leading=16, textColor=muted, alignment=TA_CENTER,
            spaceAfter=4 * mm,
        )
        heading_style = ParagraphStyle(
            "SectionHeading", parent=styles["Heading2"], fontName=cls.FONT_NAME,
            fontSize=13, leading=18, textColor=navy, spaceBefore=3 * mm,
            spaceAfter=2 * mm, borderColor=blue, borderWidth=0,
            borderPadding=(0, 0, 2 * mm, 0),
        )
        body_style = ParagraphStyle(
            "BodyCN", parent=styles["BodyText"], fontName=cls.FONT_NAME,
            fontSize=9.5, leading=16, textColor=navy, alignment=TA_LEFT,
        )
        small_style = ParagraphStyle(
            "SmallCN", parent=body_style, fontSize=8.5, leading=14, textColor=muted,
        )
        callout_style = ParagraphStyle(
            "CalloutCN", parent=body_style, fontSize=10, leading=17,
            leftIndent=3 * mm, rightIndent=3 * mm,
        )
        brand_style = ParagraphStyle(
            "Brand", parent=subtitle_style, fontName="Helvetica",
            fontSize=10, leading=13, textColor=muted,
        )
        table_header_style = ParagraphStyle(
            "TableHeader", parent=body_style, fontSize=9,
            leading=12, textColor=colors.white,
        )

        def para(value, style=body_style):
            return Paragraph(escape(str(value or "-")), style)

        def page_footer(canvas, doc):
            canvas.saveState()
            canvas.setStrokeColor(border)
            canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(muted)
            canvas.drawString(18 * mm, 8.5 * mm, "CodeMind Studio")
            canvas.setFont(cls.FONT_NAME, 8)
            canvas.drawString(48 * mm, 8.5 * mm, "能力诊断报告")
            canvas.drawRightString(A4[0] - 18 * mm, 8.5 * mm, f"第 {doc.page} 页")
            canvas.restoreState()

        story = [
            Paragraph("CodeMind Studio", brand_style),
            Paragraph("编程能力诊断报告", title_style),
            Paragraph("五维能力评估 · 薄弱项诊断 · 个性化学习建议", subtitle_style),
        ]

        user_label = username or f"用户 {matrix.get('user_id', '-')}"
        overview = Table(
            [
                [para("报告对象", small_style), para(user_label), para("当前等级", small_style), para(matrix.get("level", "初学者"))],
                [para("累计评估", small_style), para(f"{matrix.get('total_submissions', 0)} 次"), para("综合得分", small_style), para(f"{float(average_score or 0):.1f} / 100")],
                [para("最近评估", small_style), para(matrix.get("updated_at") or "暂无"), para("生成时间", small_style), para(generated_at.strftime("%Y-%m-%d %H:%M"))],
            ],
            colWidths=[25 * mm, 57 * mm, 25 * mm, 57 * mm],
        )
        overview.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), light),
            ("BACKGROUND", (0, 0), (0, -1), pale_blue),
            ("BACKGROUND", (2, 0), (2, -1), pale_blue),
            ("BOX", (0, 0), (-1, -1), 0.6, border),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, border),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([overview, Paragraph("一、五维能力概览", heading_style)])

        score_rows = [[para("能力维度", table_header_style), para("得分", table_header_style), para("水平", table_header_style), para("能力进度", table_header_style)]]
        for (key, label), score in zip(cls.DIMENSIONS, scores):
            filled = max(0, min(10, int(round(score / 10))))
            progress = "■" * filled + "□" * (10 - filled)
            score_rows.append([para(label), para(f"{score:.0f}"), para(cls._score_level(score)), para(progress)])
        score_table = Table(score_rows, colWidths=[37 * mm, 24 * mm, 32 * mm, 71 * mm], repeatRows=1)
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
            ("ALIGN", (1, 1), (2, -1), "CENTER"),
            ("TEXTCOLOR", (3, 1), (3, -1), blue),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light]),
            ("BOX", (0, 0), (-1, -1), 0.6, border),
            ("INNERGRID", (0, 0), (-1, -1), 0.35, border),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([score_table, Paragraph("二、薄弱维度诊断", heading_style)])

        if weak_dimensions:
            weak_rows = [[para("优先级", table_header_style), para("薄弱维度", table_header_style), para("当前分数", table_header_style), para("改进建议", table_header_style)]]
            for index, item in enumerate(weak_dimensions[:3], 1):
                label = item.get("label") or item.get("dimension") or "未命名维度"
                weak_rows.append([
                    para(index), para(label), para(item.get("score", 0)),
                    para(item.get("suggestion") or "建议结合专项练习逐步提升。", small_style),
                ])
            weak_table = Table(weak_rows, colWidths=[20 * mm, 34 * mm, 25 * mm, 85 * mm], repeatRows=1)
            weak_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7F1D1D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("TEXTCOLOR", (2, 1), (2, -1), red),
                ("ALIGN", (0, 1), (2, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), cls.FONT_NAME),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FEF2F2")]),
                ("BOX", (0, 0), (-1, -1), 0.6, border),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, border),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(weak_table)
        else:
            story.append(para("暂无薄弱维度数据。完成更多代码评估后，系统将提供更准确的诊断。", callout_style))

        story.append(Paragraph("三、个性化学习建议", heading_style))
        if recommendations:
            for index, item in enumerate(recommendations[:3], 1):
                title = f"{index}. {item.get('label') or item.get('dimension') or '能力提升'}（当前 {item.get('current_score', 0)} 分）"
                tasks = item.get("recommended_tasks") or []
                task_text = "、".join(str(task) for task in tasks[:5]) if tasks else "建议选择该维度的入门与进阶题目交替练习。"
                block = Table(
                    [[para(title), para(item.get("suggestion") or "制定专项练习计划。", small_style)],
                     [para("推荐练习", small_style), para(task_text, small_style)]],
                    colWidths=[37 * mm, 127 * mm],
                )
                block.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (0, -1), pale_blue),
                    ("BOX", (0, 0), (-1, -1), 0.5, border),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, border),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]))
                story.extend([KeepTogether(block), Spacer(1, 1.5 * mm)])
        else:
            story.append(para("暂无个性化建议。提交一段代码完成评估后即可生成学习路径。", callout_style))

        story.extend([
            Spacer(1, 2 * mm),
            Table([[para("说明", small_style), para("本报告根据平台内的代码评估记录自动生成，仅用于学习诊断。建议结合持续练习和项目实践观察能力变化。", small_style)]], colWidths=[20 * mm, 144 * mm], style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), light),
                ("BOX", (0, 0), (-1, -1), 0.5, border),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])),
        ])

        document.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
        buffer.seek(0)
        return buffer
