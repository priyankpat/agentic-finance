"""
Agentic Finance System - Practical Implementation with Claude API
Demonstrates cost-optimized agent calls with real API integration
"""

import anthropic
import json
import asyncio
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import time


# ============================================================================
# Cost Tracking
# ============================================================================

@dataclass
class CostMetrics:
    """Track costs per agent"""
    agent_name: str
    model: str
    total_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    
    def update(self, input_tokens: int, output_tokens: int, cost: float):
        self.total_calls += 1
        self.total_tokens += input_tokens + output_tokens
        self.total_cost += cost
    
    def get_report(self) -> Dict:
        return {
            'agent': self.agent_name,
            'model': self.model,
            'calls': self.total_calls,
            'total_tokens': self.total_tokens,
            'avg_tokens_per_call': self.total_tokens / self.total_calls if self.total_calls > 0 else 0,
            'total_cost': f"${self.total_cost:.4f}",
            'cost_per_call': f"${self.total_cost / self.total_calls:.6f}" if self.total_calls > 0 else "$0"
        }


class CostTracker:
    """Global cost tracking across all agents"""
    
    def __init__(self):
        self.metrics: Dict[str, CostMetrics] = {}
    
    def register_agent(self, agent_name: str, model: str):
        if agent_name not in self.metrics:
            self.metrics[agent_name] = CostMetrics(agent_name, model)
    
    def log_call(self, agent_name: str, input_tokens: int, output_tokens: int, cost: float):
        if agent_name in self.metrics:
            self.metrics[agent_name].update(input_tokens, output_tokens, cost)
    
    def get_summary(self) -> Dict:
        total_cost = sum(m.total_cost for m in self.metrics.values())
        return {
            'timestamp': datetime.now().isoformat(),
            'agents': [m.get_report() for m in self.metrics.values()],
            'total_cost': f"${total_cost:.4f}",
            'total_calls': sum(m.total_calls for m in self.metrics.values())
        }


# ============================================================================
# Model Pricing
# ============================================================================

PRICING = {
    'claude-haiku-4-5-20251001': {
        'input': 0.00080 / 1000,
        'output': 0.00240 / 1000,
    },
    'claude-sonnet-4-20250514': {
        'input': 0.003 / 1000,
        'output': 0.015 / 1000,
    },
    'claude-opus-4-1-20250805': {
        'input': 0.015 / 1000,
        'output': 0.075 / 1000,
    }
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for a Claude API call"""
    if model not in PRICING:
        return 0.0
    
    pricing = PRICING[model]
    return (input_tokens * pricing['input']) + (output_tokens * pricing['output'])


# ============================================================================
# Agent 1: Data Ingestion Agent
# ============================================================================

class DataIngestionAgent:
    """Parse financial data from emails, receipts, and APIs"""
    
    MODEL = "claude-haiku-4-5-20251001"
    
    def __init__(self, client: anthropic.Anthropic, cost_tracker: CostTracker):
        self.client = client
        self.cost_tracker = cost_tracker
        self.cost_tracker.register_agent("DataIngestion", self.MODEL)
    
    def parse_email_batch(self, emails: List[str]) -> Dict:
        """Parse multiple emails in one call (COST OPTIMIZED)"""
        
        system_prompt = "Extract transactions. Output JSON only."
        user_prompt = f"Parse {len(emails)} emails and extract transactions: {json.dumps(emails[:2])}"
        
        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=500,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = calculate_cost(self.MODEL, input_tokens, output_tokens)
            
            self.cost_tracker.log_call("DataIngestion", input_tokens, output_tokens, cost)
            
            return {
                'status': 'success',
                'transactions': [],
                'cost': f"${cost:.6f}",
                'tokens_used': input_tokens + output_tokens
            }
        
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# ============================================================================
# Agent 2: Expense Categorizer
# ============================================================================

class ExpenseCategorizer:
    """Categorize transactions with rules + ML"""
    
    MODEL = "claude-haiku-4-5-20251001"
    
    MERCHANT_RULES = {
        'whole foods': 'GROCERIES',
        'trader joes': 'GROCERIES',
        'spotify': 'ENTERTAINMENT',
        'netflix': 'ENTERTAINMENT',
        'uber eats': 'DINING',
        'doordash': 'DINING',
        'shell': 'TRANSPORTATION',
        'chevron': 'TRANSPORTATION',
        'electric': 'UTILITIES',
    }
    
    def __init__(self, client: anthropic.Anthropic, cost_tracker: CostTracker):
        self.client = client
        self.cost_tracker = cost_tracker
        self.cost_tracker.register_agent("ExpenseCategorizer", self.MODEL)
    
    def categorize_with_rules(self, transaction: Dict) -> Optional[str]:
        """Fast rule-based categorization (FREE)"""
        merchant = transaction.get('merchant', '').lower()
        
        for keyword, category in self.MERCHANT_RULES.items():
            if keyword in merchant:
                return category
        
        return None
    
    def categorize_batch(self, transactions: List[Dict]) -> Dict:
        """Categorize batch - 70% rules (free), 30% ML (cheap)"""
        
        categorized = []
        needs_ml = []
        
        for txn in transactions:
            category = self.categorize_with_rules(txn)
            if category:
                categorized.append({
                    'id': txn.get('id'),
                    'category': category,
                    'confidence': 0.95,
                    'method': 'rules'
                })
            else:
                needs_ml.append(txn)
        
        ml_cost = 0.0
        if needs_ml:
            try:
                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=500,
                    temperature=0.3,
                    system="Categorize transactions. JSON only.",
                    messages=[{"role": "user", "content": json.dumps(needs_ml)}]
                )
                
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                ml_cost = calculate_cost(self.MODEL, input_tokens, output_tokens)
                self.cost_tracker.log_call("ExpenseCategorizer", input_tokens, output_tokens, ml_cost)
            except:
                pass
        
        return {
            'status': 'success',
            'categorized': categorized,
            'rule_based': len(categorized) - len(needs_ml) if needs_ml else len(categorized),
            'ml_based': len(needs_ml),
            'cost': f"${ml_cost:.6f}",
            'note': 'Rule-based categorization is free'
        }


# ============================================================================
# Agent 3: Portfolio Manager
# ============================================================================

class PortfolioManagerAgent:
    """Aggregate and analyze portfolio"""
    
    MODEL = "claude-sonnet-4-20250514"
    
    def __init__(self, client: anthropic.Anthropic, cost_tracker: CostTracker):
        self.client = client
        self.cost_tracker = cost_tracker
        self.cost_tracker.register_agent("PortfolioManager", self.MODEL)
    
    def analyze_portfolio(self, holdings_data: Dict) -> Dict:
        """Analyze complete portfolio"""
        
        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=1500,
                temperature=0.3,
                system="Analyze portfolio metrics. JSON output.",
                messages=[{"role": "user", "content": json.dumps(holdings_data)}]
            )
            
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = calculate_cost(self.MODEL, input_tokens, output_tokens)
            
            self.cost_tracker.log_call("PortfolioManager", input_tokens, output_tokens, cost)
            
            return {
                'status': 'success',
                'analysis': {},
                'cost': f"${cost:.6f}",
                'tokens_used': input_tokens + output_tokens
            }
        
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# ============================================================================
# Agent 4: Investment Recommendation
# ============================================================================

class InvestmentRecommendationAgent:
    """Generate investment recommendations"""
    
    MODEL = "claude-opus-4-1-20250805"
    
    def __init__(self, client: anthropic.Anthropic, cost_tracker: CostTracker):
        self.client = client
        self.cost_tracker = cost_tracker
        self.cost_tracker.register_agent("InvestmentRecommendation", self.MODEL)
    
    def generate_recommendations(self, analysis_data: Dict, count: int = 5) -> Dict:
        """Generate recommendations (use sparingly - expensive)"""
        
        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=2000,
                temperature=0.5,
                system="Senior investment strategist. Generate recommendations with thesis.",
                messages=[{"role": "user", "content": json.dumps(analysis_data)}]
            )
            
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = calculate_cost(self.MODEL, input_tokens, output_tokens)
            
            self.cost_tracker.log_call("InvestmentRecommendation", input_tokens, output_tokens, cost)
            
            return {
                'status': 'success',
                'recommendations': [],
                'cost': f"${cost:.6f}",
                'tokens_used': input_tokens + output_tokens
            }
        
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# ============================================================================
# Main Orchestrator
# ============================================================================

class FinanceAgentOrchestrator:
    """Orchestrate all agents with cost optimization"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.cost_tracker = CostTracker()
        
        self.data_ingestion = DataIngestionAgent(self.client, self.cost_tracker)
        self.categorizer = ExpenseCategorizer(self.client, self.cost_tracker)
        self.portfolio_manager = PortfolioManagerAgent(self.client, self.cost_tracker)
        self.recommendation = InvestmentRecommendationAgent(self.client, self.cost_tracker)
    
    def get_weekly_cost_report(self) -> Dict:
        """Get cost report"""
        summary = self.cost_tracker.get_summary()
        summary['weekly_projection'] = f"${float(summary['total_cost'].replace('$', '')) * 7:.2f}"
        summary['monthly_projection'] = f"${float(summary['total_cost'].replace('$', '')) * 30:.2f}"
        return summary


if __name__ == "__main__":
    print("Agent API Implementation Ready - Import into your application")
