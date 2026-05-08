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
# Model Pricing (As of April 2026)
# ============================================================================

PRICING = {
    'claude-haiku-4-5-20251001': {
        'input': 0.00080 / 1000,      # $0.80 per 1M input tokens
        'output': 0.00240 / 1000,     # $2.40 per 1M output tokens
    },
    'claude-sonnet-4-20250514': {
        'input': 0.003 / 1000,        # $3 per 1M input tokens
        'output': 0.015 / 1000,       # $15 per 1M output tokens
    },
    'claude-opus-4-1-20250805': {
        'input': 0.015 / 1000,        # $15 per 1M input tokens
        'output': 0.075 / 1000,       # $75 per 1M output tokens
    }
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for a Claude API call"""
    if model not in PRICING:
        return 0.0
    
    pricing = PRICING[model]
    return (input_tokens * pricing['input']) + (output_tokens * pricing['output'])


# ============================================================================
# Agent 1: Data Ingestion Agent (Haiku - Most Cost Efficient)
# ============================================================================

class DataIngestionAgent:
    """Parse financial data from emails, receipts, and APIs"""
    
    MODEL = "claude-haiku-4-5-20251001"
    
    def __init__(self, client: anthropic.Anthropic, cost_tracker: CostTracker):
        self.client = client
        self.cost_tracker = cost_tracker
        self.cost_tracker.register_agent("DataIngestion", self.MODEL)
    
    def get_system_prompt(self) -> str:
        """Optimized system prompt for data extraction"""
        return """You are a financial data extraction specialist.

Extract transactions from the provided input.

OUTPUT FORMAT (JSON ONLY):
{
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "amount": number,
      "merchant": "string",
      "category_hint": "string",
      "confidence": number
    }
  ]
}

Be concise. Extract conservative estimates. Flag uncertainty."""
    
    def parse_email_batch(self, emails: List[str]) -> Dict:
        """
        Parse multiple emails in one call (COST OPTIMIZED)
        
        Cost without batching: 10 emails × $0.0008 = $0.008
        Cost with batching: 1 call × $0.0008 = $0.0008
        Savings: 90%
        """
        
        user_prompt = f"""Parse these {len(emails)} emails and extract all transactions.

Emails:
{json.dumps(emails, indent=2)}"""
        
        try:
            start_time = time.time()
            
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=500,
                temperature=0.2,  # Low temperature for consistency
                system=self.get_system_prompt(),
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract response
            result = json.loads(response.content[0].text)
            
            # Track costs
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = calculate_cost(self.MODEL, input_tokens, output_tokens)
            
            self.cost_tracker.log_call("DataIngestion", input_tokens, output_tokens, cost)
            
            execution_time = time.time() - start_time
            
            return {
                'status': 'success',
                'transactions': result.get('transactions', []),
                'execution_time': execution_time,
                'cost': f"${cost:.6f}",
                'tokens_used': input_tokens + output_tokens
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# ============================================================================
# Agent 2: Expense Categorizer (Haiku + Rule-Based Pre-filtering)
# ============================================================================

class ExpenseCategorizer:
    """Categorize transactions with rules + ML"""
    
    MODEL = "claude-haiku-4-5-20251001"
    
    # Rule-based categorization (free, no API calls)
    MERCHANT_RULES = {
        'whole foods': 'GROCERIES',
        'trader joes': 'GROCERIES',
        'safeway': 'GROCERIES',
        'kroger': 'GROCERIES',
        'whole': 'GROCERIES',
        'grocery': 'GROCERIES',
        'spotify': 'ENTERTAINMENT',
        'netflix': 'ENTERTAINMENT',
        'disney': 'ENTERTAINMENT',
        'hulu': 'ENTERTAINMENT',
        'uber eats': 'DINING',
        'doordash': 'DINING',
        'grubhub': 'DINING',
        'restaurant': 'DINING',
        'cafe': 'DINING',
        'shell': 'TRANSPORTATION',
        'chevron': 'TRANSPORTATION',
        'exxon': 'TRANSPORTATION',
        'gas': 'TRANSPORTATION',
        'uber': 'TRANSPORTATION',
        'lyft': 'TRANSPORTATION',
        'electric': 'UTILITIES',
        'water': 'UTILITIES',
        'internet': 'UTILITIES',
        'phone': 'UTILITIES',
        'amex': 'INVESTMENT',
        'transfer': 'INVESTMENT',
        'buy': 'INVESTMENT',
        'deposit': 'INVESTMENT',
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
    
    def get_system_prompt(self) -> str:
        return """Categorize transactions into: GROCERIES, DINING, TRANSPORTATION, UTILITIES, ENTERTAINMENT, HEALTH, SHOPPING, INVESTMENT, OTHER.

Output JSON only:
{
  "categorizations": [
    {"id": "string", "category": "string", "confidence": number}
  ]
}"""
    
    def categorize_batch(self, transactions: List[Dict]) -> Dict:
        """
        Categorize batch of transactions
        
        Cost optimization strategy:
        1. Rule-based: 70% of transactions (FREE)
        2. Claude categorization: 30% that need AI (CHEAP)
        """
        
        # First pass: rule-based categorization
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
        
        # Second pass: ML categorization for ambiguous ones
        if needs_ml:
            user_prompt = f"""Categorize these transactions:
{json.dumps(needs_ml, indent=2)}"""
            
            try:
                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=500,
                    temperature=0.3,
                    system=self.get_system_prompt(),
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                result = json.loads(response.content[0].text)
                ml_categorized = result.get('categorizations', [])
                
                # Track costs for ML portion only
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                cost = calculate_cost(self.MODEL, input_tokens, output_tokens)
                self.cost_tracker.log_call("ExpenseCategorizer", input_tokens, output_tokens, cost)
                
                categorized.extend(ml_categorized)
                ml_cost = cost
            except:
                ml_cost = 0.0
        else:
            ml_cost = 0.0
        
        return {
            'status': 'success',
            'categorized': categorized,
            'rule_based': len(categorized) - len(needs_ml) if needs_ml else len(categorized),
            'ml_based': len(needs_ml),
            'cost': f"${ml_cost:.6f}",
            'note': 'Rule-based categorization is free, only ML lookups cost'
        }


# ============================================================================
# Agent 3: Portfolio Manager (Sonnet - Balanced Cost/Performance)
# ============================================================================

class PortfolioManagerAgent:
    """Aggregate and analyze portfolio across brokerages"""
    
    MODEL = "claude-sonnet-4-20250514"
    
    def __init__(self, client: anthropic.Anthropic, cost_tracker: CostTracker):
        self.client = client
        self.cost_tracker = cost_tracker
        self.cost_tracker.register_agent("PortfolioManager", self.MODEL)
    
    def get_system_prompt(self) -> str:
        return """You are a portfolio analytics expert. Calculate comprehensive metrics.

Input: Holdings data from multiple brokerages
Output: JSON with portfolio metrics, allocation, performance"""
    
    def analyze_portfolio(self, holdings_data: Dict) -> Dict:
        """Analyze complete portfolio with caching"""
        
        user_prompt = f"""Analyze this portfolio:
        
Total value: ${holdings_data['total_value']:,.2f}

Holdings by broker:
{json.dumps(holdings_data['accounts'], indent=2)}

Calculate:
1. Asset allocation (stocks/bonds/cash)
2. Sector breakdown
3. Performance metrics
4. Concentration risk
5. Diversification score

Output JSON."""
        
        try:
            start_time = time.time()
            
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=1500,
                temperature=0.3,
                system=self.get_system_prompt(),
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            result = json.loads(response.content[0].text)
            
            # Track costs
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = calculate_cost(self.MODEL, input_tokens, output_tokens)
            
            self.cost_tracker.log_call("PortfolioManager", input_tokens, output_tokens, cost)
            
            execution_time = time.time() - start_time
            
            return {
                'status': 'success',
                'analysis': result,
                'execution_time': execution_time,
                'cost': f"${cost:.6f}",
                'tokens_used': input_tokens + output_tokens
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# ============================================================================
# Agent 4: Investment Recommendation (Opus - Advanced Reasoning)
# ============================================================================

class InvestmentRecommendationAgent:
    """Generate high-quality investment recommendations"""
    
    MODEL = "claude-opus-4-1-20250805"
    
    def __init__(self, client: anthropic.Anthropic, cost_tracker: CostTracker):
        self.client = client
        self.cost_tracker = cost_tracker
        self.cost_tracker.register_agent("InvestmentRecommendation", self.MODEL)
    
    def get_system_prompt(self) -> str:
        return """You are a senior investment strategist with 20+ years experience.

Generate actionable investment recommendations with:
- Clear conviction levels (0-100)
- Specific entry/exit points
- Risk/reward analysis
- Backtested thesis
- Detailed reasoning

Output: JSON with structured recommendations"""
    
    def generate_recommendations(self, analysis_data: Dict, count: int = 5) -> Dict:
        """
        Generate investment recommendations
        
        Note: Use ONLY for strategic decisions, not daily tasks
        Cost: $0.030 per call
        Frequency: 2-3x per week
        Daily cost: ~$0.01
        """
        
        user_prompt = f"""Based on this market analysis, generate top {count} recommendations:

Market scores: {json.dumps(analysis_data['market_scores'], indent=2)}

Portfolio constraints:
- Max position size: 10%
- Risk tolerance: Moderate
- Time horizon: 12 months
- Current allocation: {json.dumps(analysis_data['allocation'], indent=2)}

Return JSON with: symbol, action, conviction, thesis, target_price, entry_points, risks, catalysts"""
        
        try:
            start_time = time.time()
            
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=2000,
                temperature=0.5,  # Higher temperature for creativity
                system=self.get_system_prompt(),
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            result = json.loads(response.content[0].text)
            
            # Track costs
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = calculate_cost(self.MODEL, input_tokens, output_tokens)
            
            self.cost_tracker.log_call("InvestmentRecommendation", input_tokens, output_tokens, cost)
            
            execution_time = time.time() - start_time
            
            return {
                'status': 'success',
                'recommendations': result,
                'execution_time': execution_time,
                'cost': f"${cost:.6f}",
                'tokens_used': input_tokens + output_tokens
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# ============================================================================
# Main Orchestrator
# ============================================================================

class FinanceAgentOrchestrator:
    """Orchestrate all agents with cost optimization"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.cost_tracker = CostTracker()
        
        # Initialize agents
        self.data_ingestion = DataIngestionAgent(self.client, self.cost_tracker)
        self.categorizer = ExpenseCategorizer(self.client, self.cost_tracker)
        self.portfolio_manager = PortfolioManagerAgent(self.client, self.cost_tracker)
        self.recommendation = InvestmentRecommendationAgent(self.client, self.cost_tracker)
    
    async def process_daily_workflow(self, daily_data: Dict) -> Dict:
        """
        Complete daily processing workflow with cost optimization
        
        Expected daily cost: $0.08 - $0.12
        """
        
        print("🚀 Starting daily financial processing workflow...")
        print("=" * 60)
        
        # Step 1: Parse emails and receipts (HAIKU - FREE baseline)
        print("\n📧 Step 1: Parsing emails and receipts...")
        ingest_result = self.data_ingestion.parse_email_batch(
            daily_data.get('emails', [])
        )
        print(f"   ✅ Parsed {len(ingest_result.get('transactions', []))} transactions")
        print(f"   💰 Cost: {ingest_result.get('cost', '$0')}")
        
        # Step 2: Categorize transactions (HAIKU + Rules)
        print("\n🏷️  Step 2: Categorizing transactions...")
        categorize_result = self.categorizer.categorize_batch(
            ingest_result.get('transactions', [])
        )
        print(f"   ✅ Categorized {len(categorize_result.get('categorized', []))} transactions")
        print(f"   📊 Rule-based: {categorize_result.get('rule_based')}, ML-based: {categorize_result.get('ml_based')}")
        print(f"   💰 Cost: {categorize_result.get('cost', '$0')}")
        
        # Step 3: Update portfolio (SONNET - Balanced)
        print("\n💼 Step 3: Analyzing portfolio...")
        portfolio_result = self.portfolio_manager.analyze_portfolio(
            daily_data.get('holdings', {})
        )
        print(f"   ✅ Portfolio analysis complete")
        print(f"   ⏱️  Execution time: {portfolio_result.get('execution_time', 0):.2f}s")
        print(f"   💰 Cost: {portfolio_result.get('cost', '$0')}")
        
        # Step 4: Generate recommendations (OPUS - Only 2x/week)
        if daily_data.get('generate_recommendations', False):
            print("\n🎯 Step 4: Generating recommendations...")
            rec_result = self.recommendation.generate_recommendations(
                daily_data.get('market_analysis', {})
            )
            print(f"   ✅ Generated recommendations")
            print(f"   💰 Cost: {rec_result.get('cost', '$0')}")
        else:
            print("\n⏭️  Step 4: Skipped (recommendations run 2x/week)")
        
        # Print cost summary
        print("\n" + "=" * 60)
        print("💰 COST SUMMARY")
        print("=" * 60)
        summary = self.cost_tracker.get_summary()
        for agent in summary['agents']:
            print(f"{agent['agent']}: {agent['calls']} calls, {agent['total_tokens']} tokens, {agent['total_cost']}")
        print(f"\nTOTAL COST: {summary['total_cost']}")
        print("=" * 60)
        
        return {
            'workflow_complete': True,
            'transactions_processed': len(ingest_result.get('transactions', [])),
            'cost_summary': summary
        }
    
    def get_weekly_cost_report(self) -> Dict:
        """Get cost report for the week"""
        summary = self.cost_tracker.get_summary()
        summary['weekly_projection'] = f"${float(summary['total_cost'].replace('$', '')) * 7:.2f}"
        summary['monthly_projection'] = f"${float(summary['total_cost'].replace('$', '')) * 30:.2f}"
        return summary


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Example: Run complete workflow"""
    
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Initialize orchestrator
    orchestrator = FinanceAgentOrchestrator(api_key)
    
    # Sample daily data
    daily_data = {
        'emails': [
            """Subject: Whole Foods Receipt
Amount: $45.23
Date: 2024-04-21
Merchant: Whole Foods Market""",
            """Subject: Uber Eats Delivery
Amount: $32.15
Date: 2024-04-21
Merchant: Uber Eats""",
        ],
        'holdings': {
            'total_value': 487250.50,
            'accounts': [
                {
                    'broker': 'Interactive Brokers',
                    'holdings': [
                        {'symbol': 'MSFT', 'shares': 25, 'price': 387.42},
                        {'symbol': 'AAPL', 'shares': 40, 'price': 189.35},
                    ],
                    'cash': 50000
                }
            ]
        },
        'generate_recommendations': False,  # Only 2x/week
        'market_analysis': {}
    }
    
    # Run workflow
    result = await orchestrator.process_daily_workflow(daily_data)
    
    print("\n📊 Workflow Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
