# User Guide

## 1. Introduction

This guide explains how to use the **AI-Powered Customer Support Assistant with Live Response Guidance**.

The application is designed for customer-support training and provides three main interaction modes:

- Simulator Mode
- Manual Mode
- Replay Mode

It also provides access to:

- Knowledge Base
- Post-Interaction Reports
- Performance Analytics

---

## 2. Opening the Application

After starting the Flask application, open the local server address displayed in the terminal.

The application opens the main dashboard.

The dashboard provides navigation to the major features of the system.

---

## 3. Dashboard

The dashboard acts as the main navigation area.

The available sections include:

- Simulator
- Manual Mode
- Replay Mode
- Reports
- Performance Analytics
- Knowledge Base

Select the required option to continue.

---

# 4. Simulator Mode

## Purpose

Simulator Mode allows the trainee to practice with an AI-generated customer.

The AI customer can continue the conversation across multiple turns.

## Starting a Simulator Session

1. Open **Simulator** from the dashboard.
2. Configure the training session.
3. Select the required product.
4. Select a customer-support scenario.
5. Select the customer persona.
6. Select the difficulty level.
7. Select the language.
8. Start the session.

The system creates a new training session.

## Customer Message

After the session starts, the Customer Simulator Agent generates a customer message according to the selected configuration.

The message is then processed by the coaching system.

## Customer Analysis

The system analyzes the customer message and provides information such as:

- Intent
- Sentiment
- Frustration level

This helps the trainee understand the customer's situation.

## Knowledge Recommendation

Relevant information is retrieved from the available knowledge base when matching support information exists.

The trainee can use this information while preparing a response.

## Live Response Guidance

The trainee can use the available response-guidance functionality to obtain an AI-assisted suggested response.

The suggestion can consider:

- Current customer message
- Customer analysis
- Retrieved knowledge
- Conversation context

The suggested response is intended as guidance. The trainee can prepare the final response based on the situation.

## Submitting a Response

Enter the trainee response and submit it.

The system processes the response through the evaluation and coaching workflow.

## Response Evaluation

The submitted response is evaluated using customer-support communication factors such as:

- Empathy
- Tone
- Clarity
- Professionalism
- Resolution quality
- Knowledge relevance

## Coaching Feedback

After evaluation, coaching feedback helps identify:

- What was handled well
- What could be improved
- Communication issues
- Better response approaches

## Escalation Risk

The system also evaluates escalation risk.

Risk can be represented using levels such as:

- Low
- Medium
- High

This helps the trainee recognize difficult customer situations.

## Continuing the Conversation

After the trainee response is processed, the AI customer can generate the next message using the existing conversation context.

The trainee can continue responding for multiple turns.

---

# 5. Manual Mode

## Purpose

Manual Mode allows the trainee to enter a specific customer message instead of using an automatically generated customer.

## Using Manual Mode

1. Select **Manual Mode** from the dashboard.
2. Start the Manual Mode session.
3. Enter the customer message.
4. Submit the message.
5. Review the customer analysis.
6. Review available knowledge recommendations.
7. Use response guidance if required.
8. Enter the trainee response.
9. Submit the response.
10. Review evaluation and coaching feedback.

## When to Use Manual Mode

Manual Mode is useful when:

- Practicing a specific customer problem
- Testing a particular message
- Demonstrating message analysis
- Testing knowledge retrieval
- Practicing a difficult support situation

Manual Mode maintains its own interaction mode instead of automatically behaving as a Simulator session.

---

# 6. Replay Mode

## Purpose

Replay Mode is used to review an existing customer-agent conversation.

Instead of creating a new customer conversation, the system processes an existing transcript.

## Supported Transcript Format

The transcript should contain customer and agent messages in a clear format.

Example:

Customer: My order has not arrived yet.
Agent: I am sorry about the delay. Let me check the available information.

Customer: I have already waited for several days.
Agent: I understand your concern. I will help you with the available options.

## Using Replay Mode

1. Select **Replay Mode**.
2. Provide the supported text transcript.
3. Start transcript processing.
4. The system identifies customer-agent message pairs.
5. Each interaction is processed through the coaching workflow.
6. Review the resulting evaluation and coaching information.

## Benefits of Replay Mode

Replay Mode can be used to:

- Review previous support conversations
- Evaluate existing agent replies
- Identify communication problems
- Find repeated mistakes
- Generate coaching recommendations

---

# 7. Knowledge Base

## Purpose

The Knowledge Base contains support-related information that can be retrieved during customer interactions.

## Supported File Types

The current system supports document formats such as:

- PDF
- DOCX
- TXT

## Uploading a Document

1. Open **Knowledge Base** from the dashboard.
2. Select the upload option.
3. Choose a supported document.
4. Upload the file.
5. The backend extracts the document text.
6. Text is cleaned and divided into chunks.
7. Processed knowledge becomes available for retrieval.

## Searching Knowledge

The Knowledge Base interface can be used to search available knowledge.

During customer interactions, the Knowledge Recommendation Agent also searches relevant knowledge automatically.

## Deleting Knowledge

Where the interface provides the delete operation, stored knowledge documents can be removed when they are no longer required.

---

# 8. Knowledge Retrieval

When a customer query is processed, the system searches stored knowledge chunks.

The current workflow uses textual relevance based on:

- Tokens
- Keywords
- Available metadata signals

Relevant knowledge is ranked and returned to the coaching workflow.

The current implementation does not require a vector database.

---

# 9. Ending a Training Session

When the required conversation is complete:

1. End the current session.
2. The system processes stored interaction information.
3. Session-level performance information is calculated.
4. A final summary is generated.
5. Open the report to review the results.

---

# 10. Post-Interaction Report

The report provides an overall view of the completed training interaction.

Depending on available session information, the report can contain:

- Overall score
- Grade
- Conversation outcome
- Escalation information
- Performance dimensions
- Sentiment/performance journey
- Strengths
- Areas for improvement
- Coaching recommendations

The report allows the trainee to review the complete interaction instead of looking only at individual responses.

---

# 11. Performance Analytics

Performance Analytics provides a broader view of completed training sessions.

The analytics page can include:

- Average performance
- Performance trends
- Strongest areas
- Weakest areas
- Improvement indicators
- Escalation triggers
- Knowledge gaps

This information helps identify patterns across multiple completed sessions.

---

# 12. Recommended Training Workflow

A recommended training workflow is:

1. Add relevant support documents to the Knowledge Base.
2. Open Simulator Mode.
3. Configure a training scenario.
4. Start the AI customer interaction.
5. Review customer intent and sentiment.
6. Review relevant knowledge.
7. Use live guidance when required.
8. Prepare and submit a response.
9. Review response evaluation.
10. Review coaching feedback.
11. Observe escalation risk.
12. Continue the conversation.
13. Complete the session.
14. Review the final report.
15. Review Performance Analytics after completing multiple sessions.

---

# 13. Example Training Scenario

Consider the following customer message:

> "My refund was supposed to arrive several days ago and I still have not received it."

The system can:

1. Analyze the customer's intent.
2. Identify sentiment and frustration.
3. Search the Knowledge Base for relevant refund information.
4. Provide response guidance.
5. Allow the trainee to prepare a response.
6. Evaluate the submitted response.
7. Generate coaching feedback.
8. Assess escalation risk.
9. Store the interaction as part of the session.

This process continues for additional conversation turns where applicable.

---

# 14. Tips for Trainees

While using the application:

- Read the complete customer message carefully.
- Pay attention to sentiment and frustration.
- Use knowledge recommendations as support information.
- Do not depend entirely on the suggested response.
- Maintain empathy when the customer is frustrated.
- Keep responses clear and professional.
- Address the customer's actual problem.
- Review coaching feedback after each interaction.
- Review the final report after completing the session.
- Use analytics to identify repeated weak areas.

---

# 15. Common Issues

## Customer Message Is Not Generated

Check:

- Internet connection
- AI configuration
- Session configuration

AI-dependent functionality requires the external AI service to be available.

## Manual Message Is Not Processed

Ensure that:

- Manual Mode is selected.
- A valid session is active.
- Customer message is not empty.

## Replay Transcript Is Not Accepted

Check the transcript format.

Use clear labels:

Customer: ...
Agent: ...

Ensure that valid customer-agent pairs are available.

## Knowledge Is Not Retrieved

Check whether:

- Relevant documents were uploaded.
- Document text was successfully processed.
- The query is related to the stored content.

## AI Suggested Response Is Not Available

Check:

- Gemini configuration
- Internet connection
- Required environment variables
- External service availability

---

# 16. Important Usage Notes

The application is designed primarily as a **training and coaching prototype**.

It should not be treated as an autonomous production customer-support system.

AI-generated suggestions should be considered assistance rather than guaranteed customer-service decisions.

Knowledge recommendations depend on the content available in the project's Knowledge Base.

---

# 17. User Workflow Summary

The overall user workflow can be summarized as:

Dashboard

↓

Select Interaction Mode

↓

Start Session

↓

Receive / Enter Customer Message

↓

Review Customer Analysis

↓

Review Knowledge

↓

Use Live Guidance

↓

Submit Response

↓

Review Evaluation

↓

Review Coaching

↓

Observe Escalation Risk

↓

Continue Conversation

↓

Complete Session

↓

View Report

↓

Review Performance Analytics

---

# 18. Conclusion

The application provides an integrated environment for customer-support practice, review, and performance improvement.

Simulator Mode supports AI-generated conversations, Manual Mode supports specific customer queries, and Replay Mode supports review of existing transcripts.

Knowledge retrieval, live response guidance, response evaluation, coaching, escalation assessment, reports, and analytics work together to provide a complete customer-support training workflow.
