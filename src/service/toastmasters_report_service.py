from manager.file_manager import FileManager
from utils.report.markdown_builder import MarkdownBuilder
from utils.report.excel_builder import ExcelBuilder
from utils.report.pdf_builder import PDFBuilder
import logging

class ToastmastersReportService:
    """
    Service for generating reports from Toastmasters summary data

    Attributes:
        file_manager: FileManager instance for file operations
        app_settings: Application settings containing app configurations
        logger (logging.Logger): Logger instance for logging messages
    """
    def __init__(self, file_manager: FileManager, app_settings):
        self.file_manager = file_manager
        self.app_settings = app_settings
        self.logger = logging.getLogger(__name__)

    def generate_reports(self, clubs: dict):
        """
        Generate all requested report types

        Args:
            clubs (dict): Dictionary of Club objects by club_id
        """
        report_types = self._get_enabled_report_types()
        if not report_types:
            self.logger.warning("No report types enabled in app settings")
            return
        
        # Get the first club
        club = next(iter(clubs.values())) if clubs else None
        if not club:
            self.logger.warning("No club data available for reports")
            return        
        
        self.logger.info(f"Generating reports in the following formats: {report_types}")

        for report_type in report_types:
            if report_type == "markdown":
                self._generate_markdown_report(club)
            elif report_type == "excel":
                self._generate_excel_report(club)
            elif report_type == "pdf":
                self._generate_pdf_report(club)
            else:
                self.logger.warning(f"Report type [{report_type}] is not supported.")

    def _get_enabled_report_types(self):
        """
        Get a list of enabled report types based on app settings

        Returns:
            list: List of enabled report types
        """
        report_keys = ["markdown", "excel", "pdf"]
        return [
            key for key in report_keys 
            if self.app_settings.REPORT_TYPES.get(key, False)
        ]
    
    def _generate_markdown_report(self, club: dict):
        """
        Generate a Markdown report from the club data

        Args:
            club (dict): Club summary data

        Returns:
            None
        """
        self.logger.info("Generating Markdown report")

        # Generate the markdown report
        builder = MarkdownBuilder()
        content = builder.generate_club_report(club)
        
        # Save the report
        filename = f"{club.club_name.lower().replace(' ', '_')}_report.md"        
        success = self.file_manager.save_markdown(
            content,
            filename,
            "reports_directory"
        )
        
        if success:
            self.logger.info(f"Markdown report generated: {filename}")
        else:
            self.logger.warning(f"Failed to save Markdown report: {filename}")

    def _generate_excel_report(self, club: dict):
        """
        Generate an Excel report from the club data
        
        Args:
            club (dict): Club summary data
        """
        self.logger.info("Generating Excel report")

        # Create builder and generate report
        builder = ExcelBuilder()
        dataframes = builder.generate_club_report(club)
        
        # Save the report
        filename = f"{club.club_name.lower().replace(' ', '_')}_report.xlsx"
        success = self.file_manager.save_excel(
            dataframes,
            filename,
            "reports_directory"
        )
            
        if success:
            self.logger.info(f"Excel report generated: {filename}")
        else:
            self.logger.warning(f"Failed to save Excel report: {filename}")

    def _generate_pdf_report(self, club: dict):
        """
        Generate a PDF report from the club data

        Args:
            club (dict): Club summary data
        """
        self.logger.info("Generating PDF report")

        # Create builder and generate report
        builder = PDFBuilder()
        story = builder.generate_club_report(club)

        # Save the report
        filename = f"{club.club_name.lower().replace(' ', '_')}_report.pdf"
        success = self.file_manager.save_pdf(
            story,
            filename,
            "reports_directory"
        )

        if success:
            self.logger.info(f"PDF report generated: {filename}")
        else:
            self.logger.warning(f"Failed to save PDF report: {filename}")