#!/usr/bin/env python3
"""
Trading Performance Coach using OpenAI
Analyzes trading performance and provides insights and recommendations.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from typing import Dict, List, Optional

class TradingCoach:
    def __init__(self, api_key: str, export_dir: str = "exports"):
        self.api_key = api_key
        self.export_dir = Path(export_dir)
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    def load_monthly_data(self, year: int, month: int) -> Optional[Dict]:
        """Load monthly trading data"""
        monthly_file = self.export_dir / "monthly" / f"{year}-{month:02d}.json"
        if monthly_file.exists():
            with open(monthly_file, 'r') as f:
                return json.load(f)
        return None
    
    def load_weekly_data(self, year: int, week: int) -> Optional[Dict]:
        """Load weekly trading data"""
        weekly_file = self.export_dir / "weekly" / f"{year}-W{week:02d}.json"
        if weekly_file.exists():
            with open(weekly_file, 'r') as f:
                return json.load(f)
        return None
    
    def prepare_monthly_analysis_prompt(self, current_month: Dict, previous_month: Optional[Dict] = None) -> str:
        """Prepare the prompt for monthly analysis"""
        
        prompt = f"""
You are an experienced trading coach analyzing a prop trader's monthly performance. 
Please provide constructive feedback, insights, and actionable recommendations.

CURRENT MONTH PERFORMANCE:
- Total Trades: {current_month.get('totalTrades', 0)}
- Total P&L: ${current_month.get('totalPnL', 0):.2f}
- Win Rate: {current_month.get('winRate', 0):.1f}%
- Best Day P&L: ${current_month.get('bestDayPnL', 0):.2f}
- Worst Day P&L: ${current_month.get('worstDayPnL', 0):.2f}
- Trading Days: {current_month.get('tradingDays', 0)}
- Average P&L per Trade: ${(current_month.get('totalPnL', 0) / max(current_month.get('totalTrades', 1), 1)):.2f}
- Total Commission: ${current_month.get('totalCommissions', 0):.2f}
- Most Traded Symbols: {', '.join(current_month.get('symbols', [])[:5])}
"""

        if previous_month:
            pnl_change = current_month.get('totalPnL', 0) - previous_month.get('totalPnL', 0)
            winrate_change = current_month.get('winRate', 0) - previous_month.get('winRate', 0)
            trades_change = current_month.get('totalTrades', 0) - previous_month.get('totalTrades', 0)
            
            prompt += f"""
COMPARISON WITH PREVIOUS MONTH:
- P&L Change: ${pnl_change:.2f} ({'+' if pnl_change >= 0 else ''}{pnl_change:.2f})
- Win Rate Change: {winrate_change:.1f}% ({'+' if winrate_change >= 0 else ''}{winrate_change:.1f}%)
- Trade Volume Change: {trades_change} trades ({'+' if trades_change >= 0 else ''}{trades_change})
- Previous Month P&L: ${previous_month.get('totalPnL', 0):.2f}
- Previous Month Win Rate: {previous_month.get('winRate', 0):.1f}%
"""

        prompt += """
Please provide your analysis in the following JSON format:
{
    "overall_performance": "Brief summary of overall performance this month",
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "areas_for_improvement": ["Area 1", "Area 2", "Area 3"],
    "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
    "actionable_recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"],
    "motivation_message": "Encouraging message for the trader",
    "risk_assessment": "Assessment of current risk management",
    "next_month_focus": ["Focus area 1", "Focus area 2", "Focus area 3"]
}

Focus on:
1. Risk management and position sizing
2. Win rate vs profit factor analysis
3. Trading frequency and overtrading concerns
4. Psychological aspects and discipline
5. Market conditions and adaptability
6. Commission efficiency
7. Consistency in performance

Be constructive, specific, and actionable. Avoid generic advice.
"""
        return prompt
    
    def prepare_weekly_analysis_prompt(self, current_week: Dict, previous_weeks: List[Dict] = None) -> str:
        """Prepare the prompt for weekly analysis"""
        
        prompt = f"""
You are an experienced trading coach providing weekly performance review for a prop trader.
Focus on immediate tactical improvements and weekly patterns.

CURRENT WEEK PERFORMANCE:
- Total Trades: {current_week.get('totalTrades', 0)}
- Total P&L: ${current_week.get('totalPnL', 0):.2f}
- Win Rate: {current_week.get('winRate', 0):.1f}%
- Trading Days: {current_week.get('tradingDays', 0)}
- Best Day: ${current_week.get('bestDayPnL', 0):.2f}
- Worst Day: ${current_week.get('worstDayPnL', 0):.2f}
- Daily Consistency: {current_week.get('consistency', 'N/A')}
"""

        if previous_weeks:
            avg_pnl = np.mean([w.get('totalPnL', 0) for w in previous_weeks])
            avg_winrate = np.mean([w.get('winRate', 0) for w in previous_weeks])
            
            prompt += f"""
RECENT WEEKS COMPARISON:
- Average P&L (last 4 weeks): ${avg_pnl:.2f}
- Average Win Rate (last 4 weeks): {avg_winrate:.1f}%
- This week vs average: {'Above' if current_week.get('totalPnL', 0) > avg_pnl else 'Below'} average
"""

        prompt += """
Please provide your weekly review in JSON format:
{
    "week_summary": "Brief summary of this week's performance",
    "daily_patterns": ["Pattern 1", "Pattern 2"],
    "quick_wins": ["Quick improvement 1", "Quick improvement 2"],
    "warning_signs": ["Warning 1", "Warning 2"],
    "focus_for_next_week": ["Focus 1", "Focus 2", "Focus 3"],
    "motivation_boost": "Short encouraging message",
    "tactical_adjustments": ["Adjustment 1", "Adjustment 2"]
}

Focus on:
1. Daily trading patterns and consistency
2. Intraweek momentum and psychology
3. Quick tactical adjustments
4. Risk management on a weekly basis
5. Energy and focus levels
6. Market adaptation during the week

Keep it concise and focused on immediate actionable items.
"""
        return prompt
    
    def call_openai_api(self, prompt: str) -> Optional[Dict]:
        """Call OpenAI API and return the response"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert trading coach with deep knowledge of prop trading, risk management, and trader psychology. Provide specific, actionable advice based on the data provided."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, return as text
                return {"raw_response": content}
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    
    def generate_monthly_coaching(self, year: int, month: int) -> Optional[Dict]:
        """Generate monthly coaching report"""
        current_month = self.load_monthly_data(year, month)
        if not current_month:
            print(f"No data found for {year}-{month:02d}")
            return None
        
        # Try to load previous month
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year = year - 1
        
        previous_month = self.load_monthly_data(prev_year, prev_month)
        
        prompt = self.prepare_monthly_analysis_prompt(current_month, previous_month)
        coaching_result = self.call_openai_api(prompt)
        
        if coaching_result:
            # Save coaching report
            coaching_data = {
                "generated_at": datetime.now().isoformat(),
                "period": f"{year}-{month:02d}",
                "type": "monthly",
                "data_analyzed": current_month,
                "previous_month_data": previous_month,
                "coaching": coaching_result
            }
            
            # Save to coaching directory
            coaching_dir = self.export_dir / "coaching" / "monthly"
            coaching_dir.mkdir(parents=True, exist_ok=True)
            
            coaching_file = coaching_dir / f"{year}-{month:02d}.json"
            with open(coaching_file, 'w') as f:
                json.dump(coaching_data, f, indent=2)
            
            print(f"Monthly coaching report saved: {coaching_file}")
            return coaching_data
        
        return None
    
    def generate_weekly_coaching(self, year: int, week: int) -> Optional[Dict]:
        """Generate weekly coaching report"""
        current_week = self.load_weekly_data(year, week)
        if not current_week:
            print(f"No data found for {year}-W{week:02d}")
            return None
        
        # Load previous weeks for comparison
        previous_weeks = []
        for w in range(max(1, week-4), week):
            week_data = self.load_weekly_data(year, w)
            if week_data:
                previous_weeks.append(week_data)
        
        prompt = self.prepare_weekly_analysis_prompt(current_week, previous_weeks)
        coaching_result = self.call_openai_api(prompt)
        
        if coaching_result:
            # Save coaching report
            coaching_data = {
                "generated_at": datetime.now().isoformat(),
                "period": f"{year}-W{week:02d}",
                "type": "weekly",
                "data_analyzed": current_week,
                "previous_weeks_data": previous_weeks,
                "coaching": coaching_result
            }
            
            # Save to coaching directory
            coaching_dir = self.export_dir / "coaching" / "weekly"
            coaching_dir.mkdir(parents=True, exist_ok=True)
            
            coaching_file = coaching_dir / f"{year}-W{week:02d}.json"
            with open(coaching_file, 'w') as f:
                json.dump(coaching_data, f, indent=2)
            
            print(f"Weekly coaching report saved: {coaching_file}")
            return coaching_data
        
        return None

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate trading coaching reports')
    parser.add_argument('type', choices=['monthly', 'weekly'], help='Type of coaching report')
    parser.add_argument('--year', type=int, default=datetime.now().year, help='Year')
    parser.add_argument('--month', type=int, help='Month (for monthly reports)')
    parser.add_argument('--week', type=int, help='Week number (for weekly reports)')
    parser.add_argument('--auto', action='store_true', help='Automatically determine period')
    
    args = parser.parse_args()
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    # Get export directory
    export_dir = os.getenv('EXPORT_OUTPUT_DIR', 'exports')
    
    coach = TradingCoach(api_key, export_dir)
    
    if args.type == 'monthly':
        if args.auto:
            # Use previous month
            today = datetime.now()
            if today.day <= 5:  # First 5 days of month, analyze previous month
                month = today.month - 1
                year = today.year
                if month == 0:
                    month = 12
                    year -= 1
            else:
                month = today.month
                year = today.year
        else:
            month = args.month or datetime.now().month
            year = args.year
        
        result = coach.generate_monthly_coaching(year, month)
        if result:
            print(f"Generated monthly coaching for {year}-{month:02d}")
        else:
            print("Failed to generate monthly coaching")
    
    elif args.type == 'weekly':
        if args.auto:
            # Use previous week
            today = datetime.now()
            if today.weekday() <= 1:  # Monday or Tuesday, analyze previous week
                week_date = today - timedelta(days=7)
            else:
                week_date = today
            
            week = week_date.isocalendar()[1]
            year = week_date.year
        else:
            week = args.week or datetime.now().isocalendar()[1]
            year = args.year
        
        result = coach.generate_weekly_coaching(year, week)
        if result:
            print(f"Generated weekly coaching for {year}-W{week:02d}")
        else:
            print("Failed to generate weekly coaching")

if __name__ == "__main__":
    main()