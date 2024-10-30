import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import numpy as np
import json
import os
import math


class FloorplanApp:
    def __init__(self, root):
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self.image_path = None
        self.file_path = None

        self.root = root
        self.root.title("Floorplan Wall Detector")

        # Canvas setup
        self.canvas = tk.Canvas(root, width=1600, height=1200)
        self.canvas.pack(side=tk.LEFT)

        # Control panel for buttons
        control_panel = tk.Frame(root)
        control_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons for loading, zooming, modes, and finishing
        self.btn_load = tk.Button(control_panel, text="Load Floorplan", command=self.load_image)
        self.btn_load.pack(pady=10)
        
        self.btn_zoom_in = tk.Button(control_panel, text="+", command=self.zoom_in)
        self.btn_zoom_in.pack(pady=5)
        
        self.btn_zoom_out = tk.Button(control_panel, text="-", command=self.zoom_out)
        self.btn_zoom_out.pack(pady=5)

        # Mode buttons
        self.btn_view = tk.Button(control_panel, text="View", command=lambda: self.set_mode("view"))
        self.btn_view.pack(pady=5)
        
        self.btn_remove = tk.Button(control_panel, text="Remove Walls", command=lambda: self.set_mode("remove"))
        self.btn_remove.pack(pady=5)

        self.btn_add_wall = tk.Button(control_panel, text="Add Walls", command=lambda: self.set_mode("add_wall"))
        self.btn_add_wall.pack(pady=5)
        
        self.btn_add_dest = tk.Button(control_panel, text="Add/Remove Destination", command=lambda: self.set_mode("add_remove_dest"))
        self.btn_add_dest.pack(pady=5)

        self.btn_add_waypoint = tk.Button(control_panel, text="Add/Remove Waypoint", command=lambda: self.set_mode("add_remove_waypoint"))
        self.btn_add_waypoint.pack(pady=5)
        
        self.btn_reset_walls = tk.Button(control_panel, text="Reset Walls", command=self.reset_walls)
        self.btn_reset_walls.pack(pady=10)
        
        self.btn_finish = tk.Button(control_panel, text="Finish", command=self.finish)
        self.btn_finish.pack(pady=10)

        # Image and display variables
        self.image = None
        self.display_image = None
        self.mode = "view"
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.pan_start = None
        self.rect_start = None
        self.line_start = None

        # Data structures for storing walls, destinations, and waypoints
        self.walls = []
        self.destinations = {}
        self.waypoints = []
        self.hover_target = None  # Track hovered waypoint or destination
        self.temp_dest_coords = None  # Temporary destination coordinates

        # Bindings for panning and interactions
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)


    def load_image(self):
        default_dir = os.path.join(self.data_path, "floorplans")
        filepath = filedialog.askopenfilename(initialdir=default_dir, filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if not filepath:
            return
        self.image_path = filepath
        self.floor_name = os.path.basename(self.image_path).split('.')[0]
        self.image = cv2.imread(filepath)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        
        # Store original dimensions
        self.original_width, self.original_height = self.image.shape[1], self.image.shape[0]

        # Check for corresponding JSON file
        json_file = os.path.join(self.data_path, "maps", self.floor_name + ".json")
        if os.path.exists(json_file):
            with open(json_file, "r") as f:
                data = json.load(f)
                self.walls = [(tuple(wall[0]), tuple(wall[1])) for wall in data.get("walls", [])]
                self.waypoints = [tuple(waypoint) for waypoint in data.get("waypoints", [])]
            print(f"Loaded map from {json_file}")
        else:
            # No existing data, perform wall detection
            self.detect_walls()
        
        dest_file = os.path.join(self.data_path, "destinations.json")
        if os.path.exists(dest_file):
            with open(dest_file, "r") as f:
                all_destinations = json.load(f)
            # Load destinations for the current floor if available
            self.destinations = {name: tuple(coords) for name, coords in all_destinations.get(self.floor_name, {}).items()}
        else:
            self.destinations = {}

        self.update_canvas()


    def detect_walls(self):
        # Convert image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 100, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=10, minLineLength=20, maxLineGap=5)
        
        self.walls = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                self.walls.append(((x1, y1), (x2, y2)))


    def reset_walls(self):
        if messagebox.askyesno("Reset Walls", "Are you sure you want to reset walls? This will detect walls again and discard any current walls."):
            self.detect_walls()
            self.update_canvas()


    def update_canvas(self):
        if self.image is None:
            return

        zoomed_width = int(self.original_width * self.zoom_level)
        zoomed_height = int(self.original_height * self.zoom_level)
        resized_image = cv2.resize(self.image, (zoomed_width, zoomed_height), interpolation=cv2.INTER_LINEAR)
        
        for ((x1, y1), (x2, y2)) in self.walls:
            cv2.line(resized_image, (int(x1 * self.zoom_level), int(y1 * self.zoom_level)),
                     (int(x2 * self.zoom_level), int(y2 * self.zoom_level)), (255, 0, 0), 2)
        
        for name, (x, y, orientation) in self.destinations.items():
            color = (0, 0, 255) if (name, "dest") != self.hover_target else (255, 0, 0)
            cv2.circle(resized_image, (int(x * self.zoom_level), int(y * self.zoom_level)), 5, color, -1)
            cv2.putText(resized_image, name, (int(x * self.zoom_level) + 8, int(y * self.zoom_level) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            end_x = x + 20 * math.cos(math.radians(orientation))
            end_y = y + 20 * math.sin(math.radians(orientation))
            cv2.arrowedLine(resized_image, (int(x * self.zoom_level), int(y * self.zoom_level)),
                            (int(end_x * self.zoom_level), int(end_y * self.zoom_level)), color, 2)

        if self.temp_dest_coords:
            x, y, orientation = self.temp_dest_coords
            temp_color = (0, 255, 0)
            cv2.circle(resized_image, (int(x * self.zoom_level), int(y * self.zoom_level)), 5, temp_color, -1)
            cv2.putText(resized_image, "Temp", (int(x * self.zoom_level) + 8, int(y * self.zoom_level) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, temp_color, 1, cv2.LINE_AA)
            end_x = x + 20 * math.cos(math.radians(orientation))
            end_y = y + 20 * math.sin(math.radians(orientation))
            cv2.arrowedLine(resized_image, (int(x * self.zoom_level), int(y * self.zoom_level)),
                            (int(end_x * self.zoom_level), int(end_y * self.zoom_level)), temp_color, 2)

        for idx, (x, y) in enumerate(self.waypoints):
            color = (0, 255, 0) if (idx, "waypoint") != self.hover_target else (255, 0, 0)
            cv2.circle(resized_image, (int(x * self.zoom_level), int(y * self.zoom_level)), 5, color, -1)

        img_display = Image.fromarray(resized_image)
        self.display_image = ImageTk.PhotoImage(img_display)
        
        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.display_image)


    def zoom_in(self):
        self.zoom_level *= 1.1
        self.update_canvas()


    def zoom_out(self):
        self.zoom_level /= 1.1
        self.update_canvas()


    def set_mode(self, mode):
        self.mode = mode
        print(f"Mode set to {mode}")


    def on_click(self, event):
        x = int((event.x - self.offset_x) / self.zoom_level)
        y = int((event.y - self.offset_y) / self.zoom_level)
        
        if self.mode == "view":
            self.pan_start = (event.x, event.y)
        elif self.mode == "remove":
            self.rect_start = (x, y)
        elif self.mode == "add_wall":
            self.line_start = (x, y)
        elif self.mode == "add_remove_dest":
            if self.hover_target and self.hover_target[1] == "dest":
                name = self.hover_target[0]
                if messagebox.askyesno("Delete Destination", f"Do you want to delete destination '{name}'?"):
                    del self.destinations[name]
            else:
                self.temp_dest_coords = (x, y, 0)
            self.update_canvas()
        elif self.mode == "add_remove_waypoint":
            if self.hover_target and self.hover_target[1] == "waypoint":
                index = self.hover_target[0]
                if messagebox.askyesno("Delete Waypoint", "Do you want to delete this waypoint?"):
                    del self.waypoints[index]
            else:
                self.waypoints.append((x, y))
            self.update_canvas()


    def on_drag(self, event):
        x = int((event.x - self.offset_x) / self.zoom_level)
        y = int((event.y - self.offset_y) / self.zoom_level)

        if self.mode == "view" and self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.offset_x += dx
            self.offset_y += dy
            self.pan_start = (event.x, event.y)
            self.update_canvas()
        elif self.mode == "remove" and self.rect_start:
            self.update_canvas()
            self.canvas.create_rectangle(self.rect_start[0] * self.zoom_level + self.offset_x,
                                         self.rect_start[1] * self.zoom_level + self.offset_y,
                                         x * self.zoom_level + self.offset_x,
                                         y * self.zoom_level + self.offset_y,
                                         outline="red")
        elif self.mode == "add_remove_dest" and self.temp_dest_coords:
            start_x, start_y = self.temp_dest_coords[:2]
            angle = math.degrees(math.atan2(event.y - start_y, event.x - start_x))
            self.temp_dest_coords = (start_x, start_y, angle)
            self.update_canvas()


    def on_release(self, event):
        x = int((event.x - self.offset_x) / self.zoom_level)
        y = int((event.y - self.offset_y) / self.zoom_level)

        if self.mode == "remove" and self.rect_start:
            self.remove_walls_in_box(self.rect_start, (x, y))
            self.rect_start = None
            self.update_canvas()
        elif self.mode == "add_wall" and self.line_start:
            self.walls.append((self.line_start, (x, y)))
            self.line_start = None
            self.update_canvas()
        elif self.mode == "add_remove_dest" and self.temp_dest_coords:
            name = simpledialog.askstring("Input", "Destination Name:")
            if name:
                self.destinations[name] = self.temp_dest_coords
            self.temp_dest_coords = None
            self.update_canvas()


    def on_mouse_move(self, event):
        x = int((event.x - self.offset_x) / self.zoom_level)
        y = int((event.y - self.offset_y) / self.zoom_level)
        self.hover_target = None  # Reset hover

        for name, (dx, dy, angle) in self.destinations.items():
            if abs(dx - x) < 10 and abs(dy - y) < 10:
                self.hover_target = (name, "dest")
                break

        if not self.hover_target:
            for idx, (wx, wy) in enumerate(self.waypoints):
                if abs(wx - x) < 10 and abs(wy - y) < 10:
                    self.hover_target = (idx, "waypoint")
                    break

        self.update_canvas()


    def line_intersects_rectangle(self, x_min, x_max, y_min, y_max, line_start, line_end):
        def is_between(a, b, c):
            """ Check if c is between a and b """
            return min(a, b) <= c <= max(a, b)
        
        def on_line(p1, p2, p):
            """ Check if point p is on the line segment from p1 to p2 """
            (x1, y1), (x2, y2) = p1, p2
            (px, py) = p
            cross_product = (py - y1) * (x2 - x1) - (px - x1) * (y2 - y1)
            if abs(cross_product) != 0:
                return False
            return is_between(x1, x2, px) and is_between(y1, y2, py)

        def line_segment_intersect(p1, p2, q1, q2):
            """ Check if line segments p1p2 and q1q2 intersect """
            def direction(a, b, c):
                return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])
            
            d1 = direction(q1, q2, p1)
            d2 = direction(q1, q2, p2)
            d3 = direction(p1, p2, q1)
            d4 = direction(p1, p2, q2)
            
            if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
                return True
            if d1 == 0 and on_line(q1, q2, p1): return True
            if d2 == 0 and on_line(q1, q2, p2): return True
            if d3 == 0 and on_line(p1, p2, q1): return True
            if d4 == 0 and on_line(p1, p2, q2): return True
            return False

        corners = [(x_min, y_min), (x_min, y_max), (x_max, y_min), (x_max, y_max)]
        rectangle_sides = [
            (corners[0], corners[1]),
            (corners[1], corners[3]),
            (corners[3], corners[2]),
            (corners[2], corners[0])
        ]
        
        for side in rectangle_sides:
            if line_segment_intersect(line_start, line_end, *side):
                return True

        # Check if the line is completely inside the rectangle
        x1, y1 = line_start
        x2, y2 = line_end
        if (x_min <= x1 <= x_max and y_min <= y1 <= y_max and
            x_min <= x2 <= x_max and y_min <= y2 <= y_max):
            return True

        return False


    def remove_walls_in_box(self, start, end):
        x_min, x_max = min(start[0], end[0]), max(start[0], end[0])
        y_min, y_max = min(start[1], end[1]), max(start[1], end[1])
        updated_walls = []
        count = 0
        for wall in self.walls:
            if not self.line_intersects_rectangle(x_min, x_max, y_min, y_max, wall[0], wall[1]):
                updated_walls.append(wall)
            else:
                count += 1
        print(f"Removed {count} walls")
        self.walls = updated_walls


    def finish(self):
        if not self.walls and not self.destinations and not self.waypoints:
            messagebox.showwarning("Nothing to Save", "No data to save.")
            return

        # Ensure the maps directory exists
        maps_dir = os.path.join(self.data_path, "maps")
        if not os.path.exists(maps_dir):
            os.makedirs(maps_dir)

        # Save floor-specific map data
        output_file = os.path.join(maps_dir, f"{self.floor_name}.json")
        
        # Format data for JSON serialization
        data = {
            # "destinations": {name: (int(x), int(y)) for name, (x, y) in self.destinations.items()},
            "waypoints": [(int(x), int(y)) for x, y in self.waypoints],
            "walls": [[(int(start[0]), int(start[1])), (int(end[0]), int(end[1]))] for start, end in self.walls]
        }

        # Save to the specific floor's JSON file
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)

        # Save to the global destination file
        dest_file = os.path.join(self.data_path, "destinations.json")
        
        # Load existing destination data if the file exists
        if os.path.exists(dest_file):
            with open(dest_file, "r") as f:
                all_destinations = json.load(f)
        else:
            all_destinations = {}

        # Update the destination data for the current floor
        all_destinations[self.floor_name] = {name: (int(x), int(y)) for name, (x, y) in self.destinations.items()}
        
        # Write updated destinations back to the file
        with open(dest_file, "w") as f:
            json.dump(all_destinations, f, indent=4)

        messagebox.showinfo("Saved", f"Map saved in {output_file}, destinations updated in {dest_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FloorplanApp(root)
    root.mainloop()