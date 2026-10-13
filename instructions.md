# BALLRIQ — Multilingual Cricket Intelligence Platform

Build a modern, production-style web application called **BALLRIQ**.

BALLRIQ is inspired by the information architecture and match-detail experience of modern sports intelligence platforms such as FotMob, but it is designed specifically for **cricket** and introduces a major AI capability:

> **BALLRIQ is a multilingual AI-powered cricket audio analysis and RAG-based query engine that processes cricket commentary and conversations in Hindi and Marathi, extracts meaningful match insights, and enables users to ask natural-language questions about players, matches, events, statistics, and key moments.**

The platform must combine:

1. A **modern cricket match analytics interface**
2. **Hindi and Marathi cricket commentary processing**
3. **NLP-based speech and text analysis**
4. **Information Retrieval and semantic search**
5. A **Retrieval-Augmented Generation (RAG) question-answering engine**
6. A visual match experience inspired by professional sports applications

The application should feel like a real sports product rather than a college project dashboard.

---

# 1. Core Product Vision

Users should be able to select a cricket match and see a detailed match page containing:

- Live or recorded match score
- Teams and match information
- Match timeline
- Ball-by-ball events
- Important moments
- Key statistics
- Player performance
- Team comparison
- Commentary
- AI-generated match insights
- Audio-derived events
- Hindi and Marathi commentary transcripts
- Natural language search and question answering

The platform should support questions such as:

### Hindi

- "कोहली ने कितने रन बनाए?"
- "सबसे महत्वपूर्ण विकेट कौन सा था?"
- "भारत कब मैच में वापस आया?"
- "पावरप्ले में टीम का प्रदर्शन कैसा था?"
- "बुमराह ने किन बल्लेबाजों को आउट किया?"

### Marathi

- "कोहलीने किती धावा केल्या?"
- "सामन्यातील सर्वात महत्त्वाची विकेट कोणती होती?"
- "भारत सामन्यात पुन्हा कधी आला?"
- "पॉवरप्लेमध्ये संघाची कामगिरी कशी होती?"
- "बुमराहने कोणत्या फलंदाजांना बाद केले?"

The system should answer these questions using retrieved match data, commentary, transcripts, events, and statistics rather than hallucinating answers.

---

# 2. Main Application Structure

The homepage should contain:

## Header

- BALLRIQ logo
- Search bar
- Language selector
  - English
  - Hindi
  - Marathi
- Theme toggle
- User/profile placeholder

## Main Navigation

- Matches
- Live
- Upcoming
- Results
- Teams
- Players
- AI Search

The design should be clean, data-heavy, modern, and similar in usability to professional sports applications.

---

# 3. Match Details Page

This is the most important page.

The match page should be visually structured like a professional sports match page.

## Match Header

Display:

- Tournament/series name
- Match format
  - T20
  - ODI
  - Test
- Venue
- Match date
- Match status

Large central score display:

INDIA
186/5

vs

AUSTRALIA
182/8

India won by 5 wickets

Also display:

- Current/Final score
- Overs
- Required run rate
- Current run rate
- Match status

Example:

India 186/5 (19.2)

Australia 182/8 (20)

India won by 5 wickets.

---

# 4. Match Navigation Tabs

The match page should have the following tabs:

## Overview

The default page.

Contains:

- Match summary
- AI-generated match review
- Match momentum visualization
- Top statistics
- Key events
- Important moments

---

## Commentary

Display chronological ball-by-ball commentary.

Example:

18.4
Bumrah bowls a yorker and the batter is beaten.

18.5
WICKET! Clean bowled!

The user should be able to filter commentary by:

- All
- Wickets
- Fours
- Sixes
- Key moments

Each commentary item should support:

- Original commentary
- Hindi transcription
- Marathi transcription
- Timestamp
- Ball number
- Event type

---

## Timeline

Create a visual event timeline.

Events include:

- Wicket
- Four
- Six
- Fifty
- Century
- Partnership milestone
- Bowling milestone
- Catch
- Run out
- Match turning point

Example:

3.2 🟢 FOUR — Rohit Sharma

5.4 🔴 WICKET — Gill c Smith b Starc

8.1 🟣 SIX — Kohli

14.3 🔴 WICKET — Pandya lbw

18.5 🟢 FOUR — Match winning boundary

The timeline should be interactive.

Clicking an event should open:

- Commentary
- Audio timestamp
- Match context
- AI explanation

---

## Stats

Display professional cricket analytics.

### Team Stats

- Total score
- Run rate
- Boundaries
- Dot balls
- Extras
- Wickets
- Partnerships
- Strike rate

### Batting Stats

- Runs
- Balls
- Fours
- Sixes
- Strike rate
- Dot ball percentage

### Bowling Stats

- Overs
- Runs conceded
- Wickets
- Economy
- Dot balls
- Wides
- No balls

Include visual comparisons between teams.

---

## Players

Show player cards.

Each player card contains:

- Player image placeholder
- Name
- Role
- Team
- Runs
- Wickets
- Strike rate
- Economy
- AI-generated performance summary

Example:

Virat Kohli

78 (52)

Strike Rate: 150

AI Insight:

"Anchored India's chase during the middle overs and accelerated after the 15th over."

---

# 5. AI Match Review

Generate a concise AI-powered match summary.

Example:

"India's victory was built on a strong middle-order partnership after an early loss of wickets. Kohli stabilized the innings while Pandya increased the scoring rate during the death overs. Australia's inability to contain boundaries in overs 16–20 proved decisive."

The AI review must be generated using retrieved match information.

Do not generate unsupported claims.

---

# 6. Audio Analysis Module

This is one of the primary NLP components.

The system should accept cricket commentary audio in:

- Hindi
- Marathi

Audio pipeline:

Audio Input

↓

Audio Preprocessing

↓

Language Identification

↓

Speech-to-Text

↓

Hindi / Marathi Transcript

↓

Text Cleaning and Normalization

↓

Cricket Entity Recognition

↓

Event Extraction

↓

Match Knowledge Base

↓

Semantic Search and RAG

The system should store:

- Audio timestamp
- Original transcription
- Detected language
- Player names
- Teams
- Cricket terminology
- Event type
- Ball number if detected

---

# 7. NLP Module

This project must clearly demonstrate NLP concepts.

Implement the following components.

## Language Identification

Detect whether commentary is:

- Hindi
- Marathi
- English
- Code-mixed Hindi-English
- Code-mixed Marathi-English

Example:

"Virat ne शानदार चौका मारा."

The system should identify the language mixture and correctly process cricket terminology.

---

## Speech Recognition

Convert Hindi and Marathi commentary audio into text.

Store:

Audio Timestamp → Transcript

Example:

00:12:45

"कोहली ने शानदार कवर ड्राइव खेला और गेंद चार रन के लिए चली गई।"

---

## Text Normalization

Handle:

- Cricket abbreviations
- Numbers
- Code mixing
- Player names
- Spelling variations

Examples:

"चार रन"

"4 runs"

"फोर"

All should map to:

FOUR

---

# 8. Named Entity Recognition

Extract cricket entities.

Entities include:

### Players

Virat Kohli

Rohit Sharma

Jasprit Bumrah

### Teams

India

Australia

### Events

Four

Six

Wicket

Catch

Run Out

LBW

### Cricket Concepts

Powerplay

Death Overs

Strike Rate

Economy

Partnership

The extracted entities should be linked to the relevant match information.

---

# 9. Cricket Event Extraction

Convert unstructured commentary into structured events.

Example input:

"बुमराह ने शानदार यॉर्कर डाली और बल्लेबाज बोल्ड हो गया।"

Structured output:

Event Type: WICKET

Dismissal: BOWLED

Bowler: Jasprit Bumrah

Timestamp: 00:23:14

Importance Score: 0.92

The system should detect:

- Runs
- Fours
- Sixes
- Wickets
- Player milestones
- Partnerships
- Match turning points

---

# 10. Information Retrieval System

This component is essential for satisfying the **Information Retrieval subject**.

Create a searchable cricket knowledge base containing:

- Commentary transcripts
- Ball-by-ball events
- Match statistics
- Player statistics
- AI-generated summaries
- Extracted entities
- Match metadata

Implement two retrieval approaches.

## Lexical Retrieval

Use:

- TF-IDF
- BM25

Example query:

"Virat Kohli boundaries"

Retrieve commentary segments containing relevant information.

---

## Semantic Retrieval

Convert match information into embeddings.

Use a vector database such as:

- FAISS
- ChromaDB

Each document chunk should contain metadata:

Match ID

Inning

Over

Ball

Timestamp

Language

Players

Event Type

Example:

Document:

"18.5 Kohli hits Starc for four through cover."

Metadata:

{
match_id: 102,
over: 18,
ball: 5,
player: "Virat Kohli",
event: "FOUR",
language: "English"
}

---

# 11. Hybrid Search

Implement hybrid information retrieval.

Combine:

BM25 Score

+

Semantic Similarity Score

The system should retrieve the most relevant match information.

This should be explicitly demonstrated as an **Information Retrieval feature**.

---

# 12. RAG Query Engine

Create a conversational question-answering system.

Pipeline:

User Question

↓

Language Detection

↓

Query Translation / Normalization

↓

Hybrid Retrieval

↓

Relevant Match Documents

↓

Context Construction

↓

LLM

↓

Answer

The answer should include:

- Direct answer
- Supporting match information
- Relevant event timestamps
- Retrieved commentary where appropriate

Example:

User:

"भारत कब मैच में वापस आया?"

Answer:

"भारत ने 14वें ओवर के बाद मैच पर नियंत्रण वापस पाना शुरू किया। इस दौरान Kohli और Pandya की साझेदारी ने रन रेट बढ़ाया और आवश्यक रन रेट को नियंत्रण में लाया।"

Supporting Events:

14.2 — FOUR

15.1 — SIX

16.4 — Partnership reached 50

---

# 13. Multilingual Query Support

Users should be able to ask the same question in different languages.

Hindi:

"सबसे ज्यादा रन किसने बनाए?"

Marathi:

"सर्वाधिक धावा कोणी केल्या?"

English:

"Who scored the most runs?"

All three queries should retrieve the same underlying match information.

This demonstrates:

- Cross-lingual Information Retrieval
- Multilingual NLP
- Semantic similarity

---

# 14. AI Ask BALLRIQ

Add a floating AI assistant to every match page.

Example placeholder:

"Ask anything about this match..."

Suggested questions:

- Who was the best player?
- What was the turning point?
- Show all wickets.
- When did the momentum change?
- सर्वाधिक धावा कोणी केल्या?
- सामन्यातील टर्निंग पॉइंट कोणता होता?
- मैच का सबसे महत्वपूर्ण पल क्या था?

The assistant should understand the currently selected match and automatically restrict retrieval to that match unless the user explicitly requests broader data.

---

# 15. Match Momentum

Create a visual momentum graph.

Momentum should be calculated using:

- Runs scored
- Wickets
- Boundaries
- Required run rate
- Partnerships

Important events should create noticeable momentum changes.

Hovering over the graph should show:

Over number

Event

Commentary

AI explanation

---

# 16. Key Moment Detection

Implement an importance scoring algorithm.

Possible factors:

Importance Score =

Wicket Weight

+

Boundary Weight

+

Match Situation Weight

+

Pressure Score

+

Momentum Change

High-importance events should automatically appear in:

- Match Timeline
- AI Summary
- Key Moments section

---

# 17. System Architecture

Use the following architecture.

Frontend:

Next.js or React

Tailwind CSS

Interactive charts

Responsive design

Backend:

FastAPI or Node.js

AI/NLP Services:

Speech-to-Text

Language Detection

NER

Event Extraction

Embeddings

LLM

Information Retrieval:

BM25

Vector Database

Hybrid Search

RAG Pipeline

Database:

PostgreSQL or MongoDB

Vector database:

FAISS or ChromaDB

---

# 18. Database Design

Create the following entities.

## Match

match_id

teams

venue

date

format

result

---

## Commentary

commentary_id

match_id

inning

over

ball

timestamp

original_text

normalized_text

language

---

## Event

event_id

match_id

event_type

player

team

timestamp

importance_score

---

## Player Statistics

player_id

match_id

runs

balls

fours

sixes

wickets

economy

---

## Audio

audio_id

match_id

language

timestamp_start

timestamp_end

transcript

---

# 19. Academic Mapping

The project must clearly demonstrate both NLP and Information Retrieval.

## NLP Contributions

- Hindi speech-to-text
- Marathi speech-to-text
- Language identification
- Code-mixed language handling
- Text normalization
- Named Entity Recognition
- Cricket event extraction
- Intent detection
- Query understanding
- Multilingual semantic understanding
- Automatic match summarization

---

## Information Retrieval Contributions

- Document indexing
- Commentary indexing
- TF-IDF retrieval
- BM25 retrieval
- Vector embeddings
- Semantic search
- Hybrid retrieval
- Metadata filtering
- Cross-lingual retrieval
- Ranking
- Retrieval evaluation
- Precision@K
- Recall@K
- MRR
- nDCG

The application must visibly demonstrate that it is not simply an LLM chatbot.

The retrieval system must be a core component of the architecture.

---

# 20. Evaluation Dashboard

Create a small academic evaluation section.

## NLP Metrics

- Word Error Rate for transcription
- Language Detection Accuracy
- Entity Recognition Precision
- Entity Recognition Recall
- Entity Recognition F1 Score
- Event Extraction Accuracy

## IR Metrics

- Precision@K
- Recall@K
- MRR
- nDCG

Display these results using clean charts and tables.

---

# 21. UI Requirements

The UI should feel like a professional cricket analytics platform.

Design characteristics:

- Dark and light mode
- Dense but readable sports data layout
- Large match score header
- Horizontal navigation tabs
- Interactive event timeline
- Clean statistic cards
- Player performance cards
- Responsive mobile layout
- Floating AI assistant

The FotMob reference should influence the overall information hierarchy and match exploration experience, but the design must be original and cricket-specific.

---

# 22. Final Goal

BALLRIQ should feel like:

"A multilingual AI-powered cricket companion that combines the match-detail experience of a professional live sports platform with NLP-powered Hindi and Marathi commentary understanding and an advanced RAG-based cricket intelligence engine."

The final application should allow a user to:

1. Open a cricket match.
2. Explore score, statistics, players, timeline and commentary.
3. Listen to or upload Hindi/Marathi cricket commentary.
4. Automatically generate transcripts.
5. Extract cricket events and entities.
6. Search the match using keywords.
7. Ask natural-language questions.
8. Retrieve relevant match information.
9. Receive grounded AI-generated answers.
10. Navigate directly to the relevant event or commentary timestamp.