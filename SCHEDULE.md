# Project Schedule
- 2026-02-15: UI Framework & Responsive Menu
- 2026-02-22: Core Architecture & Multithreading
- 2026-03-01: Vision Core Basics & Laser Buffer
- 2026-03-08: Starting the Game Loop & Game Selection Preparation
- 2026-03-15: Creating Game Loader for YAML File Structure Parsing
- 2026-03-22: Basic Game Modes Logic
- 2026-03-29: Basic Game Mechanics & Mouse - Laser Simulation Interactions
- 2026-04-05: Screen Calibration
- 2026-04-12: Advanced Image Processing & Laser Detection
- 2026-04-19: Audiovisual Feedback & Visual Effects
- 2026-04-26: Edge-case Error Handling & System Stability
- 2026-05-03: Final Polish & Beta Testing
- 2026-05-10: Packaging (Installer) & Documentation

## UI Framework & Responsive Menu
Building the main menu, game selector (games), settings, and screen calibration menu items, as well as establishing basic navigation.

## Core Architecture & Multithreading
Designing the Producer-Consumer pattern. Separating the Vision Core and the Game Loop, and creating the thread-safe Shared Memory Buffer based on the LIFO (Last-In-First-Out) principle.

## Vision Core Basics & Laser Buffer
Creating the Vision-Core class and the laser buffer class. Establishing communication between the Game engine and the Vision core.

## Starting the Game Loop & Game Selection Preparation
Building the software's central control unit (Game Engine Core), which runs on the main thread. Finalizing the game selector in the main menu.

## Creating Game Loader for YAML File Structure Parsing
Writing the Configuration Manager module, which reads and instantiates in memory the data from static YAML files containing the meta, layout, globals, entities, inputs, and rules categories.

## Basic Game Modes Logic
Implementing the Event-Condition-Action logic in the Game Engine based on the parsed configurations, such as collision detection, scoring (score_add), and object destruction (destroy).

## Basic Game Mechanics & Mouse - Laser Simulation Interactions
Temporarily emulating the pointer input with a mouse, which the program translates into in-game coordinates, allowing the testing of game logic and interactions before finalizing the camera.

## Screen Calibration & Perspective Mapping
Manual calibration of the projected image's size and position to the camera's coordinate system, where the user sets the exact mapping by shooting points at the 4 corners and the center of the surface.

## Advanced Image Processing & Laser Detection
Color space conversion of the camera image (from RGB to HSV) to compensate for lighting conditions, color filtering, and precise, real-time determination of the brightest point's (laser's) coordinates and centroid using OpenCV.

## Audiovisual Feedback & Visual Effects
Building the graphics system. Implementing effects and sounds.

## Edge-case Error Handling
Filtering out potential user-induced errors. Exception handling.

## Final Polish & Beta Testing
Executing functional and non-functional tests: lag and calibration testing, and testing the accuracy of pointer detection under varying lighting conditions.

## Packaging (Installer) & Documentation
Converting the project into an installable application.