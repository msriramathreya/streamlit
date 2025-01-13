import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import ollama
import sys
import io

# Initialize session state
def initialize_session_state():
    if 'agent' not in st.session_state:
        st.session_state['agent'] = None
    if 'generated_instructions' not in st.session_state:
        st.session_state['generated_instructions'] = ""
    if 'response' not in st.session_state:
        st.session_state['response'] = ""

# Home Page Function
def home_page():
    st.title("askmukunda.com")
    st.subheader("Select an Agent to Start")

    # Big Square Buttons for Agents
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Agent 1\nModify Existing Code", key="agent1_btn"):
            st.session_state['agent'] = 1
    with col2:
        if st.button("Agent 2\nGenerate Fresh Code", key="agent2_btn"):
            st.session_state['agent'] = 2
    with col3:
        if st.button("Agent 3\nDocument Code", key="agent3_btn"):
            st.session_state['agent'] = 3

# Back to Home Button
def back_to_home():
    if st.button("Back to Home"):
        st.session_state['agent'] = None

# Agent 1: Modify Existing Code
def agent_1():
    st.title("askmukunda.com")
    st.header("Modify Existing Code")
    instructions = st.text_area("Enter Instructions to Modify Code")
    input_code = st.text_area("Paste the Code to Modify")
    if st.button("Generate Modified Code"):
        if instructions and input_code:
            template = """
            Modify the following code snippet based on these instructions:
            Instructions: {instructions}
            Code: {code}
            Provide only the revised code without explanations.
            """
            prompt = PromptTemplate(
                input_variables=["instructions", "code"],
                template=template,
            )
            chain_input = prompt.format(instructions=instructions, code=input_code)
            response = ollama.generate(model="llama3.2", prompt=chain_input)
            modified_code = response.get("response", "")
            st.text_area("Modified Code", value=modified_code, height=300, key="modified_code")
            st.download_button("Copy Code", data=modified_code, file_name="modified_code.py", mime="text/plain")
    back_to_home()

# Agent 2: Generate Fresh Code
def agent_2():
    st.title("askmukunda.com")
    st.header("Generate Fresh Code")
    program_context = st.text_area("Program Context (Max 1000 characters)")

    personas = []
    for i in range(3):
        cols = st.columns(2)
        with cols[0]:
            persona_name = st.text_input(f"Persona {i + 1} Name", key=f"persona_name_{i}")
        with cols[1]:
            persona_desc = st.text_input(f"Persona {i + 1} Description", key=f"persona_desc_{i}")
        if persona_name and persona_desc:
            personas.append({"name": persona_name, "desc": persona_desc})

    user_stories = []
    for i in range(5):
        cols = st.columns(3)
        with cols[0]:
            persona_choice = st.selectbox(f"User Story {i + 1}: Persona", options=[p['name'] for p in personas], key=f"persona_{i}")
        with cols[1]:
            action = st.text_input(f"User Story {i + 1}: Action", key=f"action_{i}")
        with cols[2]:
            benefit = st.text_input(f"User Story {i + 1}: Benefit", key=f"benefit_{i}")
        if persona_choice and action and benefit:
            user_stories.append({"persona": persona_choice, "action": action, "benefit": benefit})

    coding_language = st.selectbox("Select Coding Language", options=["Python", "JavaScript", "Java", "C++", "Go"])
    other_instructions = st.text_area("Other Instructions")

    if st.button("Generate Instructions"):
        user_story_text = "\n".join([
            f"As a {story['persona']} I want to {story['action']} so that {story['benefit']}"
            for story in user_stories
        ])
        template = """
        Generate detailed step-by-step instructions for the following program context and user stories:
        Program Context: {context}
        User Stories: {stories}
        Other Instructions: {instructions}
        Provide only bulleted instructions.
        """
        prompt = PromptTemplate(
            input_variables=["context", "stories", "instructions"],
            template=template,
        )
        chain_input = prompt.format(
            context=program_context,
            stories=user_story_text,
            instructions=other_instructions,
        )
        response = ollama.generate(model="llama3.2", prompt=chain_input)
        instructions = response.get("response", "")
        st.session_state["generated_instructions"] = instructions
        st.text_area("Generated Instructions", value=instructions, height=300, key="generated_instructions")

    if st.button("Generate Code"):
        prompt = st.session_state.get("generated_instructions", "") + f"\nLanguage: {coding_language}"
        while True:
            response = ollama.generate(model="llama3.2", prompt=prompt + f"\nNote: Output must have only {coding_language} code, do not add any other explanation.")
            code = response["response"].replace(coding_language.lower(), "").replace("```", "")
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            try:
                exec(code)
            except Exception as e:
                error_message = f"Error executing generated code: {e}"
                st.markdown(f"Code has Error, fixing... \n{response['response']} \n {error_message}")
                prompt = f"The following code has this error: {error_message} \nCode: \n{code}"
            else:
                output = buffer.getvalue()
                st.markdown(f"Code is working well. \n{response['response']} \n {output}")
                st.session_state["response"] = response["response"]
                break
            finally:
                sys.stdout = old_stdout

    question = st.text_area(label="Write your question.")
    if st.button("ASK"):
        st.markdown(st.session_state.get("response", ""))
        prompt = f"""
        Can you explain why we used this code "{question}" in the following code in very detail step by step:
        {st.session_state.get("response", "")}
        """
        answer = ollama.generate(model="llama3.2", prompt=prompt)
        st.markdown(answer["response"])
    back_to_home()

# Agent 3: Document Code
def agent_3():
    st.title("askmukunda.com")
    st.header("Document Code")
    input_code = st.text_area("Paste the Code to Document")
    if st.button("Generate Documentation"):
        if input_code:
            template = """
            Document the following code snippet in detail with bullet points:
            Code: {code}

            The documentation must include the following sections:
            1. Introduction: A summary of what the program is attempting to perform.
            2. Detailed Explanation: Each section of the code must be explained in as much detail as possible.
            Provide the documentation.
            """
            prompt = PromptTemplate(
                input_variables=["code"],
                template=template,
            )
            chain_input = prompt.format(code=input_code)
            response = ollama.generate(model="llama3.2", prompt=chain_input)
            documentation = response.get("response", "")
            st.text_area("Code Documentation", value=documentation, height=300, key="documentation")
            st.download_button("Copy Documentation", data=documentation, file_name="code_documentation.txt", mime="text/plain")

    if st.button("Generate Unit Tests"):
        if input_code:
            template = """
            Generate comprehensive unit tests for the following code:
            Code: {code}

            Ensure the tests cover all edge cases and functionalities.
            Provide the tests in the same language as the code.
            """
            prompt = PromptTemplate(
                input_variables=["code"],
                template=template,
            )
            chain_input = prompt.format(code=input_code)
            response = ollama.generate(model="llama3.2", prompt=chain_input)
            unit_tests = response.get("response", "")
            st.text_area("Generated Unit Tests", value=unit_tests, height=300, key="unit_tests")

    back_to_home()

# Main Application Logic
initialize_session_state()

if st.session_state['agent'] is None:
    home_page()
elif st.session_state['agent'] == 1:
    agent_1()
elif st.session_state['agent'] == 2:
    agent_2()
elif st.session_state['agent'] == 3:
    agent_3()
