import logging
import json
import os

class PathwayAnalyzerService:
    """
    Analyzes Toastmasters pathways and their associated projects.

    This class is responsible for loading pathway data from JSON files,
    extracting project details, and enriching project information with
    additional metadata from the pathways.

    Attributes:
        pathways_root_dir (str): The root directory where pathway files are stored.
        pathways_index (dict): Index of available pathways.
        pathways_data (dict): Dictionary containing loaded pathway data.
        logger (logging.Logger): Logger for logging messages and errors.
    """
    def __init__(self, pathways_root_dir: str = "pathways"):
        self.pathways_root_dir = pathways_root_dir
        self.pathways_index = {}
        self.pathways_data = {}
        self.logger = logging.getLogger(__name__)

    def load_pathway_data(self, index_file: str = "index.json"):
        """
        Load pathway data from the specified index file and individual pathway files
        
        Args:
            index_file (str): The name of the index file containing pathway metadata.

        Returns:
            None
        """
        try:
            # Load index json
            index_path = os.path.join(self.pathways_root_dir, index_file)
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                self.pathways_index = index_data.get('pathways_index', {})

            # Load individual pathway data
            available_pathways = self.pathways_index.get('available_pathways', [])
            for pathway in available_pathways:
                pathway_filename = pathway.get('filename')
                pathway_name = pathway.get('name')
                
                if pathway_filename and pathway_name:
                    pathway_filepath = os.path.join(self.pathways_root_dir, pathway_filename)
                    if os.path.exists(pathway_filepath):
                        with open(pathway_filepath, 'r', encoding='utf-8') as f:
                            pathway_data = json.load(f)
                            self.pathways_data[pathway_name] = pathway_data
                            self.logger.info(f"Loaded pathway data for: {pathway_name}")
                    else:
                        self.logger.warning(f"Pathway file not found: {pathway_filepath}")

            self.logger.info(f"Loaded {len(self.pathways_data)} pathway files")

        except Exception as e:
            self.logger.error(f"Error loading pathway data: {e}")

    def get_project_details(self, pathway_name: str, project_name: str, level: int):
        """
        Get project details from the pathway data

        Args:
            pathway_name (str): Name of the pathway
            project_name (str): Name of the project
            level (int): Level of the project

        Returns:
            A dict with project details or None if not found
        """
        pathway_data = self.pathways_data.get(pathway_name)
        level_key = f"Level {level}"
        level_data = pathway_data.get('levels', {}).get(level_key)

        if not pathway_data or not level_data:
            return
        
        # Normalize project names (some have spaces)
        def normalize_str (name: str): 
            return name.replace(" ", "").lower()
        
        norm_proj_name = normalize_str(project_name)
        # Search for project details
        for project in level_data.get('projects', []):
            if normalize_str(project['name']) == norm_proj_name:
                return {                    
                    'duration': project.get('duration', 'Duration not specified'),
                    'type': project.get('type')
                }
            # Check for elective options with assigned project
            if project.get('type') == "elective" and "elective" not in norm_proj_name:
                for elective in project.get('elective_options', []):
                    if normalize_str(elective.get('name', '')) == norm_proj_name:
                        return {
                            'duration': project.get('duration', 'Duration not specified')
                        }
        return
    
    def enrich_project_with_details(self, project: dict):
        """
        Enrich a project with additional details from the pathway data json files

        Args:
            project (dict): A object containing project details

        Returns:
            An enriched project dict with additional or modified details
        """
        pathway_name = project.pathway_name
        project_name = project.name
        level = project.level
        self.logger.info(f"Enriching project: {project_name} for pathway: {pathway_name}")

        # Get the additional details
        details = self.get_project_details(pathway_name, project_name, level)

        # Update project attributes if applicable
        if details:
            if details.get('duration') and details['duration'] != "":
                project.duration = details['duration']
            if details.get('type') and details['type'] != "":
                project.type = details['type']

        # return project