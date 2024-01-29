# ImageAnnotator
# Author: Longbin Jin
# MIT License
# Copyright (c) 2023 Longbin Jin
# Description: This script is used for annotating images with points and child IDs.

import os
import json
import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ExifTags

class ImageAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1280x720")  # Set the window size
        self.main_folder_path = ""  # Store the main folder path
        self.group_folder_path = ""
        self.single_folder_path = ""
        self.children = []
        self.image_files = []
        self.current_image_index = 0
        self.annotations = []
        self.last_mark = None  # Track the last mark
        self.scale_factor = 1  # Scaling factor for the resized image


        self.select_folder_button = Button(root, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack()

        self.canvas = Canvas(root, cursor="cross", width=1000, height=720)  # Set canvas size
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)

        self.control_panel = Frame(root, width=280, height=720)  # Control panel for buttons and options
        self.control_panel.pack(side=RIGHT, fill=Y)
        self.control_panel.pack_propagate(False)  # Prevent resizing of control panel

    def select_folder(self):
        self.main_folder_path = filedialog.askdirectory()  # Store the selected main folder path
        if self.main_folder_path:
            self.group_folder_path = os.path.join(self.main_folder_path, "group")
            self.single_folder_path = os.path.join(self.main_folder_path, "single")
            self.children = self.load_children(self.single_folder_path)
            self.image_files = os.listdir(self.group_folder_path)
            self.image_files = [file for file in self.image_files if file.endswith(('.jpeg', '.jpg', '.png'))]
            self.image_files = sorted(self.image_files, key=lambda x: x.split('.')[0])

            self.setup_annotation_controls()
            self.load_image()
            self.select_folder_button.destroy()  # Remove the select folder button

    def setup_annotation_controls(self):
        """Setup controls for annotation after a folder is selected."""
        for widget in self.control_panel.winfo_children():
            widget.destroy()

        Label(self.control_panel, text="Select Child").pack()  # Add label for child selection

        self.child_name_var = StringVar(self.root)
        child_names = [child['name'] for child in self.children]
        self.child_name_var.set(child_names[0])  # Set a default value
        self.child_id_option_menu = OptionMenu(self.control_panel, self.child_name_var, *child_names)
        self.child_id_option_menu.pack()

        self.save_button = Button(self.control_panel, text="Save", command=self.save_annotation)
        self.next_image_button = Button(self.control_panel, text="Next Image", command=self.next_image)

        self.save_button.pack()
        self.next_image_button.pack()

        self.saved_info_label = Label(self.control_panel, text="", justify=LEFT)
        self.saved_info_label.pack()

        # Re-establish the canvas click event binding
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def load_children(self, path):
        children = []
        for index, child_name in enumerate(sorted(os.listdir(path)), start=1):
            if os.path.isdir(os.path.join(path, child_name)):
                children.append({"child_id": index, "name": child_name})
        return children

    def get_image_info(self):
        """Get information for each image in the group folder."""
        images = []
        for image_id, image_name in enumerate(sorted(self.image_files), start=1):
            image_path = os.path.join(self.group_folder_path, image_name)
            with Image.open(image_path) as img:
                width, height = img.size
            images.append({"file_name": image_name, "height": height, "width": width, "image_id": image_id})
        return images
    
    def resize_image(self, image):
        """Resize the image so that its largest axis does not exceed 1000 pixels."""
        max_size = (1000, 720)  # Resize considering the canvas size
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image

    def load_image(self):
        image_path = os.path.join(self.group_folder_path, self.image_files[self.current_image_index])
        self.original_image = Image.open(image_path)

        # Check for and apply EXIF orientation data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(self.original_image._getexif().items())

            if exif[orientation] == 3:
                self.original_image = self.original_image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                self.original_image = self.original_image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                self.original_image = self.original_image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # No EXIF data or orientation data not found
            pass

        self.resized_image = self.resize_image(self.original_image.copy())
        self.scale_factor = max(self.original_image.size[0] / self.resized_image.size[0], 
                                self.original_image.size[1] / self.resized_image.size[1])

        self.tk_image = ImageTk.PhotoImage(self.resized_image)
        self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.last_mark = None

    def on_canvas_click(self, event):
        if self.last_mark is not None:
            self.canvas.delete(self.last_mark)  # Remove the last drawn point
        self.last_mark = self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill='red')

    def update_saved_info_display(self):
        """Update the display with all saved points for the current image."""
        image_id = self.current_image_index + 1

        # Create a dictionary to map child IDs to names
        child_id_to_name = {child['child_id']: child['name'] for child in self.children}

        saved_points = []
        for ann in self.annotations:
            if ann['image_id'] == image_id:
                child_name = child_id_to_name.get(ann['child_id'], "Unknown")
                saved_points.append(f"{child_name}: {ann['center']}")

        saved_info_text = "\n".join(saved_points)
        self.saved_info_label.config(text=saved_info_text)

    def save_annotation(self, show_message=True):
        if self.last_mark is None:
            if show_message:
                messagebox.showerror("Error", "You haven't selected the point of child!")
            return

        x, y = self.canvas.coords(self.last_mark)[:2]
        original_x, original_y = int(x * self.scale_factor), int(y * self.scale_factor)
        selected_child_name = self.child_name_var.get()
        # Find the child ID corresponding to the selected name
        child_id = next((child['child_id'] for child in self.children if child['name'] == selected_child_name), None)

        if child_id is not None:
            # ... save the annotation with the child ID ...
            image_id = self.current_image_index + 1

            # Check if child_id already exists for this image and update it
            updated = False
            for ann in self.annotations:
                if ann['child_id'] == child_id and ann['image_id'] == image_id:
                    ann['center'] = [original_x, original_y]
                    updated = True
                    break

            if not updated:
                annotation = {
                    "image_id": image_id,
                    "center": [original_x, original_y],
                    "child_id": child_id
                }
                self.annotations.append(annotation)

            self.update_saved_info_display()  # Update display with all saved points for the current image

            self.canvas.delete(self.last_mark)  # Clear the point after saving
            self.last_mark = None

    def next_image(self):
        self.save_annotation(show_message=False)  # Save without showing message
        self.export_annotations()  # Export annotations to a file
        self.saved_info_label.config(text="")  # Clear the saved info display

        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image()
        else:
            self.display_all_done()

    def display_all_done(self):
        """Display 'All is done' message, clear the canvas, and remove buttons."""
        self.canvas.delete("all")  # Clear the canvas
        self.canvas.create_text(500, 360, text="All is done", font=("Arial", 24), fill="black")
        self.canvas.unbind("<Button-1>")  # Unbind canvas click event

        # Destroy the buttons
        self.save_button.destroy()
        self.next_image_button.destroy()
        # You may also destroy other widgets here if necessary

        # Add timestamp to filename and save
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        self.export_annotations(f'annotations_{timestamp}.json')

        # Schedule to close the application after 2 seconds
        self.root.after(2000, self.root.destroy)

        # Schedule to close the application after 2 seconds
        self.root.after(2000, self.root.destroy)

    def export_annotations(self, filename="annotations.json"):
        """Export annotations with an optional filename."""
        data = {
            'annotations': self.annotations,
            'children': self.children,
            'images': self.get_image_info()
        }
        annotations_file_path = os.path.join(self.main_folder_path, filename)
        with open(annotations_file_path, 'w') as file:
            json.dump(data, file, indent=4)

# Example usage
root = Tk()
annotator = ImageAnnotator(root)
root.mainloop()
