# Smash Amiibo Editor - UI Overhaul

## Overview

This project is a complete user interface modernization of **Smash Amiibo Editor (SAE)**. The goal is to transform the application from its current utility-style layout into a cleaner, more modern, and user-friendly experience while maintaining full compatibility with existing amiibo editing functionality.

The redesign focuses on usability, visual consistency, accessibility, and future expandability.

---

# Goals

* Modernize the entire interface
* Improve navigation and workflow
* Reduce clutter and visual confusion
* Add amiibo artwork integration
* Improve organization of settings and tools
* Create a scalable design for future features
* Maintain compatibility with existing SAE functionality

---

# Planned Features

## Modern Interface

* Redesigned main window
* Cleaner spacing and alignment
* Consistent button styling
* Improved typography
* Responsive layouts
* Better visual hierarchy

---

## Dark Mode

* Complete dark theme support
* Consistent styling across all windows
* Dark settings menu
* Dark dialogs and popups
* Improved contrast and readability

---

## Amiibo Artwork Integration

### File Viewer

Display the current amiibo artwork when a file is loaded.

Features:

* Automatic artwork detection
* Artwork updates when a different amiibo is loaded
* Placeholder image when artwork is unavailable
* Optional artwork scaling modes

---

### Fighter Tab Artwork

Display artwork directly within the Fighter tab.

Features:

* Updates automatically when a character is selected
* Uses the selected fighter from the character dropdown
* Large preview area
* Consistent artwork throughout the application

---

## Character Synchronization

When changing an amiibo's fighter:

* Character artwork updates automatically
* Fighter name updates automatically
* Exported files use the correct fighter information
* Prevents mismatched character data

### Example

Loaded Amiibo:

* Mario

Selected Character:

* Link

After Saving:

* Character becomes Link
* Display name becomes Link
* Artwork becomes Link

---

## Settings Redesign

Move all application settings into a dedicated settings window.

Categories:

### General

* Language
* Startup behavior
* Update preferences

### Appearance

* Theme selection
* Dark mode
* UI scaling
* Font options

### Artwork

* Enable artwork display
* Artwork cache settings
* Artwork quality settings

### File Management

* Default save location
* Backup settings
* Export options

### Advanced

* Debug options
* Developer tools
* Experimental features

---

## Navigation Improvements

### Sidebar Navigation

Replace scattered controls with organized navigation:

* Home
* Fighter
* Personality
* Spirits
* Statistics
* Metadata
* Settings

---

## Quality of Life Features

### Search

* Search fighters
* Search spirits
* Search abilities

### Recent Files

* Recently opened amiibo files
* Quick access menu

### Drag & Drop

* Drag amiibo files directly into the editor
* Automatic loading

### Status Indicators

Display:

* Loaded amiibo
* Character
* Save status
* File path

---

## Future Expansion

Potential future additions:

* Amiibo image downloader integration
* Metadata viewer
* Batch editing
* Preset management
* Custom themes
* Plugin support
* Emuiibo compatibility tools
* JSON import/export improvements

---

# Design Philosophy

The new UI should feel:

* Modern
* Fast
* Clean
* Professional
* Beginner-friendly
* Power-user capable

The redesign should take inspiration from modern desktop applications while preserving the efficiency expected from a technical editing tool.

---

# Compatibility

The UI overhaul should:

* Preserve existing functionality
* Support existing SAE file formats
* Remain compatible with current save/export workflows
* Avoid breaking existing editing features

---

# Project Status

Current Status: Planning / UI Redesign

Focus Areas:

* Modern Layout
* Dark Mode
* Artwork Integration
* Settings Reorganization
* Navigation Improvements

---

# Credits

Original Application:

* Smash Amiibo Editor (SAE)

UI Overhaul Concept:

* Community-driven modernization project focused on improving usability, accessibility, and overall user experience.
