# MemoryGraph Knowledge Graph Schema

**Version:** 1.0  
**Purpose:** Define entity labels (node types) and relationship types (edge types) for the knowledge graph

---

## Table of Contents

1. [Entity Labels](#entity-labels)
2. [Relationship Types](#relationship-types)
3. [Property Schemas](#property-schemas)
4. [Usage Examples](#usage-examples)
5. [Extraction Rules](#extraction-rules)

---

# Entity Labels

Entity labels define the types of "things" that exist in your knowledge graph. Each captured piece of information will be analyzed to extract these entities.

## People Entities

### Person
**Description:** Any individual mentioned in notes, meetings, or communications  
**Properties:**
- `fullName`: Complete name
- `preferredName`: How they like to be called
- `title`: Job title or role
- `email`: Email address
- `phone`: Phone number
- `organization`: Where they work
- `relationship`: Your relationship to them
- `tags`: Role tags (colleague, manager, client, friend, family)
- `firstMentioned`: Date first appeared
- `lastMentioned`: Date last appeared
- `mentionCount`: Frequency of mentions

**Examples:**
- "John Smith" (colleague)
- "Dr. Sarah Chen" (collaborator)
- "Mom" (family)
- "Mike the contractor" (service provider)

**Subtypes:**
- `Colleague`: Coworker or professional peer
- `Manager`: Your direct manager or supervisor
- `Report`: Your direct report
- `Client`: Customer or client
- `Vendor`: Service provider or supplier
- `Collaborator`: Project partner
- `Mentor`: Professional mentor
- `Mentee`: Someone you mentor
- `Friend`: Personal friend
- `FamilyMember`: Family relation
- `Acquaintance`: Casual contact
- `Expert`: Subject matter expert
- `Interviewee`: Person you interviewed

## Organization Entities

### Organization
**Description:** Companies, institutions, teams, or groups  
**Properties:**
- `name`: Organization name
- `type`: Company, nonprofit, institution, team, department
- `industry`: Business sector
- `website`: URL
- `relationship`: Your connection (employer, client, partner, vendor)
- `size`: Small, medium, large, enterprise
- `location`: Primary location

**Examples:**
- "Acme Corporation" (client)
- "Stanford University" (institution)
- "Marketing Team" (internal team)
- "City Council" (government)

**Subtypes:**
- `Company`: Business organization
- `Client`: Client organization
- `Vendor`: Supplier organization
- `Partner`: Partnership organization
- `Competitor`: Competing organization
- `Institution`: Academic or research institution
- `Government`: Government entity
- `Nonprofit`: Nonprofit organization
- `Team`: Internal team or group
- `Department`: Business department
- `Community`: Online or offline community

## Project & Work Entities

### Project
**Description:** Defined initiative with goals and timeline  
**Properties:**
- `name`: Project name
- `status`: Proposed, active, on-hold, completed, cancelled
- `priority`: Low, medium, high, critical
- `startDate`: Project start
- `endDate`: Expected or actual completion
- `budget`: Financial budget
- `description`: Project description
- `goals`: Project objectives
- `tags`: Project categories

**Examples:**
- "Website Redesign Q4"
- "Product Launch 2025"
- "Home Renovation"
- "Dissertation Research"

**Subtypes:**
- `WorkProject`: Professional project
- `PersonalProject`: Personal initiative
- `Research`: Research project
- `Initiative`: Strategic initiative
- `Campaign`: Marketing or advocacy campaign

### Task
**Description:** Actionable item or action item  
**Properties:**
- `description`: What needs to be done
- `status`: Todo, in-progress, blocked, completed, cancelled
- `priority`: Low, medium, high, urgent
- `dueDate`: When it's due
- `estimatedEffort`: Time estimate
- `assignee`: Who owns it
- `context`: Where it came from
- `completedDate`: When completed
- `tags`: Task categories

**Examples:**
- "Review design mockups"
- "Call dentist for appointment"
- "Submit expense report"
- "Buy birthday gift for mom"

**Subtypes:**
- `ActionItem`: Specific action from meeting or note
- `Reminder`: Time-based reminder
- `Followup`: Follow-up task
- `Milestone`: Project milestone

### Meeting
**Description:** Scheduled or recorded meeting  
**Properties:**
- `title`: Meeting title
- `date`: Date and time
- `duration`: Length in minutes
- `type`: Standup, 1:1, planning, review, all-hands
- `location`: Physical or virtual location
- `platform`: Zoom, Webex, Teams, in-person
- `recordingUrl`: Link to recording
- `transcriptUrl`: Link to transcript
- `attendees`: List of participants
- `organizer`: Meeting organizer
- `agenda`: Meeting agenda
- `outcomes`: Key decisions and outcomes

**Examples:**
- "Q4 Planning Meeting"
- "Weekly 1:1 with Sarah"
- "Client Kickoff - Acme Corp"
- "Team Standup"

**Subtypes:**
- `OneOnOne`: 1:1 meeting
- `TeamMeeting`: Team meeting
- `ClientMeeting`: External client meeting
- `Interview`: Job or research interview
- `Workshop`: Workshop or training session
- `Conference`: Conference attendance
- `Standup`: Daily standup

## Document & Content Entities

### Note
**Description:** Captured note from any source  
**Properties:**
- `title`: Note title
- `source`: Rocketbook, audio, video, web, etc.
- `captureDate`: When captured
- `modifiedDate`: Last modification
- `content`: Note text content
- `summary`: AI-generated summary
- `category`: Note category from QR code or user
- `tags`: User and AI tags
- `confidence`: OCR or processing confidence
- `wordCount`: Length of note

**Examples:**
- "Meeting Notes - Q4 Planning"
- "Research Ideas - Oct 15"
- "Recipe - Mom's Lasagna"
- "Book Notes - Thinking Fast and Slow"

**Subtypes:**
- `HandwrittenNote`: From Rocketbook or scanning
- `AudioNote`: From audio recording
- `VideoNote`: From video recording
- `MeetingTranscript`: From meeting recording
- `WebClip`: From web capture
- `EmailCapture`: From email import
- `DocumentScan`: From document scanning
- `BookNotes`: Notes on books
- `PaperNotes`: Notes on research papers
- `Reflection`: Personal reflection or journal

### Document
**Description:** Formal document (reports, papers, presentations)  
**Properties:**
- `title`: Document title
- `type`: Report, paper, presentation, contract, etc.
- `author`: Document author
- `date`: Creation or publication date
- `url`: Online location
- `fileFormat`: PDF, DOCX, PPTX, etc.
- `pageCount`: Number of pages
- `summary`: Document summary
- `status`: Draft, review, final
- `version`: Version number

**Examples:**
- "Q3 Sales Report"
- "Research Paper: AI in Healthcare"
- "Client Proposal - Acme Corp"
- "Employee Handbook 2025"

**Subtypes:**
- `Report`: Business or research report
- `Paper`: Academic or research paper
- `Presentation`: Slide deck or presentation
- `Proposal`: Proposal document
- `Contract`: Legal contract
- `Specification`: Technical specification
- `Manual`: User or technical manual
- `Policy`: Policy document

### Resource
**Description:** Reference material, articles, books, courses  
**Properties:**
- `title`: Resource title
- `type`: Article, book, video, course, podcast
- `author`: Creator or author
- `url`: Web location
- `publicationDate`: When published
- `summary`: Content summary
- `rating`: Your rating
- `status`: To-read, reading, completed
- `notes`: Your notes on it

**Examples:**
- "Article: The Future of AI"
- "Book: Atomic Habits"
- "Course: Machine Learning Fundamentals"
- "Podcast: How I Built This"

**Subtypes:**
- `Article`: Online or print article
- `Book`: Book
- `Video`: Video content
- `Course`: Educational course
- `Podcast`: Podcast episode
- `Tutorial`: How-to tutorial
- `Paper`: Academic paper

## Concept & Topic Entities

### Concept
**Description:** Abstract idea, topic, or area of knowledge  
**Properties:**
- `name`: Concept name
- `definition`: Concept definition
- `domain`: Field or area (technology, business, personal, etc.)
- `aliases`: Alternative names
- `relatedTerms`: Similar concepts
- `importance`: How central to your work/life
- `complexity`: Simple, moderate, complex

**Examples:**
- "Machine Learning"
- "Product-Market Fit"
- "Meditation Techniques"
- "Customer Retention"

**Subtypes:**
- `Technology`: Technical concept
- `Methodology`: Process or method
- `Theory`: Theoretical framework
- `Skill`: Learnable skill
- `Topic`: General topic or theme
- `Domain`: Area of knowledge

### Keyword
**Description:** Specific term or phrase frequently mentioned  
**Properties:**
- `term`: The keyword
- `frequency`: How often mentioned
- `context`: Where it appears
- `trendingScore`: Recent increase in mentions

**Examples:**
- "API design"
- "Budget planning"
- "Work-life balance"
- "Home office setup"

## Location Entities

### Location
**Description:** Physical or virtual place  
**Properties:**
- `name`: Location name
- `type`: Office, city, country, virtual
- `address`: Physical address
- `coordinates`: Lat/long if relevant
- `timezone`: Time zone
- `significance`: Why it matters

**Examples:**
- "San Francisco Office"
- "Conference Room A"
- "Home Office"
- "Starbucks on Main St"

**Subtypes:**
- `Office`: Office location
- `City`: City
- `Country`: Country
- `Building`: Specific building
- `Room`: Room or space
- `VirtualLocation`: Virtual space (Zoom room, Slack channel)
- `TravelDestination`: Place visited or to visit

## Event & Temporal Entities

### Event
**Description:** Significant occurrence or milestone  
**Properties:**
- `name`: Event name
- `date`: When it occurred/will occur
- `type`: Conference, launch, deadline, personal
- `location`: Where it happened
- `description`: Event details
- `importance`: Significance level
- `participants`: Who was involved

**Examples:**
- "Product Launch Event"
- "AWS re:Invent 2025"
- "Wedding Anniversary"
- "Project Deadline"

**Subtypes:**
- `Conference`: Industry conference
- `Launch`: Product or project launch
- `Deadline`: Important deadline
- `Milestone`: Project milestone
- `Celebration`: Personal celebration
- `Anniversary`: Annual event
- `Appointment`: Scheduled appointment

### TimeFrame
**Description:** Period of time with significance  
**Properties:**
- `name`: Period name
- `startDate`: Start date
- `endDate`: End date
- `type`: Quarter, month, sprint, semester
- `goals`: Goals for this period

**Examples:**
- "Q4 2025"
- "Sprint 12"
- "Summer 2025"
- "Fiscal Year 2025"

## Decision & Insight Entities

### Decision
**Description:** Important decision made  
**Properties:**
- `description`: What was decided
- `date`: When decided
- `decisionMakers`: Who decided
- `rationale`: Why this decision
- `alternatives`: Options considered
- `outcome`: Result of decision
- `status`: Proposed, approved, implemented, reversed

**Examples:**
- "Chose React over Vue for frontend"
- "Decided to pursue MBA"
- "Approved budget increase"
- "Postponed product launch"

### Insight
**Description:** Important realization or learning  
**Properties:**
- `description`: The insight
- `date`: When realized
- `context`: What led to it
- `impact`: Significance
- `source`: Where it came from
- `actionable`: Can it be acted on

**Examples:**
- "Customers need mobile app more than web"
- "Morning routine improves productivity"
- "Team needs better async communication"
- "Delegation reduces bottlenecks"

## Product & Technology Entities

### Product
**Description:** Product or service (yours or others')  
**Properties:**
- `name`: Product name
- `type`: Software, hardware, service
- `vendor`: Who makes it
- `status`: Using, evaluating, retired
- `purpose`: Why you use it
- `cost`: Pricing
- `alternatives`: Other options considered

**Examples:**
- "Slack" (communication tool)
- "iPhone 15" (device)
- "AWS Lambda" (service)
- "Our SaaS Platform" (your product)

### Technology
**Description:** Technical tool, framework, or platform  
**Properties:**
- `name`: Technology name
- `type`: Language, framework, platform, tool
- `version`: Version in use
- `expertise`: Your skill level
- `purpose`: Use case
- `documentation`: Link to docs

**Examples:**
- "Python 3.11"
- "React 18"
- "PostgreSQL"
- "Docker"

## Financial Entities

### Transaction
**Description:** Financial transaction or expense  
**Properties:**
- `description`: What it was for
- `amount`: Dollar amount
- `date`: Transaction date
- `category`: Expense category
- `type`: Expense, income, investment
- `payee`: Who received payment
- `account`: Which account

**Examples:**
- "Client Payment - Acme Corp"
- "Office Supplies Purchase"
- "Conference Registration"
- "Contractor Invoice"

### Budget
**Description:** Budget allocation or financial plan  
**Properties:**
- `name`: Budget name
- `amount`: Total amount
- `period`: Time period
- `category`: What it covers
- `allocated`: How much assigned
- `spent`: How much used
- `remaining`: What's left

**Examples:**
- "Q4 Marketing Budget"
- "Home Renovation Budget"
- "Travel Budget 2025"
- "Team Expenses"

## Goal & Objective Entities

### Goal
**Description:** Long-term objective  
**Properties:**
- `description`: What you want to achieve
- `type`: Career, personal, financial, health
- `timeframe`: When to achieve by
- `status`: Not started, in progress, achieved
- `milestones`: Key steps
- `metrics`: Success measures

**Examples:**
- "Get promoted to Senior Manager"
- "Run a marathon"
- "Save $50K for house"
- "Launch side business"

### Metric
**Description:** Measurable indicator  
**Properties:**
- `name`: Metric name
- `currentValue`: Current measurement
- `targetValue`: Goal value
- `unit`: Unit of measurement
- `frequency`: How often measured
- `trend`: Improving, declining, stable

**Examples:**
- "Customer Satisfaction Score"
- "Weekly Exercise Hours"
- "Monthly Revenue"
- "Weight"

## Personal Life Entities

### Hobby
**Description:** Personal interest or hobby  
**Properties:**
- `name`: Hobby name
- `frequency`: How often engaged
- `skillLevel`: Your proficiency
- `equipment`: Tools or equipment used
- `notes`: Related notes

**Examples:**
- "Photography"
- "Woodworking"
- "Guitar"
- "Cooking"

### Health
**Description:** Health-related information  
**Properties:**
- `type`: Condition, symptom, treatment, routine
- `description`: Details
- `date`: When noted
- `provider`: Healthcare provider if relevant
- `status`: Active, resolved, monitoring

**Examples:**
- "Back pain - lower lumbar"
- "Morning stretching routine"
- "Allergy: Peanuts"
- "Physical therapy sessions"

---

# Relationship Types

Relationship types define how entities connect to each other. These are directional (from → to) unless marked as bidirectional.

## Organizational Relationships

### WORKS_FOR
**From:** Person → Organization  
**Description:** Employment relationship  
**Properties:**
- `role`: Job title
- `startDate`: Employment start
- `endDate`: Employment end (if applicable)
- `department`: Department or team

**Example:** "John Smith WORKS_FOR Acme Corporation"

### WORKS_WITH
**From:** Person ↔ Person  
**Description:** Collaborative work relationship (bidirectional)  
**Properties:**
- `context`: How they work together
- `frequency`: How often
- `projects`: Shared projects

**Example:** "Sarah WORKS_WITH Mike"

### MANAGES
**From:** Person → Person  
**Description:** Management relationship  
**Properties:**
- `startDate`: When management started
- `managementStyle`: 1:1 frequency, approach

**Example:** "Lisa MANAGES John"

### REPORTS_TO
**From:** Person → Person  
**Description:** Reporting relationship  
**Properties:**
- `startDate`: When started
- `frequency`: Check-in frequency

**Example:** "John REPORTS_TO Lisa"

### PART_OF
**From:** Team/Department → Organization  
**Description:** Organizational hierarchy  
**Properties:**
- `level`: Hierarchy level

**Example:** "Engineering Team PART_OF Acme Corporation"

### MEMBER_OF
**From:** Person → Team/Organization  
**Description:** Membership in group  
**Properties:**
- `role`: Role within group
- `startDate`: When joined
- `status`: Active, inactive

**Example:** "John MEMBER_OF Engineering Team"

## Project & Work Relationships

### ASSIGNED_TO
**From:** Task → Person  
**Description:** Task ownership  
**Properties:**
- `assignedDate`: When assigned
- `dueDate`: When due
- `priority`: Task priority

**Example:** "Code Review ASSIGNED_TO Sarah"

### PART_OF_PROJECT
**From:** Task/Note/Meeting → Project  
**Description:** Belongs to project  
**Properties:**
- `phase`: Project phase
- `relevance`: How central to project

**Example:** "Design Review Meeting PART_OF_PROJECT Website Redesign"

### DEPENDS_ON
**From:** Task/Project → Task/Project  
**Description:** Dependency relationship  
**Properties:**
- `dependencyType`: Blocking, related, prerequisite
- `strength`: Strong, weak

**Example:** "Backend Development DEPENDS_ON Database Design"

### CONTRIBUTES_TO
**From:** Person → Project  
**Description:** Person's involvement in project  
**Properties:**
- `role`: Their role
- `startDate`: When started contributing
- `hoursPerWeek`: Time commitment

**Example:** "Mike CONTRIBUTES_TO Website Redesign"

### OWNS
**From:** Person → Project/Product  
**Description:** Ownership responsibility  
**Properties:**
- `startDate`: When became owner
- `scope`: What they own

**Example:** "Sarah OWNS Mobile App Project"

### BLOCKS
**From:** Task/Issue → Task/Project  
**Description:** One thing blocking another  
**Properties:**
- `severity`: Critical, major, minor
- `since`: When blocked started

**Example:** "API Issue BLOCKS Frontend Development"

## Communication & Interaction Relationships

### ATTENDED
**From:** Person → Meeting/Event  
**Description:** Participation in meeting or event  
**Properties:**
- `role`: Organizer, presenter, participant
- `duration`: How long attended

**Example:** "John ATTENDED Q4 Planning Meeting"

### MENTIONED_IN
**From:** Entity → Note/Meeting/Document  
**Description:** Entity referenced in content  
**Properties:**
- `context`: Surrounding text
- `sentiment`: Positive, neutral, negative
- `prominence`: How central to content

**Example:** "Product Launch MENTIONED_IN Strategy Meeting"

### DISCUSSED
**From:** Meeting → Topic/Project/Decision  
**Description:** What was discussed  
**Properties:**
- `duration`: Time spent on topic
- `outcome`: Result of discussion

**Example:** "Planning Meeting DISCUSSED Budget Allocation"

### SPOKE_WITH
**From:** Person → Person  
**Description:** Communication occurred  
**Properties:**
- `date`: When communication happened
- `medium`: In-person, phone, video, email
- `topic`: What was discussed

**Example:** "John SPOKE_WITH Client (re: Requirements)"

### SENT_TO
**From:** Document/Email → Person  
**Description:** Information transmitted  
**Properties:**
- `date`: When sent
- `method`: Email, shared link, etc.

**Example:** "Proposal Document SENT_TO Client Contact"

## Knowledge & Learning Relationships

### REFERENCES
**From:** Note/Document → Resource/Document  
**Description:** Citation or reference  
**Properties:**
- `citationType`: Direct quote, paraphrase, inspiration
- `pageNumber`: Specific location if applicable

**Example:** "Research Notes REFERENCES AI Research Paper"

### RELATES_TO
**From:** Entity ↔ Entity  
**Description:** General semantic relationship (bidirectional)  
**Properties:**
- `strength`: Strong, moderate, weak
- `relationshipType`: Similar, contrasts, complements

**Example:** "Machine Learning RELATES_TO Data Science"

### TEACHES
**From:** Resource/Person → Concept/Skill  
**Description:** Learning source  
**Properties:**
- `effectiveness`: How well it teaches
- `completionDate`: When finished

**Example:** "Online Course TEACHES Python Programming"

### APPLIES_TO
**From:** Concept/Technique → Project/Problem  
**Description:** Practical application  
**Properties:**
- `effectiveness`: How well it worked
- `context`: Where applied

**Example:** "Agile Methodology APPLIES_TO Website Project"

### INSPIRED_BY
**From:** Idea/Project → Resource/Person/Event  
**Description:** Source of inspiration  
**Properties:**
- `how`: Description of inspiration

**Example:** "New Feature Idea INSPIRED_BY Competitor Analysis"

### LEARNED_FROM
**From:** Person → Person/Resource/Experience  
**Description:** Knowledge acquisition  
**Properties:**
- `what`: What was learned
- `date`: When learned

**Example:** "John LEARNED_FROM Mentor about Leadership"

## Temporal Relationships

### PRECEDED_BY
**From:** Event/Meeting/Note → Event/Meeting/Note  
**Description:** Temporal sequence  
**Properties:**
- `timeDelta`: Time between events

**Example:** "Sprint 13 PRECEDED_BY Sprint 12"

### FOLLOWED_BY
**From:** Event/Meeting/Note → Event/Meeting/Note  
**Description:** Temporal sequence (reverse)  
**Properties:**
- `timeDelta`: Time between events

**Example:** "Sprint 12 FOLLOWED_BY Sprint 13"

### OCCURRED_DURING
**From:** Event/Note/Meeting → TimeFrame  
**Description:** Temporal containment  
**Properties:**
- `exactDate`: Specific date within timeframe

**Example:** "Product Launch OCCURRED_DURING Q3 2025"

### DUE_BY
**From:** Task/Project → Date/TimeFrame  
**Description:** Deadline relationship  
**Properties:**
- `hardDeadline`: Is this flexible?
- `consequences`: What happens if missed

**Example:** "Contract Review DUE_BY Oct 31, 2025"

### SCHEDULED_FOR
**From:** Meeting/Event → Date/Time  
**Description:** Scheduled occurrence  
**Properties:**
- `recurring`: Is this recurring?
- `frequency`: How often if recurring

**Example:** "Team Standup SCHEDULED_FOR Daily 9am"

## Causal Relationships

### CAUSED_BY
**From:** Event/Decision/Insight → Event/Meeting/Discussion  
**Description:** Causal relationship  
**Properties:**
- `confidence`: How certain the causation
- `directness`: Direct or indirect cause

**Example:** "Budget Increase CAUSED_BY Revenue Growth"

### LED_TO
**From:** Decision/Action → Outcome/Event  
**Description:** Result relationship  
**Properties:**
- `timeToEffect`: How long until effect
- `magnitude`: Size of impact

**Example:** "Hiring Freeze LED_TO Project Delays"

### RESULTED_IN
**From:** Action/Event → Outcome  
**Description:** Outcome relationship  
**Properties:**
- `positive`: Was outcome positive?
- `expected`: Was this expected?

**Example:** "Marketing Campaign RESULTED_IN 50% Lead Increase"

### INFLUENCED_BY
**From:** Decision/Opinion → Person/Event/Resource  
**Description:** Influence relationship  
**Properties:**
- `strength`: How much influence
- `type`: Direct, indirect

**Example:** "Product Strategy INFLUENCED_BY Customer Feedback"

### PREVENTED
**From:** Action/Decision → Risk/Problem  
**Description:** Preventative action  
**Properties:**
- `severity`: How bad was potential issue

**Example:** "Security Audit PREVENTED Data Breach"

## Content Relationships

### SUMMARIZES
**From:** Note/Document → Meeting/Resource/Period  
**Description:** Summary relationship  
**Properties:**
- `completeness`: How comprehensive
- `format`: Bullet points, prose, etc.

**Example:** "Meeting Summary SUMMARIZES Q4 Planning Session"

### EXPANDS_ON
**From:** Note/Document → Note/Concept  
**Description:** Elaboration relationship  
**Properties:**
- `depth`: How much detail added

**Example:** "Technical Spec EXPANDS_ON Initial Proposal"

### CONTRADICTS
**From:** Statement/Note → Statement/Note  
**Description:** Conflicting information  
**Properties:**
- `severity`: How significant the contradiction
- `resolution`: How resolved

**Example:** "New Research CONTRADICTS Previous Assumption"

### SUPPORTS
**From:** Evidence/Note → Claim/Hypothesis  
**Description:** Evidential support  
**Properties:**
- `strength`: Strong, moderate, weak evidence

**Example:** "User Survey Results SUPPORTS Feature Request"

### REPLACES
**From:** Document/Decision → Document/Decision  
**Description:** Superseding relationship  
**Properties:**
- `reason`: Why replaced
- `date`: When replaced

**Example:** "New Policy REPLACES Old Policy"

### UPDATES
**From:** Note/Document → Note/Document  
**Description:** Updated version  
**Properties:**
- `majorChanges`: Significant changes made
- `version`: Version number

**Example:** "Q4 Report v2 UPDATES Q4 Report v1"

## Location Relationships

### LOCATED_IN
**From:** Entity → Location  
**Description:** Physical location  
**Properties:**
- `permanence`: Permanent, temporary
- `access`: How to access

**Example:** "Server LOCATED_IN Data Center"

### HAPPENED_AT
**From:** Event/Meeting → Location  
**Description:** Event location  
**Properties:**
- `virtual`: Is this virtual or physical?

**Example:** "Conference HAPPENED_AT Convention Center"

### WORKS_FROM
**From:** Person → Location  
**Description:** Work location  
**Properties:**
- `frequency`: How often
- `schedule`: Which days

**Example:** "Sarah WORKS_FROM Home Office"

## Hierarchical Relationships

### PARENT_OF
**From:** Entity → Entity  
**Description:** Hierarchical parent (bidirectional with CHILD_OF)  
**Properties:**
- `hierarchyType`: Organizational, conceptual, structural

**Example:** "Product Strategy PARENT_OF Feature Roadmap"

### CHILD_OF
**From:** Entity → Entity  
**Description:** Hierarchical child (bidirectional with PARENT_OF)  
**Properties:**
- `hierarchyType`: Organizational, conceptual, structural

**Example:** "Feature Roadmap CHILD_OF Product Strategy"

### INSTANCE_OF
**From:** Specific → General  
**Description:** Type relationship  
**Properties:**
- `confidence`: How certain this categorization

**Example:** "Customer Complaint INSTANCE_OF Support Issue"

### CATEGORY_OF
**From:** Category → Specific  
**Description:** Categorization (reverse of INSTANCE_OF)  
**Properties:**
- `comprehensiveness`: How many instances

**Example:** "Support Issue CATEGORY_OF Customer Complaint"

## Tag Relationships

### TAGGED_WITH
**From:** Note/Entity → Tag/Keyword  
**Description:** Tagging relationship  
**Properties:**
- `source`: User-applied or AI-extracted
- `confidence`: For AI tags

**Example:** "Meeting Notes TAGGED_WITH urgent"

### HAS_METADATA
**From:** Entity → Metadata (key:value)  
**Description:** Structured metadata  
**Properties:**
- `key`: Metadata key
- `value`: Metadata value
- `source`: How this was set

**Example:** "Project Note HAS_METADATA type:meeting"

## Personal Relationships

### KNOWS
**From:** Person ↔ Person  
**Description:** Acquaintance relationship (bidirectional)  
**Properties:**
- `howMet`: Where/how introduced
- `since`: When relationship started
- `strength`: Strong, moderate, weak

**Example:** "John KNOWS Sarah"

### RELATED_TO
**From:** Person → Person  
**Description:** Family relationship  
**Properties:**
- `relationType`: Parent, sibling, spouse, child, etc.

**Example:** "John RELATED_TO Mom (mother)"

### INTRODUCED_BY
**From:** Person → Person  
**Description:** Introduction relationship  
**Properties:**
- `date`: When introduced
- `context`: Why introduced

**Example:** "New Client INTRODUCED_BY Existing Client"

---

# Property Schemas

## Common Properties

All entities should have these base properties:

```
{
  "id": "unique-identifier",
  "label": "EntityType",
  "createdAt": "ISO-8601 timestamp",
  "updatedAt": "ISO-8601 timestamp",
  "createdBy": "system|user",
  "confidence": 0.0-1.0,
  "sourceNotes": ["note-id-1", "note-id-2"],
  "mentionCount": integer,
  "importance": 0.0-1.0,
  "verified": boolean,
  "tags": ["tag1", "tag2"],
  "metadata": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

All relationships should have these base properties:

```
{
  "type": "RELATIONSHIP_TYPE",
  "from": "entity-id",
  "to": "entity-id",
  "createdAt": "ISO-8601 timestamp",
  "weight": 0.0-1.0,
  "confidence": 0.0-1.0,
  "sourceNotes": ["note-id-1", "note-id-2"],
  "bidirectional": boolean,
  "metadata": {}
}
```

---

# Usage Examples

## Example 1: Rocketbook Meeting Note

**Captured Note:**
```
Q4 Planning Meeting - Oct 17, 2025

Attendees: Sarah (PM), Mike (Eng), Lisa (Design)
@project-alpha @urgent ::priority:high ::type:meeting

Decisions:
- Move launch date to Nov 15
- Increase budget by $50K
- Hire 2 contractors

Action Items:
☐ Sarah: Update roadmap by Friday
☐ Mike: Interview contractors next week
☐ Lisa: Finalize designs by Oct 25
```

**Extracted Entities:**

1. **Note** entity
   - `id`: note-12345
   - `title`: "Q4 Planning Meeting"
   - `captureDate`: 2025-10-17
   - `source`: rocketbook-blue
   - `tags`: ["project-alpha", "urgent"]
   - `metadata`: {priority: "high", type: "meeting"}

2. **Meeting** entity
   - `title`: "Q4 Planning Meeting"
   - `date`: 2025-10-17
   - `attendees`: ["Sarah", "Mike", "Lisa"]
   - `type`: planning

3. **Person** entities (3)
   - Sarah (PM)
   - Mike (Engineering)
   - Lisa (Design)

4. **Project** entity
   - `name`: "Project Alpha"
   - `status`: active
   - `priority`: high

5. **Decision** entities (3)
   - "Move launch date to Nov 15"
   - "Increase budget by $50K"
   - "Hire 2 contractors"

6. **Task** entities (3)
   - Update roadmap
   - Interview contractors
   - Finalize designs

7. **Event** entity
   - "Product Launch"
   - `date`: 2025-11-15

**Extracted Relationships:**

1. Note SUMMARIZES Meeting
2. Sarah ATTENDED Meeting
3. Mike ATTENDED Meeting
4. Lisa ATTENDED Meeting
5. Meeting PART_OF_PROJECT Project Alpha
6. Meeting DISCUSSED Decision (x3)
7. Decision LED_TO Event (launch date)
8. Task ASSIGNED_TO Sarah
9. Task ASSIGNED_TO Mike
10. Task ASSIGNED_TO Lisa
11. Task PART_OF_PROJECT Project Alpha
12. Project Alpha TAGGED_WITH "urgent"

## Example 2: Audio Note on Commute

**Captured Audio Transcript:**
```
"Idea for improving user onboarding. Talk to Sarah about this.
We should add a tutorial mode for first-time users.
This relates to the customer feedback we got last week
about the app being confusing. Could reduce support tickets
by 30% based on what I read in that article about onboarding best practices."
```

**Extracted Entities:**

1. **Note** entity (AudioNote)
   - Content: transcription
   - Source: audio recording
   - captureDate: 2025-10-17

2. **Idea** entity
   - "Tutorial mode for first-time users"

3. **Person** entity
   - Sarah

4. **Concept** entities
   - "User onboarding"
   - "First-time user experience"

5. **Insight** entity
   - "Confusing app reduces adoption"

6. **Metric** entity
   - "Support ticket reduction: 30%"

7. **Resource** entity
   - "Article about onboarding best practices"

8. **Task** (implicit)
   - "Talk to Sarah about onboarding idea"

**Extracted Relationships:**

1. Idea APPLIES_TO User Onboarding
2. Task ASSIGNED_TO Self (need to talk to Sarah)
3. Task MENTIONED Person (Sarah)
4. Idea INSPIRED_BY Resource (article)
5. Idea SUPPORTS Metric (30% reduction)
6. Idea ADDRESSES Insight (confusion problem)
7. Insight CAUSED_BY Customer Feedback (previous note)

## Example 3: Knowledge Graph Evolution

**Day 1:** Scan Rocketbook note about client meeting
- Creates: Client organization entity
- Creates: Meeting entity
- Creates: 3 Person entities (attendees)
- Creates: Project entity (new engagement)
- Creates: 2 Task entities (action items)

**Day 3:** Import meeting transcript from Zoom
- Matches: Same meeting entity (temporal match)
- Enriches: Meeting with full transcript
- Extracts: 10 more Concept entities from discussion
- Creates: 5 Decision entities
- Strengthens: Relationships between attendees and project

**Day 7:** Scan follow-up note
- Matches: Existing project entity
- Creates: Note entity
- Creates: Update relationship to previous meeting
- Creates: 3 new Task entities
- Shows: Progress on previous tasks (PRECEDED_BY relationships)

**Day 14:** Import email thread with client
- Matches: Client organization
- Matches: Project
- Creates: Multiple email capture entities
- Creates: DISCUSSED relationships to project topics
- Strengthens: Person-to-Person relationships

**Result after 2 weeks:**
- Single Project node connects: 10+ notes, 2 meetings, 15 tasks, 5 people, 20 concepts
- Knowledge graph shows: Decision history, task dependencies, conversation evolution
- Search query "What did client say about timeline?" returns: relevant excerpts from note, transcript, and emails
- AI can answer: "Why did we make this decision?" with full context

---

# Extraction Rules

## Entity Extraction Priorities

### High Priority (Always Extract)
1. **People** - Any named person mentioned
2. **Organizations** - Companies, institutions
3. **Projects** - Named initiatives
4. **Tasks** - Action items with checkboxes or action verbs
5. **Dates** - Explicit dates and deadlines
6. **Decisions** - Statements of choice or direction

### Medium Priority (Extract with Context)
1. **Concepts** - Domain topics mentioned multiple times
2. **Locations** - Places mentioned with context
3. **Documents** - Referenced reports, papers, presentations
4. **Products** - Tools and services mentioned
5. **Meetings** - Scheduled gatherings
6. **Events** - Significant occurrences

### Low Priority (Extract Selectively)
1. **Keywords** - Only if high frequency or importance
2. **Insights** - Only if clearly stated
3. **Resources** - Only if will be referenced again

## Relationship Extraction Rules

### Automatic Relationship Creation

**Co-occurrence Rules:**
- If 2 people mentioned in same note → Create WORKS_WITH (if work context) or KNOWS
- If person + project mentioned → Create CONTRIBUTES_TO or MENTIONED_IN
- If concept + project mentioned → Create APPLIES_TO or RELATES_TO

**Temporal Rules:**
- Notes on same day about same project → Create RELATES_TO
- Meeting + follow-up note within 7 days → Create UPDATES or FOLLOWED_BY
- Task in note + person as assignee → Create ASSIGNED_TO

**Semantic Rules:**
- "Because of X, we did Y" → Create CAUSED_BY or LED_TO
- "X works for Y" → Create WORKS_FOR
- "X reports to Y" → Create REPORTS_TO
- "Based on X" → Create INFLUENCED_BY or INSPIRED_BY

**Action Rules:**
- Checkbox item + name → Create ASSIGNED_TO
- "Follow up with X" → Create Task + ASSIGNED_TO self + INVOLVES person X
- "Review X by date" → Create Task + REFERENCES document X

### Relationship Weight Calculation

Relationship `weight` (0.0 to 1.0) based on:
- **Frequency**: How often entities co-occur (0.3 weight)
- **Recency**: How recently co-occurred (0.3 weight)
- **Explicitness**: Direct vs implied relationship (0.2 weight)
- **User confirmation**: User has verified (0.2 weight)

Example:
- First mention: weight = 0.3
- Mentioned together 5 times: weight = 0.6
- Mentioned in last 7 days: weight += 0.1 = 0.7
- User confirms relationship: weight = 0.9

### Disambiguation Rules

When same name appears:
1. Check context for disambiguating info (title, company, project)
2. Check temporal proximity (recent mentions likely same person)
3. Check relationship clusters (who they're mentioned with)
4. If uncertain: Create separate entities, flag for user review
5. Learn from user corrections

### Merge Rules

Merge entities when:
- Same name + same context (company, role)
- User confirms they're the same
- Strong clustering signal (always mentioned with same people/projects)
- Explicit alias ("Mike (Michael Smith)")

---

# Graph Query Examples

## Example Queries Users Might Make

### "Show me everything related to Project Alpha"
```
MATCH path = (p:Project {name: "Project Alpha"})-[*1..2]-(related)
RETURN path
```

Returns: All notes, meetings, people, tasks, decisions within 2 hops

### "Who have I been meeting with most this month?"
```
MATCH (me:Person {name: "Self"})-[:ATTENDED]->(m:Meeting)
WHERE m.date >= startOfMonth
MATCH (m)<-[:ATTENDED]-(other:Person)
RETURN other.name, count(m) as meetingCount
ORDER BY meetingCount DESC
```

### "What decisions led to our current product strategy?"
```
MATCH path = (d:Decision)-[:LED_TO|INFLUENCED_BY*]->(s:Strategy {name: "Current Product Strategy"})
RETURN path
```

### "Find all action items assigned to me that are overdue"
```
MATCH (me:Person {name: "Self"})<-[:ASSIGNED_TO]-(t:Task)
WHERE t.dueDate < currentDate AND t.status != "completed"
RETURN t
ORDER BY t.priority DESC, t.dueDate ASC
```

### "What have I learned about machine learning in the last 6 months?"
```
MATCH (me:Person {name: "Self"})-[:LEARNED_FROM]->(source)
-[:TEACHES]->(c:Concept {name: "Machine Learning"})
WHERE source.date >= sixMonthsAgo
RETURN source, c
```

### "Show me the evolution of the Q4 Planning discussion"
```
MATCH path = (n1:Note)-[:PRECEDED_BY|FOLLOWED_BY|UPDATES*]->(n2:Note)
WHERE n1.title CONTAINS "Q4" OR n2.title CONTAINS "Q4"
RETURN path
ORDER BY n1.captureDate
```

---

This schema provides a comprehensive foundation for building your knowledge graph. You can extend it with additional entity types and relationships as needed based on your specific use cases.
