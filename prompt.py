career_path_prompt = """
I want to become a {goal}.  
Assume I have no prior knowledge about this field.  

Provide a detailed step-by-step career path from beginner to advanced level.  
The career path should include **5 to 10 steps**, with each step progressively increasing in complexity.  

**Format Each Step as Follows:**  
1. **Step Name** – Define the goal of this step.  
   - **Summary**: Explain what should be learned in this step (topics, concepts).  
   - **Most Important Skill**: Highlight one essential skill that should be mastered at this stage.  
"""

career_step_prompt = """
    For the career step '{step_name}', provide the **What to Learn** section in the following format:

    **What to Learn:**
    - [Summary sentence about the step. This should describe the overall learning objective (e.g., Get familiar with the basics of Python programming language, including its syntax, data types, and control structures).]
    - Main Topics Covered: [List the main topics covered in the step, separated by commas (e.g., Variables, Data Types, Operators, Control Structures, Functions, Modules, and Error Handling).]

    Remove the introductory line "What to Learn:" and ensure there are no extra lines before or after the actual content. Only include the summary and main topics covered.
    """

get_learning_prompt = """
    Provide a structured A-to-Z learning guide for {topic}.
    The guide should include key concepts, step-by-step learning path, and essential resources.
    """