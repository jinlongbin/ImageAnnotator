# ImageAnnotator
ImageAnnotator is a Python-based tool for easy and precise annotation of images

## Folder structure
The selected folder should be in the following structure
```
selected folder
|----single
|    |----b1
|    |    |----1.png
|    |    |----2.png
|    |    |...
|    |----b2
|    |    |----1.png
|    |    |----2.png
|    |    |...
|    |...
|    |----g1
|    |    |----1.png
|    |    |----2.png
|    |    |...
|    |----g2
|    |    |----1.png
|    |    |----2.png
|    |    |...
|    |...
|----group
|    |----1.png
|    |----2.png
|    |...
|----annotation.json
```

## How to Use
To effectively utilize the ImageAnnotator tool, follow these simple steps:

1. **Launch the Application:** Start by running the Python script.

2. **Select a Class Folder:** Choose a folder representing a class. Ensure it contains subfolders named "single" and "group" for individual and group images, respectively.

3. **Annotate Child Face:** Click on the center point of a child's face in the image to mark it.

4. **Choose Child Name:** Select the corresponding name of the child from the dropdown menu or list provided.

5. **Save Annotation:** After marking and naming, click the "Save" button to store the annotation.

6. **Continue Annotating:** Repeat steps 3 to 5 for each child's face in the image until all relevant faces are annotated.

7. **Proceed to Next Image**: Once all faces in the current image are annotated, click the "Next Image" button to move to the next image in the folder.

Ensure the application remains open until you have completed annotating all images in the selected class folder
