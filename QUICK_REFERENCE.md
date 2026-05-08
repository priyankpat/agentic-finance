# 🎯 Agent Quick Reference Card

## Model Selection Decision Tree

```
START: New Task
    │
    ├─ Is it simple data extraction? YES → HAIKU ($0.0008/call)
    │  └─ Email parsing, receipt OCR, basic classification
    │
    ├─ Is it complex analysis needed? YES → SONNET ($0.015/call)
    │  └─ Portfolio analysis, multi-step reasoning, synthesis
    │
    └─ Is it strategic decision? YES → OPUS ($0.030/call)
       └─ Recommendations, complex optimization, high stakes
```

---

## Cost-Effective Prompting Template

### 1. HAIKU Prompts (Data Extraction)

```
SYSTEM PROMPT:
"Extract {task}. Output JSON only. Be concise."

USER PROMPT:
"{input_data}"

PARAMETERS:
- temperature: 0.2
- max_tokens: 500
- top_p: 0.9

EXPECTED COST: $0.0008-0.002/call
```

**Example Usage**:
```json
{
  "model": "claude-haiku-4-5-20251001",
  "system": "Extract transactions: date, amount, merchant. Output JSON only.",
  "messages": [{"role": "user", "content": "Whole Foods $45.23 04/21"}],
  "max_tokens": 500,
  "temperature": 0.2
}
```

### 2. SONNET Prompts (Analysis)

```
SYSTEM PROMPT:
"You are a {role}. Analyze {task}. Provide structured output in JSON."

USER PROMPT:
"{detailed_input_with_context}"

PARAMETERS:
- temperature: 0.3-0.5
- max_tokens: 1000-1500
- top_p: 0.95

EXPECTED COST: $0.015-0.025/call
```

**Example Usage**:
```json
{
  "model": "claude-sonnet-4-20250514",
  "system": "You are portfolio analyst. Calculate metrics: asset allocation, sector breakdown, concentration risk.",
  "messages": [{"role": "user", "content": "Analyze portfolio: ..."}],
  "max_tokens": 1500,
  "temperature": 0.4
}
```

### 3. OPUS Prompts (Strategic)

```
SYSTEM PROMPT:
"You are senior {role} with 20+ years experience. {task} with detailed reasoning."

USER PROMPT:
"{comprehensive_analysis_request}"

PARAMETERS:
- temperature: 0.5-0.7
- max_tokens: 2000-3000
- top_p: 0.95

EXPECTED COST: $0.025-0.050/call
```

**Example Usage**:
```json
{
  "model": "claude-opus-4-1-20250805",
  "system": "You are investment strategist. Generate high-conviction recommendations with thesis, risks, catalysts.",
  "messages": [{"role": "user", "content": "Based on analysis: ..."}],
  "max_tokens": 2500,
  "temperature": 0.6
}
```

---

## Agent Configuration Cheat Sheet

### Data Ingestion Agent
```python
config = {
    "model": "claude-haiku-4-5-20251001",
    "temperature": 0.2,      # Low = Consistent
    "max_tokens": 500,       # Keep output short
    "strategy": "batch",     # Batch 10-20 items
    "expected_cost": 0.0008, # Per batch
}
```

### Expense Categorizer
```python
config = {
    "model": "claude-haiku-4-5-20251001",
    "temperature": 0.2,      # Low = Consistent categories
    "max_tokens": 500,
    "strategy": "rule_first", # Rules before API
    "rule_match_rate": 0.70, # 70% free, 30% API
    "expected_cost": 0.0002, # After rule filtering
}
```

### Portfolio Manager
```python
config = {
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.3,      # Low = Consistent metrics
    "max_tokens": 1500,
    "cache_ttl": 300,        # 5-minute cache
    "strategy": "cached",
    "expected_cost": 0.015,  # Per portfolio
}
```

### Market Research Agent
```python
config = {
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.4,      # Moderate for analysis
    "max_tokens": 1500,
    "batch_size": 3,         # Analyze 3 stocks per call
    "cache_ttl": 3600,       # 1-hour cache
    "expected_cost": 0.005,  # Per stock (batched)
}
```

### Investment Recommendation
```python
config = {
    "model": "claude-opus-4-1-20250805",
    "temperature": 0.6,      # Higher = Creative thinking
    "max_tokens": 2500,
    "frequency": "2x_per_week", # Strategic, not daily
    "expected_cost": 0.030,  # Per recommendation batch
}
```

### Risk Assessment Agent
```python
config = {
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.3,      # Low = Consistent risk calcs
    "max_tokens": 1500,
    "cache_ttl": 3600,       # 1-hour cache
    "frequency": "daily",
    "expected_cost": 0.015,
}
```

### Reporting Agent
```python
config = {
    "model": "claude-haiku-4-5-20251001",
    "temperature": 0.2,      # Low = Professional tone
    "max_tokens": 1000,
    "template_mode": True,   # Use templates
    "batch_reports": True,   # Generate 2-3 at once
    "expected_cost": 0.0008,
}
```

---

## Cost Optimization Tactics

### Tactic 1: Batching
```python
# ❌ Expensive: 10 individual calls
for email in emails:
    result = claude.message({"content": email})
    
# Cost: 10 × $0.0008 = $0.008

# ✅ Cost-Effective: 1 batch call
result = claude.message({"content": json.dumps(emails)})

# Cost: 1 × $0.0008 = $0.0008 (90% savings!)
```

### Tactic 2: Rules-First Approach
```python
# ❌ Expensive: All to Claude
def categorize(transaction):
    result = claude.categorize(transaction)  # Always costs money
    
# ✅ Cost-Effective: Rules then Claude
def categorize(transaction):
    # Try free rules first (99% fast path)
    if transaction['merchant'] in RULES:
        return RULES[transaction['merchant']]  # FREE
    # Fall back to Claude (1% slow path)
    return claude.categorize(transaction)  # Only when needed
```

### Tactic 3: Caching
```python
# ❌ Expensive: Fetch every time
price = fetch_price("MSFT")  # API call
price = fetch_price("MSFT")  # API call again

# ✅ Cost-Effective: Cache with TTL
cache = {"MSFT": {"value": 387.42, "ttl": 300}}
price = cache.get("MSFT") or fetch_price("MSFT")
```

### Tactic 4: Off-Peak Timing
```python
# ❌ Expensive: During market hours
# 4 PM ET: Peak latency, potential rate limitations

# ✅ Cost-Effective: During off-peak
# 8 PM ET: Lower latency, potential discounts
```

### Tactic 5: Compression
```python
# ❌ Expensive: Verbose prompts
system = """You are a financial data extraction specialist.
Your job is to parse transaction data and extract key information...
(500 tokens)"""

# ✅ Cost-Effective: Concise prompts  
system = "Extract: date, amount, merchant. Output JSON only."
# (30 tokens, 94% savings!)
```

---

## Token Counting Estimates

### Input Token Examples
```
"apple" = 1 token
"I went to Whole Foods and spent $45.23" = 12 tokens
Standard email = 100-200 tokens
Portfolio with 10 holdings = 300-500 tokens
Market research data = 1000-2000 tokens
```

### Output Token Examples
```
JSON with 5 fields = 20-30 tokens
Portfolio analysis = 500-1000 tokens
Investment recommendation = 1000-2000 tokens
```

### Calculation
```
Cost = (input_tokens × input_rate) + (output_tokens × output_rate)

Example - Haiku:
100 input + 50 output = (100 × 0.0008) + (50 × 0.0024) = $0.00008 + $0.00012 = $0.0002
```

---

## Performance Targets

| Agent | Task | Target Latency | Target Cost | Target Accuracy |
|-------|------|---|---|---|
| Data Ingestion | Email batch | <500ms | $0.0008 | 98% |
| Categorizer | 10 transactions | <200ms | $0.0002 | 94% |
| Portfolio Mgr | Full analysis | <1s | $0.015 | 99.5% |
| Market Research | 3 stocks | <2s | $0.015 | 92% |
| Recommendation | 5 stocks | <3s | $0.030 | 87% |
| Risk Assessment | Full portfolio | <1.5s | $0.015 | 96% |
| Reporting | 3 reports | <500ms | $0.0008 | 100% |

---

## Weekly Monitoring Checklist

- [ ] Check cost tracker summary
- [ ] Review token usage trends
- [ ] Identify highest-cost agents
- [ ] Verify cache hit rates
- [ ] Check accuracy metrics
- [ ] Plan next week optimizations
- [ ] Update monitoring dashboard

---

## Monthly Optimization Cycle

**Week 1**: Monitor & analyze
- Cost trending
- Token efficiency
- Accuracy metrics

**Week 2**: Test & experiment
- A/B test new prompts
- Try different temperatures
- Test batching strategies

**Week 3**: Implement & optimize
- Deploy improvements
- Adjust model selection
- Refine caching

**Week 4**: Review & plan
- Monthly cost report
- ROI analysis
- Next month roadmap

---

## Emergency Optimization (If Costs Spike)

If monthly costs exceed $10:

```
STEP 1: Identify culprit
- Which agent is expensive?
- Which task is problematic?

STEP 2: Quick fixes
- Reduce max_tokens by 50%
- Switch to Haiku if possible
- Enable aggressive batching
- Clear cache, rebuild slowly

STEP 3: Deeper optimization
- Rewrite prompts for conciseness
- Implement rule-based pre-filtering
- Reduce update frequency
- Cache more aggressively

STEP 4: Review
- Was cost issue resolved?
- Did accuracy suffer?
- What's the new baseline?
```

---

## API Call Template

```python
import anthropic

client = anthropic.Anthropic(api_key="sk-...")

# Choose your model
MODEL = "claude-haiku-4-5-20251001"      # For data extraction
# MODEL = "claude-sonnet-4-20250514"    # For analysis
# MODEL = "claude-opus-4-1-20250805"    # For strategy

# Make the call
response = client.messages.create(
    model=MODEL,
    max_tokens=500,           # Adjust per task
    temperature=0.2,          # Adjust per task
    system="Your system prompt here",
    messages=[
        {
            "role": "user",
            "content": "Your user prompt here"
        }
    ]
)

# Extract and use
result = response.content[0].text
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
cost = calculate_cost(MODEL, input_tokens, output_tokens)

print(f"Result: {result}")
print(f"Cost: ${cost:.6f}")
```

---

## Common Mistakes to Avoid

❌ **Using Opus for everything**
- Increases costs 37.5x
- Overkill for simple tasks
- Use Haiku first, escalate only when needed

❌ **Not batching requests**
- 10 individual calls = 10× cost
- Group 10-20 items per request
- Savings: 90%

❌ **Verbose system prompts**
- 500 token prompt = 25x cost of 20 token prompt
- Be concise and specific
- Use examples sparingly

❌ **High max_tokens**
- max_tokens=4000 for simple extraction
- Set to 500-1000 for most tasks
- Save 75% on output token costs

❌ **No caching**
- Fetching same data repeatedly
- Implement 5-min TTL for prices
- Implement 1-hour TTL for fundamentals

❌ **Not monitoring costs**
- Costs creep up silently
- Weekly review minimum
- Set alerts at $10/month

---

## Success Metrics

Track these weekly:

```
Cost Metrics:
- Total cost this week: $_____
- Cost per transaction: $_____
- Cost per portfolio update: $_____
- Week-over-week change: _____%

Efficiency Metrics:
- Average tokens per call: _____
- Rule-based match rate: ____%
- Cache hit rate: ____%
- API calls avoided: _____

Quality Metrics:
- Categorization accuracy: ____%
- Recommendation hit rate: ____%
- Risk prediction accuracy: ____%
- User satisfaction: ____/10
```

---

## Final Tips

1. **Start conservative**: Use Haiku everywhere first
2. **Scale up as needed**: Move to Sonnet/Opus only if Haiku lacks quality
3. **Batch aggressively**: 10-20 items per call minimum
4. **Cache heavily**: 5-min for prices, 1-hour for analysis
5. **Monitor relentlessly**: Weekly cost reviews non-negotiable
6. **Test regularly**: A/B test new prompts monthly
7. **Automate everything**: No manual API calls
8. **Plan quarterly**: Major optimizations every 3 months

---

*Print this card and keep it at your desk!*
