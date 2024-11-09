# Product Requirements Document (PRD)

## 1. Introduction
This document outlines the roadmap for developing an AI agent that automates the process of gathering links to companies' profiles from the Facebook Ads Library. The primary goal is to compile these links into a file for later use in lead generation activities.

## 2. Objectives
### Primary Objective:
- Automate the collection of company profile links from the Facebook Ads Library and store them in a file.

### Future Objectives (for consideration):
- Automate sending messages to these companies.
- Automatically download product photos for AI-generated photo creation.

## 3. Features

### Phase 1: Link Collection Agent
- Search Automation: Automatically search for companies in a specified niche within the Facebook Ads Library.
- Ad Detection: Identify companies that are currently running ads.
- Profile Extraction: Extract links to these companies' profiles.
- Data Storage: Save the collected profile links into a structured file (e.g., CSV or JSON).

### Future Phases (Not for Current Implementation):
- Messaging Automation: Send predefined messages to the collected profiles.
- Photo Downloading: Automatically download product photos from company profiles.
- AI Photo Generation: Use LoRAs, especially FLUX 1.1, to generate AI-enhanced photos for these companies.
- Attachment Handling: Attach generated photos to messages sent to companies.

## 4. Requirements

### 4.1 Functional Requirements
- FR1: The agent shall allow the user to specify a niche or keywords for the search.
- FR2: The agent shall access the Facebook Ads Library and perform the search automatically.
- FR3: The agent shall identify and collect links to companies that are running ads.
- FR4: The agent shall store the collected profile links in a single file in a readable format.

### 4.2 Non-Functional Requirements
- NFR1: The system should be simple to set up and run, requiring minimal programming knowledge.
- NFR2: The agent should execute efficiently, minimizing the time taken to gather links.
- NFR3: The solution should comply with Facebook's terms of service and applicable laws.

## 5. Technologies and Tools
- Programming Language: Python (due to its simplicity and extensive libraries).
- Web Automation Tool: Selenium or Playwright for automating web interactions.
- Data Storage: CSV or JSON file for easy readability and manipulation.
- Environment: The agent should run on a standard personal computer without the need for complex setups.

## 6. Architecture Overview
A simple script-based architecture will be used:

- Input Module: Accepts user input for niche keywords.
- Automation Module: Controls the web browser to navigate the Facebook Ads Library.
- Data Extraction Module: Extracts profile links from search results.
- Storage Module: Saves the extracted links into a file.
- Main Controller: Orchestrates the flow between modules.

## 7. Implementation Plan

### Step 1: Setup Environment
- Install necessary Python packages (e.g., Selenium, pandas).
- Ensure the web driver for the browser (e.g., ChromeDriver for Chrome) is installed.

### Step 2: Develop Input Module
- Create a simple interface (could be command-line) to input niche keywords.

### Step 3: Automate Facebook Ads Library Search
- Use Selenium to open the Facebook Ads Library page.
- Input the niche keywords into the search bar.
- Filter results to show companies running ads.

### Step 4: Extract Profile Links
- Parse the search results page.
- Extract links to company profiles.
- Handle pagination if necessary to cover multiple pages of results.

### Step 5: Store Links in a File
- Collect all extracted links.
- Save them into a CSV or JSON file named appropriately (e.g., company_profiles.csv).

### Step 6: Testing
- Run the agent with test keywords.
- Verify that the links are correctly extracted and stored.
- Handle exceptions and errors gracefully.

### Step 7: Documentation
- Write clear instructions on how to set up and run the agent.
- Include comments in the code for readability.

## 8. Deliverables
- Agent Script File: A single Python script file (e.g., link_collector.py).
- Requirements File: A requirements.txt file listing necessary Python packages.
- User Guide: A simple document explaining how to use the agent.
- Collected Links File: An example output file with collected profile links.

## 9. Timeline
- Day 1-2: Setup environment and develop the input module.
- Day 3-5: Implement automation and data extraction modules.
- Day 6: Develop the storage module and integrate all components.
- Day 7: Testing and debugging.
- Day 8: Documentation and final adjustments.

## 10. Notes
- Keep the entire codebase in as few files as possible, ideally a single script for ease of use.
- Ensure compliance with Facebook's policies to prevent account restrictions.
- Future enhancements should be modular to allow easy addition to the existing agent.