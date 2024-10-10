import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import json
import os

class FloorplanApp:
    def __init__(self, root):
        self.script_path = os.path.dirname(os.path.abspath(__file__))
        self.image_path = None
        self.file_path = None

        self.root = root
        self.root.title("Floorplan Wall Detector")
        
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()
        
        self.btn_load = tk.Button(root, text="Load Floorplan", command=self.load_image)
        self.btn_load.pack()
        
        self.btn_finish = tk.Button(root, text="Finish", command=self.finish)
        self.btn_finish.pack()
        
        self.image = None
        self.display_image = None
        self.detected_walls = []
        self.rects_to_remove = []
        self.rect_start = None
        
        self.canvas.bind("<Button-1>", self.start_draw_rect)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw_rect)


    def load_image(self):
        default_dir = os.path.join(self.script_path, "floorplans")
        print(default_dir)
        filepath = filedialog.askopenfilename(initialdir=default_dir, filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if not filepath:
            return
        self.image_path = filepath
        self.image = cv2.imread(filepath)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        
        self.detect_walls()
        self.update_canvas()


    def detect_walls(self):
        hsv = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
        lower_color = np.array([0, 0, 0])
        upper_color = np.array([180, 255, 70])
        mask = cv2.inRange(hsv, lower_color, upper_color)
        
        self.detected_walls = []
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Represent the wall as a line segment from the top-left to the bottom-right of the bounding box
            self.detected_walls.append(((x, y), (x + w, y + h)))


    def update_canvas(self):
        if self.image is None:
            return
        
        # Create a blank white image
        blank_image = np.ones_like(self.image) * 255
        
        # Draw each detected wall as a line on the blank image
        for ((x1, y1), (x2, y2)) in self.detected_walls:
            cv2.line(blank_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        # Convert the blank image to PIL format for displaying
        img_display = Image.fromarray(blank_image)
        self.display_image = ImageTk.PhotoImage(image=img_display.resize((800, 600), Image.ANTIALIAS))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.display_image)


    def start_draw_rect(self, event):
        self.rect_start = (event.x, event.y)


    def draw_rect(self, event):
        if self.rect_start is None:
            return
        self.update_canvas()
        x1, y1 = self.rect_start
        x2, y2 = event.x, event.y
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)


    def end_draw_rect(self, event):
        if self.rect_start is None:
            return
        x1, y1 = self.rect_start
        x2, y2 = event.x, event.y
        self.rects_to_remove.append(((x1, y1), (x2, y2)))
        self.remove_walls_in_box(x1, y1, x2, y2)
        self.rect_start = None
        self.update_canvas()
        

    def remove_walls_in_box(self, x1, y1, x2, y2):
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        self.detected_walls = [
            wall for wall in self.detected_walls
            if not (x1 <= wall[0][0] <= x2 and y1 <= wall[0][1] <= y2)
        ]


    def finish(self):
        if not self.detected_walls:
            messagebox.showwarning("No Walls Detected", "No walls to save.")
            return

        # Ensure 'maps' directory exists
        maps_dir = os.path.join(self.script_path, "maps")
        if not os.path.exists(maps_dir):
            os.makedirs(maps_dir)
            
        # Create the JSON file name based on the image name
        image_name = os.path.basename(self.image_path).split('.')[0]
        output_file = os.path.join(maps_dir, f"{image_name}.json")
        
        # Prepare wall segments data
        walls_segments = [{"start": start, "end": end} for start, end in self.detected_walls]
        
        # Save to JSON file
        with open(output_file, "w") as f:
            json.dump(walls_segments, f, indent=4)
        
        messagebox.showinfo("Saved", f"Walls saved as line segments in {output_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FloorplanApp(root)
    root.mainloop()
