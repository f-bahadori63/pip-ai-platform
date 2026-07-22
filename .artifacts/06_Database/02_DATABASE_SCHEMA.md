# Database Schema

## Document Information

| Item | Value |

|---|---|

| Project | PIP - Project Intelligence Platform |

| Version | 1.0 |

| Status | Approved |

---

# Purpose

Define the logical database schema structure for PIP.

---

# Schema Organization

PIP database is organized into logical schemas based on business domains.

---

# Core Schemas

## 1. Project Schema

Purpose:

Store project execution information.

Main Tables:

- projects

- contracts

- milestones

- activities

---

## 2. User Schema

Purpose:

Manage users and access control.

Main Tables:

- users

- roles

- permissions

- user_roles

---

## 3. Control Schema

Purpose:

Store project control information.

Main Tables:

- risks

- issues

- costs

- progress_updates

---

## 4. Document Schema

Purpose:

Manage project documents.

Main Tables:

- documents

- revisions

- approvals

---

## 5. AI Schema

Purpose:

Store AI-related information.

Main Tables:

- recommendations

- predictions

- knowledge_items

---

# Naming Convention

Table naming:

- Lowercase

- Singular business meaning

- Underscore separation

Examples:

projects  
project_members  
risk_items  
document_revisions



---

# Schema Design Principles

- Logical separation of domains

- Consistent naming

- Easy maintenance

- Support future expansion

---

# Future Capability

The schema design supports:

- Reporting database

- Analytics layer

- AI data processing