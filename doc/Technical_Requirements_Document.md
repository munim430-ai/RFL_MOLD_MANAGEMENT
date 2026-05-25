# Technical Requirements Document

## Smart Mold Management System

### 1. Introduction
This document outlines the technical requirements for the Smart Mold Management System, a web application designed to track injection molds in plastics production factories. It details the technology stack, core functionalities, and specific technical considerations necessary for the system's development and operation.

### 2. Technology Stack
The system will be built using the following technologies:

| Category        | Technology             | Purpose                                      |
| :-------------- | :--------------------- | :------------------------------------------- |
| **Frontend**    | React + Vite + TypeScript | Core UI development and build tooling        |
| **Styling**     | Tailwind CSS           | Utility-first CSS framework                  |
| **Database**    | Supabase (PostgreSQL)  | Real-time database and backend services      |
| **QR Scanning** | `html5-qr-code`        | Camera-based QR code scanning                |
| **QR Generation** | `qrcode.react`         | Generating QR codes for printing             |
| **State Management** | Zustand                | Frontend state management                    |
| **Routing**     | React Router v6        | Client-side routing                          |
| **Date/Time**   | date-fns               | Date and time manipulation                   |
| **Export**      | Papa Parse             | CSV export functionality                     |
| **Icons**       | Lucide React           | Icon library                                 |

### 3. Core Technical Requirements

#### 3.1. QR Code Handling
*   **Encoding:** QR codes generated and scanned by the system MUST only encode raw string IDs (e.g., `MLD-001`, `A-2-2`) [1].
*   **Scanning:** The system MUST utilize `html5-qr-code` for camera-based QR scanning, ensuring mobile compatibility [1].
*   **Generation:** The system MUST use `qrcode.react` to generate printable QR labels for molds and rack positions [1].

#### 3.2. Data Management
*   **Database:** The system MUST use Supabase (PostgreSQL) for its database, leveraging its real-time capabilities [1].
*   **Timezone:** All timestamps displayed within the application MUST be in local Bangladesh time (Asia/Dhaka) [1].
*   **Data Normalization:** Mold IDs entered into the system MUST be automatically cast to uppercase [1].

#### 3.3. Offline Capability
*   The application MUST queue 
store/remove actions in `localStorage` if Supabase is unreachable [1].
*   An "offline mode" banner MUST be displayed when the application is operating in offline mode and syncing data when online [1].

#### 3.4. User Interface and Experience
*   **Responsiveness:** The application MUST be mobile-first for scanning interfaces and provide an expansive desktop layout for admin pages [1].
*   **Navigation:** A standardized bottom tab bar MUST be used on mobile, and top navigation on desktop [1].
*   **Feedback:** The system MUST provide toast notifications for success, error, and warning states [1].
*   **Loading States:** Loading skeletons MUST be displayed during data fetching [1].

#### 3.5. Security and Validation
*   **Confirmation:** The final step in the scan workflow MUST require explicit confirmation from the operator [1].
*   **Validation Rules:**
    *   Prevent overriding occupied slots without confirmation [1].
    *   Prevent removing molds from mismatched locations [1].
    *   Ensure the mold exists in the system before performing actions [1].

#### 3.6. Camera Handling
*   The application MUST provide graceful fallback and instructions if camera permissions are denied by the user [1].

### 4. References
[1] Smart Mold Management System PRD.md
