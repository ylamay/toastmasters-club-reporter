import logging
import json
from datetime import datetime
from pathlib import Path

class HTMLBuilder:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.logger = logging.getLogger(__name__)

    def generate_club_report(self, club_data, club_status_url, member_enrollment_status) -> str:
        """
        Generate complete club report with sidebar navigation layout
        
        Args:
            club_data: Club data object with statistics and members
            club_status_url: URL for the club status report
            member_enrollment_status: List of member enrollment statuses

        Returns:
            str: Complete HTML report content
        """        
        # Extract data for charts
        stats = club_data.statistics
        distribution = club_data.distribution
        
        # Prepare chart data
        pathway_chart_data = self._prepare_pathway_chart_data(distribution.pathway_distribution)
        level_chart_data = self._prepare_level_chart_data(distribution.level_distribution)

        return self._build_html_template(
            club_data.club_name,
            stats,
            club_data,
            pathway_chart_data,
            level_chart_data,
            club_status_url,
            member_enrollment_status
        )

    def _prepare_pathway_chart_data(self, pathway_distribution):
        """Convert pathway distribution to Chart.js format"""
        labels = list(pathway_distribution.keys())
        data = list(pathway_distribution.values())

        # Modern color palette
        colors = [
            '#2563EB', '#7C3AED', '#059669', '#F59E0B', 
            '#EF4444', "#B828A4", '#06B6D4', '#84CC16',
            "#5EE07F", '#F97316', '#F43F5E'
        ]

        return {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(data)],
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        }

    def _prepare_level_chart_data(self, level_distribution):
        """Convert level distribution to Chart.js format"""
        # Sort levels properly
        sorted_levels = sorted(level_distribution.items(), key=lambda x: int(x[0]))

        labels = [f"Level {level}" for level, _ in sorted_levels]
        data = [count for _, count in sorted_levels]
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Members',
                'data': data,
                'backgroundColor': '#059669',
                'borderColor': '#047857',
                'borderWidth': 1
            }]
        }
    
    def _load_css(self) -> str:
        """Load and combine CSS files"""
        css_files = [
            self.base_path / "styles" / "main.css"
        ]
        
        combined_css = []
        for css_file in css_files:
            if css_file.exists():
                combined_css.append(css_file.read_text(encoding='utf-8'))
        
        return "\n".join(combined_css)
    
    def _load_js(self) -> str:
        """Load and combine JavaScript files"""
        js_files = [
            self.base_path / "scripts" / "charts.js",
            self.base_path / "scripts" / "table-expand.js",
            self.base_path / "scripts" / "theme-toggle.js"
        ]
        
        combined_js = []
        for js_file in js_files:
            if js_file.exists():
                combined_js.append(js_file.read_text(encoding='utf-8'))
        
        return "\n".join(combined_js)

    def _build_html_template(self, club_name, stats, club_data, pathway_data, level_data, club_status_url, member_enrollment_status):
        """Build the sidebar layout HTML template"""
        total_active_pathways = sum(pathway_data['datasets'][0]['data']) if pathway_data['datasets'] else 0
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{club_name} - Progress Report</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                {self._load_css()}
            </style>
        </head>
        <body>
            <!-- Sidebar Navigation -->
            <aside class="sidebar">
                <div class="sidebar-header">
                    <div class="club-name">{club_name}</div>
                    <div class="report-date">Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
                </div>
                <nav class="sidebar-nav">
                    <a href="https://www.toastmasters.org" target="_blank" rel="noopener" class="nav-item">
                        🌐 Toastmasters.org
                    </a>
                    <a href="{club_status_url}" 
                       target="_blank" rel="noopener" class="nav-item">
                        📊 Club Status Report
                    </a>
                </nav>
                <div class="sidebar-footer">
                    <button id="themeToggle" class="nav-item theme-toggle">
                        🌙 Dark Mode
                    </button>
                </div>
            </aside>

            <!-- Main Content -->
            <main class="main-content">
                <div class="main-content-wrapper">
                    <!-- Stats Row -->
                    <section class="stats-row">
                    <div class="stats-container">
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-value">{stats.total_members}</div>
                                <div class="stat-label">Total Members</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{stats.active_members}</div>
                                <div class="stat-label">Active Members</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{total_active_pathways}</div>
                                <div class="stat-label">Active Pathways</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{stats.completed_pathways_total}</div>
                                <div class="stat-label">Completed Pathways</div>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- Content Grid -->
                <section class="content-grid">
                    <!-- Enrollment Status Section -->
                    <div class="enrollment-section">
                        <div class="section-header">
                            <div class="section-title">💳 Member Enrollment Status</div>
                        </div>
                        <div class="table-container">
                            {self._build_enrollment_status_table(member_enrollment_status)}
                        </div>
                    </div>

                    <!-- Progress and Charts Container -->
                    <div class="progress-charts-container">
                        <!-- Member Progress Section -->
                        <div class="member-section">
                            <div class="section-header">
                                <div class="section-title">👥 Member Progress Overview</div>
                            </div>
                            <div class="table-container">
                                {self._build_member_progress_table(club_data)}
                            </div>
                        </div>

                        <!-- Charts Section -->
                        <div class="charts-section">
                            <div class="chart-card">
                                <div class="chart-header">
                                    <div class="chart-title">📊 Pathway Distribution</div>
                                </div>
                                <div class="chart-container">
                                    <canvas id="pathwayChart"></canvas>
                                </div>
                            </div>
                            <div class="chart-card">
                                <div class="chart-header">
                                    <div class="chart-title">📈 Level Progress</div>
                                </div>
                                <div class="chart-container">
                                    <canvas id="levelChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                </div>
            </main>

            <script>
                // Inject chart data
                window.CHART_DATA = {{
                    pathway: {json.dumps(pathway_data)},
                    level: {json.dumps(level_data)}
                }};
                
                {self._load_js()}
            </script>                       
        </body>
        </html>
        """

    def _build_enrollment_status_table(self, member_enrollment_status):
        """Build enrollment status table with real data"""
        if not member_enrollment_status:
            return '<div class="no-data">No enrollment data available</div>'
        
        # Filter for paid members only
        paid_members = [member for member in member_enrollment_status if member.get('is_paid', False)]
        
        if not paid_members:
            return '<div class="no-data">No paid members found</div>'
        
        # Sort by inactive status first then membership_end_date string
        def sort_key(member):
            is_enrolled = member.get('is_enrolled', False)
            end_date_str = member.get('membership_end_date', '')
            
            try:
                from datetime import datetime
                # Try to parse the date string
                if end_date_str:
                    end_date = datetime.strptime(end_date_str, "%B %d, %Y")
                    return (is_enrolled, end_date)  # not is_enrolled for inactive first
                else:
                    return (is_enrolled, datetime.max)  # Put members with no date at the end
            except ValueError:
                # If date parsing fails, put at the end
                return (is_enrolled, datetime.max)

        paid_members.sort(key=sort_key)
        
        rows_html = []
        for member in paid_members:
            display_name = member.get('display_name', 'Unknown Member')
            is_enrolled = member.get('is_enrolled', False)
            membership_end_date = member.get('membership_end_date', '')
            
            # Determine status badge
            if is_enrolled and membership_end_date:
                # Check if membership is expiring soon (within 30 days)
                from datetime import datetime
                try:
                    end_date = datetime.strptime(membership_end_date, '%Y-%m-%d')
                    days_until_expiry = (end_date - datetime.now()).days
                    
                    if days_until_expiry <= 0:
                        status_class = "expired"
                        status_text = "Expired"
                    elif days_until_expiry <= 30:
                        status_class = "warning"
                        status_text = "Expiring Soon"
                    else:
                        status_class = "paid"
                        status_text = "Active"
                except Exception:
                    status_class = "paid"
                    status_text = "Active"
            else:
                status_class = "expired"
                status_text = "Inactive"
            
            # Format membership end date for display
            display_date = membership_end_date
            if membership_end_date:
                try:
                    parsed_date = datetime.strptime(membership_end_date, '%Y-%m-%d')
                    display_date = parsed_date.strftime('%b %d, %Y')
                except Exception:
                    display_date = membership_end_date
            
            rows_html.append(f"""
            <tr>
                <td><strong>{display_name}</strong></td>
                <td><span class="status-badge {status_class}">{status_text}</span></td>
                <td>{display_date}</td>
            </tr>
            """)
        
        return f"""
        <table class="enrollment-table">
            <thead>
                <tr>
                    <th>Member</th>
                    <th>Status</th>
                    <th>Membership End</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
        """

    def _build_member_progress_table(self, club_data):
        """Build member table with expandable rows"""
        members = list(club_data.members.values())
        if not members:
            return '<div class="no-data">No member data available</div>'

        # Sort by best pathway progress, desc
        def best_progress(m):
            return max((p.completion_percentage for p in (m.current_pathways or [])), default=0.0)
        members.sort(key=best_progress, reverse=True)

        # Build table rows
        rows_html = []
        for idx, m in enumerate(members):
            row_id = f"m{idx}"
            cps = m.current_pathways or []
            max_level = max(p.current_level for p in cps) if cps else 0
            best = best_progress(m)
            next_action = (m.next_projects[0].name if getattr(m, 'next_projects', None) else '—')
            active_count = len(cps)

            # Summary row
            rows_html.append(f"""
            <tr>
                <td>
                    <button class="expand-btn" data-target="{row_id}" aria-expanded="false">Details</button>
                </td>
                <td><strong>{m.display_name}</strong></td>
                <td><span class="chip">{active_count}</span></td>
                <td><span class="level-badge">L{max_level}</span></td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width:{best:.1f}%"></div>
                    </div>
                    <div class="progress-text">{best:.1f}%</div>
                </td>
                <td><span class="next-project">{next_action}</span></td>
            </tr>
            """)

            # Details row (pathways table)
            detail_rows = []
            for p in sorted(cps, key=lambda x: x.completion_percentage, reverse=True):
                # Find next project for this pathway
                next_proj = "No project assigned"
                for proj in getattr(m, 'next_projects', []) or []:
                    if getattr(proj, 'pathway_name', '') == p.name:
                        next_proj = proj.name
                        break

                priority_class = "priority-low"
                if p.completion_percentage == 0:
                    priority_class = "priority-high"
                elif p.completion_percentage < 30:
                    priority_class = "priority-medium"

                detail_rows.append(f"""
                <tr>
                    <td><div class="pathway-name">{p.name}</div></td>
                    <td><span class="level-badge">L{p.current_level}</span></td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width:{p.completion_percentage:.1f}%"></div>
                        </div>
                        <div class="progress-text">{p.completion_percentage:.1f}%</div>
                    </td>
                    <td>
                        <span class="priority-indicator {priority_class}"></span>
                        <span class="next-project">{next_proj}</span>
                    </td>
                </tr>
                """)

            rows_html.append(f"""
            <tr id="{row_id}" class="details-row">
                <td class="details-cell" colspan="6">
                    <div class="details-content">
                        <table class="pathways-table">
                            <thead>
                                <tr>
                                    <th>Pathway</th>
                                    <th>Level</th>
                                    <th>Progress</th>
                                    <th>Next Project</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(detail_rows)}
                            </tbody>
                        </table>
                    </div>
                </td>
            </tr>
            """)

        return f"""
        <table class="members-table" id="membersTable">
            <thead>
                <tr>
                    <th style="width: 80px;"></th>
                    <th style="width: 120px;">Member</th>
                    <th style="width: 80px;">Active Pathway(s)</th>
                    <th style="width: 80px;">Highest Level</th>
                    <th style="width: 150px;">Best Progress</th>
                    <th>Next Project</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
        """
