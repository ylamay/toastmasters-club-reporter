from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.units import cm
from datetime import datetime
import logging

class PDFBuilder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_club_report(self, club) -> list:
        """
        Generate an PDF report for a Toastmasters club.

        Args:
            club: Club object with statistics, distribution, and members

        Returns:
            list: List of elements to be included in the PDF report
        """    
        # Define clean styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CleanTitle', 
            parent=styles['Title'],
            fontSize=24, 
            spaceAfter=40, 
            alignment=1,
            textColor=colors.HexColor('#1B365D'),
            fontName='Helvetica-Bold'
        )
        
        section_style = ParagraphStyle(
            'SectionHeader', 
            parent=styles['Heading1'],
            fontSize=16, 
            spaceAfter=20,
            spaceBefore=30,
            textColor=colors.HexColor('#2E86AB'),
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=10
        )
        
        subsection_style = ParagraphStyle(
            'SubSection',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=15,
            spaceBefore=15,
            textColor=colors.HexColor('#5A6C7D'),
            fontName='Helvetica-Bold'
        )

        story = []
        
        # Page 1: Header + Executive Summary + Distributions
        self._add_clean_header(story, club, title_style)
        self._add_executive_summary_card(story, club)
        self._add_distribution_charts(story, club, section_style)
        
        # Page Break
        story.append(PageBreak())
        
        # Page 2: Member Progress
        self._add_member_progress_clean(story, club, section_style, subsection_style)
        
        # Page 3: Action Items (if needed)
        story.append(PageBreak())
        self._add_action_items_clean(story, club, section_style)
        
        # Footer
        self._add_clean_footer(story)
        
        return story

    def _add_clean_header(self, story, club, title_style):
        """Add clean header with plenty of white space"""
        # Title with more space
        title = Paragraph(f"{club.club_name}", title_style)
        story.append(title)
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            fontSize=14,
            alignment=1,
            textColor=colors.HexColor('#5A6C7D'),
            spaceAfter=50
        )
        subtitle = Paragraph("Club Progress Report", subtitle_style)
        story.append(subtitle)
        
        # Generation date
        date_style = ParagraphStyle(
            'DateStyle',
            fontSize=10,
            alignment=1,
            textColor=colors.grey,
            spaceAfter=40
        )
        date_text = Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", date_style)
        story.append(date_text)

    def _add_executive_summary_card(self, story, club):
        """Add executive summary as a clean card"""
        stats = club.statistics
        total_pathways = sum(club.distribution.pathway_distribution.values())
        
        # Add safety check for division by zero
        avg_pathways = f"{total_pathways/stats.total_members:.1f}" if stats.total_members > 0 else "0.0"
        
        # Create clean summary data with better spacing
        summary_data = [
            ['CLUB METRICS', ''],
            ['Total Members', str(stats.total_members)],
            ['Active Members', str(stats.active_members)],
            ['Active Pathways', str(total_pathways)],
            ['Completed Pathways', str(stats.completed_pathways_total)],
            ['Avg Pathways per Member', avg_pathways]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('SPAN', (0, 0), (1, 0)),  # Merge header cells
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Left column bold
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),       # Right column normal
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            
            # Spacing and borders
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E1E8ED')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2E86AB'))
        ]))
        
        # Center the summary card
        centered_table = Table([[summary_table]], colWidths=[7*inch])
        centered_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(centered_table)
        story.append(Spacer(1, 40))

    def _add_distribution_charts(self, story, club, section_style):
        """Add pathway and level distribution as clean charts"""
        story.append(Paragraph("📊 Pathway & Level Distribution", section_style))
        
        # Create pathway pie chart
        pathway_chart = self._create_pathway_pie_chart(club)
        
        # Create level bar chart
        level_chart = self._create_level_bar_chart(club)
        
        # Side by side layout with charts
        charts_table = Table(
            [[pathway_chart, Spacer(0.5*inch, 1), level_chart]],
            colWidths=[3.5*inch, 0.5*inch, 3.5*inch]
        )
        charts_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        
        story.append(charts_table)
        story.append(Spacer(1, 30))

    def _create_pathway_pie_chart(self, club):
        """Create pie chart for pathway distribution"""        
        # Prepare data
        pathway_data = []
        pathway_labels = []
        colors_list = [
            colors.HexColor('#2E86AB'), colors.HexColor('#A23B72'), colors.HexColor('#F18F01'),
            colors.HexColor('#F5793A'), colors.HexColor('#85C1E9'), colors.HexColor('#A569BD'),
            colors.HexColor('#58D68D'), colors.HexColor('#F7DC6F'), colors.HexColor('#EC7063')
        ]
        
        total_pathways = sum(club.distribution.pathway_distribution.values())
        
        for i, (pathway, count) in enumerate(sorted(club.distribution.pathway_distribution.items(), 
                                                key=lambda x: x[1], reverse=True)):
            pathway_data.append(count)
            # Truncate long pathway names for legend
            display_name = pathway[:20] + "..." if len(pathway) > 20 else pathway
            percentage = (count / total_pathways * 100) if total_pathways > 0 else 0
            pathway_labels.append(f"{display_name} ({percentage:.1f}%)")
        
        # Create drawing
        drawing = Drawing(width=3.5*inch, height=3*inch)
        
        # Create pie chart
        pie = Pie()
        pie.x = 0.5*inch
        pie.y = 0.5*inch
        pie.width = 2.5*inch
        pie.height = 2.5*inch
        pie.data = pathway_data
        pie.labels = [f"{d}" for d in pathway_data]  # Show counts on slices
        pie.slices.strokeWidth = 0.5
        pie.slices.strokeColor = colors.white
        
        # Apply colors
        for i, color in enumerate(colors_list[:len(pathway_data)]):
            pie.slices[i].fillColor = color
            pie.slices[i].labelRadius = 1.1
            pie.slices[i].fontName = 'Helvetica-Bold'
            pie.slices[i].fontSize = 9
            pie.slices[i].fontColor = colors.black
        
        drawing.add(pie)
        
        # Add title
        title = String(1.75*inch, 2.8*inch, 'Pathway Distribution', 
                    fontName='Helvetica-Bold', fontSize=12, 
                    textAnchor='middle', fillColor=colors.HexColor('#2E86AB'))
        drawing.add(title)
        
        # Create legend table
        legend_data = []
        for i, label in enumerate(pathway_labels):
            color_cell = Table([['']], colWidths=[0.2*inch], rowHeights=[0.15*inch])
            color_cell.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors_list[i % len(colors_list)]),
                ('GRID', (0, 0), (0, 0), 1, colors.black)
            ]))
            legend_data.append([color_cell, label])
        
        legend_table = Table(legend_data, colWidths=[0.3*inch, 2.8*inch])
        legend_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
        ]))
        
        # Combine chart and legend
        combined_table = Table([[drawing], [legend_table]], colWidths=[3.5*inch])
        combined_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        return combined_table

    def _create_level_bar_chart(self, club):
        """Create bar chart for level distribution"""        
        # Prepare data
        level_data = []
        level_labels = []
        self.logger.info("1")
        # Handle the level distribution properly - keys are strings like "1", "3", "5"
        try:
            # Convert string keys to integers for proper sorting
            level_items = []
            for level_str, count in club.distribution.level_distribution.items():
                try:
                    level_num = int(level_str)
                    level_items.append((level_num, count))
                except (ValueError, TypeError):
                    # Handle non-numeric levels
                    level_items.append((level_str, count))
            
            # Sort by level number
            sorted_levels = sorted(level_items, key=lambda x: x[0] if isinstance(x[0], int) else 999)
            
        except Exception as e:
            self.logger.warning(f"Error sorting levels: {e}")
            # Fallback to original items
            sorted_levels = list(club.distribution.level_distribution.items())
        self.logger.info("2")
        # Build data for chart
        for level, count in sorted_levels:
            level_data.append(count)
            level_labels.append(f"L{level}")  # Display as L1, L3, L5, etc.
        self.logger.info("3")
        # Handle empty data case
        if not level_data:
            # Create empty chart message
            drawing = Drawing(width=3.5*inch, height=3*inch)
            no_data_msg = String(1.75*inch, 1.5*inch, 'No level data available', 
                            fontName='Helvetica', fontSize=12, 
                            textAnchor='middle', fillColor=colors.grey)
            drawing.add(no_data_msg)
            
            # Return simple table with message
            return Table([[drawing]], colWidths=[3.5*inch])
        self.logger.info("4")
        # Create drawing
        drawing = Drawing(width=3.5*inch, height=3*inch)
        self.logger.info("5")
        # Create bar chart
        bc = VerticalBarChart()
        bc.x = 0.5*inch
        bc.y = 0.5*inch
        bc.height = 2*inch
        bc.width = 2.5*inch
        bc.data = [level_data]  # Single series
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(level_data) * 1.1
        bc.valueAxis.valueStep = max(1, max(level_data) // 5)
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 0
        bc.categoryAxis.categoryNames = level_labels
        self.logger.info("6")
        # Style the bars with safety check
        try:
            for i in range(len(level_data)):
                bc.bars[(0, i)].fillColor = colors.HexColor('#F18F01')
                bc.bars[(0, i)].strokeColor = colors.HexColor('#E67E22')
                bc.bars[(0, i)].strokeWidth = 1
        except (IndexError, KeyError, AttributeError) as e:
            # If bar styling fails, just continue without styling
            self.logger.warning(f"Could not style bars: {e}")
            pass
        self.logger.info("7")
        drawing.add(bc)
        self.logger.info("8")
        # Add title
        title = String(1.75*inch, 2.8*inch, 'Level Distribution', 
                    fontName='Helvetica-Bold', fontSize=12, 
                    textAnchor='middle', fillColor=colors.HexColor('#F18F01'))
        drawing.add(title)
        self.logger.info("9")
        # Add value labels on top of bars
        bar_width = bc.width / len(level_data)
        for i, value in enumerate(level_data):
            x_pos = bc.x + (i + 0.5) * bar_width
            y_pos = bc.y + (value / bc.valueAxis.valueMax) * bc.height + 0.1*inch
            value_label = String(x_pos, y_pos, str(value), 
                            fontName='Helvetica-Bold', fontSize=10, 
                            textAnchor='middle', fillColor=colors.black)
            drawing.add(value_label)
        self.logger.info("10")
        # Create summary table below chart
        total_levels = sum(club.distribution.level_distribution.values())
        summary_data = [['Level', 'Count', 'Percentage']]
        self.logger.info("10")
        for level, count in sorted_levels:
            percentage = f"{(count/total_levels)*100:.1f}%" if total_levels > 0 else "0%"
            summary_data.append([f"Level {level}", str(count), percentage])
        self.logger.info("11")
        summary_table = Table(summary_data, colWidths=[1*inch, 0.8*inch, 0.9*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F18F01')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E1E8ED')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF8E1')])
        ]))
        self.logger.info("12")
        # Combine chart and summary
        combined_table = Table([[drawing], [summary_table]], colWidths=[3.5*inch])
        combined_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (0, 1), 10)
        ]))
        
        return combined_table    

    def _add_member_progress_clean(self, story, club, section_style, subsection_style):
        """Add clean member progress section"""
        story.append(Paragraph("👥 Member Progress Details", section_style))
        
        # Create clean member data - one row per member-pathway combination
        member_data = [['MEMBER', 'PATHWAY', 'LEVEL', 'PROGRESS', 'NEXT PROJECT']]
        
        # Collect and sort member-pathway data
        member_pathway_data = []
        for member in club.members.values():
            if not member.current_pathways:
                continue
                
            for pathway in member.current_pathways:
                # Find next project for this pathway
                next_project = "No project assigned"
                if hasattr(member, 'next_projects') and member.next_projects:
                    for project in member.next_projects:
                        if hasattr(project, 'pathway_name') and project.pathway_name == pathway.name:
                            next_project = project.name
                            # Truncate long project names
                            if len(next_project) > 35:
                                next_project = next_project[:32] + "..."
                            break
                
                member_pathway_data.append({
                    'member_name': f"{member.first_name} {member.last_name}",
                    'pathway_name': pathway.name[:20] + "..." if len(pathway.name) > 20 else pathway.name,
                    'level': pathway.current_level,
                    'progress': pathway.completion_percentage,
                    'next_project': next_project,
                    'sort_key': f"{member.last_name}_{pathway.name}"
                })
        
        # Sort by member name, then by progress
        member_pathway_data.sort(key=lambda x: (x['sort_key'], -x['progress']))
        
        # Add to table data
        for data in member_pathway_data:
            member_data.append([
                data['member_name'],
                data['pathway_name'],
                f"Level {data['level']}",
                f"{data['progress']:.1f}%",
                data['next_project']
            ])
        
        # Create table with better spacing
        member_table = Table(member_data, colWidths=[1.8*inch, 1.8*inch, 0.8*inch, 0.8*inch, 2.3*inch])
        member_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),      # Member & Pathway left-aligned
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),   # Level, Progress, Project centered
            
            # Spacing and borders
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E1E8ED')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        
        story.append(member_table)

    def _add_action_items_clean(self, story, club, section_style):
        """Add clean action items section"""
        story.append(Paragraph("🎯 Priority Action Items", section_style))
        
        # Analyze for priority actions
        priority_actions = []
        regular_actions = []
        
        for member in club.members.values():
            if not member.next_projects:
                continue
            for project in member.next_projects:
                member_name = f"{member.first_name} {member.last_name}"
                if "elective" in project.name.lower() and "choose" in project.name.lower():
                    priority_actions.append([
                        "HIGH PRIORITY",
                        member_name,
                        "Elective Choice Required",
                        f"Help choose elective for {project.pathway_name}"
                    ])
                elif "ice breaker" in project.name.lower():
                    regular_actions.append([
                        "NORMAL",
                        member_name,
                        "First Speech Opportunity",
                        f"Schedule Ice Breaker speech"
                    ])
        
        # Combine actions
        all_actions = priority_actions + regular_actions[:5]  # Limit total actions
        
        if all_actions:
            # Add header
            action_data = [['PRIORITY', 'MEMBER', 'ACTION TYPE', 'DESCRIPTION']] + all_actions
            
            action_table = Table(action_data, colWidths=[1.2*inch, 1.8*inch, 1.8*inch, 2.7*inch])
            action_table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C44569')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                
                # Spacing and borders
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E1E8ED')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF3CD')])
            ]))
            
            story.append(action_table)
        else:
            # No actions message
            no_actions = Paragraph(
                "✅ No immediate action items required. All members are progressing well!",
                ParagraphStyle('NoActions', fontSize=12, textColor=colors.HexColor('#28A745'))
            )
            story.append(no_actions)

    def _add_clean_footer(self, story):
        """Add clean footer"""
        story.append(Spacer(1, 50))
        
        footer_style = ParagraphStyle(
            'CleanFooter', 
            fontSize=9, 
            alignment=1, 
            textColor=colors.HexColor('#6C757D')
        )
        footer_text = Paragraph(
            f"Generated by Toastmasters Club Analytics | {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            footer_style
        )
        story.append(HRFlowable(width="60%", thickness=0.5, color=colors.HexColor('#E1E8ED')))
        story.append(Spacer(1, 10))
        story.append(footer_text)