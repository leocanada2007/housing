import streamlit as st

def payment_calculator(r,P,N):
    
    # r is the annual interest rate
    # P is the principal
    # N is the loan's term
    
    r_m = r/12
    
    c = (r_m * P)/(1-(1+r_m)**(-N))
    
    return c


def interest_calculator(c,r,P,N):
    
    # c is the monthly payment from payment calculator
    # r is the annual interest rate
    # P is the principal
    # N month for interest calculation. Note this is different from the N in payment calculator 
    
    r_m = r/12
    
    i = (P*r_m-c)*((1+r_m)**N-1)/r_m + c*N
    
    return i

#%%
#==============================================================================
# Tab 1 Commission
#==============================================================================

def tab1():
  price = st.number_input("Enter Your Purchase Price")

  total_commission = 7000 + (price-100000)*0.025

  total_commission_percentage = round((total_commission/price)*100, 3)

  buy_commission = 3220+0.0115*(price-100000)

  buy_commission_percentage = round((buy_commission / price)*100, 3)

  listing_commission = 3780 + 0.0135*(price-100000)
  
  listing_commission_percentage = round((listing_commission / price)*100, 3)

  st.write("佣金总数： {}，占成交价的{}%".format(total_commission, total_commission_percentage))

  st.write("买方佣金总数： {}，占成交价的{}%".format(buy_commission, buy_commission_percentage))
  
  st.write("卖方佣金总数： {}，占成交价的{}%".format(listing_commission, listing_commission_percentage))


  
  

#%%
#==============================================================================
# Tab 2 Mortgage
#==============================================================================

def tab2():

  
  P = st.number_input("Enter Loan Amount")
  r = st.number_input("Enter Effective Annual Interest Rate in Decimals")
  N = st.number_input("Enter Amortization Period in Month")

  c = round(payment_calculator(r,P,N),2)

  st.markdown("red[Monthly Payment] is {}".format(c))

  st.title("To Calculate Cumulative Interests")

  T = st.number_input("Enter Interest Period in Month")

  i = round(interest_calculator(c, r, P, T),2)

  st.markdown("red[Cumulative Interests] for {} Months Are {}".format(T, i))




  
 

    



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
