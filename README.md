## # Zendesk Ticket Data Export

Full ticket data export (including ticket details such as comments, attachments, etc) based on date range.

#### Folder structure:

data/
├─ tickets/
│  ├─ {ticket-id}/
│  │  ├─ ticket.json
│  │  ├─ comments/
│  │  │  ├─ {comment-id}/
│  │  │  │  ├─ comment.json

#### Dependencies
-   Python 3
-   Requests