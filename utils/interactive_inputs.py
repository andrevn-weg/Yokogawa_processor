import streamlit as st
import streamlit.components.v1 as components
import json

def interactive_checkbox_number(label, checkbox_label="N/A", value=0.0, is_null=False, step=0.1, key=None):
    """
    Create an interactive checkbox and number input combination where the checkbox controls
    whether the number input is enabled/disabled.
    
    Parameters:
    -----------
    label : str
        Label for the number input field
    checkbox_label : str
        Label for the checkbox
    value : float
        Default value for the number input
    is_null : bool
        Initial state of the checkbox (True = number input disabled)
    step : float
        Step size for the number input
    key : str
        Unique key for this component
        
    Returns:
    --------
    tuple:
        (is_checkbox_checked, number_value)
    """
    # Create unique IDs for the HTML elements
    if key is None:
        key = st.session_state.get("_current_interactive_key", 0) + 1
        st.session_state["_current_interactive_key"] = key
    
    # Create IDs for each element
    checkbox_id = f"checkbox_{key}"
    number_id = f"number_{key}"
    container_id = f"container_{key}"
    result_id = f"result_{key}"
    
    # Create hidden input to store result
    result_key = f"result_{key}"
    if result_key not in st.session_state:
        st.session_state[result_key] = json.dumps({"checked": is_null, "value": value})
    
    # Define the HTML/JS component
    html_code = f"""
    <div id="{container_id}" style="margin-bottom: 0.5rem;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <input 
                type="checkbox" 
                id="{checkbox_id}" 
                name="{checkbox_id}"
                {"checked" if is_null else ""}
                style="margin-right: 0.5rem;"
            >
            <label for="{checkbox_id}" style="margin-bottom: 0; font-weight: normal;">{checkbox_label}</label>
        </div>
        <div>
            <label for="{number_id}" style="font-weight: normal; display: block; margin-bottom: 0.25rem;">{label}</label>
            <input 
                type="number" 
                id="{number_id}" 
                name="{number_id}"
                value="{value}"
                step="{step}"
                {"disabled" if is_null else ""}
                style="width: 100%; padding: 0.375rem 0.75rem; border: 1px solid #ced4da; border-radius: 0.25rem; line-height: 1.5;"
            >
        </div>
        <input type="hidden" id="{result_id}" value='{{"checked":{str(is_null).lower()}, "value":{value}}}'>
    </div>"""    # Add JavaScript for interactivity
    html_code += f"""
    <script>
    (function() {{
        // Get elements
        const checkbox = document.getElementById('{checkbox_id}');
        const numberInput = document.getElementById('{number_id}');
        const resultInput = document.getElementById('{result_id}');
        
        // Function to update the hidden result input
        function updateResult() {{
            const result = {{
                checked: checkbox.checked,
                value: numberInput.value !== "" ? parseFloat(numberInput.value) : 0
            }};
            resultInput.value = JSON.stringify(result);
            
            // Send to Streamlit using the setComponentValue API
            if (window.Streamlit) {{
                const serialized = JSON.stringify(result);
                window.Streamlit.setComponentValue(serialized);
            }}
        }}
        
        // Update number input state based on checkbox
        function updateNumberState() {{
            numberInput.disabled = checkbox.checked;
            updateResult();
        }}
        
        // Add event listeners
        checkbox.addEventListener('change', updateNumberState);
        numberInput.addEventListener('input', updateResult);
        
        // Initialize
        updateNumberState();
        
        // Make sure Streamlit knows we're ready
        if (window.Streamlit) {{
            window.Streamlit.setFrameHeight();
        }}
    }})();
    </script>
    """
    
    # Render the component
    component_value = components.html(html_code, height=120)
    
    # Parse the result
    if component_value:
        try:
            result = json.loads(component_value)
            st.session_state[result_key] = component_value
            return result["checked"], result["value"]
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Fall back to the stored value if component hasn't sent a new value
    try:
        stored_result = json.loads(st.session_state[result_key])
        return stored_result["checked"], stored_result["value"]
    except (json.JSONDecodeError, KeyError):
        return is_null, value
