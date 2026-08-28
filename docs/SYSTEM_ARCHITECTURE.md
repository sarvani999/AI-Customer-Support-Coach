# System Architecture

## 1. Overview

The **AI-Powered Customer Support Assistant with Live Response Guidance** follows a modular multi-agent architecture.

Instead of placing the complete customer-support workflow inside a single component, different responsibilities are handled by specialized agents and supporting modules.

The central **Agent Orchestrator** coordinates these components and controls the processing flow of a customer interaction.

The architecture supports:

- AI-based customer simulation
- Customer message analysis
- Knowledge retrieval
- Live response guidance
- Trainee response evaluation
- Coaching feedback
- Escalation assessment
- Multi-turn conversation management
- Post-interaction reporting
- Performance analytics

The application supports three interaction modes:

1. Simulator Mode
2. Manual Mode
3. Replay Mode

---

## 2. High-Level Architecture

The system can be represented at a high level as:

User / Trainee

↓

Frontend Interface

↓

Flask Backend

↓

Session Management

↓

Agent Orchestrator

↓

Specialized AI and Processing Agents

↓

Knowledge Base / AI Services

↓

Evaluation and Coaching Results

↓

Frontend Display

↓

Post-Interaction Report and Analytics

The frontend is responsible for user interaction, while the backend manages requests, session state, orchestration, knowledge retrieval, and communication with the different agents.

---

## 3. Multi-Agent Architecture

The project uses multiple specialized agents instead of depending on a single AI component.

The major agents are:

1. Customer Simulator Agent
2. Intent and Sentiment Agent
3. Knowledge Recommendation Agent
4. Response Evaluator
5. Coaching Agent
6. Escalation Agent
7. Post-Interaction Summary Agent
8. Agent Orchestrator

Each component has a specific responsibility.

This separation improves modularity and makes individual components easier to test, maintain, and enhance.

---

## 4. Agent Orchestrator

The **Agent Orchestrator** is the central coordination component of the multi-agent system.

Its responsibility is not limited to calling a single model. It coordinates the sequence in which different agents process the conversation.

During an interaction, the orchestrator can coordinate:

- Customer message analysis
- Knowledge retrieval
- Trainee response evaluation
- Coaching generation
- Escalation assessment
- Conversation history
- Generation of the next customer message

The orchestrator also considers the selected interaction mode.

For example:

- Simulator Mode requires generation of the next AI customer message.
- Manual Mode processes customer messages entered manually.
- Replay Mode processes existing conversation content.

This prevents the complete workflow from being manually coordinated independently by the frontend.

---

## 5. Customer Simulator Agent

The **Customer Simulator Agent** is responsible for creating realistic customer messages during Simulator Mode.

The simulator can use information such as:

- Product
- Scenario
- Customer persona
- Difficulty level
- Language
- Previous conversation history

The generated customer message becomes the input for the remaining coaching workflow.

### Multi-Turn Behavior

The simulator maintains conversation context.

This is important because customer support conversations normally contain multiple turns.

For example:

Customer:

"My order has still not arrived."

Trainee:

"I am sorry about the delay. Let me check the available information."

The next customer message should relate to the previous trainee response rather than starting a completely unrelated conversation.

Conversation history is therefore provided as context when generating later customer messages.

### AI and Fallback Behavior

When the configured generative AI service is available, the simulator can generate dynamic customer messages.

Fallback responses are available for cases where AI generation is unavailable.

---

## 6. Intent and Sentiment Agent

The **Intent and Sentiment Agent** analyzes the customer's message.

Its output provides information required by other parts of the coaching system.

Typical analysis includes:

- Intent
- Sentiment
- Frustration level

### Intent

Intent represents the main reason for the customer's message.

Examples may include:

- Return request
- Refund delay
- Late delivery
- Payment issue
- Cancellation
- Wrong item
- Damaged item

### Sentiment

Sentiment represents the emotional direction of the message.

For example:

- Positive
- Neutral
- Negative

### Frustration

Frustration indicates how dissatisfied or emotionally affected the customer appears.

This information is useful for coaching and escalation assessment.

---

## 7. Knowledge Recommendation Agent

The **Knowledge Recommendation Agent** provides relevant support information for the current customer problem.

Instead of expecting the trainee to manually search all available support documents, the system retrieves relevant information from the processed knowledge base.

The general flow is:

Customer Query

↓

Query Processing

↓

Knowledge Search

↓

Relevance Scoring

↓

Relevant Knowledge Chunks

↓

Knowledge Recommendation

The retrieved knowledge can be used while generating response guidance and evaluating the interaction.

---

## 8. Knowledge Storage Architecture

The project contains a lightweight knowledge storage mechanism.

Supported document types include:

- PDF
- DOCX
- TXT

The processing pipeline is:

Document

↓

Text Extraction

↓

Text Cleaning

↓

Chunking

↓

Metadata Processing

↓

Knowledge Storage

The processed knowledge is stored in a JSON-based structure.

### Chunking

Large documents are divided into smaller overlapping text chunks.

Chunking makes it possible to retrieve only the parts of a document that are relevant to the current customer query.

### Retrieval

The current implementation uses token/keyword-based relevance scoring together with available metadata signals.

Therefore, the current project should be described as a **lightweight RAG-style retrieval system**.

It does not currently use a dedicated embedding model and vector database for semantic similarity search.

A vector-based retrieval architecture can be introduced as a future enhancement.

---

## 9. Response Evaluator

The **Response Evaluator** analyzes the response submitted by the trainee.

Its purpose is to determine whether the trainee's reply is suitable for the current customer interaction.

Evaluation can consider communication dimensions such as:

- Empathy
- Tone
- Clarity
- Professionalism
- Resolution quality
- Policy or knowledge relevance

The evaluation result becomes an input for the coaching process and final performance reporting.

---

## 10. Coaching Agent

The **Coaching Agent** provides guidance to the trainee.

It supports two important areas of the system.

### Response Guidance

Before submitting a response, the trainee can request an AI-assisted suggested reply.

The suggestion can use context such as:

- Current customer message
- Customer analysis
- Retrieved knowledge
- Conversation context

The purpose is to guide the trainee rather than automatically replace the trainee's role.

### Coaching Feedback

After the trainee submits a response, coaching feedback can be generated based on the response evaluation.

The coaching output helps identify:

- Positive aspects of the response
- Areas requiring improvement
- Communication issues
- Better approaches for handling the customer

Fallback coaching behavior can be used if the AI service is unavailable.

---

## 11. Escalation Agent

The **Escalation Agent** evaluates the possibility that the conversation may require escalation.

Unlike general response generation, escalation assessment benefits from understandable and explainable decision factors.

The assessment can consider:

- Customer sentiment
- Frustration level
- Escalation-related keywords or expressions
- Current conversation conditions

The output can classify risk into levels such as:

- Low
- Medium
- High

This information helps the trainee understand when a customer interaction is becoming difficult.

---

## 12. Session Manager

The **Session Manager** maintains information related to an active coaching session.

A session can store:

- Interaction mode
- Product
- Scenario
- Persona
- Difficulty
- Language
- Conversation turns
- Customer messages
- Trainee replies
- Customer analysis
- Knowledge results
- Response evaluations
- Coaching feedback
- Escalation information
- Final summary

Without session management, each request would behave as an independent interaction.

Session state enables multi-turn coaching.

### Current Storage Limitation

The current implementation primarily maintains session information in application memory.

Therefore, session information is not designed as permanent production storage.

Persistent database integration is a future enhancement.

---

## 13. Simulator Mode Architecture

Simulator Mode provides AI-generated customer interactions.

The processing flow is:

Start Session

↓

Select Product / Scenario / Persona / Difficulty / Language

↓

Generate Customer Message

↓

Analyze Customer Message

↓

Retrieve Relevant Knowledge

↓

Display Analysis and Guidance

↓

Trainee Writes Response

↓

Evaluate Trainee Response

↓

Generate Coaching Feedback

↓

Assess Escalation Risk

↓

Update Session

↓

Generate Next Customer Message

↓

Continue Conversation

↓

End Session

↓

Generate Final Report

This creates a multi-turn AI-based training environment.

---

## 14. Manual Mode Architecture

Manual Mode allows the user to provide the customer message directly.

The flow is:

Start Manual Session

↓

Enter Customer Message

↓

Analyze Message

↓

Retrieve Knowledge

↓

Assess Escalation

↓

Provide Response Guidance

↓

Enter Trainee Response

↓

Evaluate Response

↓

Generate Coaching

↓

Update Session

Manual Mode does not require the system to begin the interaction with an automatically generated customer scenario.

This mode is useful for testing or practicing a specific customer message.

---

## 15. Replay Mode Architecture

Replay Mode processes an existing customer-agent transcript.

The supported transcript structure follows a format such as:

Customer: Message from customer  
Agent: Response from support agent

Customer: Next customer message  
Agent: Next support response

The processing flow is:

Upload Transcript

↓

Read Transcript

↓

Parse Customer-Agent Pairs

↓

Process Customer Message

↓

Analyze Customer Context

↓

Process Existing Agent Response

↓

Evaluate Response

↓

Generate Coaching Information

↓

Continue With Next Pair

Replay Mode allows previously completed interactions to be reviewed using the coaching system.

---

## 16. Live Response Guidance Flow

Live response guidance is an important feature of the project.

The general flow is:

Current Customer Message

+

Intent / Sentiment / Frustration

+

Relevant Knowledge

+

Conversation Context

↓

Coaching / Guidance Component

↓

Suggested Support Response

The suggested response is displayed to assist the trainee.

The trainee can still decide how to formulate and submit the final response.

---

## 17. Complete Multi-Agent Processing Flow

A normal interaction can involve the following sequence:

### Step 1: Receive Customer Message

The system receives a customer message from:

- Customer Simulator Agent,
- Manual Mode input, or
- Replay transcript.

### Step 2: Analyze Customer

The Intent and Sentiment Agent processes the customer message.

### Step 3: Retrieve Knowledge

The Knowledge Recommendation Agent retrieves relevant support information.

### Step 4: Generate Guidance

Available analysis, knowledge, and conversation context can be used to provide a suggested response.

### Step 5: Receive Trainee Response

The trainee prepares and submits a response.

### Step 6: Evaluate Response

The Response Evaluator analyzes the trainee response.

### Step 7: Generate Coaching

The Coaching Agent provides feedback based on the interaction and evaluation.

### Step 8: Assess Escalation

The Escalation Agent determines the current escalation risk.

### Step 9: Store Turn

Interaction information is stored as part of the current session.

### Step 10: Continue Conversation

In Simulator Mode, the Customer Simulator Agent generates the next context-aware customer message.

The cycle continues until the session is completed.

---

## 18. Post-Interaction Summary Architecture

When the training session ends, stored session information is used to generate the final summary.

The flow is:

Completed Conversation Turns

↓

Stored Evaluations

↓

Coaching Information

↓

Escalation Information

↓

Post-Interaction Summary Agent

↓

Final Performance Summary

The resulting report can contain:

- Overall score
- Grade
- Conversation outcome
- Escalation status
- Performance dimensions
- Strengths
- Areas for improvement
- Personalized coaching recommendations

---

## 19. Performance Analytics Architecture

Performance Analytics uses information from completed sessions.

The analytics layer can summarize:

- Average performance
- Performance trends
- Strongest areas
- Weakest areas
- Improvement indicators
- Escalation triggers
- Knowledge gaps

This extends the application from individual interaction feedback to broader training analysis.

---

## 20. Frontend Architecture

The frontend provides interfaces for:

- Dashboard
- Simulator Mode
- Manual Mode
- Replay Mode
- Reports
- Performance Analytics
- Knowledge Base

HTML provides page structure.

CSS handles presentation and layout.

JavaScript handles interactive behavior and communication with backend endpoints.

The frontend sends user actions to the Flask backend and displays the returned analysis, guidance, evaluation, coaching, and session information.

---

## 21. Backend Architecture

The Flask backend acts as the communication layer between the frontend and the application's processing modules.

Its responsibilities include:

- Serving application pages
- Receiving frontend requests
- Creating and managing sessions
- Passing interaction data to the orchestrator
- Processing Manual and Replay inputs
- Handling knowledge base operations
- Returning analysis and coaching results
- Providing report and analytics data

This separates presentation logic from the core AI and coaching logic.

---

## 22. Data Flow

The main data flow can be summarized as:

Frontend Request

↓

Flask Route

↓

Session Validation

↓

Agent Orchestrator

↓

Analysis + Knowledge + Evaluation + Coaching + Escalation

↓

Session Manager

↓

Structured Backend Response

↓

Frontend Update

This structure allows the frontend to remain focused on user interaction while backend modules perform the processing.

---

## 23. External AI Integration

Generative AI is used where dynamic language generation improves the training experience.

Examples include:

- Dynamic customer simulation
- Suggested support responses
- Coaching feedback

External AI configuration is maintained separately from the source code where sensitive credentials are involved.

API credentials should not be committed to GitHub.

The `.env` configuration is excluded from version control.

---

## 24. Error and Fallback Handling

AI services may occasionally be unavailable because of:

- Missing API configuration
- Network problems
- External service errors
- Request failures

Selected AI components therefore include fallback behavior.

This allows basic application functionality to continue instead of making the entire training workflow dependent on a single external request.

---

## 25. Separation of Responsibilities

The architecture follows separation of concerns.

| Component | Primary Responsibility |
|---|---|
| Frontend | User interaction and result presentation |
| Flask Backend | Request handling and application routing |
| Agent Orchestrator | Multi-agent workflow coordination |
| Customer Simulator Agent | Customer message generation |
| Intent/Sentiment Agent | Customer message analysis |
| Knowledge Agent | Relevant support information retrieval |
| Response Evaluator | Trainee response evaluation |
| Coaching Agent | Guidance and coaching |
| Escalation Agent | Escalation risk assessment |
| Session Manager | Conversation/session state |
| Summary Agent | Post-interaction summary |
| Analytics | Cross-session performance information |

---

## 26. Architectural Advantages

The multi-agent architecture provides several advantages.

### Modularity

Each agent performs a specific task.

### Maintainability

Individual modules can be updated with limited impact on unrelated functionality.

### Extensibility

Additional agents or processing steps can be introduced later.

### Reusability

Analysis, knowledge retrieval, evaluation, and coaching components can be reused across different interaction modes.

### Explainability

Specialized components such as escalation assessment can provide understandable decision factors.

### Training-Oriented Design

The architecture supports the entire training lifecycle rather than only generating chatbot responses.

---

## 27. Current Architectural Limitations

The current prototype has several architectural limitations:

- Session storage is primarily in-memory.
- Knowledge retrieval does not yet use a vector database.
- Some functionality depends on an external generative AI service.
- Production-grade authentication and authorization are not yet implemented.
- The application is designed as a training prototype rather than a high-scale production support platform.

---

## 28. Future Architectural Improvements

The architecture can be extended with:

- Persistent SQL or NoSQL database
- Vector database
- Embedding-based semantic search
- Advanced RAG pipeline
- Authentication and role-based authorization
- Supervisor dashboard
- Cloud deployment
- Centralized logging
- Application monitoring
- Voice-based simulation
- Real customer-support platform integration
- Long-term trainee performance storage
- More advanced multi-agent communication

---

## 29. Conclusion

The system architecture separates customer simulation, customer understanding, knowledge retrieval, response evaluation, coaching, escalation assessment, session management, and reporting into specialized components.

The **Agent Orchestrator** acts as the central coordination layer that connects these components into a complete multi-turn coaching workflow.

This architecture allows the project to function as more than a basic chatbot. It provides a structured AI-assisted environment for practicing, evaluating, and improving customer-support interactions.
