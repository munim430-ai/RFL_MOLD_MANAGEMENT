# Backend Schema Document

## Smart Mold Management System

### 1. Introduction
This document details the backend database schema for the Smart Mold Management System. The system utilizes a PostgreSQL database, hosted on Supabase, to manage mold metadata, rack positions, mold locations, and activity logs. This schema is designed to support the real-time tracking and management functionalities outlined in the Product Requirements Document (PRD).

### 2. Database Technology
The system will use **PostgreSQL** as its relational database, leveraging **Supabase** for hosting and real-time capabilities [1].

### 3. Core Database Tables
The following tables form the core of the Smart Mold Management System's backend schema:

#### 3.1. `molds` Table
This master table stores metadata for all injection molds.

| Column Name        | Data Type          | Constraints / Description                                     |
| :----------------- | :----------------- | :------------------------------------------------------------ |
| `id`               | `TEXT`             | Primary Key, Unique Mold ID (e.g., `MLD-001`), auto-uppercase [1] |
| `name`             | `TEXT`             | Human-readable name of the mold                               |
| `product`          | `TEXT`             | Product manufactured by this mold                             |
| `cavities`         | `INTEGER`          | Number of cavities in the mold                                |
| `weight`           | `NUMERIC`          | Weight of the mold (e.g., in kg)                              |
| `machine_compatibility` | `TEXT[]`           | Array of machine IDs this mold is compatible with             |
| `status`           | `TEXT`             | Current status of the mold (e.g., 'Available', 'In Use', 'Maintenance', 'Repair') |
| `last_maintenance_date` | `TIMESTAMP WITH TIME ZONE` | Date of the last maintenance                                  |
| `next_maintenance_date` | `TIMESTAMP WITH TIME ZONE` | Scheduled date for the next maintenance (for alerts)          |
| `shot_count`       | `INTEGER`          | Total number of shots taken by the mold                       |
| `created_at`       | `TIMESTAMP WITH TIME ZONE` | Timestamp of record creation, default `now()`                 |
| `updated_at`       | `TIMESTAMP WITH TIME ZONE` | Timestamp of last update, default `now()`                     |

#### 3.2. `rack_positions` Table
This master table defines all physical storage slots for molds.

| Column Name        | Data Type          | Constraints / Description                                     |
| :----------------- | :----------------- | :------------------------------------------------------------ |
| `id`               | `TEXT`             | Primary Key, Unique Rack Position ID (e.g., `A-1-1`, `ZONE-A`) [1] |
| `rack_name`        | `TEXT`             | Name of the rack (e.g., 'Rack A')                             |
| `row`              | `INTEGER`          | Row number within the rack (NULL for zone areas)              |
| `col`              | `INTEGER`          | Column number within the rack (NULL for zone areas)           |
| `is_zone`          | `BOOLEAN`          | Flag indicating if it's a zone area (e.g., 'ZONE-A') [1]      |
| `created_at`       | `TIMESTAMP WITH TIME ZONE` | Timestamp of record creation, default `now()`                 |
| `updated_at`       | `TIMESTAMP WITH TIME ZONE` | Timestamp of last update, default `now()`                     |

#### 3.3. `mold_locations` Table
This table tracks the current live state of stored molds, indicating which mold is in which rack position.

| Column Name        | Data Type          | Constraints / Description                                     |
| :----------------- | :----------------- | :------------------------------------------------------------ |
| `id`               | `UUID`             | Primary Key, Unique identifier for the location record        |
| `mold_id`          | `TEXT`             | Foreign Key referencing `molds.id`                            |
| `rack_position_id` | `TEXT`             | Foreign Key referencing `rack_positions.id`, Unique (one mold per position) [1] |
| `stored_at`        | `TIMESTAMP WITH TIME ZONE` | Timestamp when the mold was stored at this location           |
| `operator_name`    | `TEXT`             | Name of the operator who stored the mold                      |
| `created_at`       | `TIMESTAMP WITH TIME ZONE` | Timestamp of record creation, default `now()`                 |
| `updated_at`       | `TIMESTAMP WITH TIME ZONE` | Timestamp of last update, default `now()`                     |

#### 3.4. `activity_log` Table
This append-only table records all historical 
actions of mold storage and removal.

| Column Name        | Data Type          | Constraints / Description                                     |
| :----------------- | :----------------- | :------------------------------------------------------------ |
| `id`               | `UUID`             | Primary Key, Unique identifier for the log entry              |
| `mold_id`          | `TEXT`             | Foreign Key referencing `molds.id`                            |
| `rack_position_id` | `TEXT`             | Foreign Key referencing `rack_positions.id`                   |
| `action_type`      | `TEXT`             | Type of action (e.g., 'Store', 'Remove')                      |
| `timestamp`        | `TIMESTAMP WITH TIME ZONE` | Timestamp of the action, default `now()`                      |
| `operator_name`    | `TEXT`             | Name of the operator who performed the action                 |
| `details`          | `TEXT`             | Additional details about the action (e.g., 'manual override') |

### 4. Relationships
*   `mold_locations.mold_id` -> `molds.id`
*   `mold_locations.rack_position_id` -> `rack_positions.id`
*   `activity_log.mold_id` -> `molds.id`
*   `activity_log.rack_position_id` -> `rack_positions.id`

### 5. Supabase Considerations
*   **Real-time:** Supabase's real-time capabilities will be utilized for immediate updates to `mold_locations` and `activity_log` [1].
*   **Row Level Security (RLS):** RLS will be implemented to ensure that users can only access and modify data relevant to their roles and permissions.
*   **Functions/Triggers:** PostgreSQL functions and triggers may be used to automate tasks such as updating `updated_at` timestamps or enforcing complex business logic.

### 6. References
[1] Smart Mold Management System PRD.md
