
#-------------------------------------
# Constants to Adjust
#-------------------------------------
# Whether to save the raw endpoint data from the API responses
# (Club and Member summaries are saved regardless)
SAVE_ENDPOINT_DATA = True

# Types of reports to generate using the summary files
# Location of the report files will be determined by the file manager (in session/reports)
REPORT_TYPES = {
    'markdown': True,
    'excel': True,  # Requires pandas
    'pdf': True     # Requires reportlab
}

#-------------------------------------
# Base URLs for general auth/session handling (Don't change these)
#-------------------------------------
LOGIN_URL = "https://www.toastmasters.org/login"
BASECAMP_URL = "https://app.basecamp.toastmasters.org/dashboard"

#-------------------------------------
# Full list of endpoints to call (Don't change these unless you need to add new endpoints)
#-------------------------------------
# These are the primary endpoints that will be called to fetch data
# Overview and progress are the main endpoints for club data
# The progress_detail endpoint is used to fetch detailed progress for each user (using their username and course_id)
# Profile is used to fetch club_id and user_id for admin user running the script
API_ENDPOINTS = {
    'overview': 'https://basecamp.toastmasters.org/api/bcm/member/overview/?club={club_id}&page={page}',
    'progress': 'https://basecamp.toastmasters.org/api/bcm/progress/?club={club_id}&page={page}',
    'progress_detail': 'https://basecamp.toastmasters.org/api/bcm/progress/{course_id}/detail?user={username}',
    'profile': 'https://basecamp.toastmasters.org/api/ti/profile/{user_id}/about/'
}