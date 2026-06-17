# Case Study: Spring Garden Waldorf School and Linden

Spring Garden Waldorf School is a K-8 Waldorf school in Copley, Ohio. SageRock built the school an admissions assistant named Linden, reachable at linden@ask.sagerock.com.

## The challenge

Like most schools, Spring Garden's admissions information lived in many places at once: web forms, a tour-scheduling tool, the admissions inbox, an email marketing platform, the student information system, website visitor data, and ad accounts. Knowing where each family stood meant checking eight different systems.

## What we built

We connected eight sources into one read-only data store for the school:

- Gravity Forms, the inquiry and open-house forms on sgws.org, via real-time webhook
- Calendly, for tour scheduling, via webhook with an hourly backstop
- the admissions inbox in Gmail, synced hourly
- Constant Contact, for campaigns, opens, clicks, and opt-outs, nightly
- FACTS SIS, the applications data of record, nightly
- the website visitor tracker, live with an hourly stitch
- Google Ads, for spend, clicks, and conversions, daily
- Google Analytics, for traffic by channel, daily

## The result

Linden has fourteen read-only data tools plus the ability to draft email replies and flag escalations. The team can ask Linden about any prospective family and get an answer that pulls from all eight sources at once: who they are, where they are in the pipeline, when they were last contacted, and how they have engaged. Linden drafts the reply, and a staff member always reviews and sends it. Linden never writes back to any source system.
