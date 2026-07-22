# Database Design

## Document Information

| Item | Value |

|---|---|

| Project | PIP - Project Intelligence Platform |

| Version | 1.0 |

| Status | Approved |

---

# Database Purpose

Define the initial database structure required for PIP core modules.

---

# Database Technology

Primary Database:

- PostgreSQL

Reason:

- Open source

- Reliable

- Supports complex relationships

- Suitable for enterprise applications

---

# Core Tables

## projects

Purpose:

Store project master information.

Main Fields:

- id

- name

- client

- contract_number

- start_date

- end_date

- status

---

## users

Purpose:

Store system users.

Main Fields:

- id

- name

- email

- password_hash

- status

---

## roles

Purpose:

Manage user access levels.

Main Fields:

- id

- name

- description

---

## activities

Purpose:

Store project schedule activities.

Main Fields:

- id

- project_id

- name

- start_date

- finish_date

- progress

---

## documents

Purpose:

Store project document metadata.

Main Fields:

- id

- project_id

- title

- revision

- status

---

## risks

Purpose:

Store project risks.

Main Fields:

- id

- project_id

- description

- probability

- impact

- status

---

## cost_items

Purpose:

Store project cost information.

Main Fields:

- id

- project_id

- category

- budget

- actual_cost

---

# Database Design Principles

- Normalized structure

- Referential integrity

- Audit capability

- Secure access

- Future scalability