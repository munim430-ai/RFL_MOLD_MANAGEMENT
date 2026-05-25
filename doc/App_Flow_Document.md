# App Flow Document

## Smart Mold Management System

### 1. Introduction
This document outlines the key application flows and user journeys within the Smart Mold Management System. It describes the sequence of interactions for core features, providing a clear understanding of how users navigate and perform tasks within the application.

### 2. Core Application Flows

#### 2.1. Mold Tracking Workflow (Scan & Track - `/scan`)
This is the primary mobile-first workflow for factory operators to manage mold locations.

1.  **Access Scan Page:** User navigates to the `/scan` page (default home page).
2.  **Select Action:** User selects either "Store Mold" or "Remove Mold" [1].
3.  **Scan Mold QR:** User activates the camera and scans the QR code on the mold.
    *   System fetches mold details. If mold not found or QR invalid, an error is displayed, and manual input option is provided [1].
4.  **Scan Rack Position QR:** User scans the QR code of the rack position.
    *   System fetches rack position details. If position not found or QR invalid, an error is displayed, and manual input option is provided [1].
    *   **Validation (Store Mold):** If the rack position is already occupied, the system prompts for explicit confirmation before proceeding [1].
    *   **Validation (Remove Mold):** If the mold scanned does not match the mold currently in the scanned rack position, the system prevents the action and displays an error [1].
5.  **Confirm Action:** User reviews the scanned mold and rack position details and explicitly confirms the action.
    *   Upon confirmation, the system updates `mold_locations` and logs the activity in `activity_log` [1].
    *   Success or error toast notifications are displayed [1].

#### 2.2. Mold Search Workflow (`/search`)
This flow allows users to find specific molds and view their status and location.

1.  **Access Search Page:** User navigates to the `/search` page.
2.  **Enter Search Query:** User inputs a search term (mold ID, name, product, or machine) into the search bar [1].
3.  **View Search Results:** The system displays a list of matching molds.
    *   Each result shows location badges, status, and maintenance alerts [1].
    *   Rack positions are highlighted in blue, and zone locations in amber [1].

#### 2.3. Rack Visualization Workflow (`/rack`)
This flow provides a visual overview of mold storage within a specific rack.

1.  **Access Rack View Page:** User navigates to the `/rack` page.
2.  **View Rack Grid:** The system displays a 3x3 visual grid representing Rack A.
    *   Blue cells indicate occupied slots; grey cells indicate empty slots [1].
    *   A separate list for "A Zone" molds is displayed [1].
    *   Overall occupancy statistics are shown [1].
3.  **View Mold Details (Optional):** User clicks on an occupied cell in the grid.
    *   A side panel appears, displaying detailed information about the mold in that slot [1].

#### 2.4. Mold Database Management Workflow (`/molds`)
This flow is for administrators to manage the master list of molds.

1.  **Access Mold Database Page:** User navigates to the `/molds` page.
2.  **View Mold List:** The system displays molds in a table/card layout.
    *   Visual status badges and maintenance warnings (Red for ≤7 days, Amber for ≤30 days) are shown [1].
3.  **Perform CRUD Operations:**
    *   **Create:** User clicks "Add New Mold", fills out a slide-in form with mold details, and submits. Mold ID is automatically cast to uppercase [1].
    *   **Read:** User views details of existing molds.
    *   **Update:** User clicks "Edit" on a mold, modifies details in the slide-in form, and submits.
    *   **Delete:** User clicks "Delete" on a mold and confirms the action.

#### 2.5. Activity Log Review Workflow (`/log`)
This flow allows users to audit historical mold movements.

1.  **Access Activity Log Page:** User navigates to the `/log` page.
2.  **View Log Entries:** The system displays a reverse-chronological table of all "store" and "remove" actions [1].
3.  **Filter Log (Optional):** User applies filters by action type, mold ID, or date range [1].
4.  **Export Data (Optional):** User clicks "Export CSV" to download the filtered activity log [1].

#### 2.6. QR Label Printing Workflow (`/qr-print`)
This flow enables the generation of physical QR labels.

1.  **Access QR Print Page:** User navigates to the `/qr-print` page.
2.  **Generate QR Codes:** The system displays clean, printable grids of QR codes.
    *   QR codes encode raw IDs (e.g., `MLD-001`, `A-2-2`) [1].
3.  **Print Labels:** User uses the browser's print functionality. The system uses `@media print` to hide navigation elements during printing [1].

#### 2.7. Settings Management Workflow (`/settings`)
This flow allows users to configure application settings.

1.  **Access Settings Page:** User navigates to the `/settings` page.
2.  **Configure Settings:** User can:
    *   Set company/operator name [1].
    *   Load demo sample data [1].
    *   Clear all application data (with confirmation prompt) [1].

### 3. References
[1] Smart Mold Management System PRD.md
