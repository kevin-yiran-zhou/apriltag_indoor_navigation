import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import os
import math
from pathfinder import find_optimal_path
import json

class PathfinderGUI:
    def __init__(self, root):
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self.image_path = None

        self.root = root
        self.root.title("Pathfinder")

        # Canvas setup
        self.canvas = tk.Canvas(root, width=1600, height=1200)
        self.canvas.pack(side=tk.LEFT)

        # Control panel for buttons
        control_panel = tk.Frame(root)
        control_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons for loading the map, finding path, and zooming
        self.btn_load = tk.Button(control_panel, text="Load Floorplan", command=self.load_image)
        self.btn_load.pack(pady=10)

        self.btn_find_path = tk.Button(control_panel, text="Find Path", command=self.find_path)
        self.btn_find_path.pack(pady=10)

        self.btn_zoom_in = tk.Button(control_panel, text="+", command=self.zoom_in)
        self.btn_zoom_in.pack(pady=5)

        self.btn_zoom_out = tk.Button(control_panel, text="-", command=self.zoom_out)
        self.btn_zoom_out.pack(pady=5)

        # Image and display variables
        self.image = None
        self.display_image = None
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.pan_start = None
        self.start_pose = None
        self.dest_point = None
        self.path = None
        self.walls = []
        self.destinations = {}
        self.waypoints = []

        self.selected_dest_point = None
        self.is_defining_pose = False

        # Bindings for interactions
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def load_image(self):
        default_dir = os.path.join(self.data_path, "floorplans")
        filepath = filedialog.askopenfilename(initialdir=default_dir, filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if not filepath:
            return
        self.image_path = filepath
        self.floor_name = os.path.basename(self.image_path).split('.')[0]  # Set image_name based on the file
        self.image = cv2.imread(filepath)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

        # Store original dimensions
        self.original_width, self.original_height = self.image.shape[1], self.image.shape[0]

        # Load map data (walls, waypoints)
        json_file = os.path.join(self.data_path, "maps", self.floor_name + ".json")
        if os.path.exists(json_file):
            with open(json_file, "r") as f:
                data = json.load(f)
                self.walls = [(tuple(wall[0]), tuple(wall[1])) for wall in data.get("walls", [])]
                self.waypoints = [tuple(waypoint) for waypoint in data.get("waypoints", [])]
            print(f"Loaded map from {json_file}")
        else:
            print(f"No map file found for {self.floor_name}")
            return

        # Load destinations from the global destinations.json file
        dest_file = os.path.join(self.data_path, "destinations.json")
        if os.path.exists(dest_file):
            with open(dest_file, "r") as f:
                all_destinations = json.load(f)
            # Load destinations for the current floor only
            self.destinations = {name: tuple(coords) for name, coords in all_destinations.get(self.floor_name, {}).items()}
        else:
            print(f"Destinations file not found.")
            self.destinations = {}

        self.update_canvas()

    def zoom_in(self):
        self.zoom_level *= 1.1
        self.update_canvas()

    def zoom_out(self):
        self.zoom_level /= 1.1
        self.update_canvas()

    def update_canvas(self):
        if self.image is None:
            return

        zoomed_width = int(self.original_width * self.zoom_level)
        zoomed_height = int(self.original_height * self.zoom_level)
        resized_image = cv2.resize(self.image, (zoomed_width, zoomed_height), interpolation=cv2.INTER_LINEAR)

        # Draw walls on the image
        for ((x1, y1), (x2, y2)) in self.walls:
            cv2.line(resized_image, (int(x1 * self.zoom_level), int(y1 * self.zoom_level)),
                     (int(x2 * self.zoom_level), int(y2 * self.zoom_level)), (255, 0, 0), 2)

        # Draw destinations, highlighting the selected one in red
        for name, (x, y) in self.destinations.items():
            color = (0, 0, 255)  # Default blue color
            if self.selected_dest_point == name:
                color = (255, 0, 0)  # Selected destination is red
            cv2.circle(resized_image, (int(x * self.zoom_level), int(y * self.zoom_level)), 5, color, -1)
            cv2.putText(resized_image, name, (int(x * self.zoom_level) + 8, int(y * self.zoom_level) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # Draw the starting point with an orientation arrow if defined
        if self.start_pose:
            x, y, theta = self.start_pose
            arrow_length = 30
            end_x = x + arrow_length * math.cos(math.radians(theta))
            end_y = y + arrow_length * math.sin(math.radians(theta))
            cv2.arrowedLine(resized_image, (int(x * self.zoom_level), int(y * self.zoom_level)),
                            (int(end_x * self.zoom_level), int(end_y * self.zoom_level)), (0, 255, 0), 2)

        # Draw the calculated path
        if self.path:
            for i in range(len(self.path) - 1):
                cv2.line(resized_image,
                         (int(self.path[i][0] * self.zoom_level), int(self.path[i][1] * self.zoom_level)),
                         (int(self.path[i + 1][0] * self.zoom_level), int(self.path[i + 1][1] * self.zoom_level)),
                         (0, 255, 255), 5)

        img_display = Image.fromarray(resized_image)
        self.display_image = ImageTk.PhotoImage(img_display)

        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.display_image)

    def on_click(self, event):
        x = int((event.x - self.offset_x) / self.zoom_level)
        y = int((event.y - self.offset_y) / self.zoom_level)

        # If no start pose, allow setting start pose
        if self.start_pose is None:
            self.start_pose = (x, y, 0)  # Default orientation is 0 degrees
            self.is_dragging_pose = True  # Start dragging to adjust orientation
        else:
            # Select destination
            selected = False
            for name, (dx, dy) in self.destinations.items():
                if abs(dx - x) < 10 and abs(dy - y) < 10:
                    self.selected_dest_point = name  # Highlight selected destination
                    print(f"Destination selected: {self.selected_dest_point}")
                    selected = True
                    break

            if not selected:
                self.selected_dest_point = None  # Deselect if no destination selected

        self.update_canvas()

    def on_drag(self, event):
        # Adjust orientation based on dragging
        if self.is_dragging_pose:
            x, y = int((event.x - self.offset_x) / self.zoom_level), int((event.y - self.offset_y) / self.zoom_level)
            start_x, start_y = self.start_pose[:2]
            angle = math.degrees(math.atan2(y - start_y, x - start_x))
            self.start_pose = (start_x, start_y, angle)
            self.update_canvas()

    def on_release(self, event):
        if self.is_dragging_pose:
            # Stop dragging, finalize start pose
            self.is_dragging_pose = False

        self.update_canvas()

    def find_path(self):
        if self.start_pose is None or self.selected_dest_point is None:
            messagebox.showwarning("Missing Data", "Please select both a start point and a destination.")
            return

        # Call the pathfinding algorithm
        start_pose = (self.start_pose[0], self.start_pose[1], self.start_pose[2])
        try:
            self.path = find_optimal_path(self.floor_name, start_pose, self.selected_dest_point)
        except Exception as e:
            messagebox.showwarning("Pathfinding Error", f"Error finding path: {e}")
            self.path = None

        self.update_canvas()


if __name__ == "__main__":
    root = tk.Tk()
    app = PathfinderGUI(root)
    root.mainloop()
