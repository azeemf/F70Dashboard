import streamlit as st

my_list = ["a", "b", "c"]
show_next = st.button("next")

# Initialize the current index
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

while 1: 

    # Whenever someone clicks on the button
    if show_next:
        
        # Show next element in list
        st.write(my_list[st.session_state.current_index])
        # Update and store the index
        st.session_state.current_index += 1

