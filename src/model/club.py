import logging
from datetime import datetime
from collections import Counter

class Statistics:
    """
    Represents the statistics of a Toastmasters club.

    Attributes:
        total_members (int): Total number of members in the club.
        active_members (int): Number of active members in the club.
        completed_pathways_total (int): Total number of completed pathways across all members.
        summary_generated_at (str): Timestamp when the summary was generated.
    """
    def __init__(self, total_members: int, active_members: int, completed_pathways_total: int):
        self.total_members = total_members
        self.active_members = active_members
        self.completed_pathways_total = completed_pathways_total
        self.summary_generated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            'total_members': self.total_members,
            'active_members': self.active_members,
            'completed_pathways_total': self.completed_pathways_total,
            'summary_generated_at': self.summary_generated_at
        }

class Distribution:
    """
    Represents the distribution of pathways and levels in a Toastmasters club.

    Attributes:
        pathway_distribution (dict): Distribution of pathways across members.
        level_distribution (dict): Distribution of levels across pathways.
    """
    def __init__(self, pathway_distribution: dict, level_distribution: dict):
        self.pathway_distribution = pathway_distribution
        self.level_distribution = level_distribution

    def to_dict(self) -> dict:
        return {
            'pathway_distribution': self.pathway_distribution,
            'level_distribution': self.level_distribution
        }

class Club:
    """
    Represents a Toastmasters club.

    Attributes:
        club_id (str): Unique identifier for the club.
        club_name (str): The name of the club.
        members (dict): A dictionary of members, where keys are member IDs and values are Member objects.
        statistics (Statistics): Statistics object containing club statistics.
        distribution (Distribution): Distribution object containing pathway and level distributions.
        logger (logging.Logger): Logger for logging club activities.
    """
    def __init__(self, club_id: str, club_name: str, dashboard_club_id: str, members: dict = None):
        self.club_id = club_id
        self.club_name = club_name
        self.dashboard_club_id = dashboard_club_id
        self.members = members or {}
        self.statistics = None
        self.distribution = None
        self.logger = logging.getLogger(__name__)

    def generate_summary(self, member_enrollment_status: list):
        """
        Generate a summary of the club's activities and member progress.

        Args:
            member_enrollment_status (list): List of member enrollment statuses

        Returns:
            None
        """
        # General counts
        paid_members = [member for member in member_enrollment_status if member.get('is_paid', False)]
        total_members = len(paid_members)
        active_members = sum(
            1 for member in paid_members
            if member.get('is_enrolled', False)
        )

        # Pathway stats
        pathway_distribution = Counter()
        level_distribution = Counter()
        completed_pathways_total = 0
        
        for member in self.members.values():
            completed_pathways_total += member.summary.completed_pathways

            # Handle distribution counts (active)
            for pathway in member.current_pathways:
                if pathway.status == "active":
                    pathway_distribution[pathway.name] += 1

                    level_key = pathway.current_level
                    level_distribution[level_key] += 1

        # Create statistics object
        self.statistics = Statistics(
            total_members=total_members,
            active_members=active_members,
            completed_pathways_total=completed_pathways_total
        )

        # Create distribution object
        self.distribution = Distribution(
            pathway_distribution=dict(pathway_distribution),
            level_distribution=dict(level_distribution)
        )

        self.logger.info(f"Club summary generated for {len(self.members)} members")

    def to_dict(self) -> dict:
        return {
            "club_id": self.club_id,
            "club_name": self.club_name,
            "dashboard_club_id": self.dashboard_club_id,
            "statistics": self.statistics.to_dict() if self.statistics else None,
            "distribution": self.distribution.to_dict() if self.distribution else None,
            "members": [member.to_dict() for member in self.members.values()]
        }