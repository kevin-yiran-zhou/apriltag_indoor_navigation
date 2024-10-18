import json
import math
import heapq
import os

# Function to load map data
def load_map_data(floor_name):
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

    # Check for corresponding JSON file
    json_file = os.path.join(data_path, "maps", floor_name + ".json")
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            data = json.load(f)
            walls = [(tuple(wall[0]), tuple(wall[1])) for wall in data.get("walls", [])]
            waypoints = [tuple(waypoint) for waypoint in data.get("waypoints", [])]
        print(f"Loaded map from {json_file}")
    else:
        print(f"Map file {json_file} not found.")
        return
    
    dest_file = os.path.join(data_path, "destinations.json")
    if os.path.exists(dest_file):
        with open(dest_file, "r") as f:
            all_destinations = json.load(f)
        # Load destinations for the current floor if available
        destinations = {name: tuple(coords) for name, coords in all_destinations.get(floor_name, {}).items()}
    else:
        print(f"Destinations file {dest_file} not found.")
        return

    return walls, waypoints, destinations


# Function to check if a line intersects any walls
def line_is_clear(point1, point2, walls):
    for wall in walls:
        if lines_intersect(point1, point2, wall[0], wall[1]):
            return False
    return True


# Line intersection function
def lines_intersect(p1, p2, q1, q2):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    return (ccw(p1, q1, q2) != ccw(p2, q1, q2)) and (ccw(p1, p2, q1) != ccw(p1, p2, q2))


# Heuristic function for A* (Euclidean distance)
def heuristic(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


# A* search algorithm
def a_star_search(graph, start, goal):
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while queue:
        _, current = heapq.heappop(queue)
        
        if current == goal:
            break
        
        for next_node in graph[current]:
            new_cost = cost_so_far[current] + graph[current][next_node]
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(next_node, goal)
                heapq.heappush(queue, (priority, next_node))
                came_from[next_node] = current
    
    # Reconstruct path
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


# Function to build the graph
def build_graph(waypoints, walls, start_point, end_point):
    nodes = waypoints.copy()
    nodes.extend([start_point, end_point])
    graph = {node: {} for node in nodes}
    
    for i, node_a in enumerate(nodes):
        for node_b in nodes[i+1:]:
            if line_is_clear(node_a, node_b, walls):
                distance = heuristic(node_a, node_b)
                graph[node_a][node_b] = distance
                graph[node_b][node_a] = distance
    return graph


# Main function to find the path
def find_optimal_path(floor_name, start_pose, end_point):
    walls, waypoints, destinations = load_map_data(floor_name)
    
    # If the end point is a destination name, get its coordinates
    if isinstance(end_point, str) and end_point in destinations:
        end_point = destinations[end_point]
    elif isinstance(end_point, tuple):
        pass  # Use the provided coordinates
    else:
        raise ValueError("End point must be a tuple of coordinates or a valid destination name.")
    
    start_point = (start_pose[0], start_pose[1])
    
    # Build the graph
    print("Building graph...")
    graph = build_graph(waypoints, walls, start_point, end_point)
    print("Graph built.")
    
    # Check if start and end points are connected to the graph
    if start_point not in graph or end_point not in graph:
        print("No path found: Start or end point is not connected to the graph.")
        return None
    
    # Find the path using A*
    print("Finding optimal path...")
    path = a_star_search(graph, start_point, end_point)
    print("Optimal path found.")
    
    return path


# Example usage
if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    floor_name = "basic-floor-plan"
    start_pose = (543, 149, 0)  # x, y, angle in degrees
    end_point = "Bedroom 1"  # Destination name or (x, y) coordinates
    
    path = find_optimal_path(floor_name, start_pose, end_point)
    if path:
        print("Optimal path:")
        for point in path:
            print(point)
    else:
        print("No path found.")