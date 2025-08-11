import logging
import json
from datetime import datetime
from pathlib import Path

class HTMLBuilder:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.logger = logging.getLogger(__name__)

    def generate_club_report(self, club_data) -> str:
        """
        Generate complete club report with charts and data
        
        Args:
            markdown: Markdown content string
            club_data: Dict from your JSON structure
            
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
            level_chart_data
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
            self.base_path / "scripts" / "theme-toggle.js",
            self.base_path / "scripts" / "charts.js", 
            self.base_path / "scripts" / "table-expand.js"
        ]
        
        combined_js = []
        for js_file in js_files:
            if js_file.exists():
                combined_js.append(js_file.read_text(encoding='utf-8'))
        
        return "\n".join(combined_js)    

    def _build_html_template(self, club_name, stats, club_data, pathway_data, level_data):
        """Build the complete HTML template"""
        # Calculate total active pathways for the metric
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
            <div class="report-container">
                <header class="report-header" id="topNav">
                    <div class="header-left">
                        <div class="club-title-row">
                            <h1>{club_name}</h1>
                            <a class="nav-link club-link" href="https://www.toastmasters.org" target="_blank" rel="noopener">Toastmasters.org</a>
                        </div>
                        <span class="report-date">Generated {datetime.now().strftime('%B %Y')}</span>
                    </div>
                    <nav class="header-right">
                        <button id="themeToggle" class="theme-toggle" aria-label="Toggle theme" title="Toggle theme">🌙</button>
                    </nav>
                </header>
                
                <div class="dashboard-grid">
                    <div class="stats-panel">
                        <div class="card">
                            <div class="metric-value">{stats.total_members}</div>
                            <div class="metric-label">Total Members</div>
                        </div>
                        <div class="card">
                            <div class="metric-value">{stats.active_members}</div>
                            <div class="metric-label">Active Members</div>
                        </div>
                        <div class="card">
                            <div class="metric-value">{total_active_pathways}</div>
                            <div class="metric-label">Active Pathways</div>
                        </div>
                        <div class="card">
                            <div class="metric-value">{stats.completed_pathways_total}</div>
                            <div class="metric-label">Completed Pathways</div>
                        </div>
                        
                        <!-- FUTURE: Club goals section -->
                        <div class="goals-placeholder">
                            <div class="card goals-card">
                                <div class="metric-label">Club Goals</div>
                                <div class="goals-summary">Coming Soon</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="charts-panel">
                        <div class="chart-card">
                            <div class="chart-title">&#x1F4CA; Pathway Distribution</div>
                            <div class="chart-container">
                                <canvas id="pathwayChart"></canvas>
                            </div>
                        </div>
                        <div class="chart-card">
                            <div class="chart-title">&#128200; Level Progress</div>
                            <div class="chart-container">
                                <canvas id="levelChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                {self._build_member_progress_section(club_data)}
            </div>

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

    def _build_member_progress_section(self, club_data):
        """Build member table with expandable rows"""
        members = list(club_data.members.values())
        if not members:
            return '<div class="member-section"><div class="section-title">&#x1F465; No Member Data Available</div></div>'

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
                <td style="width:32px;">
                    <button class="expand-btn" data-target="{row_id}" aria-expanded="false">Details</button>
                </td>
                <td><strong>{m.display_name}</strong></td>
                <td><span class="chip">{active_count} active</span></td>
                <td><span class="level-badge">L{max_level}</span></td>
                <td>
                    <div class="progress-bar progress-bar--sm">
                        <div class="progress-fill" style="width:{best:.1f}%"></div>
                    </div>
                    <div class="progress-text" style="font-size:.8rem">{best:.1f}% best</div>
                </td>
                <td><span class="next-project">{next_action}</span></td>
            </tr>
            """)

            # Details row (pathways table)
            detail_rows = []
            for p in sorted(cps, key=lambda x: x.completion_percentage, reverse=True):
                # Find next project for this pathway (if present)
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
                    <td style="width:70px"><span class="level-badge">L{p.current_level}</span></td>
                    <td>
                        <div class="progress-bar progress-bar--sm">
                            <div class="progress-fill" style="width:{p.completion_percentage:.1f}%"></div>
                        </div>
                        <div class="progress-text" style="font-size:.8rem">{p.completion_percentage:.1f}%</div>
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
                                    <th style="width:40%">Pathway</th>
                                    <th style="width:10%">Level</th>
                                    <th style="width:25%">Progress</th>
                                    <th style="width:25%">Next Project</th>
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

        # Render section with table and toggle script
        return f"""
        <div class="member-section">
            <div class="section-title">&#x1F465; Member Progress Overview</div>
            <div class="table-container">
                <table class="members-table" id="membersTable">
                    <thead>
                        <tr>
                            <th></th>
                            <th>Member</th>
                            <th>Active Pathways</th>
                            <th>Highest Level</th>
                            <th>Best Progress</th>
                            <th>Next Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows_html)}
                    </tbody>
                </table>
            </div>
        </div>
        """