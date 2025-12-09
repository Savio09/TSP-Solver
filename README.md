# San Francisco TSP Solver - Interactive Web Application

A production-ready web application for visualizing and solving the Traveling Salesman Problem (TSP) across 10 locations in San Francisco. Built with Flask backend and interactive JavaScript frontend featuring real-time animations and an interactive map powered by Leaflet.js.

## Project Overview

This application was developed for a Minerva University Optimization course project. It implements two different approaches to solving the TSP with animated visualizations:

1. **MTZ (Miller-Tucker-Zemlin)**: Classic formulation with all subtour elimination constraints included upfront
2. **Lazy Subtour Elimination**: Iterative approach that adds constraints only when subtours are detected, with step-by-step animation showing the subtour elimination process

## Problem Instance

The tour visits 10 locations in San Francisco, starting and ending at:

- **RH** - Residence Hall (2550 Van Ness Avenue) - Start/End Point
- **GGP** - Golden Gate Park
- **FW** - Fisherman's Wharf
- **YBG** - Yerba Buena Gardens
- **EXP** - Exploratorium
- **MDP** - Mission Dolores Park
- **BH** - Bernal Heights
- **SP** - Salesforce Park
- **US** - Union Square
- **P39** - Pier 39

All locations use real geographic coordinates (latitude and longitude) and estimated travel times in minutes.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Modern web browser (Chrome, Firefox, Safari, or Edge)

### Installation

1. Clone or download this repository

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask application:

   ```bash
   python index.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

The application will start with an interactive map showing all 10 San Francisco locations.

## Live Demo

A live version of this application is deployed on Vercel. Visit the deployment to see the TSP solver in action without local setup.

Note: Initial load may take a few seconds due to serverless cold start.

## Dependencies

### Backend (Python)

- **Flask** - Web application framework and REST API
- **numpy** - Numerical computations and matrix operations
- **cvxpy** - Convex optimization modeling and MILP formulation

### Frontend (JavaScript/CSS)

- **Leaflet.js** - Interactive map library (loaded via CDN)
- **Vanilla JavaScript** - No additional frameworks required
- **CSS3** - Modern styling with animations

### MILP Solvers

The default solver is CBC (Coin-or Branch and Cut), which is included with cvxpy. Alternative solvers can be selected:

- **CBC** (default) - Open-source, reliable
- **GLPK_MI** - GNU Linear Programming Kit
- **HiGHS** - High-performance solver
- **SCIP** - Academic solver (requires separate installation)
- **GUROBI** - Commercial solver (requires license)

## How to Use

1. **Launch the application**

   - Start the Flask server: `python index.py`
   - Open browser to http://localhost:5000

2. **Select solution method**

   - Click "Solve with MTZ" for the compact formulation
   - Click "Solve with Lazy Subtours" for the iterative approach with animations

3. **Watch the optimization process**

   - For MTZ: Solution appears after single solve (5-10 seconds)
   - For Lazy: Animation shows each iteration as subtours are detected and eliminated
   - Green markers indicate current edges being explored
   - Red lines show the evolving tour

4. **View results**

   - Total travel time displayed in minutes
   - Complete tour path shown on map
   - Ordered list of locations visited
   - For Lazy method: Summary of subtours eliminated at each iteration

5. **Change solver** (optional)
   - Select different MILP solver from dropdown
   - Re-run optimization to compare performance

## 🧮 Optimization Model

### Decision Variables

- **X[i,j]**: Binary variable (0 or 1) indicating if the tour goes from location i to location j
- **u[i]** (MTZ only): Continuous variable representing the order of visit to location i

### Constraints

**Both methods include:**

- **Degree constraints**: Each location has exactly one incoming and one outgoing edge
- **No self-loops**: Cannot travel from a location to itself

**MTZ method adds:**

- **MTZ subtour elimination**: `u[i] - u[j] + n*X[i,j] ≤ n - 1` for all i,j ≠ 0
- Forces a consistent ordering of visits, preventing disconnected subtours

**Lazy method adds:**

- **Dynamic subtour cuts**: When a solution contains multiple disconnected cycles, adds constraints:
  - `Σ(i,j∈S) X[i,j] ≤ |S| - 1` for each subtour S
- Iteratively refines the solution until a single tour is found

### Objective Function

Minimize total travel time: `Σ(i,j) C[i,j] * X[i,j]`

Where C[i,j] is the travel time (in minutes) from location i to location j.

## Cost Matrix

The 10×10 cost matrix represents travel times in minutes between all location pairs. The diagonal contains large penalties (1,000,000) to prevent self-loops. These values are based on estimated travel times within San Francisco accounting for distance, traffic patterns, and typical travel modes.

## Interactive Visualization Features

The application provides a rich interactive map experience:

### Map Display

- **Leaflet.js powered map**: Interactive pan and zoom capabilities
- **Real San Francisco geography**: Actual street map with OpenStreetMap tiles
- **Location markers**: All 10 destinations clearly marked
- **Custom styling**: Start/end point distinguished from other locations

### Animation System

- **Real-time edge drawing**: Watch as the algorithm explores different connections
- **Subtour detection**: For lazy method, see disconnected cycles being identified
- **Progressive rendering**: Each iteration displayed step-by-step
- **Color coding**: Different colors for intermediate vs. final solutions
- **Smooth transitions**: CSS-powered animations for professional appearance

### Results Display

- **Total travel time**: Displayed in minutes
- **Tour sequence**: Ordered list of location codes and full names
- **Iteration count**: For lazy method, shows number of refinement steps
- **Subtour information**: Details on which node sets were eliminated

## Application Architecture

### Backend (Flask - Python)

```
index.py
├── Flask routes
│   ├── GET /           - Serves main HTML page
│   ├── GET /api/data   - Returns location and cost data
│   └── POST /api/solve - Executes TSP solver and returns results
├── Solver functions
│   ├── solve_tsp_mtz()              - MTZ formulation
│   └── solve_tsp_lazy_animated()    - Lazy cuts with animation data
└── Data structures
    ├── LOCATIONS, LOCATION_NAMES
    ├── COST_MATRIX
    └── COORDS
```

### Frontend (HTML/CSS/JavaScript)

```
templates/index.html
├── HTML structure
│   ├── Control panel (method and solver selection)
│   ├── Map container (Leaflet.js)
│   └── Results panel (tour information)
├── CSS styling
│   ├── Modern responsive layout
│   ├── Animation keyframes
│   └── Color scheme and typography
└── JavaScript logic
    ├── Map initialization and marker placement
    ├── API calls to Flask backend
    ├── Animation controller for lazy method
    └── Results rendering and display
```

## Customization Guide

### Modifying Locations

To update location data, edit `index.py`:

```python
# Update location codes
LOCATIONS = ["RH", "GGP", "FW", ...]

# Update location names
LOCATION_NAMES = {
    "RH": "Your Location Name",
    ...
}

# Update coordinates (latitude, longitude)
COORDS = {
    "RH": (37.7992733, -122.4236169),
    ...
}
```

### Updating Travel Times

Modify the `COST_MATRIX` in `index.py`. Ensure the matrix is symmetric and has large values (1,000,000) on the diagonal.

### Changing Map Appearance

Edit `templates/index.html`:

- **Map tiles**: Change OpenStreetMap URL to other tile providers
- **Marker colors**: Modify CSS in the `<style>` section
- **Animation speed**: Adjust `setTimeout` values in JavaScript
- **Zoom level**: Change initial map zoom parameter

### Adding More Locations

1. Extend the `LOCATIONS` list with new codes
2. Add entries to `LOCATION_NAMES` dictionary
3. Add coordinates to `COORDS` dictionary
4. Expand `COST_MATRIX` to n×n dimensions (where n is total locations)
5. Test with both MTZ and Lazy methods

## Technical Implementation Details

### Optimization Model

**Decision Variables:**

- X[i,j]: Binary variables (0 or 1) for edge selection
- u[i]: Continuous variables for MTZ ordering (MTZ method only)
  **Constraints:**
- Degree constraints: One incoming and one outgoing edge per location
- No self-loops: X[i,i] = 0 for all i
- MTZ subtour elimination: u[i] - u[j] + n\*X[i,j] <= n - 1
- Lazy subtour cuts: Sum of edges within subtour S <= |S| - 1

**Objective Function:**
Minimize total travel time = Sum over all i,j of C[i,j] \* X[i,j]

### Solver Implementation

Both methods use cvxpy for MILP formulation:

**MTZ Method:**

1. Create binary variables X[i,j] and continuous variables u[i]
2. Add all constraints upfront (degree + MTZ)
3. Solve once with MILP solver
4. Extract tour from solution

**Lazy Method:**

1. Create binary variables X[i,j]
2. Add only degree constraints initially
3. Solve MILP
4. Detect subtours in solution using graph traversal
5. Add cuts for each subtour found
6. Repeat steps 3-5 until single tour obtained
7. Return tour with animation data for each iteration

## Academic Context

This project demonstrates key concepts in optimization:

### Mathematical Concepts

- Mixed-Integer Linear Programming (MILP) formulation
- Binary decision variables and constraints
- Subtour elimination techniques (MTZ vs. lazy constraints)
- NP-hard problem solving with exact methods
- Branch-and-bound algorithms (used internally by solvers)

### Software Engineering

- RESTful API design with Flask
- Frontend-backend separation
- Asynchronous JavaScript for smooth UX
- Responsive web design
- Data serialization (JSON)

### Learning Objectives

- Understanding TSP complexity and formulations
- Comparing different constraint strategies
- Practical implementation of optimization algorithms
- Creating interactive visualizations for technical concepts
- Building production-ready web applications

## Project Structure

```
tsp-solver/
├── index.py                # Flask backend with TSP solvers
├── templates/
│   └── index.html          # Frontend UI with Leaflet.js map
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel deployment configuration
├── runtime.txt            # Python version for deployment
├── README.md              # This file
└── CHANGELOG.md           # Version history and fixes
```

## Troubleshooting

### Solver Errors

**Problem:** "The solver CBC is not installed"

**Solution:** Install CBC solver:

```bash
pip install cvxopt
# or try different solver
```

### Display Issues

**Problem:** Map doesn't load or shows gray tiles

**Solution:**

- Check internet connection (Leaflet.js loads from CDN)
- Verify browser console for JavaScript errors
- Try different browser (Chrome recommended)

**Problem:** Animation doesn't play smoothly

**Solution:**

- Close other browser tabs to free memory
- Animation speed can be adjusted in JavaScript code
- Try MTZ method if lazy animation is slow

### Installation Issues

**Problem:** cvxpy installation fails

**Solution:** Install with pre-built binaries:

```bash
pip install --upgrade pip
pip install cvxpy --prefer-binary
```

**Problem:** Flask import error

**Solution:** Ensure virtual environment is activated and dependencies installed:

```bash
pip install -r requirements.txt
```

## License

This project is created for academic purposes as part of a Minerva University course project CS164 Optimizations.

## Author

Built with ❤️ by [Fortune Declan](https://declann.codes) & [James Olaitan](https://github.com/JamesOlaitan)

## Acknowledgments

- Prof. John Levitt
- cvxpy development team for optimization framework
- Leaflet.js community for mapping library
- Open-source MILP solver communities (CBC, GLPK, HiGHS)
- OpenStreetMap contributors for map tiles

### Web Technologies

- Flask Documentation: https://flask.palletsprojects.com/
- Leaflet.js Documentation: https://leafletjs.com/
- OpenStreetMap: https://www.openstreetmap.org/

---

**Note**: This application is designed for educational purposes and demonstration of optimization concepts. For production routing applications with many locations, consider specialized TSP solvers like Concorde, LKH, or Google OR-Tools.
