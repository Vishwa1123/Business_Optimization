import pulp
import numpy as np
import matplotlib.pyplot as plt

class FurnitureBusinessOptimization:
    def __init__(self):
        # Business Constraints and Parameters
        self.manufacturing_capacity = {
            'wood_hours': 1200,  # Total available woodworking hours
            'design_hours': 400,  # Available design hours
            'budget': 150000,     # Total budget for materials and design
        }
        
        # Existing Product Lines
        self.products = {
            'dining_table': {
                'profit_per_unit': 350,
                'wood_hours_per_unit': 8,
                'material_cost': 250,
                'design_complexity': 15
            },
            'bookshelf': {
                'profit_per_unit': 250,
                'wood_hours_per_unit': 6,
                'material_cost': 180,
                'design_complexity': 10
            },
            'office_chair': {
                'profit_per_unit': 200,
                'wood_hours_per_unit': 4,
                'material_cost': 150,
                'design_complexity': 8
            }
        }
        
        # New Product Design Parameters
        self.new_product_design = {
            'design_hours_required': 100,
            'prototype_cost': 5000,
            'estimated_profit_per_unit': 275,
            'wood_hours_per_unit': 5,
            'material_cost_per_unit': 200
        }
    
    def optimize_business_strategy(self):
        # Create the linear programming problem
        prob = pulp.LpProblem("Furniture_Business_Optimization", pulp.LpMaximize)
        
        # Decision Variables
        # Existing products production
        product_vars = {
            name: pulp.LpVariable(f"Produce_{name}", lowBound=0, cat='Integer')
            for name in self.products
        }
        
        # New product design and production decision
        design_new_product = pulp.LpVariable("Design_New_Product", cat='Binary')
        new_product_units = pulp.LpVariable("New_Product_Units", lowBound=0, cat='Integer')
        
        # Objective Function: Maximize Total Profit
        # Include potential profit from new product design and production
        objective = sum(
            self.products[name]['profit_per_unit'] * product_vars[name] 
            for name in self.products
        )
        
        # Add new product design and production to objective
        objective += (
            design_new_product * (-self.new_product_design['prototype_cost']) +  # Design cost
            self.new_product_design['estimated_profit_per_unit'] * new_product_units  # New product profit
        )
        
        prob += objective, "Total_Profit"
        
        # Constraints
        # 1. Woodworking Hours Constraint
        prob += (
            sum(self.products[name]['wood_hours_per_unit'] * product_vars[name] for name in self.products) +
            (self.new_product_design['wood_hours_per_unit'] * new_product_units) 
            <= self.manufacturing_capacity['wood_hours'], 
            "Woodworking_Hours_Constraint"
        )
        
        # 2. Design Hours Constraint
        prob += (
            design_new_product * self.new_product_design['design_hours_required'] +
            sum(self.products[name]['design_complexity'] * product_vars[name] for name in self.products)
            <= self.manufacturing_capacity['design_hours'], 
            "Design_Hours_Constraint"
        )
        
        # 3. Budget Constraint
        prob += (
            sum(self.products[name]['material_cost'] * product_vars[name] for name in self.products) +
            (design_new_product * self.new_product_design['prototype_cost']) +
            (self.new_product_design['material_cost_per_unit'] * new_product_units)
            <= self.manufacturing_capacity['budget'], 
            "Budget_Constraint"
        )
        
        # 4. New Product Constraints
        # Only produce new product units if design is approved
        prob += new_product_units <= 50 * design_new_product
        
        # Solve the problem
        prob.solve()
        
        # Prepare results
        results = {
            'status': pulp.LpStatus[prob.status],
            'total_profit': pulp.value(prob.objective),
            'production_plan': {},
            'new_product_design': bool(design_new_product.varValue),
            'new_product_units': int(new_product_units.varValue) if design_new_product.varValue else 0
        }
        
        # Collect production details
        for name, var in product_vars.items():
            results['production_plan'][name] = int(var.varValue)
        
        return results
    
    def visualize_results(self, results):
        # Create a bar plot of production plan
        plt.figure(figsize=(10, 6))
        products = list(results['production_plan'].keys())
        units = list(results['production_plan'].values())
        
        plt.bar(products, units)
        plt.title('Optimal Production Plan')
        plt.xlabel('Product')
        plt.ylabel('Number of Units')
        plt.xticks(rotation=45)
        
        for i, v in enumerate(units):
            plt.text(i, v, str(v), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('production_plan.png')
        plt.close()
    
    def run_optimization(self):
        # Main method to run the entire optimization process
        results = self.optimize_business_strategy()
        
        # Print Detailed Results
        print("\n--- Furniture Business Optimization Results ---")
        print(f"Optimization Status: {results['status']}")
        print(f"\nTotal Projected Profit: ${results['total_profit']:,.2f}")
        
        print("\nProduction Plan:")
        for product, units in results['production_plan'].items():
            print(f"{product.replace('_', ' ').title()}: {units} units")
        
        print("\nNew Product Design:")
        print(f"Design Approved: {results['new_product_design']}")
        print(f"New Product Units: {results['new_product_units']}")
        
        # Visualize results
        self.visualize_results(results)
        
        return results

# Run the optimization
if __name__ == "__main__":
    business_optimizer = FurnitureBusinessOptimization()
    business_optimizer.run_optimization()
