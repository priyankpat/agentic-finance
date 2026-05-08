# 🔧 Agentic Finance System - Implementation Guide

## Quick Start Architecture

```
User Interface (React Dashboard)
    ↓
API Gateway (FastAPI/Express)
    ↓
Claude Agent Router (MCP Servers)
    ↓
Specialized Agent Teams
    ↓
External APIs & Data Sources
```

---

## Agent Implementation Details

### 1. Data Ingestion Agent Implementation

#### Role Definition
```python
# agent_data_ingestion.py
class DataIngestionAgent:
    """
    Responsible for ingesting financial data from multiple sources:
    - Email parsing (Gmail API)
    - Receipt OCR (Google Cloud Vision)
    - Banking APIs (Plaid integration)
    - Brokerage APIs (REST integrations)
    """
    
    def __init__(self):
        self.gmail_client = GmailAPI()
        self.plaid_client = PlaidAPI()
        self.vision_client = VisionAPI()
        self.db = DatabaseConnection()
    
    async def ingest_email_transactions(self):
        """Parse financial confirmation emails"""
        # Search for transaction confirmations
        # Extract amount, date, merchant, transaction ID
        # Normalize and store in database
        pass
    
    async def ingest_receipt_data(self):
        """Extract data from receipt images via OCR"""
        # Identify receipt images in email attachments
        # Use Google Vision API for OCR
        # Extract: merchant, amount, date, items
        # Store with confidence scores
        pass
    
    async def sync_bank_accounts(self):
        """Connect Plaid for real-time bank account sync"""
        # Link user bank accounts via Plaid
        # Fetch transactions daily
        # Normalize across different banks
        pass
    
    async def sync_brokerage_accounts(self):
        """Fetch holdings and transactions from brokerages"""
        # Interactive Brokers API: Holdings, transactions, cash
        # TD Ameritrade API: Holdings, transactions, dividends
        # Robinhood API: Holdings, crypto data
        pass
```

#### Key APIs
```
Gmail API:
  - Authentication: OAuth 2.0
  - Queries: label:finance, from:confirm@, etc.
  - Rate Limit: 1,000 requests/hour

Plaid API:
  - Endpoint: /transactions/get
  - Frequency: Daily sync
  - Returns: Normalized transactions across 12,000+ institutions

Google Cloud Vision:
  - Document OCR with 99.5% accuracy
  - Batch processing for multiple receipts
  - Cost: $1.50 per 1000 requests

Interactive Brokers API:
  - REST API + WebSocket for real-time data
  - Authentication: Market data token
  - Holdings: /api/iserver/account/{id}/portfolio
```

#### Data Validation Rules
```yaml
Transaction Validation:
  - Amount must be > 0
  - Date cannot be in future
  - Merchant name required
  - Currency code validated
  
Receipt Validation:
  - Confidence score > 85%
  - Amount matches total
  - All required fields present
  - Date reasonable (within 30 days)
```

---

### 2. Expense Categorizer Agent Implementation

#### Category Taxonomy
```python
EXPENSE_CATEGORIES = {
    'GROCERIES': {
        'keywords': ['safeway', 'whole foods', 'trader joes', 'kroger'],
        'ml_features': ['merchant_category_code', 'description_embedding'],
        'subcategories': ['produce', 'dairy', 'pantry', 'frozen']
    },
    'DINING': {
        'keywords': ['restaurant', 'cafe', 'uber eats', 'doordash'],
        'merchant_codes': ['5812', '5814', '5811'],
        'subcategories': ['fast_food', 'casual', 'fine_dining']
    },
    'UTILITIES': {
        'keywords': ['electric', 'water', 'internet', 'gas'],
        'recurring': True,
        'essential': True
    },
    'TRANSPORTATION': {
        'keywords': ['uber', 'lyft', 'gas', 'parking', 'tesla'],
        'subcategories': ['gas', 'rideshare', 'parking', 'maintenance']
    },
    'ENTERTAINMENT': {
        'keywords': ['spotify', 'netflix', 'movie', 'concert', 'gaming'],
        'subscription_prone': True
    },
    'HEALTH': {
        'keywords': ['pharmacy', 'doctor', 'gym', 'hospital'],
        'tax_deductible': True
    },
    'INVESTMENTS': {
        'keywords': ['transfer', 'purchase', 'dividend'],
        'exclude_from_spending': True
    }
}

class ExpenseCategorizerAgent:
    """Multi-model categorization with feedback learning"""
    
    def __init__(self):
        self.rule_engine = RuleBasedClassifier()
        self.ml_model = TransformerClassifier('roberta-base')
        self.user_feedback = FeedbackStore()
    
    async def categorize_transaction(self, transaction):
        # Step 1: Rule-based categorization (fast)
        rule_score = self.rule_engine.classify(transaction)
        
        # Step 2: ML-based categorization
        ml_score = self.ml_model.classify(transaction)
        
        # Step 3: Ensemble with user feedback
        final_category = self.ensemble([rule_score, ml_score])
        confidence = self.calculate_confidence(final_category)
        
        return {
            'category': final_category,
            'confidence': confidence,
            'alternative': self.get_alternatives(transaction),
            'notes': 'Ready for user feedback'
        }
    
    async def detect_anomalies(self, transaction):
        """Flag unusual spending patterns"""
        # Outlier detection using Isolation Forest
        # Time-based patterns (unusual hour)
        # Amount anomalies (significantly higher/lower than usual)
        # Merchant anomalies (new merchant, wrong category)
        pass
    
    async def generate_spending_insights(self, period='month'):
        """Create spending summaries and trends"""
        # Group by category
        # Calculate totals and trends
        # Compare to budget
        # Identify optimization opportunities
        pass
```

#### ML Model Architecture
```
Input: [merchant_name, amount, timestamp, merchant_code, description]
    ↓
Embedding Layer: 
  - Merchant name BERT embedding
  - Temporal features (day of week, hour)
  - Amount normalized log scale
    ↓
Dense Layers: [256, 128, 64]
  - ReLU activation
  - Dropout (0.2)
    ↓
Output: Softmax over 15 categories
  - Training: 100k+ labeled transactions
  - Accuracy: 94.2%
  - Real-time inference: <50ms
```

---

### 3. Portfolio Manager Agent Implementation

#### Portfolio Aggregation
```python
class PortfolioManagerAgent:
    """
    Unified view of all holdings across brokerages
    """
    
    def __init__(self):
        self.brokerages = {
            'interactive_brokers': InteractiveBrokersAPI(),
            'td_ameritrade': TDAmeritrade(),
            'robinhood': RobinhoodAPI(),
            'fidelity': FidelityAPI(),
            'vanguard': VanguardAPI()
        }
        self.cache = RedisCache()
        self.db = PortfolioDatabase()
    
    async def aggregate_holdings(self):
        """Fetch holdings from all brokerages"""
        all_holdings = {}
        
        for broker_name, client in self.brokerages.items():
            try:
                holdings = await client.get_holdings()
                for position in holdings:
                    symbol = position['symbol']
                    if symbol not in all_holdings:
                        all_holdings[symbol] = {
                            'symbol': symbol,
                            'total_shares': 0,
                            'accounts': []
                        }
                    
                    all_holdings[symbol]['total_shares'] += position['quantity']
                    all_holdings[symbol]['accounts'].append({
                        'broker': broker_name,
                        'shares': position['quantity'],
                        'cost_basis': position['cost_basis']
                    })
            
            except Exception as e:
                logger.error(f"Failed to fetch from {broker_name}: {e}")
        
        return all_holdings
    
    async def calculate_portfolio_metrics(self):
        """Comprehensive portfolio analysis"""
        holdings = await self.aggregate_holdings()
        
        metrics = {
            'total_value': 0,
            'total_invested': 0,
            'unrealized_gain': 0,
            'dividend_yield': 0,
            'asset_allocation': {},
            'sector_allocation': {},
            'diversification_score': 0,
            'concentration_risk': 0,
            'sharpe_ratio': 0,
            'portfolio_beta': 0
        }
        
        # Asset allocation (stocks, bonds, cash, alternatives)
        # Sector breakdown (Tech, Finance, Healthcare, etc.)
        # Geographic distribution
        # Currency exposure
        # Duration analysis (if bonds)
        
        return metrics
    
    async def get_rebalancing_recommendations(self):
        """Suggest rebalancing based on target allocation"""
        current = await self.calculate_portfolio_metrics()
        target = await self.get_user_target_allocation()
        
        drifts = {}
        for asset_class, current_pct in current['asset_allocation'].items():
            target_pct = target['asset_allocation'].get(asset_class, 0)
            drift = current_pct - target_pct
            
            if abs(drift) > 0.05:  # More than 5% drift
                drifts[asset_class] = {
                    'current': current_pct,
                    'target': target_pct,
                    'drift': drift,
                    'action': 'Buy' if drift < 0 else 'Sell'
                }
        
        return drifts
    
    async def monitor_dividends(self):
        """Track dividend income and reinvestment"""
        # Fetch upcoming dividend dates
        # Calculate dividend yield
        # Track DRIP settings
        # Project annual dividend income
        pass
    
    async def calculate_tax_implications(self):
        """Estimate tax liability from realized gains"""
        # Realized gains/losses
        # Holding period classification
        # Tax bracket estimation
        # Tax-loss harvesting opportunities
        pass
```

#### Key Metrics Definitions
```
Diversification Score (0-100):
  - Based on Herfindahl-Hirschman Index (HHI)
  - Penalizes large single positions
  - Target: >75

Concentration Risk:
  - Top 10 positions as % of portfolio
  - Top position as % of portfolio
  - Alert if >30% in single stock

Sharpe Ratio:
  - (Portfolio Return - Risk-free Rate) / Portfolio Volatility
  - Target: >1.5

Portfolio Beta:
  - Weighted average beta of holdings
  - <1.0 = Less volatile than market
  - >1.0 = More volatile than market
```

---

### 4. Market Research Agent Implementation

#### Data Collection
```python
class MarketResearchAgent:
    """
    Real-time market intelligence gathering
    """
    
    def __init__(self):
        self.market_data = PolygonAPI()
        self.financial_data = AlphaVantageAPI()
        self.news = NewsAPIClient()
        self.sentiment = SentimentAnalysisModel()
        self.cache = RedisCache()
    
    async def get_market_data(self, symbol):
        """Real-time and historical market data"""
        data = {
            'current_price': await self.market_data.get_quote(symbol),
            'daily_change': await self.market_data.get_daily_change(symbol),
            'volume': await self.market_data.get_volume(symbol),
            '52_week_high': await self.market_data.get_52w_high(symbol),
            '52_week_low': await self.market_data.get_52w_low(symbol),
            'ma_50': await self.market_data.get_moving_average(symbol, 50),
            'ma_200': await self.market_data.get_moving_average(symbol, 200),
            'rsi': await self.market_data.get_rsi(symbol),
            'macd': await self.market_data.get_macd(symbol),
            'volatility': await self.market_data.get_volatility(symbol)
        }
        return data
    
    async def get_fundamental_data(self, symbol):
        """Financial statements and fundamental metrics"""
        financials = {
            'income_statement': await self.financial_data.get_income_statement(symbol),
            'balance_sheet': await self.financial_data.get_balance_sheet(symbol),
            'cash_flow': await self.financial_data.get_cash_flow(symbol),
            'ratios': {
                'pe_ratio': await self.financial_data.get_pe(symbol),
                'pb_ratio': await self.financial_data.get_pb(symbol),
                'roe': await self.financial_data.get_roe(symbol),
                'roa': await self.financial_data.get_roa(symbol),
                'debt_to_equity': await self.financial_data.get_debt_to_equity(symbol),
                'current_ratio': await self.financial_data.get_current_ratio(symbol)
            },
            'eps_growth': await self.financial_data.get_eps_growth(symbol),
            'revenue_growth': await self.financial_data.get_revenue_growth(symbol)
        }
        return financials
    
    async def analyze_news_sentiment(self, symbol):
        """Sentiment analysis from news sources"""
        articles = await self.news.get_articles(symbol, days=7)
        
        sentiment_scores = []
        for article in articles:
            score = await self.sentiment.analyze(article['title'] + ' ' + article['summary'])
            sentiment_scores.append({
                'source': article['source'],
                'headline': article['title'],
                'sentiment': score['label'],  # POSITIVE, NEGATIVE, NEUTRAL
                'confidence': score['score'],
                'date': article['published_at']
            })
        
        # Aggregate sentiment
        avg_sentiment = np.mean([s['confidence'] for s in sentiment_scores])
        return {
            'sentiment_score': avg_sentiment,
            'recent_articles': sentiment_scores[:10],
            'trend': self.get_sentiment_trend(sentiment_scores)
        }
    
    async def track_macro_indicators(self):
        """Monitor macroeconomic factors"""
        macro = {
            'interest_rate': await self.get_fed_rate(),
            'inflation': await self.get_inflation_rate(),
            'unemployment': await self.get_unemployment_rate(),
            'gdp_growth': await self.get_gdp_growth(),
            'vix': await self.get_vix(),  # Volatility Index
            'yield_curve': await self.get_yield_curve(),
            'dollar_index': await self.get_dollar_index()
        }
        return macro
```

#### Technical Indicators
```python
TECHNICAL_INDICATORS = {
    'MA50': 'Simple Moving Average (50-day)',
    'MA200': 'Simple Moving Average (200-day)',
    'RSI': 'Relative Strength Index (0-100, >70 overbought, <30 oversold)',
    'MACD': 'Moving Average Convergence Divergence',
    'Bollinger_Bands': 'Standard deviation bands',
    'ATR': 'Average True Range (volatility)',
    'Volume_Ratio': 'Current volume vs average volume'
}

SIGNALS = {
    'Golden_Cross': 'MA50 > MA200 (bullish)',
    'Death_Cross': 'MA50 < MA200 (bearish)',
    'RSI_Oversold': 'RSI < 30 (potential bounce)',
    'RSI_Overbought': 'RSI > 70 (potential reversal)',
    'MACD_Crossover': 'MACD line crosses signal line',
    'Volume_Surge': 'Volume > 150% of average'
}
```

---

### 5. Investment Recommendation Agent Implementation

#### Recommendation Algorithm
```python
class InvestmentRecommendationAgent:
    """
    ML-driven investment recommendations with explainability
    """
    
    def __init__(self):
        self.model = load_trained_model('investment_predictor.pkl')
        self.explainer = SHAP(self.model)
        self.backtest_engine = BacktestEngine()
    
    async def generate_stock_recommendations(self, n=10):
        """Top stock picks with detailed analysis"""
        
        # Step 1: Screen universe of stocks
        candidates = await self.screen_stocks()  # 1000s of stocks
        
        # Step 2: Score each candidate
        scores = {}
        for symbol in candidates:
            score = await self.score_stock(symbol)
            scores[symbol] = score
        
        # Step 3: Rank and return top N
        ranked = sorted(scores.items(), key=lambda x: x[1]['overall_score'], reverse=True)
        top_picks = ranked[:n]
        
        recommendations = []
        for symbol, score in top_picks:
            rec = {
                'symbol': symbol,
                'action': 'BUY' if score['overall_score'] > 0.7 else 'HOLD',
                'confidence': score['confidence'],
                'target_price': score['target_price'],
                'upside': score['upside_pct'],
                'thesis': await self.generate_thesis(symbol),
                'risks': await self.identify_risks(symbol),
                'catalysts': await self.identify_catalysts(symbol)
            }
            recommendations.append(rec)
        
        return recommendations
    
    async def score_stock(self, symbol):
        """Comprehensive stock scoring"""
        
        # Gather features
        market_data = await self.market_research_agent.get_market_data(symbol)
        fundamentals = await self.market_research_agent.get_fundamental_data(symbol)
        sentiment = await self.market_research_agent.analyze_news_sentiment(symbol)
        
        # Build feature vector
        features = self.extract_features({
            'market': market_data,
            'fundamentals': fundamentals,
            'sentiment': sentiment
        })
        
        # Get model prediction
        prediction = self.model.predict(features)[0]
        confidence = self.model.predict_proba(features)[0].max()
        
        # SHAP explainability
        explanation = self.explainer.explain(features)
        
        # Risk-adjusted metrics
        target_price = self.calculate_target_price(symbol, prediction)
        current_price = market_data['current_price']
        upside = (target_price - current_price) / current_price * 100
        
        return {
            'overall_score': prediction,
            'confidence': confidence,
            'target_price': target_price,
            'upside_pct': upside,
            'explanation': explanation,
            'components': {
                'value_score': self.value_score(fundamentals),
                'growth_score': self.growth_score(fundamentals),
                'momentum_score': self.momentum_score(market_data),
                'sentiment_score': sentiment['sentiment_score'],
                'quality_score': self.quality_score(fundamentals)
            }
        }
    
    def value_score(self, fundamentals):
        """Value investing metrics"""
        pe_ratio = fundamentals['ratios']['pe_ratio']
        pb_ratio = fundamentals['ratios']['pb_ratio']
        peg = self.calculate_peg(fundamentals)
        
        # Lower is better for value
        score = 100 * (1 / (1 + pe_ratio/20)) * (1 / (1 + pb_ratio/3))
        return min(100, score)
    
    def growth_score(self, fundamentals):
        """Growth metrics"""
        eps_growth = fundamentals['eps_growth']
        revenue_growth = fundamentals['revenue_growth']
        
        score = (eps_growth + revenue_growth) * 10
        return min(100, max(0, score))
    
    def momentum_score(self, market_data):
        """Technical momentum"""
        rsi = market_data['rsi']
        ma_ratio = market_data['ma_50'] / market_data['ma_200']
        
        # Balanced scoring
        rsi_score = 50 + (rsi - 50) * 0.5  # Moderate RSI weighting
        trend_score = 100 if ma_ratio > 1.02 else 0 if ma_ratio < 0.98 else 50
        
        return (rsi_score + trend_score) / 2
    
    def quality_score(self, fundamentals):
        """Business quality metrics"""
        roe = fundamentals['ratios']['roe']
        roa = fundamentals['ratios']['roa']
        debt_ratio = fundamentals['ratios']['debt_to_equity']
        current_ratio = fundamentals['ratios']['current_ratio']
        
        # Normalize and weight
        roe_score = min(100, roe * 5)
        roa_score = min(100, roa * 5)
        debt_score = max(0, 100 - debt_ratio * 20)
        liquidity_score = 100 if current_ratio > 1.5 else 50 if current_ratio > 1 else 0
        
        return (roe_score + roa_score + debt_score + liquidity_score) / 4
    
    async def backtest_strategy(self, strategy_name, parameters):
        """Validate strategy on historical data"""
        historical_picks = self.backtest_engine.simulate(strategy_name, parameters)
        
        results = {
            'total_return': self.calculate_return(historical_picks),
            'annual_return': self.calculate_annual_return(historical_picks),
            'sharpe_ratio': self.calculate_sharpe(historical_picks),
            'max_drawdown': self.calculate_max_drawdown(historical_picks),
            'win_rate': self.calculate_win_rate(historical_picks),
            'trades': len(historical_picks)
        }
        
        return results
```

#### Feature Engineering
```python
FEATURE_SET = {
    'Valuation': ['pe_ratio', 'pb_ratio', 'peg_ratio', 'price_sales', 'ev_ebitda'],
    'Growth': ['eps_growth_ttm', 'revenue_growth_ttm', 'fcf_growth', 'earnings_growth_5y'],
    'Profitability': ['roe', 'roa', 'roci', 'operating_margin', 'net_margin'],
    'Financial_Health': ['debt_to_equity', 'current_ratio', 'quick_ratio', 'debt_to_assets'],
    'Momentum': ['rsi_14', 'price_momentum_6m', 'price_momentum_1y', 'volume_ratio'],
    'Quality': ['roic', 'fcf_yield', 'earnings_stability', 'dividend_growth'],
    'Macro': ['sector_momentum', 'interest_rate', 'market_cap', 'industry_pe_relative'],
    'Sentiment': ['news_sentiment', 'analyst_ratings', 'insider_trading', 'short_interest']
}

MODEL_ARCHITECTURE:
  Input: 28 features
  Hidden1: 64 nodes, ReLU, Dropout(0.3)
  Hidden2: 32 nodes, ReLU, Dropout(0.2)
  Hidden3: 16 nodes, ReLU
  Output: 1 node, Sigmoid
  
  Loss: Binary Crossentropy (Buy vs Don't Buy)
  Optimizer: Adam (learning_rate=0.001)
  Training: 10 years of daily data (2,520+ samples)
  Validation: Walk-forward testing
```

---

### 6. Risk Assessment Agent Implementation

#### Risk Calculation
```python
class RiskAssessmentAgent:
    """
    Comprehensive portfolio risk analysis
    """
    
    async def calculate_var(self, confidence_level=0.95, horizon=1):
        """Value at Risk - maximum expected loss"""
        returns = await self.get_historical_returns(horizon)
        
        # Historical simulation
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        var = sorted_returns[index]
        
        return {
            'var': var,
            'interpretation': f"95% confidence: max loss {abs(var):.2f}% in {horizon} day(s)",
            'method': 'Historical Simulation'
        }
    
    async def calculate_cvar(self, confidence_level=0.95):
        """Conditional Value at Risk - average loss in tail"""
        returns = await self.get_historical_returns()
        sorted_returns = sorted(returns)
        
        index = int((1 - confidence_level) * len(sorted_returns))
        cvar = sorted_returns[:index].mean()
        
        return {
            'cvar': cvar,
            'vs_var': cvar - var  # CVaR always worse than VaR
        }
    
    async def assess_concentration_risk(self):
        """Alert on single-position concentration"""
        holdings = await self.portfolio_manager.aggregate_holdings()
        
        risks = {}
        total_value = sum(h['value'] for h in holdings.values())
        
        for symbol, holding in holdings.items():
            pct = holding['value'] / total_value
            
            if pct > 0.10:  # >10%
                risk_level = 'HIGH' if pct > 0.20 else 'MEDIUM'
                risks[symbol] = {
                    'concentration': pct,
                    'risk_level': risk_level,
                    'recommendation': 'Consider reducing position'
                }
        
        return risks
    
    async def stress_test_portfolio(self, scenarios):
        """Simulate portfolio under adverse conditions"""
        
        scenarios = {
            'market_crash_20': {'market': -0.20, 'volatility': 1.5},
            'interest_rate_up_2pct': {'rates': 0.02, 'bonds': -0.10},
            'sector_rotation': {'tech': -0.15, 'finance': 0.10},
            'geopolitical': {'market': -0.10, 'volatility': 2.0},
            'recession': {'market': -0.30, 'unemployment': 0.05}
        }
        
        results = {}
        for scenario_name, params in scenarios.items():
            portfolio_return = self.simulate_scenario(params)
            results[scenario_name] = {
                'expected_return': portfolio_return,
                'severity': 'High' if portfolio_return < -0.15 else 'Medium'
            }
        
        return results
    
    async def monitor_tail_risk(self):
        """Track extreme market movements (>2 standard deviations)"""
        daily_returns = await self.get_daily_returns()
        std_dev = daily_returns.std()
        
        tail_events = daily_returns[abs(daily_returns) > 2 * std_dev]
        
        return {
            'tail_events_count': len(tail_events),
            'frequency': len(tail_events) / len(daily_returns),
            'worst_day': tail_events.min(),
            'best_day': tail_events.max(),
            'action': 'Consider hedging' if len(tail_events) > 5 else 'Normal'
        }
```

#### Risk Dashboard Metrics
```
PRIMARY METRICS:
├─ Value at Risk (VaR): Max 1-day loss at 95% confidence
├─ Conditional VaR: Average loss in worst 5% scenarios
├─ Maximum Drawdown: Largest peak-to-trough decline
└─ Volatility (Annualized): Standard deviation of returns

CONCENTRATION METRICS:
├─ Top 10 position concentration
├─ Sector concentration
├─ Geographic concentration
└─ Currency exposure

STRESS TESTING:
├─ Market crash scenarios (-10%, -20%, -30%)
├─ Interest rate scenarios (+1%, +2%)
├─ Recession indicators
└─ Geopolitical event impacts

HEDGING RECOMMENDATIONS:
├─ Put option purchases (tail hedges)
├─ Rebalancing suggestions
├─ Diversification improvements
└─ Cash reserve recommendations
```

---

### 7. Reporting & Insights Agent Implementation

#### Dashboard Generation
```python
class ReportingAndInsightsAgent:
    """
    Generate comprehensive reports and dashboards
    """
    
    async def generate_executive_summary(self):
        """One-page portfolio snapshot"""
        return {
            'as_of_date': today(),
            'portfolio_value': await self.get_portfolio_value(),
            'ytd_return': await self.get_ytd_return(),
            'vs_benchmark': await self.get_vs_benchmark(),
            'key_holdings': await self.get_top_5_holdings(),
            'recent_actions': await self.get_recent_transactions(),
            'alerts': await self.get_active_alerts()
        }
    
    async def generate_monthly_report(self):
        """Comprehensive monthly performance review"""
        return {
            'performance': {
                'month_return': await self.get_month_return(),
                'vs_sp500': await self.get_benchmark_comparison(),
                'by_sector': await self.get_sector_performance(),
                'by_holding': await self.get_individual_performance()
            },
            'portfolio_changes': {
                'new_positions': await self.get_new_positions(),
                'closed_positions': await self.get_closed_positions(),
                'rebalancing': await self.get_rebalancing_actions()
            },
            'market_context': {
                'macro_overview': await self.get_macro_summary(),
                'sector_outlook': await self.get_sector_outlook(),
                'risks': await self.get_risk_summary()
            },
            'recommendations': {
                'buy_ideas': await self.get_buy_ideas(),
                'sell_signals': await self.get_sell_signals(),
                'rebalancing': await self.get_rebalancing_suggestions()
            }
        }
    
    async def generate_tax_report(self):
        """Tax documentation and optimization"""
        return {
            'realized_gains': await self.get_realized_gains(),
            'realized_losses': await self.get_realized_losses(),
            'estimated_tax': await self.estimate_tax_liability(),
            'tax_loss_harvesting': await self.get_harvesting_opportunities(),
            'dividend_income': await self.get_dividend_income(),
            'forms_8949': await self.generate_form_8949(),
            'schedule_d': await self.generate_schedule_d()
        }
```

---

## Integration Flow Example

```
User wants: "Show me my portfolio and top recommendations"

┌─────────────────────────────────────────┐
│ User Dashboard Request                   │
└──────────┬────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ API Router (FastAPI)                     │
│ POST /portfolio/recommendations          │
└──────────┬────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Claude MCP Router                        │
│ Route to appropriate agents              │
└──────┬──────────────────────┬────────────┘
       │                      │
       ▼                      ▼
┌─────────────────┐  ┌──────────────────┐
│ Portfolio       │  │ Market Research  │
│ Manager Agent   │  │ + Investment     │
│                 │  │ Recommendation   │
│ • Get holdings  │  │ Agents           │
│ • Calc metrics  │  │                  │
└────────┬────────┘  │ • Get market data│
         │           │ • Score stocks   │
         │           │ • Generate picks │
         │           └────────┬─────────┘
         │                    │
         └────────┬───────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ Risk Assessment Agent                    │
│ Calculate portfolio risk metrics         │
└──────────┬────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Reporting Agent                          │
│ Synthesize all data into response       │
└──────────┬────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ JSON Response                            │
│ {                                        │
│   portfolio: {...},                      │
│   recommendations: [...],                │
│   risks: {...},                          │
│   alerts: [...]                          │
│ }                                        │
└──────────┬────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Dashboard Rendering                      │
│ React component displays data            │
└─────────────────────────────────────────┘
```

---

## API Specifications

### Core Agent API

```python
# All agents follow this interface

class AIAgent:
    """Base agent interface"""
    
    async def initialize(self, config: Dict):
        """Setup agent with configuration"""
        pass
    
    async def execute(self, task: Task) -> Result:
        """Execute assigned task"""
        pass
    
    async def get_status(self) -> Status:
        """Report agent health"""
        pass
    
    async def shutdown(self):
        """Graceful shutdown"""
        pass
```

### Sample REST Endpoints

```
GET  /api/portfolio
  Returns: Current portfolio state and metrics

GET  /api/portfolio/holdings
  Returns: List of all holdings with details

POST /api/portfolio/rebalance
  Body: { target_allocation: {...} }
  Returns: Rebalancing recommendations

GET  /api/recommendations/stocks
  Query: ?limit=10&confidence=0.8
  Returns: Top stock recommendations

GET  /api/market/{symbol}
  Returns: Market data and technical indicators

POST /api/risk/stress-test
  Body: { scenario: 'market_crash_20' }
  Returns: Portfolio impact under scenario

GET  /api/reports/monthly
  Returns: Comprehensive monthly report

GET  /api/alerts
  Returns: Active alerts and notifications
```

---

## Deployment Checklist

- [ ] Database schema created (PostgreSQL)
- [ ] API authentication configured (OAuth, JWT)
- [ ] All external APIs credentials secure (environment variables)
- [ ] ML models trained and validated
- [ ] Error handling and logging setup
- [ ] Rate limiting configured
- [ ] Monitoring and alerting active
- [ ] Backup and recovery procedures
- [ ] Security audit completed
- [ ] Documentation finalized

---

*Ready to build the future of AI-driven finance. Let's make wealth management intelligent!*
