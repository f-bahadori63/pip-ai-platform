# Business Entities

## Document Information

| Item | Value |

|---|---|

| Project | PIP - Project Intelligence Platform |

| Version | 1.0 |

| Status | Approved |

---

# Core Entities

## Project

Description:

Main business object representing an industrial project.

Attributes:

- Project ID

- Project Name

- Client

- Contract Number

- Start Date

- End Date

- Status

---

## Contract

Description:

Defines contractual information of the project.

Attributes:

- Contract ID

- Contract Type

- Contract Value

- Duration

- Client

- Contractor

---

## Activity

Description:

Represents a planned project activity.

Attributes:

- Activity ID

- Name

- Duration

- Start Date

- Finish Date

- Progress

---

## Document

Description:

Represents controlled project information.

Attributes:

- Document ID

- Title

- Type

- Revision

- Status

---

## Risk

Description:

Represents project uncertainties.

Attributes:

- Risk ID

- Description

- Probability

- Impact

- Response Plan

---

## Cost Item

Description:

Represents project financial elements.

Attributes:

- Cost ID

- Category

- Budget

- Actual Cost

- Forecast

---

## User

Description:

Represents system users.

Attributes:

- User ID

- Name

- Role

- Organization

---

## AI Recommendation

Description:

Represents AI-generated project insights.

Attributes:

- Recommendation ID

- Type

- Source Data

- Confidence Level

- Action

---

# Entity Classification

## Master Entities

- Project

- User

- Contract

## Transaction Entities

- Activity

- Cost Item

- Risk

- Document

## Intelligence Entities

- Recommendation

- Prediction

- Knowledge Item