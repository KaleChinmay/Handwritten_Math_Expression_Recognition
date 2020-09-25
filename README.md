# Handwritten Mathematical Expression Recognition
Pattern Recognition project
This is a code for pattern recognition for recognizing Math Expression and parsing them from scratch.

Dataset used : # CROHME dataset.
It has two types of data:
a. Dataset with individial math symbols
b. Dataset with mathematical expression.

Each mathematical symbol and an expression is represented by inkml files. Inkml files are xml files containing information like character traces, id, source, ground 
truth etc. 

The project is divided into 3 parts:

1. Segmentation
2. Classification
3. Parsing

Each step has a standalone python code which creates intermediate data files. Each step is evaluated with ground truth files in CROHME dataset.

