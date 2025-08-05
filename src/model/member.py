import logging

class Pathway:
    """
    Represents a Toastmasters pathway summary for a member (Replace current_pathways)
    """
    def __init__(
        self,
        name: str,
        course_id: str,
        current_level: int,
        completion_percentage: float,
        remaining_projects_in_level: int,
        remaining_projects_in_pathway: int,
        status: str
    ):
        self.name = name
        self.course_id = course_id
        self.current_level = current_level
        self.completion_percentage = completion_percentage
        self.remaining_projects_in_level = remaining_projects_in_level
        self.remaining_projects_in_pathway = remaining_projects_in_pathway
        self.status = status

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "course_id": self.course_id,
            "current_level": self.current_level,
            "completion_percentage": self.completion_percentage,
            "remaining_projects_in_level": self.remaining_projects_in_level,
            "remaining_projects_in_pathway": self.remaining_projects_in_pathway,
            "status": self.status
        }

class Project:
    """
    Represents a Toastmasters project within a pathway for a member (Replace next_projects)
    """
    def __init__(
        self,
        name: str,
        type: str,
        pathway_name: str,
        course_id: str,
        duration: str,
        level: int
    ):
        self.name = name
        self.type = type
        self.pathway_name = pathway_name
        self.course_id = course_id
        self.duration = duration
        self.level = level

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "pathway_name": self.pathway_name,
            "course_id": self.course_id,
            "duration": self.duration,
            "level": self.level
        }

class Summary:
    """
    Represents a summary for a member (Replace summary)
    """
    def __init__(
        self,
        total_pathways: int,
        active_pathways: int,
        completed_pathways: int,
        most_active_pathway: str = None
    ):
        self.total_pathways = total_pathways
        self.active_pathways = active_pathways
        self.completed_pathways = completed_pathways
        self.most_active_pathway = most_active_pathway

    def to_dict(self) -> dict:
        return {
            "total_pathways": self.total_pathways,
            "active_pathways": self.active_pathways,
            "completed_pathways": self.completed_pathways,
            "most_active_pathway": self.most_active_pathway
        }

class Member:
    """
    Represents a Toastmasters member.

    Attributes:
        member_id (int): Unique identifier for the member.
        username (str): Username of the member.
        first_name (str): First name of the member.
        last_name (str): Last name of the member.
        display_name (str): Full name of the member.
        email (str): Email address of the member.
        completed_pathways (list): List of completed pathways.
        next_projects (list): List of next projects for the member.
        current_pathways (list): List of current pathways with progress.
        summary (dict): Summary of member's progress and statistics.
        logger (logging.Logger): Logger for debugging and information.
    """
    def __init__(self, member_id: int, username: str, first_name: str, last_name: str, email: str, completed_pathways: list = None):
        self.member_id = member_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.display_name = f"{first_name} {last_name}"
        self.email = email
        self.completed_pathways = completed_pathways or []
        self.next_projects = []
        self.current_pathways = []
        self.summary = None
        self.logger = logging.getLogger(__name__)

    def add_pathway_progress(self, pathway_name: str, course_id: str, progression: dict):
        """
        Add pathway progress from progress data
        
        Args:
            pathway_name (str): Name of the pathway.
            course_id (str): Course ID associated with the pathway.
            progression (dict): Progression data containing levels and completion status.

        Returns:
            None
        """
        # Calculate current level and completion percentage
        current_level, remaining_projects_in_level = self._calculate_current_level(progression)
        completion_percentage, remaining_projects_in_pathway = self._calculate_completion_percentage(progression)
        
        pathway_info = Pathway(
            name=pathway_name,
            course_id=course_id,
            current_level=current_level,
            completion_percentage=completion_percentage,
            remaining_projects_in_level=remaining_projects_in_level,
            remaining_projects_in_pathway=remaining_projects_in_pathway,
            status="completed" if pathway_name in self.completed_pathways else "active"
        )
        
        self.current_pathways.append(pathway_info)

    def add_detailed_progress(self, course_id: str, detailed_data: dict):
        """
        Process detailed progress data to find next projects

        Args:
            course_id (str): Course ID associated with the pathway.
            detailed_data (dict): Detailed progress data containing blocks and chapters.

        Returns:
            None
        """
        blocks = detailed_data.get('blocks', {})
        if not blocks:
            return

        pathway_name = blocks.get('display_name', 'Unknown')
        next_projects = self._extract_next_projects(blocks, pathway_name, course_id)
        # Append the immediate project for the course
        if next_projects:
            self.next_projects.append(next_projects[0])

    def _calculate_current_level(self, progression: dict) -> int:
        """
        Calculate the current level based on progression

        Args:
            progression (dict): Progression data containing levels and completion status.

        Returns:
            tuple: Current level (int) and remaining projects in that level (int).
        """
        current_level = 1
        remaining_projects = 0

        # Iterate through levels to find the current level
        for level_name, level_data in progression.items():
            if level_name.startswith('Level'):
                level_num = self._extract_level_number(level_name)
                if level_data.get('approved', False) or level_data.get('completed', 0) == level_data.get('total', 0):
                    current_level = level_num + 1
                elif level_data.get('completed', 0) > 0:
                    current_level = level_num
                    remaining_projects = level_data.get('total', 0) - level_data.get('completed', 0)
                    break
        return min(current_level, 5), max(remaining_projects, 0)  # Max level: 5, Min projects: 0

    def _calculate_completion_percentage(self, progression: dict) -> float:
        """
        Calculate overall completion percentage

        Args:
            progression (dict): Progression data containing levels and completion status.

        Returns:
            tuple: Completion percentage (float) and remaining projects in the pathway (int).
        """
        total_projects = 0
        completed_projects = 0
        
        for level_name, level_data in progression.items():
            if level_name.startswith('Level'):
                total_projects += level_data.get('total', 0)
                completed_projects += level_data.get('completed', 0)
        
        completion_percentage = round((completed_projects / total_projects * 100), 1) if total_projects > 0 else 0.0
        remaining_projects = max((total_projects - completed_projects), 0)
        return completion_percentage, remaining_projects

    def _extract_next_projects(self, blocks: dict, pathway_name: str, course_id: str) -> list:
        """
        Extract next incomplete projects from detailed blocks data

        Args:
            blocks (dict): Detailed blocks data containing chapters and projects.
            pathway_name (str): Name of the pathway.
            course_id (str): Course ID associated with the pathway.

        Returns:
            list: List of next incomplete projects with details.
        """
        next_projects = []
        
        for chapter in blocks.get('children', []):
            if chapter.get('type') != 'chapter':
                continue
                
            level_name = chapter.get('display_name', '')
            level_num = self._extract_level_number(level_name)
            
            # Find incomplete projects in this level
            incomplete_projects = []
            elective_choices = []
            completed_electives = 0
            
            for child in chapter.get('children', []):
                if child.get('type') == 'sequential':
                    if not child.get('complete', False):
                        if child.get('block_lib_type') == 'elective':
                            elective_choices.append(child)
                        else:
                            project = Project(
                                name=child.get('display_name', 'Unknown Project').replace("(Legacy)", ""),
                                type="speech" if 'speech' in child.get('display_name', '').lower() else "project",
                                pathway_name=pathway_name,
                                course_id=course_id,
                                duration="Duration not specified",  # Fallback value
                                level=level_num                                
                            )
                            incomplete_projects.append(project)
                    if child.get('complete', False) and child.get('block_lib_type') == 'elective':
                        completed_electives += 1
            
            # Handle elective choices
            if elective_choices:
                min_req_electives = chapter.get('min_req_electives', 0)
                remaining_electives = min_req_electives - completed_electives
                if min_req_electives > 0:
                    project = Project(
                        name=f"Choose {remaining_electives} elective(s) from {level_name}",
                        type="elective",
                        pathway_name=pathway_name,
                        course_id=course_id,                    
                        duration="Varies by selection",
                        level=level_num
                    )
                    incomplete_projects.append(project)
            
            next_projects.extend(incomplete_projects)
            
            # If we found incomplete projects in this level, stop here (next projects are in current level)
            if incomplete_projects:
                break
                
        return next_projects

    def _extract_level_number(self, level_name: str) -> int:
        """
        Extract level number from level name

        Args:
            level_name (str): Name of the level, e.g., "Level 1", "Level 2".

        Returns:
            int: Extracted level number, or 0 if not found.
        """
        if 'Level' in level_name:
            try:
                return int(level_name.split('Level')[1].strip().split()[0])
            except Exception:
                pass
        return 0

    def generate_summary(self):
        """
        Generate member summary

        Returns:
            None
        """

        total_pathways = self._get_total_pathway_count() #len(self.current_pathways) + len(self.completed_pathways)
        active_pathways = len([p for p in self.current_pathways if p.status == 'active'])
        completed_pathways = len(self.completed_pathways)
        
        # Find most active pathway (highest completion percentage)
        most_active = max(self.current_pathways, key=lambda x: x.completion_percentage, default=None)
        most_active_pathway = most_active.name if most_active else 'None'

        summary = Summary(
            total_pathways=total_pathways,
            active_pathways=active_pathways,
            completed_pathways=completed_pathways,
            most_active_pathway=most_active_pathway
        )
        self.summary = summary

    def _get_total_pathway_count(self) -> int:
        """
        Determine total pathway count based on if the completed pathways are included

        Returns:
            int: Total number of pathways (current + completed).
        """
        actual_pathway_total = len(self.current_pathways)
        
        for completed_pathway in self.completed_pathways:
            if completed_pathway in [p.name for p in self.current_pathways]:
                continue
            actual_pathway_total += 1

        return actual_pathway_total

    def to_dict(self) -> dict:
        return {
            "member_id": self.member_id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "summary": self.summary.to_dict() if self.summary else None,
            "next_projects": [project.to_dict() for project in self.next_projects],
            "current_pathways": [pathway.to_dict() for pathway in self.current_pathways]
        }