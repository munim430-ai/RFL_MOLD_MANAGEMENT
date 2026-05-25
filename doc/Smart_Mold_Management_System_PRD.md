# Product Requirements Document (PRD)
## Smart Mold Management System

### 1. Project Overview
The **Smart Mold Management Web Application** is a full-stack system designed for plastics production factories. Its primary goal is to track injection molds stored in physical racks utilizing a **dual-QR scan workflow** (one scan for the mold, one for the rack position). This ensures accurate, real-time logging of exactly when and where each mold is stored or removed.

### 2. Technology Stack
* **Frontend:** React + Vite + TypeScript
* **Styling:** Tailwind CSS
* **Database:** Supabase (PostgreSQL) — real-time capabilities
* **QR Scanning:** `html5-qr-code` (camera-based, mobile-compatible)
* **QR Generation:** `qrcode.react` (for printing physical labels)
* **State Management:** Zustand
* **Routing:** React Router v6
* **Date/Time:** date-fns
* **Export:** Papa Parse (CSV export)
* **Icons:** Lucide React

### 3. Database Schema
The system relies on a PostgreSQL database (Supabase) with the following core tables:
* **`molds`**: Master table for mold metadata (ID, name, product, cavities, weight, machine compatibility, status, maintenance dates, shot count).
* **`rack_positions`**: Master table for physical storage slots (ID, rack name, row, col, zone flag). Includes fixed slots (e.g., A-1-1) and zone areas (e.g., ZONE-A).
* **`mold_locations`**: Live state table tracking the current position of stored molds.
* **`activity_log`**: Historical append-only log of all "store" and "remove" actions, including timestamps and operator names.

### 4. Core Features & Pages

#### 4.1. Scan & Track (`/scan` - Default Home Page)
* **Purpose:** The primary mobile-first interface for operators on the factory floor.
* **Workflow (Dual-QR):**
    1.  Select Action: "Store Mold" or "Remove Mold".
    2.  Step 1: Scan Mold QR (fetches mold details).
    3.  Step 2: Scan Rack Position QR (fetches position details).
    4.  Step 3: Confirm Action.
* **Validation:** Prevent overriding occupied slots without confirmation, prevent removing from mismatched locations, and ensure the mold exists.
* **Fallback:** Manual text input for IDs if the camera fails.

#### 4.2. Search Molds (`/search`)
* **Purpose:** Universal search by mold ID, name, product, or machine.
* **UI:** Displays location badges, statuses, and maintenance alerts. Highlights rack positions in blue and zone locations in amber.

#### 4.3. Rack View (`/rack`)
* **Purpose:** Visual representation of physical storage.
* **UI:** 3x3 visual grid for Rack A. Blue cells indicate occupied slots; grey indicates empty. Clicking a cell reveals a side panel with mold details. Includes a separate list for "A Zone" molds and overall occupancy stats.

#### 4.4. Mold Database (`/molds`)
* **Purpose:** Admin interface to manage the master mold list.
* **UI:** Table/card layout with CRUD capabilities via a slide-in form. Visual status badges and maintenance warnings (Red for ≤7 days, Amber for ≤30 days).

#### 4.5. Activity Log (`/log`)
* **Purpose:** Audit trail of all mold movements.
* **UI:** Reverse-chronological table filterable by action, mold ID, and date. Includes pagination and a CSV export feature.

#### 4.6. QR Label Printer (`/qr-print`)
* **Purpose:** Generate physical labels for molds and racks.
* **UI:** Displays clean, printable grids of QR codes encoding raw IDs (e.g., `MLD-001`, `A-2-2`). Uses `@media print` to hide navigation during printing.

#### 4.7. Settings (`/settings`)
* **Purpose:** App configuration and data management.
* **Features:** Set company/operator name, load demo sample data, and clear data (with confirmation).

### 5. UI/UX Requirements
* **Responsiveness:** Mobile-first design for scanning; expansive desktop layout for admin pages. Standardized bottom tab bar on mobile, top navigation on desktop.
* **Color System:**
    * Green: Available
    * Blue: Running (or occupied rack slot)
    * Red: Repair (or urgent maintenance)
    * Amber: Maintenance (or "A Zone")
* **Feedback:** Toast notifications for success/error/warning states. Loading skeletons during data fetching.

### 6. Technical & Implementation Notes
1.  **QR Encoding:** QR codes must only encode raw string IDs (e.g., `MLD-001`).
2.  **Timezone:** All timestamps must display in local Bangladesh time (Asia/Dhaka).
3.  **Data Normalization:** Mold IDs must be automatically cast to uppercase on input.
4.  **Offline Capability:** If Supabase is unreachable, the app should queue store/remove actions in `localStorage` and sync when online, displaying an "offline mode" banner.
5.  **Camera Handling:** Graceful fallback and instructions if camera permissions are denied.
6.  **Explicit Confirmation:** Auto-assignment is prohibited; the final step in the scan workflow *must* be confirmed by the operator.
