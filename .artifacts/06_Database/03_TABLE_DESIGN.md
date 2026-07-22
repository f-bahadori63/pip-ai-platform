# Table Design

## Document Information

| Item | Value |

|---|---|

| Project | PIP - Project Intelligence Platform |

| Version | 1.0 |

| Status | Approved |

---

# Purpose

Define the main database tables and their primary fields for PIP.

---

# Project Tables

## projects

Purpose:

Store project master information.

Fields:

- id

- name

- client

- contract_number

- start_date

- end_date

- status

- created_at

---

## contracts

Purpose:

Store contract information.

Fields:

- id

- project_id

- contract_type

- contract_value

- start_date

- end_date

---

## activities

Purpose:

Store schedule activities.

Fields:

- id

- project_id

- name

- planned_start

- planned_finish

- actual_start

- actual_finish

- progress

---

# User Tables

## users

Purpose:

Store system users.

Fields:

- id

- name

- email

- password_hash

- status

---

## roles

Purpose:

Store access roles.

Fields:

- id

- name

- description

---

## permissions

Purpose:

Store system permissions.

Fields:

- id

- name

- description

---

# Control Tables

## risks

Purpose:

Store project risks.

Fields:

- id

- project_id

- description

- probability

- impact

- response

---

## costs

Purpose:

Store project costs.

Fields:

- id

- project_id

- category

- budget

- actual_cost

- forecast

---

# Document Tables

## documents

Purpose:

Store document information.

Fields:

- id

- project_id

- title

- document_type

- status

---

## revisions

Purpose:

Store document revisions.

Fields:

- id

- document_id

- revision_number

- revision_date

---

# AI Tables

## recommendations

Purpose:

Store AI-generated recommendations.

Fields:

- id

- project_id

- type

- content

- confidence_level

---

# Table Design Rules

- Every table has a primary key

- Relationships use foreign keys

- Audit fields are included

- Data integrity is mandatory