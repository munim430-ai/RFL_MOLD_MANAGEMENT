# UI/UX Document

## Smart Mold Management System

### 1. Introduction
This document outlines the User Interface (UI) and User Experience (UX) design principles and requirements for the Smart Mold Management System. The goal is to create an intuitive, efficient, and visually consistent application that caters to both mobile operators and desktop administrators.

### 2. General UI/UX Principles
*   **Mobile-First Design:** The application prioritizes a mobile-first approach, especially for the core scanning functionalities, ensuring ease of use for operators on the factory floor [1].
*   **Responsiveness:** The UI will adapt seamlessly to various screen sizes, offering an expansive desktop layout for administrative tasks and a compact, optimized layout for mobile devices [1].
*   **Consistency:** A consistent design language, including typography, spacing, and component styling, will be maintained throughout the application.
*   **Clarity and Simplicity:** The interface will be clean, uncluttered, and easy to understand, minimizing cognitive load for users.
*   **Feedback and Guidance:** Users will receive clear and immediate feedback on their actions and system status.

### 3. Key UI/UX Requirements

#### 3.1. Layout and Navigation
*   **Mobile Navigation:** A standardized bottom tab bar will be used for primary navigation on mobile devices, providing quick access to core features like Scan & Track, Search Molds, and Rack View [1].
*   **Desktop Navigation:** A top navigation bar will be implemented for desktop layouts, accommodating more links and administrative sections [1].
*   **Content Organization:** Information will be logically grouped and presented to facilitate efficient task completion.

#### 3.2. Color System
The application will utilize a specific color palette to convey status and information effectively:

| Color   | Purpose                                      |
| :------ | :------------------------------------------- |
| **Green** | Indicates availability or success states     |
| **Blue**  | Represents items that are running or occupied rack slots [1] |
| **Red**   | Signifies repair status or urgent maintenance alerts [1] |
| **Amber** | Denotes maintenance warnings or "A Zone" locations [1] |

#### 3.3. Feedback Mechanisms
*   **Toast Notifications:** Success, error, and warning messages will be communicated via transient toast notifications, providing immediate feedback without interrupting the user workflow [1].
*   **Loading Skeletons:** To enhance perceived performance and user experience, loading skeletons will be displayed during data fetching operations [1].
*   **Confirmation Dialogs:** Critical actions, such as clearing data or overriding occupied slots, will require explicit confirmation through modal dialogs to prevent accidental operations [1].

#### 3.4. Specific Page UI/UX Considerations
*   **Scan & Track (`/scan`):**
    *   Mobile-optimized layout with large, tappable areas for action selection and QR scanning [1].
    *   Clear visual cues for each step of the dual-QR workflow [1].
    *   Prominent display of mold and rack details after scanning for confirmation [1].
    *   Manual text input option for IDs will be easily accessible as a fallback [1].
*   **Search Molds (`/search`):**
    *   Universal search bar with clear input field [1].
    *   Search results will display location badges, statuses, and maintenance alerts prominently [1].
    *   Visual differentiation of rack positions (blue) and zone locations (amber) [1].
*   **Rack View (`/rack`):**
    *   Intuitive 3x3 visual grid for Rack A, using color coding (blue for occupied, grey for empty) [1].
    *   Interactive cells that reveal a side panel with mold details upon clicking [1].
    *   Clear display of "A Zone" molds and overall occupancy statistics [1].
*   **Mold Database (`/molds`):**
    *   Table/card layout for easy viewing and management of mold data [1].
    *   Slide-in forms for CRUD operations to maintain context [1].
    *   Visual status badges and maintenance warnings (Red for ≤7 days, Amber for ≤30 days) will be easily discernible [1].
*   **Activity Log (`/log`):**
    *   Reverse-chronological table with clear columns for action, mold ID, timestamp, and operator [1].
    *   Filtering options will be easily accessible and intuitive [1].
    *   Prominent CSV export button [1].
*   **QR Label Printer (`/qr-print`):**
    *   Clean, minimalist layout optimized for printing [1].
    *   QR codes will be clearly displayed with their corresponding raw IDs [1].
    *   Navigation elements will be hidden during print mode using `@media print` styles [1].

### 4. References
[1] Smart Mold Management System PRD.md
