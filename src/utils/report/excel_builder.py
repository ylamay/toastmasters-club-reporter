import pandas as pd
import logging

class ExcelBuilder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_club_report(self, club: dict) -> dict:
        """
        Generate an Excel report for a Toastmasters club.

        Args:
            club (dict): Club object with statistics, distribution, and members

    Returns:
        dict: Dictionary with single formatted DataFrame
    """
        # Create the report
        report_data = self._create_formatted_report(club)
        
        return {'Club Report': report_data}

    def _create_formatted_report(self, club):
        """Create a well-formatted single DataFrame report"""
        
        # Club Overview Section
        stats = club.statistics
        total_pathways = sum(club.distribution.pathway_distribution.values())
        avg_pathways = round(total_pathways / stats.total_members, 1) if stats.total_members > 0 else 0
        
        club_overview = pd.DataFrame({
            'Metric': ['Total Members', 'Active Members', 'Total Active Pathways', 
                    'Completed Pathways', 'Average Pathways per Member'],
            'Value': [stats.total_members, stats.active_members, total_pathways, 
                    stats.completed_pathways_total, avg_pathways]
        })
        
        # Add section headers and spacing
        sections = []
        
        # Add club overview with header
        header_df = pd.DataFrame({'Metric': ['CLUB OVERVIEW'], 'Value': ['']})
        sections.append(header_df)
        sections.append(club_overview)
        sections.append(pd.DataFrame({'Metric': [''], 'Value': ['']}))  # Spacer
        
        # Pathway Distribution
        pathway_header = pd.DataFrame({'Metric': ['PATHWAY DISTRIBUTION'], 'Value': ['']})
        pathway_data = []
        total_pathways = sum(club.distribution.pathway_distribution.values())
        
        for pathway, count in sorted(club.distribution.pathway_distribution.items(), 
                                key=lambda x: x[1], reverse=True):
            percentage = round((count / total_pathways * 100), 1) if total_pathways > 0 else 0
            pathway_data.append({'Metric': pathway, 'Value': f"{count} members ({percentage}%)"})
        
        pathway_df = pd.DataFrame(pathway_data)
        sections.append(pathway_header)
        sections.append(pathway_df)
        sections.append(pd.DataFrame({'Metric': [''], 'Value': ['']}))  # Spacer
        
        # Level Distribution
        level_header = pd.DataFrame({'Metric': ['LEVEL DISTRIBUTION'], 'Value': ['']})
        level_data = []
        total_levels = sum(club.distribution.level_distribution.values())
        
        for level, count in sorted(club.distribution.level_distribution.items()):
            percentage = round((count / total_levels * 100), 1) if total_levels > 0 else 0
            level_data.append({'Metric': level, 'Value': f"{count} pathways ({percentage}%)"})
        
        level_df = pd.DataFrame(level_data)
        sections.append(level_header)
        sections.append(level_df)
        sections.append(pd.DataFrame({'Metric': [''], 'Value': ['']}))  # Spacer
        
        # Member Details with expanded columns
        member_header = pd.DataFrame({
            'Metric': ['MEMBER PATHWAY DETAILS'],
            'Value': [''],
            'Pathway': [''],
            'Current Project': [''],
            'Duration': [''],
            'Level': [''],
            'Progress': ['']
        })
        
        # Create member data with all columns
        member_data = []
        for member in club.members.values():
            if not member.next_projects:
                continue
                
            for pathway in member.current_pathways:
                current_project = 'No project assigned'
                project_duration = 'Not specified'
                
                for project in member.next_projects:
                    if project.pathway_name == pathway.name:
                        current_project = project.name
                        project_duration = getattr(project, 'duration', 'Not specified')
                        break
                
                member_data.append({
                    'Metric': f"{member.first_name} {member.last_name}",
                    'Value': '',  # Empty for formatting
                    'Pathway': pathway.name,
                    'Current Project': current_project,
                    'Duration': project_duration,
                    'Level': f"Level {pathway.current_level}",
                    'Progress': pathway.completion_percentage / 100
                })
        
        # Sort by member name
        member_data.sort(key=lambda x: x['Metric'])
        member_df = pd.DataFrame(member_data)      
        
        # Add column headers for member section
        member_columns = pd.DataFrame({
            'Metric': ['Member Name'],
            'Value': [''],
            'Pathway': ['Pathway'],
            'Current Project': ['Current Project'],
            'Duration': ['Duration'],
            'Level': ['Level'],
            'Progress': ['Progress']
        })
        
        sections.append(member_header)
        sections.append(member_columns)
        sections.append(member_df)
        
        # Combine all sections
        final_report = pd.concat(sections, ignore_index=True)
        
        return final_report