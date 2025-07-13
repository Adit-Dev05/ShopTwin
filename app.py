import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import pandas as pd
from simulation.logic import CustomerSimulator
from simulation.dashboard import AnalyticsDashboard
import time
import base64
from io import BytesIO
import PIL.Image
import os
from simulation.pathfinding_cv import load_aisle_mask, compute_full_path, draw_path_on_image, overlay_mask_on_map
import cv2
import numpy as np
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="ShopTwin - Customer Journey Simulator",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 0.5rem 0;
        color: #4a4e69 !important;
    }
    .insight-box strong {
        color: #22223b !important;
    }
    .persona-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
    }
    .section-tooltip {
        cursor: help;
        border-bottom: 1px dotted #888;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

# Persona avatars (simple emoji mapping)
PERSONA_AVATARS = {
    "Eco-Conscious Millennial": "🌱",
    "Budget Shopper": "💸",
    "Convenience Seeker": "⚡",
    "Health Enthusiast": "🏥",
    "Family Planner": "👨‍👩‍👧‍👦",
    "Impulse Buyer": "🤩"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    # Header
    st.markdown('<h1 class="main-header">🛒 ShopTwin</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Customer Journey Simulator for Walmart</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎭 Customer Persona")
        
        # Persona selection with avatars
        personas = list(PERSONA_AVATARS.keys())
        persona_options = [f"{PERSONA_AVATARS[p]} {p}" for p in personas]
        persona_map = {f"{PERSONA_AVATARS[p]} {p}": p for p in personas}
        selected_persona_label = st.selectbox("Select Customer Persona", persona_options)
        selected_persona = persona_map[selected_persona_label]
        
        st.markdown("---")
        
        # Budget sensitivity
        st.subheader("💰 Budget Sensitivity")
        budget_sensitivity = st.slider("Budget Level (1-5)", 1, 5, 3, 
                                     help="1 = Very budget-conscious, 5 = Price-insensitive")
        
        st.markdown("---")
        
        # Preferences
        st.subheader("⚙️ Shopping Preferences")
        eco_preference = st.checkbox("🌱 Eco-friendly preference", value=False)
        time_constraint = st.checkbox("⏰ Time constraint", value=False)
        health_focus = st.checkbox("🏥 Health-focused", value=False)
        convenience_priority = st.checkbox("🚀 Convenience priority", value=False)
        
        st.markdown("---")
        
        # Parameter presets (save/load)
        st.subheader("Presets")
        if st.button("Save Preset"):
            st.session_state['preset'] = {
                'persona': selected_persona,
                'budget': budget_sensitivity,
                'eco': eco_preference,
                'time': time_constraint,
                'health': health_focus,
                'convenience': convenience_priority
            }
            st.success("Preset saved!")
        if st.button("Load Preset") and 'preset' in st.session_state:
            preset = st.session_state['preset']
            selected_persona = preset['persona']
            budget_sensitivity = preset['budget']
            eco_preference = preset['eco']
            time_constraint = preset['time']
            health_focus = preset['health']
            convenience_priority = preset['convenience']
            st.success("Preset loaded!")
        
        st.markdown("---")
        
        # Simulation button
        simulate_btn = st.button("🎯 Simulate Customer Journey", type="primary", use_container_width=True)
        if simulate_btn:
            with st.spinner("Simulating customer journey..."):
                try:
                    simulator = CustomerSimulator()
                    results = simulator.simulate_journey(
                        persona=selected_persona,
                        budget_sensitivity=budget_sensitivity,
                        preferences={
                            'eco_preference': eco_preference,
                            'time_constraint': time_constraint,
                            'health_focus': health_focus,
                            'convenience_priority': convenience_priority
                        },
                        entrance="Southwest Entrance",
                        exit="Southwest Exit"
                    )
                    st.session_state.simulation_results = results
                    st.success("Simulation completed!")
                except Exception as e:
                    st.error(f"Simulation failed: {e}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🏪 Store Layout & Customer Path")
        
        # Debug: Option to show mask overlay
        debug_mask_overlay = st.checkbox("Show aisle mask overlay (debug)", value=False)
        if debug_mask_overlay:
            img_path = os.path.join(BASE_DIR, "assets", "walmart_layout.png")
            mask_path = os.path.join(BASE_DIR, "assets", "aisle_mask_resized.png")
            img = PIL.Image.open(img_path)
            mask_img = PIL.Image.open(mask_path)
            img_np = np.array(img)
            mask_np = np.array(mask_img)
            overlay = overlay_mask_on_map(img_np, mask_np, alpha=0.4)
            st.image(overlay, caption="Aisle Mask Overlay on Store Map (debug)", use_container_width=True)
        
        if st.session_state.simulation_results:
            # Create store layout visualization
            create_store_visualization(st.session_state.simulation_results)
        else:
            st.info("👈 Select a persona and click 'Simulate' to see the customer journey!")
    
    with col2:
        st.header("📊 Quick Stats")
        
        if st.session_state.simulation_results:
            display_quick_stats(st.session_state.simulation_results)
        else:
            st.info("No simulation data available")
    
    # Bottom dashboard panel
    if st.session_state.simulation_results:
        st.markdown("---")
        st.header("📈 Journey Analytics & Insights")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            create_time_analysis(st.session_state.simulation_results)
        
        with col2:
            create_insights_panel(st.session_state.simulation_results)

    # Download/export buttons
    if st.session_state.simulation_results:
        st.download_button(
            label="Download Results (JSON)",
            data=json.dumps(st.session_state.simulation_results, indent=2),
            file_name="simulation_results.json",
            mime="application/json"
        )
        dwell_data = list(st.session_state.simulation_results['dwell_time'].items())
        df = pd.DataFrame(dwell_data)
        df.columns = ["Section", "Time"]
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Dwell Times (CSV)",
            data=csv,
            file_name="dwell_times.csv",
            mime="text/csv"
        )

def create_store_visualization(results):
    """Create the advanced store layout visualization with customer path over the Walmart map image"""
    img_path = os.path.join(BASE_DIR, "assets", "walmart_layout.png")
    mask_path = os.path.join(BASE_DIR, "assets", "aisle_mask.png")
    img = PIL.Image.open(img_path)
    width, height = img.size

    # Load and resize mask if needed
    mask_img = PIL.Image.open(mask_path)
    mask_width, mask_height = mask_img.size
    if (width, height) != (mask_width, mask_height):
        st.warning(f"Resizing aisle mask from {mask_width}x{mask_height} to {width}x{height} for alignment.")
        mask_img = mask_img.resize((width, height), PIL.Image.Resampling.NEAREST)
        # Save to a temporary file for OpenCV loading
        temp_mask_path = os.path.join(BASE_DIR, "assets", "aisle_mask_resized.png")
        mask_img.save(temp_mask_path)
        mask_path = temp_mask_path

    with open(os.path.join(BASE_DIR, "data", "store_layout.json"), "r") as f:
        store_data = json.load(f)
    section_coords = {}
    for s in store_data['sections']:
        x, y = s['position']['x'], s['position']['y']
        if 0 <= x <= 1 and 0 <= y <= 1:
            px, py = int(x * width), int(y * height)
        else:
            px, py = int(x), int(y)
        section_coords[s['name']] = (px, py)

    path_sections = results['path']
    
    # Display path information
    st.subheader("🛣️ Customer Journey Path")
    st.write(f"**Entrance:** {path_sections[0] if path_sections else 'N/A'}")
    st.write(f"**Exit:** {path_sections[-1] if path_sections else 'N/A'}")
    st.write(f"**Total Sections Visited:** {len(path_sections)}")
    
    # Show the path sequence
    if len(path_sections) > 2:
        path_display = " → ".join(path_sections[1:-1])  # Exclude entrance and exit
        st.write(f"**Path:** {path_sections[0]} → {path_display} → {path_sections[-1]}")
    
    # Count visits to each section
    visit_counts = Counter(path_sections)
    # Only keep the first visit to each section for visualization
    unique_sections = []
    seen = set()
    for section in path_sections:
        if section not in seen:
            unique_sections.append(section)
            seen.add(section)
    stop_points = [section_coords[section] for section in unique_sections if section in section_coords]

    if len(stop_points) >= 2:
        try:
            from simulation.pathfinding_cv import snap_to_aisle, overlay_points_and_paths, load_aisle_mask
            grid, _ = load_aisle_mask(mask_path)
            if grid is None:
                st.warning(f"Aisle mask not found or could not be loaded: {mask_path}.")
                st.image(img, caption="Walmart Store Layout", use_container_width=True)
                return
        except Exception as e:
            st.warning(f"Aisle mask error: {e}")
            st.image(img, caption="Walmart Store Layout", use_container_width=True)
            return
        snapped_stops = [snap_to_aisle(grid, pt) for pt in stop_points]
        from simulation.pathfinding_cv import astar
        path_segments = []
        failed_pairs = []
        for i in range(len(snapped_stops)-1):
            start, end = snapped_stops[i], snapped_stops[i+1]
            segment = astar(grid, start, end)
            if segment is None:
                failed_pairs.append((start, end))
                continue
            path_segments.append(segment)
        img_color = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        dwell_times = []
        for section in unique_sections:
            dwell_times.append(results['dwell_time'].get(section, 0))
        img_with_overlay, walkability = overlay_points_and_paths(
            img_color, snapped_stops, path_segments, failed_pairs, dwell_times, walkable_mask=grid,
            section_names=unique_sections, visit_counts=visit_counts)
        img_display = cv2.cvtColor(img_with_overlay, cv2.COLOR_BGR2RGB)
        st.image(img_display, caption="Walmart Store Layout with Customer Journey Path", use_container_width=True)
        
        # Add path analysis
        st.markdown("---")
        st.subheader("📊 Path Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Path Efficiency:**")
            # Use section names for filtering
            special_sections = set([s['name'] for s in store_data['sections'] if s.get('type') in ['entry', 'exit', 'checkout']])
            visited_sections = len(set(path_sections) - special_sections)
            total_sections = len(store_data['sections']) - len(special_sections)
            efficiency = (visited_sections / total_sections) * 100 if total_sections > 0 else 0
            st.metric("Coverage", f"{efficiency:.1f}%")
        
        with col2:
            st.write("**Path Characteristics:**")
            if len(path_sections) > 2:
                # Calculate path length (number of transitions)
                path_length = len(path_sections) - 1
                st.metric("Path Length", f"{path_length} steps")
    else:
        st.image(img, caption="Walmart Store Layout", use_container_width=True)

def display_quick_stats(results):
    """Display quick statistics about the simulation"""
    
    # Total time
    total_time = sum(results['dwell_time'].values())
    st.metric("⏱️ Total Time", f"{total_time} min")
    
    # Sections visited
    sections_visited = len(results['path'])
    st.metric("📍 Sections Visited", sections_visited)
    
    # Sections skipped
    sections_skipped = len(results['skipped'])
    st.metric("⏭️ Sections Skipped", sections_skipped)
    
    # Most time spent
    if results['dwell_time']:
        max_section = max(results['dwell_time'], key=results['dwell_time'].get)
        max_time = results['dwell_time'][max_section]
        st.metric("⏰ Longest Dwell", f"{max_section}: {max_time} min")
    
    # Path efficiency
    efficiency = (sections_visited / (sections_visited + sections_skipped)) * 100
    st.metric("📈 Path Efficiency", f"{efficiency:.1f}%")

def create_time_analysis(results):
    """Create time analysis chart"""
    
    if not results['dwell_time']:
        st.info("No dwell time data available")
        return
    
    # Create bar chart
    dwell_data = list(results['dwell_time'].items())
    df = pd.DataFrame(dwell_data)
    df.columns = ['Section', 'Time']
    df = df.sort_values('Time', ascending=True)
    
    fig = px.bar(df, x='Time', y='Section', orientation='h',
                 title="Time Spent per Section",
                 color='Time',
                 color_continuous_scale='Blues')
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_insights_panel(results):
    """Create insights and recommendations panel"""
    
    st.subheader("🧠 AI-Generated Insights")
    
    # Create dashboard instance
    dashboard = AnalyticsDashboard()
    insights = dashboard.generate_insights(results)
    
    for insight in insights:
        st.markdown(f"""
        <div class="insight-box">
            <strong>💡 {insight['title']}</strong><br>
            {insight['description']}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("🎯 Recommendations")
    recommendations = dashboard.generate_recommendations(results)
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")

# Persona summary table (skeleton)
def persona_summary_table():
    st.subheader("Persona Summary Table")
    # TODO: Aggregate and display summary stats for all personas
    st.info("Persona summary table coming soon!")

if __name__ == "__main__":
    main()