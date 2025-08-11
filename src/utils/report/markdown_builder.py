from datetime import datetime
import logging

class MarkdownBuilder:
    def __init__(self):
        self.content = []
        self.logger = logging.getLogger(__name__)

    def generate_club_report(self, club) -> str:
        """
        Generate complete club report - main orchestration method
        
        Args:
            club: Club object with statistics, distribution, and members
            
        Returns:
            str: Complete markdown report content
        """
        timestamp = datetime.now().strftime("%B %d, %Y")
        
        # Build the complete report
        self.h1(f"{club.club_name} - Club Progress Summary")
        self.text(self.italic(f"Generated on {timestamp}"))
        self.hr()

        # Add all sections
        self._add_club_overview(club)
        self.hr()

        self._add_distribution(club)
        self.hr()
        
        self._add_member_progress(club)
        self.hr()
        
        self._add_next_actions(club)
        
        return self.build()
    
    #----------------------------
    # Helper Methods for Markdown Formatting
    #----------------------------
    def h1(self, text): 
        self.content.append(f"# {text}\n")
        return self
    
    def h2(self, text): 
        self.content.append(f"\n## {text}\n")
        return self
    
    def h3(self, text): 
        self.content.append(f"\n### {text}\n")
        return self
    
    def italic(self, text): 
        return f"*{text}*"
    
    def bold(self, text): 
        return f"**{text}**"
    
    def table(self, headers, rows):
        if not rows:
            return self
        lines = [f"| {' | '.join(headers)} |", f"| {' | '.join(['---'] * len(headers))} |"]
        for row in rows:
            lines.append(f"| {' | '.join(str(cell) for cell in row)} |")
        self.content.append("\n".join(lines) + "\n")
        return self
    
    def progress_bar(self, percentage): 
        return f"![{percentage}%](https://progress-bar.xyz/{int(percentage)})"
    
    def hr(self): 
        self.content.append("\n---\n")
        return self
    
    def text(self, text): 
        self.content.append(f"{text}\n")
        return self
    
    def build(self): 
        return "\n".join(self.content)
    
    #----------------------------
    # Methods to Add Sections
    #----------------------------
    def _add_club_overview(self, club: dict):
        """
        Add club overview section
        """
        stats = club.statistics
        total_pathways = sum(club.distribution.pathway_distribution.values())
        avg_pathways = round(total_pathways / stats.total_members, 1) if stats.total_members > 0 else 0
        
        self.h2(":scroll: Club Overview")
        overview_data = [
            ["**Total Members**", stats.total_members],
            ["**Active Members**", stats.active_members], 
            ["**Total Active Pathways**", total_pathways],
            ["**Completed Pathways**", stats.completed_pathways_total],
            ["**Average Pathways per Member**", avg_pathways]
        ]
        self.table(["Metric", "Value"], overview_data)

    def _add_distribution(self, club: dict):
        """
        Add distribution section with pathway and level distributions
        """
        self.h2(":bar_chart: Distribution")

        self._add_pathway_distribution(club)
        
        self._add_level_distribution(club)             

    def _add_pathway_distribution(self, club: dict):
        """
        Add pathway distribution with progress bars
        """
        self.text("<details>")
        self.text("<summary>Open to view Pathway Distribution</summary>")
        
        total_pathways = sum(club.distribution.pathway_distribution.values())
        
        for pathway, count in sorted(club.distribution.pathway_distribution.items(), 
                                   key=lambda x: x[1], reverse=True):
            percentage = round((count / total_pathways * 100), 1) if total_pathways > 0 else 0
            progress_bar = self.progress_bar(percentage)
            self.text(f"**{pathway}**: {count} members")
            self.text(progress_bar)

        self.text("</details>")

    def _add_level_distribution(self, club: dict):
        """
        Add level distribution with progress bars
        """
        self.text("<details>")
        self.text("<summary>Open to view Level Distribution</summary>")

        total_members = sum(club.distribution.level_distribution.values())
        
        # Sort by level number
        sorted_levels = sorted(club.distribution.level_distribution.items(), 
                             key=lambda x: x[0])
        
        for level, count in sorted_levels:
            percentage = round((count / total_members * 100), 1) if total_members > 0 else 0
            progress_bar = self.progress_bar(percentage)
            self.text(f"**Level {level}**: {count} pathways")
            self.text(progress_bar)

        self.text("</details>")

    def _add_member_progress(self, club: dict):
        """
        Add member progress section
        """
        self.h2(":busts_in_silhouette: Member Progress")
        self.text("<details>")
        self.text("<summary>Open to view Member Progress</summary>")        

        # Group members by highest level
        advanced_members = []  # Level 3+
        beginning_members = []  # Level 1-2
        
        for member in club.members.values():
            if not member.current_pathways:
                continue
                
            highest_level = max(pathway.current_level for pathway in member.current_pathways)
            member_data = {
                'member': member,
                'highest_level': highest_level,
                'pathway_count': len(member.current_pathways)
            }
            
            if highest_level >= 3:
                advanced_members.append(member_data)
            else:
                beginning_members.append(member_data)
        
        # Advanced Members (with multiple pathway details)
        if advanced_members:
            self.h3(":star2: Advanced Members (Level 3+)")
            for member_data in sorted(advanced_members, 
                                    key=lambda x: max(p.completion_percentage for p in x['member'].current_pathways), 
                                    reverse=True):
                self._add_advanced_member(member_data)
        
        # Beginning Members (simple table)
        if beginning_members:
            self.h3(":rocket: Beginning Members (Level 1-2)")
            member_rows = []
            for member_data in sorted(beginning_members, 
                                    key=lambda x: max(p.completion_percentage for p in x['member'].current_pathways), 
                                    reverse=True):
                member = member_data['member']
                primary_pathway = max(member.current_pathways, key=lambda p: p.completion_percentage)
                next_project = member.next_projects[0].name if member.next_projects else "No project assigned"
                progress_bar = self.progress_bar(primary_pathway.completion_percentage)
                
                member_rows.append([
                    self.bold(f"{member.first_name} {member.last_name}"),
                    primary_pathway.name,
                    f"{progress_bar}",
                    next_project
                ])
            
            self.table(["Member", "Primary Pathway", "Progress", "Next Project"], member_rows)

        self.text("</details>")

    def _add_advanced_member(self, member_data: dict):
        """
        Add detailed view for advanced member
        """
        member = member_data['member']
        highest_progress = max(p.completion_percentage for p in member.current_pathways)
        
        # Collapsible section
        summary_text = f"<summary><strong>{member.first_name} {member.last_name}</strong> - {member_data['pathway_count']} Active Pathway{'s' if member_data['pathway_count'] > 1 else ''}"
        if member_data['pathway_count'] > 1:
            summary_text += f" | {highest_progress}% Progress (Highest)"
        else:
            summary_text += f" | {highest_progress}% Progress"
        summary_text += "</summary>"
        
        self.text("<details>")
        self.text(summary_text)
        
        # Pathway table
        pathway_rows = []
        for pathway in sorted(member.current_pathways, key=lambda p: p.completion_percentage, reverse=True):
            next_project = "No project assigned"
            for project in member.next_projects:
                if project.pathway_name == pathway.name:
                    next_project = project.name
                    break
            
            progress_bar = self.progress_bar(pathway.completion_percentage)
            pathway_rows.append([
                self.bold(pathway.name),
                pathway.current_level,
                f"{progress_bar}",
                next_project
            ])
        
        self.table(["Pathway", "Level", "Progress", "Next Project"], pathway_rows)
        self.text("</details>")

    def _add_next_actions(self, club: dict):
        """
        Add actionable next steps
        """
        self.h2(":dart: Immediate Next Steps")
        self.text("<details>")
        self.text("<summary>Open to view Next Steps</summary>")        

        # Analyze member data for specific actions
        elective_choices = []
        first_speeches = []
        
        for member in club.members.values():
            if not member.next_projects:
                continue
                
            for project in member.next_projects:
                if "elective" in project.name.lower() and "choose" in project.name.lower():
                    elective_choices.append(f"**{member.first_name} {member.last_name}**: {project.name} ({project.pathway_name})")
                elif "ice breaker" in project.name.lower():
                    first_speeches.append(f"**{member.first_name} {member.last_name}**: {project.name} ({project.pathway_name})")
        
        # Priority Actions
        self.h3(":fire: Priority Actions Needed:")
        
        if first_speeches:
            self.text("\n**First Pathway Speech Opportunities:**")
            for speech in first_speeches:
                self.text(f"- {speech}")

        if elective_choices:
            self.text("**Elective Choices Required:**")
            for choice in elective_choices:
                self.text(f"- {choice}")
        
        # Club Goals
        self.h3(":trophy: Club Goals:")
        goals = []
        if first_speeches:
            goals.append(f":chart_with_upwards_trend: Get {len(first_speeches)} new member{'s' if len(first_speeches) > 1 else ''} started with Ice Breaker speeches")
        if elective_choices:
            goals.append(f":dart: Support {len(elective_choices)} member{'s' if len(elective_choices) > 1 else ''} with elective choices")            
        
        # Check for members close to completion
        near_completion = [m for m in club.members.values() 
                          if any(p.completion_percentage > 80 for p in m.current_pathways)]
        if near_completion:
            goals.append(":star2: Celebrate upcoming pathway completions")
        
        for goal in goals:
            self.text(f"- {goal}")

        self.text("</details>")