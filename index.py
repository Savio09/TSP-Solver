"""
Interactive TSP Solver with Web Visualization
Uses Flask backend + HTML/CSS/JS frontend for animated solving
"""

from flask import Flask, render_template, jsonify, request
import numpy as np
import cvxpy as cp
from typing import List, Tuple, Dict
import json
import time

app = Flask(__name__)

# Problem data (same as before)
LOCATIONS = ["RH", "GGP", "FW", "YBG", "EXP", "MDP", "BH", "SP", "US", "P39"]

LOCATION_NAMES = {
    "RH": "Residence Hall (2550 Van Ness)",
    "GGP": "Golden Gate Park",
    "FW": "Fisherman's Wharf",
    "YBG": "Yerba Buena Gardens",
    "EXP": "Exploratorium",
    "MDP": "Mission Dolores Park",
    "BH": "Bernal Heights",
    "SP": "Salesforce Park",
    "US": "Union Square",
    "P39": "Pier 39",
}

COST_MATRIX = np.array(
    [
        [1000000, 37, 17, 24, 27, 28, 46, 27, 18, 16],
        [37, 1000000, 35, 25, 45, 16, 46, 28, 26, 37],
        [17, 35, 1000000, 26, 12, 42, 62, 24, 18, 8],
        [24, 25, 26, 1000000, 22, 21, 36, 7, 5, 22],
        [27, 45, 12, 22, 1000000, 32, 52, 16, 19, 8],
        [28, 16, 42, 21, 32, 1000000, 29, 20, 17, 44],
        [46, 46, 62, 36, 52, 29, 1000000, 40, 43, 60],
        [27, 28, 24, 7, 16, 20, 40, 1000000, 6, 19],
        [18, 26, 18, 5, 19, 17, 43, 6, 1000000, 12],
        [16, 37, 8, 22, 8, 44, 60, 19, 12, 1000000],
    ],
    dtype=float,
)

COORDS = {
    "RH": (37.7992733, -122.4236169),
    "GGP": (37.769089891975725, -122.48288044398697),
    "FW": (37.808554042534496, -122.41569725932902),
    "YBG": (37.785115559363426, -122.40223338631426),
    "EXP": (37.80181746236321, -122.39734800350925),
    "MDP": (37.76042200389471, -122.42688173419899),
    "BH": (37.74348530538466, -122.41361934584009),
    "SP": (37.78994295860268, -122.39614414583785),
    "US": (37.78760386789979, -122.40674289238692),
    "P39": (37.80884250074092, -122.40990683419665),
}


def solve_tsp_mtz(
    C: np.ndarray, solver_name: str = "ECOS_BB"
) -> Tuple[float, np.ndarray, List[int]]:
    """Solve TSP using MTZ formulation"""
    n = C.shape[0]
    X = cp.Variable((n, n), boolean=True)
    u = cp.Variable(n)

    constraints = []
    for i in range(n):
        constraints.append(X[i, i] == 0)

    for i in range(n):
        constraints.append(cp.sum(X[i, :]) == 1)
        constraints.append(cp.sum(X[:, i]) == 1)

    constraints.append(u[0] == 1)
    for i in range(1, n):
        constraints.append(u[i] >= 2)
        constraints.append(u[i] <= n)

    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                constraints.append(u[i] - u[j] + n * X[i, j] <= n - 1)

    objective = cp.Minimize(cp.sum(cp.multiply(C, X)))
    prob = cp.Problem(objective, constraints)

    # Use ECOS_BB which is included with cvxpy by default for MILP
    prob.solve(solver=cp.ECOS_BB)

    if prob.status not in ["optimal", "optimal_inaccurate"]:
        raise RuntimeError(f"Solver failed with status: {prob.status}")

    X_val = np.round(X.value).astype(int)

    tour = [0]
    current = 0
    for _ in range(n - 1):
        next_idx = np.where(X_val[current] == 1)[0][0]
        tour.append(next_idx)
        current = next_idx
    tour.append(0)

    return prob.value, X_val, tour


def solve_tsp_lazy_animated(C: np.ndarray, solver_name: str = "ECOS_BB") -> Dict:
    """Solve TSP using lazy method, returning animation steps"""
    n = C.shape[0]
    X = cp.Variable((n, n), boolean=True)

    constraints = []
    for i in range(n):
        constraints.append(cp.sum(X[i, :]) == 1)
        constraints.append(cp.sum(X[:, i]) == 1)
        constraints.append(X[i, i] == 0)

    subtour_cuts = []
    animation_steps = []
    iteration = 0

    while True:
        iteration += 1

        objective = cp.Minimize(cp.sum(cp.multiply(C, X)))
        prob = cp.Problem(objective, constraints)
        # Use ECOS_BB which is included with cvxpy by default for MILP
        prob.solve(solver=cp.ECOS_BB)

        if prob.status not in ["optimal", "optimal_inaccurate"]:
            raise RuntimeError(f"Solver failed with status: {prob.status}")

        X_val = np.round(X.value).astype(int)

        # Record current edges for animation
        edges = []
        for i in range(n):
            for j in range(n):
                if X_val[i, j] == 1:
                    edges.append([i, j])

        # Find connected components
        adj = {i: [] for i in range(n)}
        for i in range(n):
            for j in range(n):
                if X_val[i, j] == 1:
                    adj[i].append(j)

        visited = [False] * n
        components = []

        for start in range(n):
            if not visited[start]:
                stack = [start]
                comp = []
                visited[start] = True
                while stack:
                    u = stack.pop()
                    comp.append(u)
                    neighbors = adj[u] + [k for k in range(n) if u in adj[k]]
                    for v in neighbors:
                        if not visited[v]:
                            visited[v] = True
                            stack.append(v)
                components.append(sorted(comp))

        # Store this iteration's state (convert all to native Python types)
        step = {
            "iteration": int(iteration),
            "objective": float(prob.value),
            "edges": [[int(e[0]), int(e[1])] for e in edges],
            "components": [[int(x) for x in comp] for comp in components],
            "is_final": len(components) == 1 and len(components[0]) == n,
        }
        animation_steps.append(step)

        if len(components) == 1 and len(components[0]) == n:
            break

        # Add cuts for subtours
        new_cuts = 0
        for comp in components:
            if len(comp) < n:
                S = comp
                cut_expr = cp.sum([X[i, j] for i in S for j in S])
                constraints.append(cut_expr <= len(S) - 1)
                subtour_cuts.append(S)
                new_cuts += 1

        if new_cuts == 0:
            break

    # Reconstruct final tour
    tour = [0]
    current = 0
    for _ in range(n - 1):
        next_idx = np.where(X_val[current] == 1)[0][0]
        tour.append(next_idx)
        current = next_idx
    tour.append(0)

    return {
        "optimal_value": prob.value,
        "tour": tour,
        "subtour_cuts": subtour_cuts,
        "animation_steps": animation_steps,
    }


@app.route("/")
def index():
    """Render main page"""
    return render_template("index.html")


@app.route("/api/data")
def get_data():
    """Return location data for map initialization"""
    locations_data = []
    for i, code in enumerate(LOCATIONS):
        lat, lng = COORDS[code]
        locations_data.append(
            {
                "id": i,
                "code": code,
                "name": LOCATION_NAMES[code],
                "lat": lat,
                "lng": lng,
            }
        )

    return jsonify({"locations": locations_data, "cost_matrix": COST_MATRIX.tolist()})


@app.route("/api/solve", methods=["POST"])
def solve():
    """Solve TSP and return results"""
    data = request.json
    method = data.get("method", "mtz")
    solver = data.get("solver", "CBC")

    try:
        if method == "mtz":
            optimal_value, X_val, tour = solve_tsp_mtz(COST_MATRIX, solver)

            # Convert tour to edges for animation (convert to native Python int)
            edges = []
            for i in range(len(tour) - 1):
                edges.append([int(tour[i]), int(tour[i + 1])])

            return jsonify(
                {
                    "success": True,
                    "method": "MTZ",
                    "optimal_value": float(optimal_value),
                    "tour": [int(x) for x in tour],  # Convert numpy int64 to Python int
                    "edges": edges,
                    "animation_steps": [
                        {
                            "iteration": 1,
                            "objective": float(optimal_value),
                            "edges": edges,
                            "components": [list(range(10))],
                            "is_final": True,
                        }
                    ],
                }
            )

        else:  # lazy
            result = solve_tsp_lazy_animated(COST_MATRIX, solver)
            return jsonify(
                {
                    "success": True,
                    "method": "Lazy Subtours",
                    "optimal_value": float(result["optimal_value"]),
                    "tour": [int(x) for x in result["tour"]],  # Convert to Python int
                    "subtour_cuts": [
                        [int(x) for x in cut] for cut in result["subtour_cuts"]
                    ],
                    "animation_steps": result["animation_steps"],
                }
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
