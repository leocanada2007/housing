import streamlit as st


#%%
#==============================================================================
# Tab 1 Overall
#==============================================================================

def tab1():
  number = st.number_input("Enter Your Purchase Price")
  st.write("123")

  
  


    



#==============================================================================
# Main body
#==============================================================================

def run():
    
    
    
    # Add a radio box
    select_tab = st.sidebar.radio("Select tab", ['佣金', '贷款'])

    # Show the selected tab
    if select_tab == '佣金':
        tab1()
    elif select_tab == '贷款':
        tab2()
   
        
if __name__ == "__main__":
    run()   
