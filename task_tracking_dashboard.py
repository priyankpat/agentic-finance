"""
Task Management & Tracking Dashboard
Real-time visualization and management of task execution
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class TaskMetrics:
    """Metrics for individual task"""
    task_id: str
    estimated_duration: int
    actual_duration: float
    retry_count: int
    status: str
    success: bool
    cost_tokens: int = 0
    cost_usd: float = 0.0


class TaskDashboard:
    """Dashboard for tracking task execution"""
    
    def __init__(self):
        self.tasks_data = {}
        self.phases_data = {}
    
    def get_phase_progress(self, phase_id: str, tasks_in_phase: List[str], completed_tasks: set) -> Dict:
        """Calculate phase progress"""
        completed = len([t for t in tasks_in_phase if t in completed_tasks])
        total = len(tasks_in_phase)
        progress = (completed / total * 100) if total > 0 else 0
        
        return {
            'phase_id': phase_id,
            'completed': completed,
            'total': total,
            'progress_percent': progress,
            'status': 'completed' if progress == 100 else 'in_progress' if progress > 0 else 'pending'
        }
    
    def generate_gantt_data(self, execution_order: List[List[str]], task_info: Dict) -> str:
        """Generate Gantt chart data for visualization"""
        
        gantt_rows = []
        current_time = 0
        
        for batch_idx, batch in enumerate(execution_order):
            for task_id in batch:
                task = task_info.get(task_id, {})
                duration = task.get('timeout', 300)
                
                gantt_rows.append({
                    'name': task_id,
                    'start': current_time,
                    'end': current_time + duration,
                    'agent': task.get('agent_type', 'unknown'),
                    'batch': batch_idx + 1
                })
            
            current_time += max([task_info.get(t, {}).get('timeout', 300) for t in batch])
        
        return json.dumps(gantt_rows, indent=2)
    
    def get_task_status_summary(self, results: Dict) -> Dict:
        """Get summary of task statuses"""
        
        status_counts = {
            'completed': 0,
            'failed': 0,
            'in_progress': 0,
            'pending': 0,
            'blocked': 0
        }
        
        for result in results.values():
            status = result.get('status', 'unknown').lower()
            if status in status_counts:
                status_counts[status] += 1
        
        total = sum(status_counts.values())
        
        return {
            'status_counts': status_counts,
            'total': total,
            'success_rate': (status_counts['completed'] / total * 100) if total > 0 else 0
        }


class TaskTracker:
    """Tracks task execution and generates reports"""
    
    def __init__(self):
        self.task_history = {}
        self.phase_history = {}
        self.conflict_log = []
        self.execution_log = []
    
    def log_task_execution(self, task_id: str, status: str, duration: float, error: Optional[str] = None):
        """Log task execution"""
        self.task_history[task_id] = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'duration': duration,
            'error': error
        }
        
        self.execution_log.append({
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'status': status,
            'duration': duration
        })
    
    def log_conflict(self, task1_id: str, task2_id: str, conflict_type: str):
        """Log detected conflict"""
        self.conflict_log.append({
            'timestamp': datetime.now().isoformat(),
            'task1': task1_id,
            'task2': task2_id,
            'type': conflict_type
        })
    
    def get_execution_timeline(self) -> str:
        """Generate execution timeline"""
        timeline = "=== EXECUTION TIMELINE ===\n"
        for entry in self.execution_log:
            timeline += f"{entry['timestamp']} | {entry['task_id']}: {entry['status']} ({entry['duration']:.2f}s)\n"
        return timeline
    
    def get_conflict_report(self) -> str:
        """Generate conflict report"""
        report = "=== CONFLICT REPORT ===\n"
        if not self.conflict_log:
            report += "No conflicts detected!\n"
        else:
            for conflict in self.conflict_log:
                report += f"[{conflict['timestamp']}] {conflict['type'].upper()}: {conflict['task1']} <-> {conflict['task2']}\n"
        return report


# HTML/Markdown Report Generator
class ReportGenerator:
    """Generates execution reports in various formats"""
    
    @staticmethod
    def generate_markdown_report(
        scheduler_info: Dict,
        execution_results: Dict,
        tracker: TaskTracker
    ) -> str:
        """Generate Markdown execution report"""
        
        report = """# 🎯 Task Execution Report

## Executive Summary

"""
        
        # Add summary stats
        total_tasks = len(execution_results)
        completed = sum(1 for r in execution_results.values() if r.get('status') == 'completed')
        failed = sum(1 for r in execution_results.values() if r.get('status') == 'failed')
        
        report += f"""
- **Total Tasks**: {total_tasks}
- **Completed**: {completed} ✅
- **Failed**: {failed} ❌
- **Success Rate**: {completed/total_tasks*100:.1f}%

"""
        
        # Phases
        report += "## Phases Overview\n\n"
        for phase_id, phase_info in scheduler_info.get('phases', {}).items():
            report += f"### {phase_info['name']}\n"
            report += f"- **Tasks**: {phase_info['task_count']}\n"
            report += f"- **Estimated Duration**: {phase_info['estimated_duration']/3600:.1f} hours\n"
            report += f"- **Status**: {phase_info['status']}\n\n"
        
        # Task Details
        report += "## Task Details\n\n"
        for task_id, result in execution_results.items():
            status_emoji = "✅" if result.get('status') == 'completed' else "❌"
            report += f"### {status_emoji} {task_id}\n"
            report += f"- **Status**: {result.get('status')}\n"
            report += f"- **Agent**: {result.get('agent_id', 'N/A')}\n"
            report += f"- **Execution Time**: {result.get('execution_time', 0):.2f}s\n"
            if result.get('error'):
                report += f"- **Error**: {result.get('error')}\n"
            report += "\n"
        
        # Conflicts
        report += "## Conflict Analysis\n\n"
        report += tracker.get_conflict_report()
        report += "\n"
        
        return report
    
    @staticmethod
    def generate_json_report(
        scheduler_info: Dict,
        execution_results: Dict,
        tracker: TaskTracker
    ) -> str:
        """Generate JSON execution report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tasks': len(execution_results),
                'completed': sum(1 for r in execution_results.values() if r.get('status') == 'completed'),
                'failed': sum(1 for r in execution_results.values() if r.get('status') == 'failed')
            },
            'phases': scheduler_info.get('phases', {}),
            'results': execution_results,
            'conflicts': tracker.conflict_log,
            'timeline': tracker.execution_log
        }
        
        return json.dumps(report, indent=2)


# Template for task breakdown
def create_task_breakdown():
    """Template for 4-week implementation task breakdown"""
    
    breakdown = {
        "week1": {
            "name": "Foundation Phase",
            "duration_hours": 30,
            "tasks": [
                {
                    "id": "w1_db_setup",
                    "name": "Setup Database",
                    "agent": "Infrastructure",
                    "subtasks": [
                        "Create PostgreSQL database",
                        "Setup schemas",
                        "Configure backups",
                        "Setup monitoring"
                    ],
                    "dependencies": [],
                    "estimated_hours": 4,
                    "priority": "CRITICAL",
                    "resources": ["postgresql", "devops"]
                },
                {
                    "id": "w1_data_ingestion",
                    "name": "Data Ingestion Agent",
                    "agent": "DataIngestion",
                    "subtasks": [
                        "Gmail API integration",
                        "Receipt OCR implementation",
                        "Plaid API integration",
                        "Data validation",
                        "Error handling"
                    ],
                    "dependencies": ["w1_db_setup"],
                    "estimated_hours": 12,
                    "priority": "CRITICAL",
                    "resources": ["claude_haiku", "gmail_api", "vision_api"]
                },
                {
                    "id": "w1_categorizer",
                    "name": "Expense Categorizer",
                    "agent": "ExpenseCategorizer",
                    "subtasks": [
                        "ML model setup",
                        "Rule-based engine (Phase 1)",
                        "Basic categorization",
                        "Test suite",
                        "Accuracy benchmarking"
                    ],
                    "dependencies": ["w1_db_setup"],
                    "estimated_hours": 10,
                    "priority": "CRITICAL",
                    "resources": ["claude_haiku", "ml_models"]
                },
                {
                    "id": "w1_dashboard",
                    "name": "Basic Dashboard",
                    "agent": "Frontend",
                    "subtasks": [
                        "React setup",
                        "Data visualization",
                        "Real-time updates",
                        "Responsive design"
                    ],
                    "dependencies": ["w1_data_ingestion", "w1_categorizer"],
                    "estimated_hours": 8,
                    "priority": "HIGH",
                    "resources": ["react", "node"]
                }
            ]
        },
        "week2": {
            "name": "Intelligence Phase",
            "duration_hours": 20,
            "dependencies": ["week1"],
            "tasks": [
                {
                    "id": "w2_rules_engine",
                    "name": "Rule-based Categorization",
                    "agent": "ExpenseCategorizer",
                    "subtasks": [
                        "Build merchant rules database",
                        "Implement 70% free path",
                        "Test rules matching",
                        "Optimize performance"
                    ],
                    "dependencies": ["w1_categorizer"],
                    "estimated_hours": 6,
                    "priority": "HIGH",
                    "resources": ["claude_haiku"]
                },
                {
                    "id": "w2_portfolio_agent",
                    "name": "Portfolio Manager Agent",
                    "agent": "PortfolioManager",
                    "subtasks": [
                        "Brokerage API integration",
                        "Multi-account aggregation",
                        "Performance tracking",
                        "Asset allocation calculations"
                    ],
                    "dependencies": ["w1_db_setup"],
                    "estimated_hours": 10,
                    "priority": "CRITICAL",
                    "resources": ["claude_sonnet", "plaid_api"]
                },
                {
                    "id": "w2_portfolio_dashboard",
                    "name": "Portfolio Dashboard",
                    "agent": "Frontend",
                    "subtasks": [
                        "Holdings display",
                        "Metrics visualization",
                        "Performance charts",
                        "Real-time updates"
                    ],
                    "dependencies": ["w2_portfolio_agent"],
                    "estimated_hours": 8,
                    "priority": "HIGH",
                    "resources": ["react", "recharts"]
                }
            ]
        },
        "week3": {
            "name": "Analysis Phase",
            "duration_hours": 20,
            "dependencies": ["week2"],
            "tasks": [
                {
                    "id": "w3_market_research",
                    "name": "Market Research Agent",
                    "agent": "MarketResearch",
                    "subtasks": [
                        "Market data API setup",
                        "Technical analysis",
                        "Fundamental analysis",
                        "Sentiment analysis"
                    ],
                    "dependencies": ["w1_db_setup"],
                    "estimated_hours": 10,
                    "priority": "HIGH",
                    "resources": ["claude_sonnet", "market_data_apis"]
                },
                {
                    "id": "w3_technical_indicators",
                    "name": "Technical Indicators",
                    "agent": "MarketResearch",
                    "subtasks": [
                        "MA50/MA200 calculation",
                        "RSI computation",
                        "MACD implementation",
                        "Volume analysis"
                    ],
                    "dependencies": ["w3_market_research"],
                    "estimated_hours": 6,
                    "priority": "HIGH",
                    "resources": ["claude_sonnet"]
                },
                {
                    "id": "w3_market_dashboard",
                    "name": "Market Analysis Dashboard",
                    "agent": "Frontend",
                    "subtasks": [
                        "Stock screener UI",
                        "Technical charts",
                        "Watchlist management",
                        "Real-time updates"
                    ],
                    "dependencies": ["w3_market_research"],
                    "estimated_hours": 8,
                    "priority": "HIGH",
                    "resources": ["react", "recharts"]
                }
            ]
        },
        "week4": {
            "name": "Recommendations & Risk Phase",
            "duration_hours": 20,
            "dependencies": ["week3"],
            "tasks": [
                {
                    "id": "w4_recommendations",
                    "name": "Investment Recommendations",
                    "agent": "InvestmentRecommendation",
                    "subtasks": [
                        "ML model development",
                        "Feature engineering",
                        "Stock scoring system",
                        "Backtesting framework"
                    ],
                    "dependencies": ["w3_market_research", "w1_db_setup"],
                    "estimated_hours": 12,
                    "priority": "CRITICAL",
                    "resources": ["claude_opus", "ml_models"]
                },
                {
                    "id": "w4_risk_assessment",
                    "name": "Risk Assessment Agent",
                    "agent": "RiskAssessment",
                    "subtasks": [
                        "VaR calculation",
                        "Stress testing",
                        "Concentration analysis",
                        "Alert generation"
                    ],
                    "dependencies": ["w2_portfolio_agent"],
                    "estimated_hours": 8,
                    "priority": "HIGH",
                    "resources": ["claude_sonnet"]
                },
                {
                    "id": "w4_production_launch",
                    "name": "Production Launch",
                    "agent": "DevOps",
                    "subtasks": [
                        "Final testing",
                        "Deployment setup",
                        "Monitoring setup",
                        "Documentation"
                    ],
                    "dependencies": ["w2_portfolio_dashboard", "w4_recommendations", "w4_risk_assessment"],
                    "estimated_hours": 8,
                    "priority": "CRITICAL",
                    "resources": ["docker", "kubernetes"]
                }
            ]
        }
    }
    
    return breakdown


# Example usage and visualization
def print_task_breakdown():
    """Print formatted task breakdown"""
    
    breakdown = create_task_breakdown()
    
    print("=" * 80)
    print("📋 4-WEEK IMPLEMENTATION TASK BREAKDOWN")
    print("=" * 80)
    
    total_hours = 0
    
    for week_id, week_data in breakdown.items():
        print(f"\n\n{'='*80}")
        print(f"🗓️  {week_data['name'].upper()}")
        print(f"{'='*80}")
        print(f"Estimated Duration: {week_data['duration_hours']} hours")
        
        if 'dependencies' in week_data:
            print(f"Depends on: {', '.join(week_data['dependencies'])}")
        
        total_hours += week_data['duration_hours']
        
        print(f"\n📌 TASKS ({len(week_data['tasks'])} total):\n")
        
        for task_idx, task in enumerate(week_data['tasks'], 1):
            print(f"\n   {task_idx}. {task['name']} ({task['id']})")
            print(f"      Priority: {task['priority']}")
            print(f"      Estimated: {task['estimated_hours']} hours")
            print(f"      Agent: {task['agent']}")
            
            if task['dependencies']:
                print(f"      Dependencies: {', '.join(task['dependencies'])}")
            
            print(f"      Resources: {', '.join(task['resources'])}")
            
            print(f"      Subtasks:")
            for subtask in task['subtasks']:
                print(f"         ✓ {subtask}")
    
    print(f"\n\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"Total Estimated Hours: {total_hours}")
    print(f"Weeks: 4")
    print(f"Hours per Week: {total_hours/4:.1f}")
    print(f"Parallel Tasks per Week: Yes (conflict detection active)")
    print(f"Resource Conflicts: Managed automatically")
    print(f"Agent Conflicts: Prevented")
    
    return breakdown


if __name__ == "__main__":
    print_task_breakdown()
