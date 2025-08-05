from model.member import Member
from model.club import Club
from service.pathway_analyzer_service import PathwayAnalyzerService
from manager.environment_manager import EnvironmentManager
import logging

class ToastmastersDataService:
    """
    Service for managing Toastmasters data

    Attributes:
        env_manager (EnvironmentManager): Environment manager for handling directories and paths
        pathway_analyzer_service (PathwayAnalyzerService): Service for analyzing pathway data
        logger (logging.Logger): Logger instance for logging messages
    """
    def __init__(self, env_manager: EnvironmentManager):
        self.env_manager = env_manager
        self.pathway_analyzer_service = None
        self.logger = logging.getLogger(__name__)

    def initialize_pathway_analyzer_service(self):
        """
        Initialize and load pathway data

        Returns:
            None
        """
        if self.env_manager.pathways_directory:
            self.pathway_analyzer_service = PathwayAnalyzerService(self.env_manager.pathways_directory)
            self.pathway_analyzer_service.load_pathway_data()
        else:
            self.logger.warning("Project root not provided, pathway enrichment unavailable")        

    def get_user_course_combinations(self, data_output: dict, endpoint_name: str = "progress"):
        """
        Extract unique username/course_id combinations from progress data

        Args:
            data_output (dict): Dictionary containing endpoint data
            endpoint_name (str): Name of the endpoint to extract combinations from

        Returns:
            list: List of unique (username, course_id) tuples
        """
        self.logger.info("Getting username/course_id combinations")
        progress_data = data_output.get(endpoint_name, [])

        combinations = []
        for group in progress_data:
            results = group.get('results', [])
            for result in results:
                user_name = result.get('user', {}).get('username')
                course_id = result.get('course_id')

                if user_name and course_id:
                    combinations.append((user_name, course_id))

        return list(set(combinations))

    def build_member_index(self, data_output: dict):
        """
        Build comprehensive member index from all data sources

        Args:
            data_output (dict): Dictionary containing data from all endpoints

        Returns:
            dict: Dictionary of Member objects indexed by username
        """
        # Initialize the pathway analyzer
        if self.pathway_analyzer_service is None:
            self.initialize_pathway_analyzer_service()

        members = {}

        # Step 1: Process overview data for basic member info
        for overview_page in data_output.get('overview', []):
            for result in overview_page.get('results', []):
                user = result['user']
                username = user['username']
                
                if username not in members:
                    members[username] = Member(
                        member_id=user['id'],
                        username=username,
                        first_name=user['first_name'],
                        last_name=user['last_name'],
                        email=user['email'],
                        completed_pathways=result.get('completed_paths', [])
                    )

        # Step 2: Process progress data for pathway progression
        for progress_page in data_output.get('progress', []):
            for result in progress_page.get('results', []):
                username = result['user']['username']
                if username in members:
                    members[username].add_pathway_progress(
                        pathway_name=result['path_name'],
                        course_id=result['course_id'],
                        progression=result['progression']
                    )

        # Step 3: Process detailed progress data for next projects
        for detail_entry in data_output.get('progress_detail', []):
            username = detail_entry['username']
            course_id = detail_entry['course_id']
            
            if username in members:
                members[username].add_detailed_progress(course_id, detail_entry['data'])

        # Step 4: Enrich projects with additional details from pathway files
        if self.pathway_analyzer_service:
            for member in members.values():
                for project in member.next_projects:
                    self.pathway_analyzer_service.enrich_project_with_details(project)

        # Step 5: Generate summaries for all members
        for member in members.values():
            member.generate_summary()

        self.logger.info(f"Built member index for {len(members)} members")
        return members
    
    def build_club_index(self, club_id: str, club_name: str, members: dict):
        """
        Build comprehensive club index from all member data

        Args:
            club_id (str): ID of the club
            club_name (str): Name of the club
            members (dict): Dictionary of Member objects indexed by username

        Returns:
            Club: Club object containing all members and their summaries
        """
        # Create a club instance
        club = Club(club_id, club_name, members)

        # Generate the club summary
        club.generate_summary()
        
        self.logger.info(f"Built club index for {len(members)} members")

        # Match member object parent layout
        return {
            club_id: club
        }