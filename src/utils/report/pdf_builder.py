from reportlab.lib import colors # type: ignore
from reportlab.lib.pagesizes import letter, inch # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable # type: ignore
from reportlab.graphics.shapes import Drawing, String, Rect # type: ignore
from reportlab.graphics.charts.piecharts import Pie # type: ignore
from reportlab.graphics.charts.barcharts import VerticalBarChart # type: ignore
from datetime import datetime
import logging

class PDFBuilder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_club_report(self, club) -> list:
        """
        Generate a modern single-page PDF report for a Toastmasters club.

        Args:
            club: Club object with statistics, distribution, and members

        Returns:
            list: List of elements to be included in the PDF report
        """    
        # Modern color palette
        self.colors = {
            'primary': colors.HexColor('#2563EB'),      # Modern blue
            'secondary': colors.HexColor('#7C3AED'),    # Modern purple  
            'accent': colors.HexColor('#059669'),       # Modern green
            'warning': colors.HexColor('#DC2626'),      # Modern red
            'surface': colors.HexColor('#F8FAFC'),      # Light gray
            'text': colors.HexColor('#1E293B'),         # Dark gray
            'muted': colors.HexColor('#64748B')         # Medium gray
        }
        
        story = []
        
        # Single page layout
        self._add_modern_header(story, club)
        self._add_dashboard_layout(story, club)
        self._add_compact_footer(story)
        
        return story

    def _add_modern_header(self, story, club):
        """Add modern compact header"""
        # Title row with club name and date
        header_data = [[
            f"{club.club_name}",
            f"Progress Report • {datetime.now().strftime('%B %Y')}"
        ]]
        
        header_table = Table(header_data, colWidths=[4.5*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 20),
            ('TEXTCOLOR', (0, 0), (0, 0), self.colors['primary']),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, 0), 12),
            ('TEXTCOLOR', (1, 0), (1, 0), self.colors['muted']),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15)
        ]))
        
        story.append(header_table)

    def _add_dashboard_layout(self, story, club):
        """Add modern dashboard-style layout"""
        # Top row: Metrics + Charts
        metrics_section = self._create_metrics_cards(club)
        charts_section = self._create_compact_charts(club)
        
        top_layout = Table([[metrics_section, charts_section]], 
                          colWidths=[3.7*inch, 4*inch])
        top_layout.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10)
        ]))
        
        story.append(top_layout)
        story.append(Spacer(1, 20))
        
        # Bottom row: Member Progress Table
        story.append(self._create_compact_member_table(club))

    def _create_metrics_cards(self, club):
        """Create modern metric cards"""
        stats = club.statistics
        total_pathways = sum(club.distribution.pathway_distribution.values())
        avg_pathways = f"{total_pathways/stats.total_members:.1f}" if stats.total_members > 0 else "0.0"
        
        # Create 2x2 grid of metric cards
        card_data = [
            [f"{stats.total_members}", f"{stats.active_members}"],
            ["Total Members", "Active Members"],
            [f"{total_pathways}", f"{avg_pathways}"],
            ["Active Pathways", "Avg per Member"]
        ]
        
        metrics_table = Table(card_data, colWidths=[1.7*inch, 1.7*inch], 
                             rowHeights=[0.6*inch, 0.3*inch, 0.6*inch, 0.3*inch])
        
        metrics_table.setStyle(TableStyle([
            # Big numbers styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 24),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['primary']),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 24),
            ('TEXTCOLOR', (0, 2), (-1, 2), self.colors['secondary']),
            ('ALIGN', (0, 0), (-1, 2), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 2), 'MIDDLE'),
            
            # Labels styling
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('TEXTCOLOR', (0, 1), (-1, 1), self.colors['muted']),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica'),
            ('FONTSIZE', (0, 3), (-1, 3), 10),
            ('TEXTCOLOR', (0, 3), (-1, 3), self.colors['muted']),
            ('ALIGN', (0, 1), (-1, 3), 'CENTER'),
            ('VALIGN', (0, 1), (-1, 3), 'MIDDLE'),
            
            # Card styling
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['surface']),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
        ]))
        
        return metrics_table

    def _create_mini_pie_chart(self, club):
        """Create compact pie chart with better text handling"""
        pathway_data = []
        pathway_labels = []
        modern_colors = [
            self.colors['primary'], self.colors['secondary'], self.colors['accent'],
            colors.HexColor('#F59E0B'), colors.HexColor('#EF4444'), colors.HexColor('#8B5CF6')
        ]
        
        total_pathways = sum(club.distribution.pathway_distribution.values())
        
        # Take top 4 pathways only (less crowding)
        top_pathways = sorted(club.distribution.pathway_distribution.items(), 
                            key=lambda x: x[1], reverse=True)[:4]
        
        for i, (pathway, count) in enumerate(top_pathways):
            pathway_data.append(count)
            # Shorter names for better fit
            short_name = pathway[:10] + "..." if len(pathway) > 10 else pathway
            percentage = (count / total_pathways * 100) if total_pathways > 0 else 0
            pathway_labels.append(f"{short_name}")  # Remove percentage from chart
        
        # Create larger drawing for better text fit
        drawing = Drawing(width=2.1*inch, height=2.5*inch)
        
        # Title
        title = String(1.05*inch, 2.3*inch, 'Top Pathways', 
                    fontName='Helvetica-Bold', fontSize=10, 
                    textAnchor='middle', fillColor=self.colors['text'])
        drawing.add(title)
        
        # Pie chart - make it smaller to leave room for legend
        pie = Pie()
        pie.x = 0.1*inch
        pie.y = 1.0*inch
        pie.width = 1.2*inch
        pie.height = 1.2*inch
        pie.data = pathway_data
        pie.labels = [str(d) for d in pathway_data]  # Just show counts
        pie.slices.strokeWidth = 1
        pie.slices.strokeColor = colors.white
        
        for i, color in enumerate(modern_colors[:len(pathway_data)]):
            pie.slices[i].fillColor = color
            pie.slices[i].labelRadius = 0.7
            pie.slices[i].fontName = 'Helvetica-Bold'
            pie.slices[i].fontSize = 9
            pie.slices[i].fontColor = colors.white
        
        drawing.add(pie)
        
        # Better legend with color boxes
        legend_start_y = 0.8*inch
        for i, (pathway, count) in enumerate(top_pathways):
            y_pos = legend_start_y - (i * 0.15*inch)
            
            # Color box
            color_box = Rect(1.4*inch, y_pos, 0.08*inch, 0.08*inch)
            color_box.fillColor = modern_colors[i]
            color_box.strokeColor = colors.white
            color_box.strokeWidth = 0.5
            drawing.add(color_box)
            
            # Label text - shorter
            short_pathway = pathway[:8] + "..." if len(pathway) > 8 else pathway
            percentage = (count / total_pathways * 100) if total_pathways > 0 else 0
            legend_text = String(1.52*inch, y_pos + 0.02*inch, 
                            f"{short_pathway} ({percentage:.0f}%)", 
                            fontName='Helvetica', fontSize=7, 
                            fillColor=self.colors['text'])
            drawing.add(legend_text)
        
        return drawing

    def _create_mini_bar_chart(self, club):
        """Create compact bar chart with better sizing"""
        level_data = []
        level_labels = []
        
        # Sort levels
        try:
            level_items = []
            for level_str, count in club.distribution.level_distribution.items():
                try:
                    level_num = int(level_str)
                    level_items.append((level_num, count))
                except (ValueError, TypeError):
                    level_items.append((level_str, count))
            
            sorted_levels = sorted(level_items, key=lambda x: x[0] if isinstance(x[0], int) else 999)
        except:
            sorted_levels = list(club.distribution.level_distribution.items())
        
        for level, count in sorted_levels:
            level_data.append(count)
            level_labels.append(f"L{level}")
        
        if not level_data:
            empty_drawing = Drawing(width=2.1*inch, height=2.5*inch)
            no_data_msg = String(1.05*inch, 1.25*inch, 'No level data', 
                            fontName='Helvetica', fontSize=10, 
                            textAnchor='middle', fillColor=self.colors['muted'])
            empty_drawing.add(no_data_msg)
            return empty_drawing
        
        # Create larger drawing
        drawing = Drawing(width=2.1*inch, height=2.5*inch)
        
        # Title
        title = String(1.05*inch, 2.3*inch, 'Level Progress', 
                    fontName='Helvetica-Bold', fontSize=10, 
                    textAnchor='middle', fillColor=self.colors['text'])
        drawing.add(title)
        
        # Bar chart - adjusted sizing
        bc = VerticalBarChart()
        bc.x = 0.3*inch
        bc.y = 0.6*inch
        bc.height = 1.5*inch
        bc.width = 1.5*inch
        bc.data = [level_data]
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(level_data) * 1.2
        bc.categoryAxis.categoryNames = level_labels
        bc.categoryAxis.labels.fontSize = 8
        bc.valueAxis.labels.fontSize = 7
        bc.categoryAxis.labels.dy = -5
        
        # Modern bar colors
        for i in range(len(level_data)):
            try:
                bc.bars[(0, i)].fillColor = self.colors['accent']
                bc.bars[(0, i)].strokeColor = colors.white
                bc.bars[(0, i)].strokeWidth = 1
            except:
                pass
        
        drawing.add(bc)
        
        # Add value labels on bars
        bar_width = bc.width / len(level_data) if level_data else 1
        for i, value in enumerate(level_data):
            x_pos = bc.x + (i + 0.5) * bar_width
            y_pos = bc.y + (value / bc.valueAxis.valueMax) * bc.height + 0.05*inch
            value_label = String(x_pos, y_pos, str(value), 
                            fontName='Helvetica-Bold', fontSize=8, 
                            textAnchor='middle', fillColor=self.colors['text'])
            drawing.add(value_label)
        
        return drawing

    def _create_compact_charts(self, club):
        """Create compact side-by-side charts with better spacing"""
        # Pathway pie chart (compact)
        pathway_chart = self._create_mini_pie_chart(club)
        
        # Level bar chart (compact)  
        level_chart = self._create_mini_bar_chart(club)
        
        # Combine charts horizontally with more space
        charts_layout = Table([[pathway_chart, level_chart]], 
                            colWidths=[2.1*inch, 2.1*inch])
        charts_layout.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        return charts_layout

    def _add_dashboard_layout(self, story, club):
        """Add modern dashboard-style layout with better proportions"""
        # Top row: Metrics + Charts
        metrics_section = self._create_metrics_cards(club)
        charts_section = self._create_compact_charts(club)
        
        # Adjust column widths for better fit
        top_layout = Table([[metrics_section, charts_section]], 
                        colWidths=[3.4*inch, 4.2*inch])
        top_layout.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5)
        ]))
        
        story.append(top_layout)
        story.append(Spacer(1, 15))
        
        # Bottom row: Member Progress Table
        story.append(self._create_compact_member_table(club))

    def _create_compact_member_table(self, club):
        """Create compact member progress table with better column sizing"""
        # Create section header
        section_header = Paragraph("👥 Member Progress", 
            ParagraphStyle('SectionHeader', fontSize=12, spaceAfter=8, 
                        textColor=self.colors['primary'], fontName='Helvetica-Bold'))
        
        # Collect member data (top 8 most active to fit better)
        member_data = [['MEMBER', 'PATHWAY', 'LEVEL', 'PROGRESS', 'NEXT PROJECT']]
        
        member_pathway_data = []
        for member in club.members.values():
            if not member.current_pathways:
                continue
                
            for pathway in member.current_pathways:
                next_project = "No project assigned"
                if hasattr(member, 'next_projects') and member.next_projects:
                    for project in member.next_projects:
                        if hasattr(project, 'pathway_name') and project.pathway_name == pathway.name:
                            next_project = project.name
                            break
                
                member_pathway_data.append({
                    'member_name': f"{member.first_name} {member.last_name}"[:30],  # Increased limit
                    'pathway_name': pathway.name,
                    'level': pathway.current_level,
                    'progress': pathway.completion_percentage,
                    'next_project': next_project
                })
        
        # Sort by progress (highest first) and take top 8
        member_pathway_data.sort(key=lambda x: -x['progress'])
        
        for data in member_pathway_data:  # Reduced to 8 rows
            member_data.append([
                data['member_name'],
                data['pathway_name'],
                f"L{data['level']}",
                f"{data['progress']:.0f}%",
                data['next_project']
            ])
        
        # Create compact table with better column widths
        member_table = Table(member_data, colWidths=[1.6*inch, 1.6*inch, 0.8*inch, 0.8*inch, 2.8*inch])
        member_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),  # Reduced header font size
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['text']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),  # Reduced data font size
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
            
            # Spacing - reduced padding
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            
            # Borders and alternating rows
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['surface']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['surface']])
        ]))
        
        # Combine header and table
        return Table([[section_header], [member_table]], colWidths=[7.1*inch])

    def _add_compact_footer(self, story):
        """Add minimal footer"""
        story.append(Spacer(1, 20))
        
        footer_text = Paragraph(
            f"Generated {datetime.now().strftime('%B %d, %Y')} • Toastmasters Analytics",
            ParagraphStyle('Footer', fontSize=8, alignment=1, 
                          textColor=self.colors['muted'])
        )
        story.append(footer_text)