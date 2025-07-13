import random
import json
from typing import Dict, List, Any
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import os

class CustomerSimulator:
    """
    Simulates customer shopping behavior based on persona and preferences
    """
    
    def __init__(self):
        # Load section names and coordinates from store_layout.json
        with open(os.path.join("data", "store_layout.json"), "r") as f:
            store_data = json.load(f)
        self.sections = [s['name'] for s in store_data['sections']]
        self.section_coords = {s['name']: (s['position']['x'], s['position']['y']) for s in store_data['sections']}
        self.entrances = [s['name'] for s in store_data['sections'] if s.get('type') == 'entry']
        self.checkout = [s['name'] for s in store_data['sections'] if s.get('type') == 'checkout']
        # Persona data with new section names
        self.persona_data = self._load_persona_data()
    
    def _load_persona_data(self) -> Dict[str, Dict]:
        """Load persona behavior patterns for new layout"""
        return {
            "Eco-Conscious Millennial": {
                "preferred_sections": ["Fresh Produce", "Bakery", "Deli South", "Health & Wellness", "Eco", "Dairy"],
                "avoided_sections": ["Meat", "Frozen", "Adult Beverages", "Auto"],
                "dwell_time_multiplier": 1.3,
                "budget_sensitivity": 2,
                "path_style": "purposeful"
            },
            "Budget Shopper": {
                "preferred_sections": ["Grocery", "Bread", "Pantry", "Bedding", "Celebrate"],
                "avoided_sections": ["Premium", "Jewelry & Accessories", "Auto", "Furniture"],
                "dwell_time_multiplier": 1.5,
                "budget_sensitivity": 1,
                "path_style": "efficient"
            },
            "Convenience Seeker": {
                "preferred_sections": ["Snacks", "Deli North", "Checkout", "Pet", "Frozen"],
                "avoided_sections": ["Crafts", "Seasonal", "Auto", "Paint"],
                "dwell_time_multiplier": 0.7,
                "budget_sensitivity": 4,
                "path_style": "quick"
            },
            "Health Enthusiast": {
                "preferred_sections": ["Fresh Produce", "Health & Wellness", "Bakery", "Dairy", "Pharmacy"],
                "avoided_sections": ["Snacks", "Adult Beverages", "Auto", "Paint"],
                "dwell_time_multiplier": 1.4,
                "budget_sensitivity": 3,
                "path_style": "thorough"
            },
            "Family Planner": {
                "preferred_sections": ["Grocery", "Bakery", "Meat", "Boys", "Girls", "Mens", "Ladies'", "Toys"],
                "avoided_sections": ["Jewelry & Accessories", "Auto", "Paint"],
                "dwell_time_multiplier": 1.2,
                "budget_sensitivity": 2,
                "path_style": "comprehensive"
            },
            "Impulse Buyer": {
                "preferred_sections": ["Electronics", "Jewelry & Accessories", "Cosmetics", "Snacks", "Celebrate"],
                "avoided_sections": ["Pharmacy", "Auto", "Paint"],
                "dwell_time_multiplier": 0.9,
                "budget_sensitivity": 5,
                "path_style": "wandering"
            }
        }
    
    def simulate_journey(self, persona: str, budget_sensitivity: int, 
                        preferences: Dict[str, bool], entrance: str = "", exit: str = "") -> Dict[str, Any]:
        persona_info = self.persona_data.get(persona, self.persona_data["Budget Shopper"])
        path = self._generate_path(persona_info, preferences, budget_sensitivity, entrance, exit)
        dwell_time = self._calculate_dwell_times(path, persona_info, preferences)
        skipped = self._get_skipped_sections(path, persona_info, preferences)
        return {
            "path": path,
            "dwell_time": dwell_time,
            "skipped": skipped,
            "persona": persona,
            "budget_sensitivity": budget_sensitivity,
            "preferences": preferences
        }
    def _generate_path(self, persona_info: Dict, preferences: Dict, budget_sensitivity: int, entrance: str = "", exit: str = "") -> List[str]:
        # Use selected entrance/exit if provided
        start_entrance = entrance if entrance in self.entrances else random.choice(self.entrances)
        end_exit = exit if exit in self.checkout or exit in self.sections else self.checkout[0]
        
        # Create a more realistic path that follows store layout
        path = [start_entrance]
        
        # Define store zones for better path planning
        store_zones = {
            "front_left": ["Auto", "Paint", "Hardware", "Home Office", "Electronics", "Pet", "Cleaning", "Household Paper"],
            "front_right": ["Dairy", "Adult Beverages", "Snacks", "Deli North", "Grocery", "Meat", "Frozen", "Bakery", "Bread", "Fresh Produce", "Deli South"],
            "back_left": ["Sporting Goods", "Toys", "Garden", "Cosmetics", "Health & Wellness", "Health", "Pharmacy"],
            "back_middle": ["Furniture", "Home", "Storage/Laundry", "Kitchen & Dining", "Bath", "Bedding"],
            "back_right": ["Crafts", "Celebrate", "Seasonal", "Girls", "Boys", "Shoes", "Jewelry & Accessories", "Baby", "Mens", "Sleepwear & Panties", "Ladies'"]
        }
        
        available_sections = [s for s in self.sections if s not in self.entrances + self.checkout]
        preferred = [s for s in persona_info["preferred_sections"] if s in available_sections]
        avoided = [s for s in persona_info["avoided_sections"] if s in available_sections]
        
        # Budget sensitivity
        if budget_sensitivity <= 2:
            avoided += ["Jewelry & Accessories", "Premium"]
        
        # Eco preference
        if preferences.get('eco_preference', False):
            preferred += ["Fresh Produce", "Eco"]
            if "Eco" in avoided:
                avoided.remove("Eco")
        
        # Health focus
        if preferences.get('health_focus', False):
            preferred += ["Health & Wellness", "Pharmacy", "Fresh Produce"]
            avoided += ["Snacks", "Adult Beverages"]
        
        # Time constraint
        if preferences.get('time_constraint', False):
            path_style = "quick"
        else:
            path_style = persona_info["path_style"]
        
        # Generate path based on style and store layout
        sections_to_visit = self._plan_path_by_style(path_style, preferred, avoided, available_sections, store_zones)
        
        # Create a more realistic path that follows store flow
        final_path = self._create_realistic_path(start_entrance, sections_to_visit, end_exit, store_zones)
        
        return final_path
    
    def _plan_path_by_style(self, path_style: str, preferred: List[str], avoided: List[str], 
                           available_sections: List[str], store_zones: Dict) -> List[str]:
        """Plan sections to visit based on path style"""
        if path_style == "quick":
            # Quick path: minimal sections, mostly preferred
            sections_to_visit = random.sample(preferred, min(3, len(preferred)))
        elif path_style == "efficient":
            # Efficient path: preferred sections + a few others
            sections_to_visit = preferred[:5] + random.sample([s for s in available_sections if s not in preferred and s not in avoided], 2)
        elif path_style == "purposeful":
            # Purposeful path: focused on preferred sections
            sections_to_visit = preferred[:random.randint(4, 6)]
        elif path_style == "thorough":
            # Thorough path: preferred + some exploration
            sections_to_visit = preferred + random.sample([s for s in available_sections if s not in preferred and s not in avoided], 3)
        elif path_style == "comprehensive":
            # Comprehensive path: visit most sections except avoided
            sections_to_visit = [s for s in available_sections if s not in avoided]
        else:  # wandering
            # Wandering path: random selection
            sections_to_visit = random.sample([s for s in available_sections if s not in avoided], random.randint(5, 10))
        
        return sections_to_visit
    
    def _create_realistic_path(self, entrance: str, sections_to_visit: List[str], exit: str, store_zones: Dict) -> List[str]:
        """Create a realistic path that follows store layout and flow"""
        path = [entrance]
        
        # Determine entrance zone and plan route
        entrance_zone = self._get_section_zone(entrance, store_zones)
        
        # Create a logical flow through the store
        # Start from entrance, work through zones, end at checkout
        zone_order = self._get_zone_order(entrance_zone)
        
        # Distribute sections across zones in logical order
        zone_sections = {}
        for zone in zone_order:
            zone_sections[zone] = [s for s in sections_to_visit if s in store_zones.get(zone, [])]
        
        # Build path through zones
        for zone in zone_order:
            if zone_sections.get(zone):
                # Add sections in this zone
                path.extend(zone_sections[zone])
        
        # Ensure exit is at the end
        if exit not in path:
            path.append(exit)
        else:
            # Move exit to the end if already present
            path = [p for p in path if p != exit] + [exit]
        
        return path
    
    def _get_section_zone(self, section: str, store_zones: Dict) -> str:
        """Determine which zone a section belongs to"""
        for zone, sections in store_zones.items():
            if section in sections:
                return zone
        return "front_left"  # default
    
    def _get_zone_order(self, start_zone: str) -> List[str]:
        """Get logical zone order based on store layout"""
        # Define logical flow through the store
        zone_flows = {
            "front_left": ["front_left", "back_left", "back_middle", "back_right", "front_right"],
            "front_right": ["front_right", "back_right", "back_middle", "back_left", "front_left"]
        }
        return zone_flows.get(start_zone, ["front_left", "back_left", "back_middle", "back_right", "front_right"])
    def _calculate_dwell_times(self, path: List[str], persona_info: Dict, preferences: Dict) -> Dict[str, int]:
        dwell_times = {}
        base_multiplier = persona_info["dwell_time_multiplier"]
        # Assign base dwell times by section type or name
        for section in path:
            base_time = 5
            if "Bakery" in section: base_time = 7
            if "Produce" in section: base_time = 8
            if "Deli" in section: base_time = 6
            if "Checkout" in section: base_time = 3
            if "Health" in section: base_time = 7
            if "Jewelry" in section: base_time = 4
            if "Electronics" in section: base_time = 10
            if "Meat" in section: base_time = 6
            if "Frozen" in section: base_time = 4
            if "Toys" in section: base_time = 5
            if "Auto" in section: base_time = 2
            # Persona multiplier
            time = int(base_time * base_multiplier)
            # Preferences
            if preferences.get('time_constraint', False):
                time = int(time * 0.7)
            if preferences.get('health_focus', False) and ("Health" in section or "Produce" in section):
                time = int(time * 1.2)
            if preferences.get('eco_preference', False) and ("Eco" in section or "Produce" in section):
                time = int(time * 1.3)
            # Randomness
            time += random.randint(-2, 2)
            time = max(1, time)
            dwell_times[section] = time
        return dwell_times
    def _get_skipped_sections(self, path: List[str], persona_info: Dict, preferences: Dict) -> List[str]:
        all_sections = set(self.sections)
        visited_sections = set(path)
        skipped = list(all_sections - visited_sections)
        avoided = persona_info["avoided_sections"]
        skipped = sorted(skipped, key=lambda x: x not in avoided)
        return skipped

class MockMLSimulator:
    """
    Mock ML-based simulator using sklearn DecisionTreeClassifier
    This is an optional advanced feature
    """
    
    def __init__(self):
        self.model = None
        self._train_model()
    
    def _train_model(self):
        """Train a mock decision tree model"""
        # Mock training data
        X = np.random.rand(100, 5)  # 5 features: persona_encoding, budget, eco, time, health
        y = np.random.randint(0, 16, 100)  # 16 possible sections
        
        self.model = DecisionTreeClassifier(max_depth=5)
        self.model.fit(X, y)
    
    def predict_section(self, features: List[float]) -> str:
        """Predict next section based on features"""
        if self.model is None:
            return 'Entrance'
        prediction = self.model.predict([features])[0]
        sections = [
            'Entrance', 'Electronics', 'Clothing', 'Home',
            'Produce', 'Dairy', 'Meat', 'Frozen',
            'Pantry', 'Beverages', 'Snacks', 'Bakery',
            'Pharmacy', 'Eco', 'Premium', 'Checkout'
        ]
        return sections[prediction] 