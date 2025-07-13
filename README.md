# 🛒 ShopTwin - Customer Journey Simulator

A full-stack web application that simulates in-store customer journeys at Walmart based on persona input. ShopTwin provides interactive visualizations, analytics, and AI-generated insights to help understand customer behavior patterns.

## 🚀 Features

### 🎭 Customer Personas
- **Eco-Conscious Millennial**: Values sustainability, prefers organic products
- **Budget Shopper**: Price-conscious, efficient shopping patterns
- **Convenience Seeker**: Time-focused, quick visits
- **Health Enthusiast**: Wellness-oriented, thorough product research
- **Family Planner**: Comprehensive shopping for family needs
- **Impulse Buyer**: Spontaneous purchases, browsing behavior

### 📊 Interactive Visualizations
- **Store Layout Heatmap**: 4x4 grid showing store sections with dwell times
- **Customer Path Animation**: Visual representation of shopping journey
- **Time Analysis Charts**: Bar charts showing time spent per section
- **Real-time Analytics**: Quick stats and efficiency metrics

### 🧠 AI-Generated Insights
- **Behavioral Analysis**: Persona-specific shopping pattern insights
- **Recommendations**: Actionable suggestions for store optimization
- **Path Efficiency**: Analysis of customer journey effectiveness
- **Dwell Time Analysis**: Understanding customer engagement

### ⚙️ Customizable Parameters
- **Budget Sensitivity**: 1-5 scale affecting shopping behavior
- **Shopping Preferences**: Eco-friendly, time constraints, health focus
- **Persona Selection**: Choose from 6 different customer types

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Visualization**: Plotly (interactive charts and heatmaps)
- **Data Processing**: Pandas (data manipulation)
- **Machine Learning**: Scikit-learn (optional ML simulation)
- **Data Format**: JSON (configuration and results)

## 📁 Project Structure

```
/shoptwin
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── simulation/
│   ├── __init__.py       # Package initialization
│   ├── logic.py          # Customer simulation logic
│   └── dashboard.py      # Analytics and insights
├── data/
│   ├── store_layout.json # Store configuration
│   └── persona_samples.json # Customer persona data
└── assets/               # Static assets (icons, logos)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shoptwin
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 🎯 Usage Guide

### 1. Select Customer Persona
- Choose from 6 different customer personas in the left sidebar
- Each persona has unique shopping behaviors and preferences

### 2. Configure Parameters
- **Budget Sensitivity**: Adjust from 1 (very budget-conscious) to 5 (price-insensitive)
- **Shopping Preferences**: Toggle options like eco-friendly, time constraints, health focus

### 3. Run Simulation
- Click the "🎯 Simulate Customer Journey" button
- Watch the simulation generate a customer path through the store

### 4. Analyze Results
- **Store Layout**: View the 4x4 grid with heatmap showing dwell times
- **Customer Path**: See the red line showing the customer's journey
- **Quick Stats**: Review key metrics like total time and efficiency
- **Analytics**: Explore detailed insights and recommendations

### 5. Interpret Insights
- **AI-Generated Insights**: Read behavioral analysis and recommendations
- **Time Analysis**: Understand which sections get the most attention
- **Path Efficiency**: See how effectively the customer navigated the store

## 📊 Understanding the Visualizations

### Store Layout Heatmap
- **Blue intensity**: Represents dwell time (darker = longer time)
- **Red path**: Shows customer journey through the store
- **Section labels**: Each cell represents a store section

### Time Analysis Chart
- **Horizontal bar chart**: Shows time spent in each section
- **Color gradient**: Indicates relative time spent
- **Sorted by time**: Most time-consuming sections first

### Quick Stats Panel
- **Total Time**: Complete shopping duration
- **Sections Visited**: Number of areas the customer explored
- **Path Efficiency**: Percentage of store sections utilized
- **Longest Dwell**: Section with maximum engagement

## 🧠 Simulation Logic

### Persona-Based Decision Making
Each persona follows specific behavioral patterns:

- **Preferred Sections**: Areas the persona is likely to visit
- **Avoided Sections**: Areas the persona typically skips
- **Dwell Time Multiplier**: How long the persona spends browsing
- **Path Style**: Shopping approach (quick, efficient, thorough, etc.)

### Preference Modifiers
- **Eco Preference**: Increases time in sustainable sections
- **Time Constraint**: Reduces overall shopping time
- **Health Focus**: Prioritizes wellness-related areas
- **Budget Sensitivity**: Affects premium section avoidance

### Path Generation Algorithms
- **Rule-based Logic**: Uses persona preferences and store layout
- **Randomization**: Adds realistic variability to paths
- **Efficiency Calculation**: Measures path effectiveness

## 🔧 Customization

### Adding New Personas
1. Edit `data/persona_samples.json`
2. Add new persona with shopping behavior data
3. Update `simulation/logic.py` persona data

### Modifying Store Layout
1. Edit `data/store_layout.json`
2. Adjust section positions and characteristics
3. Update visualization code in `app.py`

### Custom Insights
1. Modify `simulation/dashboard.py`
2. Add new insight templates
3. Update recommendation generation logic

## 📈 Future Enhancements

- **Real-time Data Integration**: Connect to actual store analytics
- **Advanced ML Models**: Implement more sophisticated prediction algorithms
- **Multi-store Support**: Simulate different store layouts
- **Seasonal Variations**: Add time-based behavioral changes
- **Mobile App**: Create companion mobile application
- **API Integration**: Provide REST API for external systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the code comments for implementation details

## 🙏 Acknowledgments

- Walmart for inspiration on retail analytics
- Streamlit team for the excellent web framework
- Plotly for powerful visualization capabilities
- The open-source community for various dependencies

---

**ShopTwin** - Understanding customer behavior, one simulation at a time! 🛒✨ 