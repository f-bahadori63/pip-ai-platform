# Entity Relationship

## Document Information

| Item | Value |

|---|---|

| Project | PIP - Project Intelligence Platform |

| Version | 1.0 |

| Status | Approved |

---

# Relationship Overview

The Project entity is the central entity in PIP.

---

# Core Relationships

## Project → Activity

Relationship:

Project 1 ---- N Activity

Meaning:

A project contains multiple schedule activities.

---

## Project → Document

Relationship:

Project 1 ---- N Document

Meaning:

A project contains multiple controlled documents.

---

## Project → Risk

Relationship:

Project 1 ---- N Risk

Meaning:

A project can have multiple identified risks.

---

## Project → Cost Item

Relationship:

Project 1 ---- N Cost Item

Meaning:

A project contains multiple cost records.

---

## User → Role

Relationship:

Role 1 ---- N User

Meaning:

One role can be assigned to multiple users.

---

## User → Project

Relationship:

User N ---- N Project

Meaning:

Users can participate in multiple projects.

---

## Project → AI Recommendation

Relationship:

Project 1 ---- N AI Recommendation

Meaning:

AI generates multiple insights for a project.

---

# Relationship Rules

- Every transactional entity must reference a Project.

- All critical changes must be traceable.

- Relationships must support future module expansion.