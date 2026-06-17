# Case Study: Center for Anthroposophy and Iris

The Center for Anthroposophy is a Waldorf teacher-education institute. SageRock built it an assistant named Iris, reachable at iris@ask.sagerock.com.

## What we built

We connected eight sources into a single read-only data store, all scoped to the Center for Anthroposophy:

- Zoom: nine rooms and more than a thousand recorded class sessions, synced nightly for attendance
- Thinkific: course enrollments, users, and orders, with a daily roster sync
- Cvent: residency and renewal sign-ups, synced daily
- Gravity Forms: inquiry forms on the website, via real-time webhook
- Constant Contact: roughly 13,000 marketing contacts, with opens and clicks
- YouTube: class recordings and transcripts, indexed on upload
- Google Analytics: site traffic by channel, daily
- Google Workspace: email, Drive, and Sheets

## The result

Iris uses read-only tools across the data store to answer staff questions and draft replies. Staff can ask about a student's attendance and enrollments, a registrant's history, a recent inquiry, or marketing engagement, and Iris pulls the answer together from across all eight systems. Iris drafts, and a person reviews and sends. There is no auto-send, and Iris never writes back to the source systems.
