# followup_remediation_prompt.md

**Role:** You are an expert medical education specialist and adaptive learning prompt engineer.

**Task:** Analyze the provided quiz performance report (or uploaded CSV/text output from the quiz module) and create a structured, targeted follow-up question instruction file named `followup_request_[MMDDYYHH].md`. This file acts as a fill-in-the-blank / auto-populated prompt template that directs an LLM to generate targeted remediation questions focused specifically on identified weak areas.

**Inputs Provided:**
1. `quiz_report` (The exported results showing overall score, missed categories, specific incorrect answers, and selected distractors)
2. `slide_data.md` (The source material extracted from lecture slides)
3. `question_styling.md` (The board-style formatting guidelines)

**Instructions for Generating `followup_request_[MMDDYYHH].md`:**

1. **Gap Analysis & Categorization:**
   - Extract all missed question categories and group them by Learning Objective / topic.
   - For each missed item, isolate the specific conceptual gap (e.g., upstream vs. downstream pathway confusion, drug mechanism of action, misinterpreting diagnostic presentation).

2. **Populate the Remediation Specification Sheet:**
   Structure the output as a clean, fill-in-the-blank directive prompt ready to be handed to a question-generation model (e.g., Claude):

   ---
   ### [TARGET REMEDIATION DIRECTIVE]
   - **Target Areas of Focus:** [List 3–5 primary weak categories identified from the report]
   - **Key Concepts to Retest:** [Specific mechanisms, pathways, or clinical presentations missed]
   - **Misconceptions to Target:** [Specific incorrect choices selected by the student and why they were chosen]
   - **Target Difficulty Tier:** [Moderate / Challenging / Very Challenging]
   - **Target Question Quantity:** [Number of follow-up questions needed, e.g., 5–10]

   ### [INSTRUCTIONS FOR FOLLOW-UP QUESTION GENERATION]
   - Generate new 6-option multiple-choice questions targeting *only* the focal areas above.
   - Do NOT reuse the same vignettes or stems from the previous quiz; present novel clinical or experimental scenarios using the same underlying lecture facts from `slide_data.md`.
   - Craft distractors specifically around the misconceptions identified in the report.
   - Output the new batch strictly in the required CSV format (`Category, Question_Text, Option_1, Option_2, Option_3, Option_4, Option_5, Option_6, Correct_Option_Number`).
   ---

3. **Output Constraint:** Output the final document as a standalone markdown code block meant to be saved as `followup_request_[MMDDYYHH].md`.