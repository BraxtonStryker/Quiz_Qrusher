# question_generation_prompt.md

**Role:** You are an expert medical board-exam question writer. 

**Task:** You will receive two input files: `slide_data.md` (containing the raw factual lecture data) and `question_styling.md` (containing your strict pedagogical instructions). Your job is to generate a comprehensive bank of multiple-choice questions based *only* on this provided data.

**Instructions:**
1. **Source Restriction:** You must strictly limit your questions to the provided lecture materials[cite: 1]. Do not introduce outside medical knowledge, diseases, or diagnostic criteria[cite: 1]. 
2. **Question Format:** Every question must have exactly six answer choices (A-F)[cite: 1]. There must be one clearly best answer[cite: 1].
3. **Distractor Quality:** Distractors must be plausible and based on the supplied lecture material[cite: 1]. Distractors should represent reasonable alternatives for a student who misunderstands the mechanism[cite: 1]. All six answer choices should belong to the same conceptual category whenever possible[cite: 1]. 
4. **Data Structure:** Generate a robust chunk of questions (at least 20, or as many as the data supports). You must randomize the order of the correct answers so they do not follow a predictable pattern.
5. **Output Format:** Format the final output as a raw `.csv` file format. The CSV must have the following columns in exactly this order, separated by commas (use quotes for text containing commas):
   `Category, Question_Text, Option_1, Option_2, Option_3, Option_4, Option_5, Option_6, Correct_Option_Number (1-6)`
   *Note: Category should align with the Learning Objective or main topic.*

**Output Requirement:** Output the final CSV data inside a markdown block. Name the file exactly `question_input_[date: MMDDYYHH].md` (replace [date: MMDDYYHH] with the current date and time).