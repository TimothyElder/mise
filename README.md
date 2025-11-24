# Mise <img src='src/mise/assets/mise.png' align="right" height="138.5" /></a>

>For the professional, one's meez is an obsession, one's sword and shield, the only thing standing between you and chaos. If you have your meez right, it means you have your head together, you are "set up", stocked, organized, ready with everything you need and are likely to need for the tasks at hand.
<p align="right"/>Anthony Bourdain, <em>Le Halles Cookbook</em></p>

The ambition for [Mise](https://en.wikipedia.org/wiki/Mise_en_place) is to make it an open source qualitative data analysis tool that social scientists can use as an alternative to some of the more bloated and expensive proprietary software out there. It is meant to preserve some of the functionality that can be found in software like atlas.ti or Dedoose while having no cost and a more straightforward design.

## Proposed Order of Development

1.	Data Manager (Backend)
    - Define how documents and codes will be stored and retrieved.
    - Decide whether to use JSON, SQLite, or another format.
    - Implement basic CRUD operations for documents and codes.
    - Example: A Project class that manages documents and a Code class to store and handle codes.
    - What database to use?
2.	Text Processing
    - Implement logic for tagging and calculating co-occurrence relationships between codes.
    - This is also where algorithms for analyzing text (e.g., tokenization, counting) will live.
3.	Visualization Logic
    - Start with co-occurrence data structures and test generating NetworkX graphs from them.
    - Ensure the backend produces data that can easily plug into a visualization.
4.	Basic GUI Skeleton
    - Create a minimal GUI (main window, menus, placeholders) to test interactions with the backend.
    - Example: A basic interface to upload a document and view its contents.
5.	Incremental GUI Features
    - Build and connect each GUI feature to the backend step by step.
    - Start with simple document management and then add more complex functionality like tagging and visualization.

## Some Helpers

For visualizing dependencies

```
pyreverse -o png -p mise mise
pydeps mise --max-bacon=2 --show-deps

```