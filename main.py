import streamlit as st


#%%
#==============================================================================
# Tab 1 Overall
#==============================================================================

def tab1():
  price = st.number_input("Enter Your Purchase Price")

  total_commission = 7000 + (price-100000)*0.025

  total_commission_percentage = round((total_commission/price)*100, 2)

  buy_commission = 3220+0.0115*(price-100000)

  buy_commission_percentage = buy_commission / price

  listing_commission = 3780 + 0.0135*(price-100000)

  st.write("hello {}".format(total_commission))


  
  


    



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
