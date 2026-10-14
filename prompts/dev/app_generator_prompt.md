# quiz_module_prompt.md

**Role:** You are an expert Front-End Web Developer (Claude).

**Task:** Create a self-contained, easy-to-use HTML/CSS/JS quiz module that runs entirely offline in a local web browser.

**Instructions:**
1. **Data Upload:** The module must feature a file upload button on the start screen that accepts a `.csv` file. 
2. **CSV Parsing:** Write vanilla JavaScript to parse the uploaded CSV. The CSV will contain headers: `Category, Question_Text, Option_1, Option_2, Option_3, Option_4, Option_5, Option_6, Correct_Option_Number`.
3. **Quiz Interface:** 
    * Present the questions cleanly one at a time or in a highly readable scrollable list.
    * Use a modern, minimalist UI (e.g., simple radio buttons for the 6 options).
    * Include a prominent "Submit Quiz" button at the very end.
4. **Grading & Reporting:**
    * Upon submission, instantly grade the quiz. 
    * Generate a grading report display that shows the user's overall score.
    * Break down the user's performance by identifying weakness categories (derived from the `Category` column of missed questions).
    * List the specific questions the user got wrong alongside the correct answers.
5. **Export Functionality:** Provide a "Download Report" button on the results screen that exports the user's grading report (missed categories and wrong questions) as a `.txt` or `.csv` file to assist them with follow-up question generation.
6. **Code Requirements:** The entire application must be delivered as a single `index.html` file with embedded `<style>` and `<script>` tags so the user can double-click it and run it immediately offline without a server. 

**Output Requirement:** Provide the complete HTML code in a single markdown code block.