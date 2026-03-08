#!/usr/bin/env python3
"""
Crafted Food Cost Variance Tracking System
Compares theoretical vs actual ingredient usage
Tolerance: 10-15%
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Recipe database (key ingredients only for tracking)
RECIPES = {
    # Protein Shakes
    'Dark Panther': {'banana': 100, 'protein_powder_chocolate': 30, 'oreo': 2, 'dates': 3, 'milk': 200},
    'Velvet Claws': {'banana': 100, 'vanilla_protein_powder': 30, 'mixed_berry': 40, 'acai': 40, 'milk': 200},
    'Mad Monkey': {'banana': 200, 'peanut_butter': 15, 'dates': 3, 'vanilla_protein': 30, 'milk': 200},
    'Iron Fuel': {'cacao_nibs': 15, 'dates': 4, 'almond': 20, 'dark_chocolate_powder': 20, 'milk': 200},
    'Berry Queens': {'mixed_berry': 200, 'coconut_water': 200, 'vanilla_protein': 30, 'almond': 20},
    'Tropical Boost': {'dragon_fruit': 100, 'watermelon': 100, 'pineapple': 100, 'coconut_water': 200, 'vanilla_protein': 30},
    'Mango Punch': {'banana': 200, 'mango': 100, 'coconut_water': 100, 'vanilla_protein_powder': 30},
    'Gamma Green': {'banana': 200, 'baby_spinach': 100, 'mint': 30, 'coconut_water': 100, 'milk': 100, 'vanilla_protein': 30},
    'Xmas 2025 Shake': {'dragon_fruit': 200, 'strawberry': 150, 'vanilla_protein': 30, 'banana': 100},
    
    # Coffee
    'Flat White': {'ground_coffee': 18, 'fresh_milk': 200},
    'Latte': {'ground_coffee': 16, 'fresh_milk': 200},
    'Cappuccino': {'ground_coffee': 16, 'fresh_milk': 170},
    'Americano': {'ground_coffee': 18, 'hot_water': 200},
    'Double Espresso': {'ground_coffee': 18},
    'Machiato': {'ground_coffee': 16},
    'Mochachino': {'ground_coffee': 16, 'chocolate_powder': 8, 'fresh_milk': 200},
    
    # Milk Beverages
    'Matcha': {'matcha_powder': 6, 'fresh_milk': 150, 'hot_water': 65},
    'Hot Chocolate': {'chocolate_powder': 16, 'fresh_milk': 200, 'hot_water': 65},
    'Iced Chocolate': {'chocolate_powder': 15, 'fresh_milk': 250, 'hot_water': 50},
    
    # Juices
    'Orange Juice': {'tangerine': 280},
    'Pineapple Juice': {'pineapple': 250},
    'Watermelon Juice': {'watermelon': 250},
    'Mango Juice': {'mango': 200, 'water': 60},
    'Dragon Fruit Juice': {'dragon_fruit': 170},
    'Lime & Mint Juice': {'lime': 50, 'mint_leaf': 3},
    'Garden Juice': {'apple': 150, 'cucumber': 150, 'celery': 5, 'lime': 50, 'kale': 45},
    'Golden Hour Juice': {'orange': 185, 'carrot': 100, 'pineapple': 90},
    'Red Ribbon Juice': {'watermelon': 290, 'strawberry': 52},
    'Tropicana Juice': {'watermelon': 290, 'pineapple': 90, 'orange': 185},
    'Jamu': {'turmeric': 100, 'tonic_water': 1},
    
    # Food Items
    'Island Sweet Platter': {'pancake_batter': 1, 'butter': 10, 'banana': 50, 'mango': 50, 'dragon_fruit': 50},
    'Tropical Smash': {'avocado': 100, 'egg': 2, 'sourdough_bread': 1, 'edamame': 10, 'feta_cheese': 5},
    'Bali Brekky Tacos': {'tortilla': 2, 'egg': 2, 'avocado': 100, 'feta_cheese': 5},
    'Protein Power Bowl': {'tomato': 50, 'pumpkin': 65, 'tempe': 3, 'egg': 1, 'quinoa': 50, 'spinach': 50, 'avocado': 100},
    'Tribal Bruschetta Trio': {'avocado_smash': 40, 'cherry_tomato': 30, 'pineapple': 40, 'baguette': 3, 'mozzarella': 8},
    'Chicken Sandwich': {'chicken_breast': 70, 'avocado': 100, 'romaine': 50, 'mozzarella': 40, 'sourdough': 100, 'tomato': 70},
    'Romaine Salad': {'chicken_breast': 70, 'cherry_tomato': 50, 'parmesan': 10, 'crouton': 50, 'romaine': 70},
    'Croissant Sandwich': {'croissant': 1, 'tomato': 70, 'avocado': 100, 'mozzarella': 40, 'egg': 1},
    'Crafted Omelette': {'egg': 2, 'tomato': 20, 'mushroom': 20, 'feta_cheese': 5, 'sourdough': 1},
    'Fruit Platter': {'pineapple': 60, 'mango': 60, 'watermelon': 100, 'banana': 100, 'dragonfruit': 60},
}

class FoodCostTracker:
    def __init__(self, tolerance_percent=15):
        self.tolerance = tolerance_percent / 100
        self.data_file = '/root/.openclaw/workspace/crafted_reports/food_cost_tracking.json'
        self.load_data()
    
    def load_data(self):
        """Load tracking data from file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'monthly_periods': {},
                'daily_sales': {},
                'theoretical_usage': {},
                'actual_purchases': {},
                'variances': {}
            }
    
    def save_data(self):
        """Save tracking data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_daily_sales(self, date, sales_by_item):
        """
        Record daily sales from Mokapos
        sales_by_item: dict {item_name: quantity_sold}
        """
        self.data['daily_sales'][date] = sales_by_item
        
        # Calculate theoretical usage for this day
        theoretical = defaultdict(float)
        for item, qty_sold in sales_by_item.items():
            if item in RECIPES:
                for ingredient, qty_per_item in RECIPES[item].items():
                    theoretical[ingredient] += qty_per_item * qty_sold
        
        self.data['theoretical_usage'][date] = dict(theoretical)
        self.save_data()
        return dict(theoretical)
    
    def record_purchases(self, date, purchases):
        """
        Record actual ingredient purchases from expense sheets
        purchases: dict {ingredient_name: quantity_purchased}
        """
        if date not in self.data['actual_purchases']:
            self.data['actual_purchases'][date] = {}
        
        for ingredient, qty in purchases.items():
            if ingredient in self.data['actual_purchases'][date]:
                self.data['actual_purchases'][date][ingredient] += qty
            else:
                self.data['actual_purchases'][date][ingredient] = qty
        
        self.save_data()
    
    def calculate_monthly_variance(self, month_key):
        """
        Calculate variance for a monthly period (21st-20th)
        Returns items with variance > tolerance
        """
        # Sum all theoretical usage for the month
        total_theoretical = defaultdict(float)
        total_actual = defaultdict(float)
        
        for date, usage in self.data['theoretical_usage'].items():
            if date.startswith(month_key):  # Format: YYYY-MM-DD
                for ingredient, qty in usage.items():
                    total_theoretical[ingredient] += qty
        
        for date, purchases in self.data['actual_purchases'].items():
            if date.startswith(month_key):
                for ingredient, qty in purchases.items():
                    total_actual[ingredient] += qty
        
        # Calculate variances
        variances = {}
        all_ingredients = set(total_theoretical.keys()) | set(total_actual.keys())
        
        for ingredient in all_ingredients:
            theory = total_theoretical.get(ingredient, 0)
            actual = total_actual.get(ingredient, 0)
            
            if theory > 0:
                variance_pct = ((actual - theory) / theory) * 100
            else:
                variance_pct = 100 if actual > 0 else 0
            
            # Flag if outside tolerance
            is_flagged = abs(variance_pct) > (self.tolerance * 100)
            
            variances[ingredient] = {
                'theoretical': theory,
                'actual': actual,
                'variance_qty': actual - theory,
                'variance_percent': round(variance_pct, 1),
                'flagged': is_flagged
            }
        
        self.data['variances'][month_key] = variances
        self.save_data()
        return variances
    
    def generate_variance_report(self, month_key):
        """Generate a formatted variance report"""
        variances = self.calculate_monthly_variance(month_key)
        
        report = []
        report.append(f"📊 FOOD COST VARIANCE REPORT - {month_key}")
        report.append(f"Tolerance: ±{self.tolerance*100:.0f}%")
        report.append("")
        
        # Flagged items (outside tolerance)
        flagged = {k: v for k, v in variances.items() if v['flagged']}
        
        if flagged:
            report.append("🚨 FLAGGED ITEMS (Outside Tolerance):")
            report.append("-" * 60)
            for ingredient, data in sorted(flagged.items(), 
                                            key=lambda x: abs(x[1]['variance_percent']), 
                                            reverse=True):
                emoji = "📈" if data['variance_percent'] > 0 else "📉"
                report.append(f"{emoji} {ingredient.upper()}")
                report.append(f"   Theoretical: {data['theoretical']:.0f} units")
                report.append(f"   Actual: {data['actual']:.0f} units")
                report.append(f"   Variance: {data['variance_percent']:+.1f}%")
                
                if data['variance_percent'] > 0:
                    report.append(f"   ⚠️  OVER-CONSUMPTION: {data['variance_qty']:.0f} units wasted/extra")
                else:
                    report.append(f"   ⚠️  UNDER-CONSUMPTION: {abs(data['variance_qty']):.0f} units missing")
                report.append("")
        else:
            report.append("✅ All ingredients within tolerance range!")
            report.append("")
        
        # Summary stats
        report.append("📈 SUMMARY:")
        report.append(f"   Total items tracked: {len(variances)}")
        report.append(f"   Flagged items: {len(flagged)}")
        if flagged:
            report.append(f"   Items needing attention: {', '.join(list(flagged.keys())[:5])}")
        
        return "\n".join(report)
    
    def get_ingredient_alerts(self, month_key):
        """Get just the flagged ingredients for quick reference"""
        variances = self.calculate_monthly_variance(month_key)
        flagged = {k: v for k, v in variances.items() if v['flagged']}
        return flagged

# Helper functions for daily operations
def record_sales_from_mokapos(mokapos_data):
    """
    Extract sales data from Mokapos response and record it
    """
    tracker = FoodCostTracker()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Parse Mokapos sales data
    # This is a placeholder - actual implementation depends on Mokapos data format
    sales = {}
    
    if isinstance(mokapos_data, dict) and 'sales' in mokapos_data:
        # Extract items sold from Mokapos data
        for item in mokapos_data['sales']:
            item_name = item.get('name', '')
            qty = item.get('quantity', 0)
            if item_name and qty > 0:
                sales[item_name] = sales.get(item_name, 0) + qty
    
    if sales:
        theoretical = tracker.record_daily_sales(today, sales)
        return {
            'date': today,
            'sales_recorded': sales,
            'theoretical_usage': theoretical
        }
    return None

def extract_purchases_from_expenses(expense_data):
    """
    Extract ingredient purchases from expense sheet data
    """
    tracker = FoodCostTracker()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Map expense categories to ingredients
    # This is a simplified mapping - customize based on your expense sheet structure
    ingredient_mapping = {
        'Food Item': {
            'banana': 'banana',
            'avocado': 'avocado',
            'milk': 'milk',
            'egg': 'egg',
            # Add more mappings
        }
    }
    
    purchases = {}
    for entry in expense_data:
        item = entry.get('item', '').lower()
        qty = entry.get('qty', 0)
        
        # Try to match to ingredient
        for keyword, ingredient_name in ingredient_mapping.items():
            if keyword in item:
                purchases[ingredient_name] = purchases.get(ingredient_name, 0) + qty
                break
    
    if purchases:
        tracker.record_purchases(today, purchases)
    
    return purchases

if __name__ == '__main__':
    # Example usage
    tracker = FoodCostTracker(tolerance_percent=15)
    
    # Record some example sales
    example_sales = {
        'Dark Panther': 5,
        'Tropical Smash': 3,
        'Flat White': 10,
        'Chicken Sandwich': 2
    }
    
    theoretical = tracker.record_daily_sales('2026-03-07', example_sales)
    print("Theoretical usage for today:")
    print(json.dumps(theoretical, indent=2))
    
    # Record example purchases
    example_purchases = {
        'banana': 800,  # grams
        'avocado': 500,
        'milk': 2000,
        'egg': 20,
        'ground_coffee': 200
    }
    
    tracker.record_purchases('2026-03-07', example_purchases)
    
    # Generate report for March 2026 (period 21 Feb - 20 Mar)
    print("\n" + "="*60)
    report = tracker.generate_variance_report('2026-03')
    print(report)
