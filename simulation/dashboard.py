import random
from typing import Dict, List, Any

class AnalyticsDashboard:
    """
    Generates analytics insights and recommendations from simulation results
    """
    
    def __init__(self):
        self.dwell_time_templates = [
            "Customer spent {time} minutes in {section}, indicating high interest in this category.",
            "Longest dwell time was {time} minutes in {section}, suggesting this area needs attention.",
            "Quick visit to {section} ({time} min) suggests customers may need better product visibility."
        ]
        self.path_efficiency_templates = [
            "Customer visited {visited} out of {total} sections, showing {efficiency}% path efficiency.",
            "Path covered {visited} sections with {skipped} skipped areas.",
            "Customer journey was {efficiency}% efficient, visiting {visited} sections."
        ]
        self.persona_behavior_templates = [
            "As a {persona}, customer showed typical behavior by visiting {preferred_sections}.",
            "Persona-driven choices led to {skipped_count} sections being skipped.",
            "Budget sensitivity level {budget} influenced shopping patterns significantly."
        ]
        self.eco_preference_template = "Eco-preference led to {eco_behavior} behavior in sustainable sections."
        self.time_constraint_template = "Time constraint resulted in {time_behavior} shopping pattern."
        self.health_focus_template = "Health focus influenced {health_behavior} in wellness-related areas."
        self.comparative_template = "Compared to {other_persona}, {persona} spent {factor}x longer in {section}."
        self.contextual_template = "This {persona} spent {percent}% more time in {section} than average."
        self.recommendation_templates = [
            "Place {product_type} near {section} to capture {persona} attention.",
            "Consider cross-merchandising {section1} and {section2} for better flow.",
            "Optimize {section} layout to reduce dwell time and improve efficiency.",
            "Add signage in {section} to guide {persona} customers more effectively.",
            "Consider promotional displays in {section} to attract {persona} shoppers.",
            "Review pricing strategy in {section} for {budget_level} budget sensitivity.",
            "Improve product placement in {section} to reduce skipped sections.",
            "Add eco-friendly options in {section} to appeal to sustainability-focused customers.",
            "Optimize checkout process to reduce wait times for time-constrained shoppers.",
            "Consider health-focused product placement in {section} for wellness-oriented customers."
        ]
    
    def generate_insights(self, results: Dict[str, Any], all_results: List[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Generate robust, contextual, and comparative AI-like insights from simulation results"""
        if all_results is None:
            all_results = []
        insights = []
        # Dwell time insight
        if results['dwell_time']:
            max_section = max(results['dwell_time'], key=results['dwell_time'].get)
            max_time = results['dwell_time'][max_section]
            template = random.choice(self.dwell_time_templates)
            insight = template.format(time=max_time, section=max_section)
            insights.append({
                "title": "Dwell Time Analysis",
                "description": insight
            })
        # Path efficiency insight
        total_sections = len(results.get('path', []))
        skipped_count = len(results.get('skipped', []))
        efficiency = (total_sections / (total_sections + skipped_count)) * 100 if (total_sections + skipped_count) > 0 else 0
        template = random.choice(self.path_efficiency_templates)
        insight = template.format(
            visited=total_sections,
            total=total_sections + skipped_count,
            efficiency=f"{efficiency:.1f}",
            skipped=skipped_count
        )
        insights.append({
            "title": "Path Efficiency",
            "description": insight
        })
        # Persona behavior insight
        persona = results.get('persona', 'Unknown')
        budget = results.get('budget_sensitivity', 3)
        preferred_sections = ', '.join(results.get('path', [])[1:-1])  # Exclude entrance/checkout
        template = random.choice(self.persona_behavior_templates)
        insight = template.format(
            persona=persona,
            preferred_sections=preferred_sections,
            skipped_count=skipped_count,
            budget=budget
        )
        insights.append({
            "title": "Persona Behavior Pattern",
            "description": insight
        })
        # Preference-based insights
        preferences = results.get('preferences', {})
        if preferences.get('eco_preference', False):
            eco_behavior = "heightened interest in sustainable products"
            insight = self.eco_preference_template.format(eco_behavior=eco_behavior)
            insights.append({
                "title": "Eco-Preference Impact",
                "description": insight
            })
        if preferences.get('time_constraint', False):
            time_behavior = "accelerated shopping with focused product selection"
            insight = self.time_constraint_template.format(time_behavior=time_behavior)
            insights.append({
                "title": "Time Constraint Effect",
                "description": insight
            })
        if preferences.get('health_focus', False):
            health_behavior = "increased time spent in wellness and fresh food areas"
            insight = self.health_focus_template.format(health_behavior=health_behavior)
            insights.append({
                "title": "Health Focus Influence",
                "description": insight
            })
        # Contextual insight (compare to average if all_results provided)
        if all_results:
            for section in results['dwell_time']:
                persona_time = results['dwell_time'][section]
                avg_time = sum(r['dwell_time'].get(section, 0) for r in all_results) / len(all_results)
                if avg_time > 0:
                    percent = int(100 * (persona_time - avg_time) / avg_time)
                    if abs(percent) > 20:
                        insight = self.contextual_template.format(
                            persona=persona, percent=abs(percent), section=section)
                        insights.append({
                            "title": "Contextual Insight",
                            "description": insight
                        })
                        break
        # Comparative insight (compare to another persona if all_results provided)
        if all_results and len(all_results) > 1:
            for other in all_results:
                if other['persona'] != persona:
                    for section in results['dwell_time']:
                        t1 = results['dwell_time'][section]
                        t2 = other['dwell_time'].get(section, 0)
                        if t2 > 0 and t1 / t2 > 1.5:
                            factor = round(t1 / t2, 1)
                            insight = self.comparative_template.format(
                                other_persona=other['persona'], persona=persona, factor=factor, section=section)
                            insights.append({
                                "title": "Comparative Insight",
                                "description": insight
                            })
                            break
                    break
        return insights
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on simulation results"""
        
        recommendations = []
        persona = results.get('persona', 'Customer')
        budget_level = results.get('budget_sensitivity', 3)
        path = results.get('path', [])
        skipped = results.get('skipped', [])
        dwell_time = results.get('dwell_time', {})
        
        # Get sections for recommendations
        high_dwell_sections = [s for s, t in dwell_time.items() if t > 8]
        low_dwell_sections = [s for s, t in dwell_time.items() if t < 3 and s not in ['Entrance', 'Checkout']]
        
        # Generate 5-7 recommendations
        num_recommendations = random.randint(5, 7)
        attempts = 0
        max_attempts = 20  # Prevent infinite loop
        while len(recommendations) < num_recommendations and attempts < max_attempts:
            template = random.choice(self.recommendation_templates)
            
            # Fill template with appropriate values
            if "{product_type}" in template:
                product_types = ["organic snacks", "premium beverages", "eco-friendly products", "health supplements"]
                product_type = random.choice(product_types)
                section = random.choice(path) if path else "Produce"
                recommendation = template.format(
                    product_type=product_type,
                    section=section,
                    persona=persona
                )
            elif "{section1}" in template and "{section2}" in template:
                if len(path) >= 2:
                    section1, section2 = random.sample(path[1:-1], 2)  # Exclude entrance/checkout
                    recommendation = template.format(section1=section1, section2=section2)
                else:
                    recommendation = template.format(section1="Produce", section2="Dairy")
            elif "{section}" in template:
                if high_dwell_sections:
                    section = random.choice(high_dwell_sections)
                elif low_dwell_sections:
                    section = random.choice(low_dwell_sections)
                elif skipped:
                    section = random.choice(skipped)
                else:
                    section = random.choice(path) if path else "Produce"
                
                recommendation = template.format(
                    section=section,
                    persona=persona,
                    budget_level=budget_level
                )
            else:
                recommendation = template
            
            # Only add if not duplicate
            if recommendation not in recommendations:
                recommendations.append(recommendation)
            attempts += 1
        return recommendations[:num_recommendations]
    
    def generate_advanced_analytics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advanced analytics metrics"""
        
        path = results.get('path', [])
        dwell_time = results.get('dwell_time', {})
        skipped = results.get('skipped', [])
        
        analytics = {
            "total_time": sum(dwell_time.values()),
            "average_dwell_time": sum(dwell_time.values()) / len(dwell_time) if dwell_time else 0,
            "path_length": len(path),
            "sections_skipped": len(skipped),
            "efficiency_score": len(path) / (len(path) + len(skipped)) if (len(path) + len(skipped)) > 0 else 0,
            "most_visited_section": max(dwell_time, key=dwell_time.get) if dwell_time else None,
            "least_visited_section": min(dwell_time, key=dwell_time.get) if dwell_time else None,
            "bottleneck_sections": [s for s, t in dwell_time.items() if t > 10],
            "quick_sections": [s for s, t in dwell_time.items() if t < 3 and s not in ['Entrance', 'Checkout']]
        }
        
        return analytics
    
    def generate_persona_comparison(self, results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple persona simulations"""
        
        if not results_list:
            return {}
        
        comparison = {
            "personas": [],
            "total_times": [],
            "efficiency_scores": [],
            "path_lengths": [],
            "most_common_sections": []
        }
        
        for results in results_list:
            persona = results.get('persona', 'Unknown')
            total_time = sum(results.get('dwell_time', {}).values())
            path_length = len(results.get('path', []))
            skipped_count = len(results.get('skipped', []))
            efficiency = path_length / (path_length + skipped_count) if (path_length + skipped_count) > 0 else 0
            
            comparison["personas"].append(persona)
            comparison["total_times"].append(total_time)
            comparison["efficiency_scores"].append(efficiency)
            comparison["path_lengths"].append(path_length)
            comparison["most_common_sections"].extend(results.get('path', [])[1:-1])  # Exclude entrance/checkout
        
        # Find most common sections across all personas
        from collections import Counter
        section_counts = Counter(comparison["most_common_sections"])
        comparison["most_common_sections"] = [section for section, count in section_counts.most_common(5)]
        
        return comparison
    
    def frequency_heatmap(self, all_results: List[Dict[str, Any]] = None):
        if all_results is None:
            all_results = []
        # TODO: Implement frequency heatmap for section visits
        pass
    
    def path_comparison(self, results1: Dict[str, Any], results2: Dict[str, Any]):
        # TODO: Implement side-by-side path comparison
        pass
    
    def bottleneck_detection(self, all_results: List[Dict[str, Any]] = None):
        if all_results is None:
            all_results = []
        # TODO: Highlight sections with high dwell/skipped rates
        pass
    
    def persona_summary_table(self, all_results: List[Dict[str, Any]] = None):
        if all_results is None:
            all_results = []
        # TODO: Tabular view of all personas with key stats
        pass
    
    def scenario_replay(self, results: Dict[str, Any]):
        # TODO: Animate the customer's path step-by-step
        pass
    
    def dynamic_filtering(self, all_results: List[Dict[str, Any]] = None, filters: Dict = None):
        if all_results is None:
            all_results = []
        if filters is None:
            filters = {}
        # TODO: Filter analytics by persona, budget, or preference
        pass
    
    def hover_details(self, section: str, results: Dict[str, Any]):
        # TODO: Show detailed stats for each section on hover
        pass