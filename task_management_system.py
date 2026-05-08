"""
Agentic Finance System - Task Management & Parallel Execution
Handles task decomposition, dependencies, conflict detection, and parallel execution
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import asyncio
import json
from abc import ABC, abstractmethod
import hashlib


# ============================================================================
# Task Enums & Data Structures
# ============================================================================

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"           # Not yet started
    WAITING_DEPENDENCIES = "waiting_dependencies"  # Waiting for deps
    IN_PROGRESS = "in_progress"   # Currently executing
    COMPLETED = "completed"       # Finished successfully
    FAILED = "failed"             # Execution failed
    BLOCKED = "blocked"           # Can't execute (conflict/resource)
    CANCELLED = "cancelled"       # Explicitly cancelled


class TaskPriority(Enum):
    """Task priority levels for scheduling"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ConflictType(Enum):
    """Types of conflicts between tasks"""
    RESOURCE_CONFLICT = "resource"         # Both need same resource
    AGENT_CONFLICT = "agent"               # Same agent assigned
    DATA_CONFLICT = "data"                 # Reading/writing same data
    TIMING_CONFLICT = "timing"             # Sequential requirement
    UNKNOWN = "unknown"


class ExecutionModel(Enum):
    """How tasks can be executed"""
    SEQUENTIAL = "sequential"     # Must run one after another
    PARALLEL = "parallel"         # Can run simultaneously
    BATCH = "batch"               # Run in batches
    SCHEDULED = "scheduled"       # Run at specific time
    CONDITIONAL = "conditional"   # Depends on other task results


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TaskDependency:
    """Represents a dependency between tasks"""
    dependent_task_id: str      # Task that depends
    required_task_id: str       # Task that must complete first
    dependency_type: str        # "blocks" | "requires_output" | "requires_state"
    critical: bool = True       # If True, must wait; if False, can proceed


@dataclass
class ResourceRequirement:
    """Resource needed by a task"""
    resource_type: str          # "api", "database", "memory", "agent", "cache"
    resource_id: str           # Specific resource (e.g., "email_api", "sonnet_model")
    exclusive: bool = False    # Must be exclusively held
    estimated_duration: int = 60  # Seconds


@dataclass
class TaskResult:
    """Result of task execution"""
    task_id: str
    status: TaskStatus
    result_data: Optional[Dict] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    agent_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'result_data': self.result_data,
            'error': self.error,
            'execution_time': self.execution_time,
            'agent_id': self.agent_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


@dataclass
class Task:
    """Represents a single unit of work"""
    task_id: str
    agent_type: str                         # Which agent should execute this
    task_type: str                          # What kind of work: "ingest", "categorize", etc
    description: str
    payload: Dict
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    
    # Execution control
    execution_model: ExecutionModel = ExecutionModel.SEQUENTIAL
    max_retries: int = 3
    timeout_seconds: int = 300
    
    # Dependencies & resources
    dependencies: List[TaskDependency] = field(default_factory=list)
    required_resources: List[ResourceRequirement] = field(default_factory=list)
    blocked_tasks: Set[str] = field(default_factory=set)
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    
    # Results
    result: Optional[TaskResult] = None
    
    def get_resource_keys(self) -> Set[str]:
        """Get unique resource identifiers"""
        return {f"{r.resource_type}:{r.resource_id}" for r in self.required_resources}
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'agent_type': self.agent_type,
            'task_type': self.task_type,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.name,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'retry_count': self.retry_count
        }


@dataclass
class TaskPhase:
    """Groups related tasks into a phase"""
    phase_id: str
    name: str
    description: str
    task_ids: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    can_parallelize: bool = True
    estimated_duration: int = 0  # Seconds
    dependencies: List[str] = field(default_factory=list)  # Other phase IDs
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'phase_id': self.phase_id,
            'name': self.name,
            'description': self.description,
            'task_count': len(self.task_ids),
            'status': self.status.value,
            'can_parallelize': self.can_parallelize,
            'estimated_duration': self.estimated_duration
        }


# ============================================================================
# Conflict Detection
# ============================================================================

class ConflictDetector:
    """Detects conflicts between tasks"""
    
    @staticmethod
    def detect_agent_conflict(task1: Task, task2: Task) -> Optional[ConflictType]:
        """Check if both tasks are assigned to same agent"""
        if task1.agent_type == task2.agent_type:
            return ConflictType.AGENT_CONFLICT
        return None
    
    @staticmethod
    def detect_resource_conflict(task1: Task, task2: Task) -> Optional[ConflictType]:
        """Check if tasks need exclusive access to same resource"""
        resources1 = task1.get_resource_keys()
        resources2 = task2.get_resource_keys()
        
        shared = resources1 & resources2
        if shared:
            # Check if any are exclusive
            for req1 in task1.required_resources:
                for req2 in task2.required_resources:
                    key1 = f"{req1.resource_type}:{req1.resource_id}"
                    key2 = f"{req2.resource_type}:{req2.resource_id}"
                    if key1 == key2 and (req1.exclusive or req2.exclusive):
                        return ConflictType.RESOURCE_CONFLICT
        return None
    
    @staticmethod
    def detect_data_conflict(task1: Task, task2: Task) -> Optional[ConflictType]:
        """Check if tasks write to same data"""
        # Check if payload has overlapping data targets
        payload1_str = json.dumps(task1.payload, sort_keys=True)
        payload2_str = json.dumps(task2.payload, sort_keys=True)
        
        hash1 = hashlib.md5(payload1_str.encode()).hexdigest()
        hash2 = hashlib.md5(payload2_str.encode()).hexdigest()
        
        # If same data hash and both are writes, conflict
        if hash1 == hash2 and task1.task_type in ["write", "update", "categorize"]:
            if task2.task_type in ["write", "update", "categorize"]:
                return ConflictType.DATA_CONFLICT
        return None
    
    @staticmethod
    def has_conflict(task1: Task, task2: Task) -> Tuple[bool, Optional[ConflictType]]:
        """Check for any conflict between tasks"""
        
        # Check agent conflict
        if ConflictDetector.detect_agent_conflict(task1, task2):
            return True, ConflictType.AGENT_CONFLICT
        
        # Check resource conflict
        if ConflictDetector.detect_resource_conflict(task1, task2):
            return True, ConflictType.RESOURCE_CONFLICT
        
        # Check data conflict
        if ConflictDetector.detect_data_conflict(task1, task2):
            return True, ConflictType.DATA_CONFLICT
        
        return False, None


# ============================================================================
# Task Scheduler
# ============================================================================

class TaskScheduler:
    """Schedules tasks respecting dependencies and conflicts"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.phases: Dict[str, TaskPhase] = {}
        self.execution_order: List[List[str]] = []  # Tasks grouped by parallel batch
        self.conflicts: Dict[str, List[Tuple[str, ConflictType]]] = {}
        self.conflict_detector = ConflictDetector()
    
    def add_task(self, task: Task) -> bool:
        """Add a task to the scheduler"""
        if task.task_id in self.tasks:
            return False
        self.tasks[task.task_id] = task
        return True
    
    def add_phase(self, phase: TaskPhase) -> bool:
        """Add a phase and its tasks"""
        if phase.phase_id in self.phases:
            return False
        self.phases[phase.phase_id] = phase
        
        # Add all tasks in phase
        for task_id in phase.task_ids:
            if task_id not in self.tasks:
                return False
        
        return True
    
    def detect_all_conflicts(self) -> Dict[str, List[Tuple[str, ConflictType]]]:
        """Detect all conflicts in task graph"""
        self.conflicts = {}
        
        task_list = list(self.tasks.values())
        for i, task1 in enumerate(task_list):
            self.conflicts[task1.task_id] = []
            
            for task2 in task_list[i+1:]:
                has_conflict, conflict_type = self.conflict_detector.has_conflict(task1, task2)
                if has_conflict:
                    self.conflicts[task1.task_id].append((task2.task_id, conflict_type))
                    if task2.task_id not in self.conflicts:
                        self.conflicts[task2.task_id] = []
                    self.conflicts[task2.task_id].append((task1.task_id, conflict_type))
        
        return self.conflicts
    
    def validate_dependencies(self) -> Tuple[bool, Optional[str]]:
        """Check for circular dependencies"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            for dep in task.dependencies:
                if dep.required_task_id not in visited:
                    if has_cycle(dep.required_task_id):
                        return True
                elif dep.required_task_id in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        for task_id in self.tasks:
            if task_id not in visited:
                if has_cycle(task_id):
                    return False, f"Circular dependency detected involving {task_id}"
        
        return True, None
    
    def calculate_execution_order(self) -> List[List[str]]:
        """
        Calculate execution order respecting:
        1. Dependencies
        2. Conflicts (serialized)
        3. Priorities
        """
        
        # Validate first
        valid, error = self.validate_dependencies()
        if not valid:
            raise ValueError(error)
        
        # Detect conflicts
        self.detect_all_conflicts()
        
        # Topological sort with conflict resolution
        execution_order = []
        ready_tasks = set()
        completed = set()
        
        # Find tasks with no dependencies
        for task_id, task in self.tasks.items():
            if not task.dependencies:
                ready_tasks.add(task_id)
        
        while ready_tasks or len(completed) < len(self.tasks):
            if not ready_tasks:
                # No ready tasks, must be a cycle or deadlock
                break
            
            # Group ready tasks into parallel batch
            batch = []
            batch_resources = set()
            excluded = set()
            
            # Sort by priority (higher first)
            sorted_ready = sorted(
                ready_tasks,
                key=lambda tid: self.tasks[tid].priority.value,
                reverse=True
            )
            
            for task_id in sorted_ready:
                task = self.tasks[task_id]
                
                # Check conflicts with other batch tasks
                can_run_parallel = True
                for other_id in batch:
                    has_conflict, _ = self.conflict_detector.has_conflict(
                        task, 
                        self.tasks[other_id]
                    )
                    if has_conflict:
                        can_run_parallel = False
                        break
                
                # Check resource conflicts
                task_resources = task.get_resource_keys()
                if batch_resources & task_resources:
                    can_run_parallel = False
                
                if can_run_parallel:
                    batch.append(task_id)
                    batch_resources.update(task_resources)
            
            if batch:
                execution_order.append(batch)
                
                # Mark completed and find newly ready tasks
                for task_id in batch:
                    ready_tasks.remove(task_id)
                    completed.add(task_id)
                    
                    # Mark dependent tasks as ready if all deps done
                    for other_id, task in self.tasks.items():
                        if other_id not in completed:
                            all_deps_done = all(
                                dep.required_task_id in completed
                                for dep in task.dependencies
                            )
                            if all_deps_done:
                                ready_tasks.add(other_id)
        
        self.execution_order = execution_order
        return execution_order
    
    def get_task_batch_info(self) -> List[Dict]:
        """Get execution info for each batch"""
        info = []
        for batch_idx, batch in enumerate(self.execution_order):
            batch_info = {
                'batch': batch_idx + 1,
                'total_batches': len(self.execution_order),
                'tasks': [],
                'parallelizable': True,
                'estimated_duration': 0
            }
            
            for task_id in batch:
                task = self.tasks[task_id]
                batch_info['tasks'].append({
                    'task_id': task_id,
                    'agent_type': task.agent_type,
                    'task_type': task.task_type,
                    'priority': task.priority.name,
                    'timeout': task.timeout_seconds
                })
                batch_info['estimated_duration'] += task.timeout_seconds
            
            info.append(batch_info)
        
        return info


# ============================================================================
# Resource Manager
# ============================================================================

class ResourceManager:
    """Manages resource allocation to tasks"""
    
    def __init__(self):
        self.resource_holders: Dict[str, List[str]] = {}  # resource_id -> [task_ids]
        self.task_resources: Dict[str, Set[str]] = {}      # task_id -> resource_ids
        self.resource_locks: Dict[str, bool] = {}          # resource_id -> locked
    
    def allocate_resource(self, task_id: str, resource_key: str, exclusive: bool = False) -> bool:
        """
        Allocate a resource to a task
        Returns True if successful, False if resource unavailable
        """
        if exclusive and self.resource_locks.get(resource_key, False):
            return False
        
        if resource_key not in self.resource_holders:
            self.resource_holders[resource_key] = []
        
        self.resource_holders[resource_key].append(task_id)
        
        if task_id not in self.task_resources:
            self.task_resources[task_id] = set()
        self.task_resources[task_id].add(resource_key)
        
        if exclusive:
            self.resource_locks[resource_key] = True
        
        return True
    
    def release_resources(self, task_id: str) -> bool:
        """Release all resources held by a task"""
        if task_id not in self.task_resources:
            return False
        
        for resource_key in self.task_resources[task_id]:
            if resource_key in self.resource_holders:
                if task_id in self.resource_holders[resource_key]:
                    self.resource_holders[resource_key].remove(task_id)
            
            # Clear lock if this was the only holder
            if resource_key in self.resource_holders:
                if not self.resource_holders[resource_key]:
                    self.resource_locks[resource_key] = False
        
        del self.task_resources[task_id]
        return True
    
    def get_resource_status(self) -> Dict:
        """Get status of all resources"""
        return {
            'resource_holders': self.resource_holders,
            'resource_locks': self.resource_locks,
            'task_count': len(self.task_resources)
        }


# ============================================================================
# Task Executor
# ============================================================================

class TaskExecutor:
    """Executes tasks in parallel with proper synchronization"""
    
    def __init__(self, scheduler: TaskScheduler):
        self.scheduler = scheduler
        self.resource_manager = ResourceManager()
        self.results: Dict[str, TaskResult] = {}
        self.execution_stats = {
            'total_tasks': 0,
            'completed': 0,
            'failed': 0,
            'total_time': 0.0
        }
    
    async def execute_batch(self, batch: List[str]) -> Dict[str, TaskResult]:
        """Execute a batch of tasks in parallel"""
        
        # Create async tasks
        batch_results = {}
        tasks = []
        
        for task_id in batch:
            task = self.scheduler.tasks[task_id]
            tasks.append(asyncio.create_task(
                self._execute_single_task(task)
            ))
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for task_id, result in zip(batch, results):
            if isinstance(result, Exception):
                batch_results[task_id] = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=str(result)
                )
            else:
                batch_results[task_id] = result
                self.results[task_id] = result
        
        return batch_results
    
    async def _execute_single_task(self, task: Task) -> TaskResult:
        """Execute a single task with timeout and error handling"""
        
        task.started_at = datetime.now()
        task.status = TaskStatus.IN_PROGRESS
        
        try:
            # Allocate resources
            for req in task.required_resources:
                resource_key = f"{req.resource_type}:{req.resource_id}"
                if not self.resource_manager.allocate_resource(
                    task.task_id, 
                    resource_key, 
                    req.exclusive
                ):
                    task.status = TaskStatus.BLOCKED
                    return TaskResult(
                        task_id=task.task_id,
                        status=TaskStatus.BLOCKED,
                        error="Resource unavailable"
                    )
            
            # Execute with timeout
            start = datetime.now()
            
            # Simulate execution (in real system, call agent)
            await asyncio.sleep(0.1)  # Simulated work
            
            end = datetime.now()
            execution_time = (end - start).total_seconds()
            
            task.completed_at = end
            task.status = TaskStatus.COMPLETED
            
            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result_data={'simulated': True},
                execution_time=execution_time,
                start_time=start,
                end_time=end
            )
            
            self.results[task.task_id] = result
            self.execution_stats['completed'] += 1
            
            return result
        
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.PENDING
                return await self._execute_single_task(task)
            
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="Task timeout"
            )
        
        except Exception as e:
            task.status = TaskStatus.FAILED
            self.execution_stats['failed'] += 1
            
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
        
        finally:
            # Release resources
            self.resource_manager.release_resources(task.task_id)
    
    async def execute_all(self) -> Dict[str, TaskResult]:
        """Execute all tasks in order"""
        
        execution_order = self.scheduler.calculate_execution_order()
        total_start = datetime.now()
        
        for batch_idx, batch in enumerate(execution_order):
            print(f"\n▶️  Executing Batch {batch_idx + 1}/{len(execution_order)}")
            print(f"   Tasks: {', '.join(batch)}")
            
            # Execute batch
            batch_results = await self.execute_batch(batch)
            
            # Report results
            for task_id, result in batch_results.items():
                status_icon = "✅" if result.status == TaskStatus.COMPLETED else "❌"
                print(f"   {status_icon} {task_id}: {result.status.value}")
        
        total_end = datetime.now()
        self.execution_stats['total_time'] = (total_end - total_start).total_seconds()
        self.execution_stats['total_tasks'] = len(self.scheduler.tasks)
        
        return self.results
    
    def get_execution_report(self) -> Dict:
        """Generate execution report"""
        return {
            'stats': self.execution_stats,
            'results': {k: v.to_dict() for k, v in self.results.items()},
            'execution_order': self.scheduler.execution_order,
            'conflicts': self.scheduler.conflicts,
            'resource_status': self.resource_manager.get_resource_status()
        }


# ============================================================================
# Example Usage
# ============================================================================

async def example_4week_plan():
    """Example: 4-week implementation plan with tasks"""
    
    scheduler = TaskScheduler()
    
    # === WEEK 1: Foundation ===
    week1_tasks = [
        Task(
            task_id="w1_db_setup",
            agent_type="Infrastructure",
            task_type="setup",
            description="Setup PostgreSQL database",
            payload={'databases': ['finance_db']},
            priority=TaskPriority.CRITICAL,
            required_resources=[
                ResourceRequirement("database", "postgresql", exclusive=True)
            ]
        ),
        Task(
            task_id="w1_data_ingestion",
            agent_type="DataIngestion",
            task_type="setup",
            description="Implement Data Ingestion Agent",
            payload={'components': ['email_parser', 'receipt_ocr']},
            priority=TaskPriority.CRITICAL,
            dependencies=[
                TaskDependency("w1_data_ingestion", "w1_db_setup", "blocks")
            ],
            required_resources=[
                ResourceRequirement("api", "gmail_api"),
                ResourceRequirement("api", "vision_api")
            ]
        ),
        Task(
            task_id="w1_categorizer",
            agent_type="ExpenseCategorizer",
            task_type="setup",
            description="Implement Expense Categorizer Agent",
            payload={'ml_models': ['classifier']},
            priority=TaskPriority.CRITICAL,
            dependencies=[
                TaskDependency("w1_categorizer", "w1_db_setup", "blocks")
            ],
            required_resources=[
                ResourceRequirement("api", "claude_haiku")
            ]
        ),
        Task(
            task_id="w1_dashboard",
            agent_type="Frontend",
            task_type="setup",
            description="Create basic dashboard",
            payload={'framework': 'react'},
            priority=TaskPriority.HIGH,
            dependencies=[
                TaskDependency("w1_dashboard", "w1_data_ingestion", "requires_output"),
                TaskDependency("w1_dashboard", "w1_categorizer", "requires_output")
            ],
            required_resources=[
                ResourceRequirement("api", "node_modules")
            ]
        ),
    ]
    
    # === WEEK 2: Intelligence ===
    week2_tasks = [
        Task(
            task_id="w2_rules_engine",
            agent_type="ExpenseCategorizer",
            task_type="enhancement",
            description="Add rule-based categorization (70% free path)",
            payload={'rules': ['merchant_rules', 'category_rules']},
            priority=TaskPriority.HIGH,
            dependencies=[
                TaskDependency("w2_rules_engine", "w1_categorizer", "blocks")
            ]
        ),
        Task(
            task_id="w2_portfolio_agent",
            agent_type="PortfolioManager",
            task_type="setup",
            description="Implement Portfolio Manager Agent",
            payload={'brokerages': ['ib', 'td', 'fidelity']},
            priority=TaskPriority.CRITICAL,
            dependencies=[
                TaskDependency("w2_portfolio_agent", "w1_db_setup", "blocks")
            ],
            required_resources=[
                ResourceRequirement("api", "claude_sonnet"),
                ResourceRequirement("api", "plaid_api")
            ]
        ),
        Task(
            task_id="w2_portfolio_dashboard",
            agent_type="Frontend",
            task_type="setup",
            description="Create portfolio dashboard",
            payload={'components': ['holdings_table', 'metrics']},
            priority=TaskPriority.HIGH,
            dependencies=[
                TaskDependency("w2_portfolio_dashboard", "w2_portfolio_agent", "requires_output")
            ]
        ),
    ]
    
    # === WEEK 3: Analysis ===
    week3_tasks = [
        Task(
            task_id="w3_market_research",
            agent_type="MarketResearch",
            task_type="setup",
            description="Implement Market Research Agent",
            payload={'data_sources': ['alpha_vantage', 'polygon', 'newsapi']},
            priority=TaskPriority.HIGH,
            dependencies=[
                TaskDependency("w3_market_research", "w1_db_setup", "blocks")
            ],
            required_resources=[
                ResourceRequirement("api", "claude_sonnet"),
                ResourceRequirement("api", "market_data_apis")
            ]
        ),
        Task(
            task_id="w3_technical_indicators",
            agent_type="MarketResearch",
            task_type="enhancement",
            description="Add technical indicator calculations",
            payload={'indicators': ['ma50', 'rsi', 'macd']},
            priority=TaskPriority.HIGH,
            dependencies=[
                TaskDependency("w3_technical_indicators", "w3_market_research", "blocks")
            ]
        ),
    ]
    
    # === WEEK 4: Recommendations & Risk ===
    week4_tasks = [
        Task(
            task_id="w4_recommendations",
            agent_type="InvestmentRecommendation",
            task_type="setup",
            description="Implement Investment Recommendation Agent",
            payload={'model': 'ml_investment_model'},
            priority=TaskPriority.CRITICAL,
            dependencies=[
                TaskDependency("w4_recommendations", "w3_market_research", "requires_output"),
                TaskDependency("w4_recommendations", "w1_db_setup", "blocks")
            ],
            required_resources=[
                ResourceRequirement("api", "claude_opus"),
                ResourceRequirement("memory", "ml_models", exclusive=True)
            ]
        ),
        Task(
            task_id="w4_risk_assessment",
            agent_type="RiskAssessment",
            task_type="setup",
            description="Implement Risk Assessment Agent",
            payload={'metrics': ['var', 'sharpe', 'beta']},
            priority=TaskPriority.HIGH,
            dependencies=[
                TaskDependency("w4_risk_assessment", "w2_portfolio_agent", "requires_output")
            ],
            required_resources=[
                ResourceRequirement("api", "claude_sonnet")
            ]
        ),
        Task(
            task_id="w4_launch",
            agent_type="DevOps",
            task_type="deployment",
            description="Deploy complete system to production",
            payload={'environment': 'production'},
            priority=TaskPriority.CRITICAL,
            dependencies=[
                TaskDependency("w4_launch", "w2_portfolio_dashboard", "blocks"),
                TaskDependency("w4_launch", "w4_recommendations", "blocks"),
                TaskDependency("w4_launch", "w4_risk_assessment", "blocks")
            ]
        ),
    ]
    
    # Add all tasks
    all_tasks = week1_tasks + week2_tasks + week3_tasks + week4_tasks
    for task in all_tasks:
        scheduler.add_task(task)
    
    # Create phases
    phases = [
        TaskPhase(
            phase_id="week1",
            name="Week 1: Foundation",
            description="Setup database, data ingestion, and basic dashboard",
            task_ids=[t.task_id for t in week1_tasks],
            estimated_duration=30*3600  # 30 hours
        ),
        TaskPhase(
            phase_id="week2",
            name="Week 2: Intelligence",
            description="Add portfolio management and rule-based categorization",
            task_ids=[t.task_id for t in week2_tasks],
            dependencies=["week1"],
            estimated_duration=20*3600
        ),
        TaskPhase(
            phase_id="week3",
            name="Week 3: Analysis",
            description="Implement market research and analysis",
            task_ids=[t.task_id for t in week3_tasks],
            dependencies=["week2"],
            estimated_duration=20*3600
        ),
        TaskPhase(
            phase_id="week4",
            name="Week 4: Recommendations",
            description="Add recommendations and risk management",
            task_ids=[t.task_id for t in week4_tasks],
            dependencies=["week3"],
            estimated_duration=20*3600
        ),
    ]
    
    for phase in phases:
        scheduler.add_phase(phase)
    
    # Calculate execution plan
    print("=" * 70)
    print("🎯 4-WEEK IMPLEMENTATION PLAN WITH TASK SCHEDULING")
    print("=" * 70)
    
    execution_order = scheduler.calculate_execution_order()
    
    print("\n📊 EXECUTION PLAN:")
    print("-" * 70)
    
    batch_info = scheduler.get_task_batch_info()
    for batch in batch_info:
        print(f"\n▶️  BATCH {batch['batch']}/{batch['total_batches']}")
        print(f"   Estimated Duration: {batch['estimated_duration']}s")
        print(f"   Parallelizable: {'Yes' if batch['parallelizable'] else 'No'}")
        print("   Tasks:")
        for task_info in batch['tasks']:
            print(f"     • {task_info['task_id']}")
            print(f"       Agent: {task_info['agent_type']}")
            print(f"       Type: {task_info['task_type']}")
    
    # Detect conflicts
    print("\n" + "=" * 70)
    print("⚠️  CONFLICT ANALYSIS")
    print("-" * 70)
    
    conflicts = scheduler.detect_all_conflicts()
    conflict_count = sum(len(v) for v in conflicts.values())
    
    if conflict_count == 0:
        print("✅ No conflicts detected! All parallel tasks can run safely.")
    else:
        print(f"❌ Found {conflict_count} conflicts:\n")
        for task_id, task_conflicts in conflicts.items():
            if task_conflicts:
                print(f"   {task_id}:")
                for conflicting_task, conflict_type in task_conflicts:
                    print(f"      ⚠️  {conflict_type.value} with {conflicting_task}")
    
    # Show phases
    print("\n" + "=" * 70)
    print("📅 PHASES")
    print("-" * 70)
    
    for phase_id, phase in scheduler.phases.items():
        print(f"\n{phase.name}")
        print(f"   Tasks: {len(phase.task_ids)}")
        print(f"   Estimated: {phase.estimated_duration/3600:.1f} hours")
        print(f"   Tasks: {', '.join(phase.task_ids[:3])}")
        if len(phase.task_ids) > 3:
            print(f"           {', '.join(phase.task_ids[3:])}")
    
    # Execute
    print("\n" + "=" * 70)
    print("🚀 EXECUTING TASKS")
    print("-" * 70)
    
    executor = TaskExecutor(scheduler)
    results = await executor.execute_all()
    
    # Report
    print("\n" + "=" * 70)
    print("📈 EXECUTION REPORT")
    print("-" * 70)
    
    report = executor.get_execution_report()
    stats = report['stats']
    
    print(f"\nTotal Tasks: {stats['total_tasks']}")
    print(f"Completed: {stats['completed']}")
    print(f"Failed: {stats['failed']}")
    print(f"Total Time: {stats['total_time']:.2f}s")
    print(f"Success Rate: {stats['completed']/stats['total_tasks']*100:.1f}%")


if __name__ == "__main__":
    asyncio.run(example_4week_plan())
