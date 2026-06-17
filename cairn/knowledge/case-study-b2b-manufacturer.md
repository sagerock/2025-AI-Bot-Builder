# Case Study: A National Manufacturer and Athena

SageRock's work is not only for schools. We built a national B2B manufacturer a marketing assistant named Athena, reachable at athena@ask.sagerock.com. At the client's request, the company is not named.

## The challenge

A national marketing team was running campaigns across five major systems with no single place to see how everything was performing together.

## What we built

We connected five sources into one unified, read-only marketing data store:

- Salesforce: campaigns and members, kept in sync
- the company's email marketing platform: a large contact base across dozens of campaigns, with sends, opens, and clicks
- Google Ads: paid search and video, synced daily
- LinkedIn Ads: B2B lead-generation campaigns
- Matomo: web analytics across several sites, via live API

## The result

Every Monday, Athena reads across all five sources and emails the marketing team one plain-English note: ad spend and conversions, B2B leads, email engagement, web traffic, and pipeline. Athena writes the note and a person reads it. It never changes the ad accounts or any source system. One weekly read, instead of five dashboards no one had time to open.
