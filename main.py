import streamlit as st
import requests
import io
import numpy as np
import pandas as pd
import plotly.express as px

def amortization(r,P,a,t):
    
    # r is the nominal annual interest rate
    # P is the principal
    # a is amortization in month
    # t is the mortgage term in month
    # f is the payment frequency
    

    r = r/100

    r_e = (1+r/2)**2-1
    
    r_m = (1+r_e)**(1/12)-1  
    
    c = (r_m * P)/(1-(1+r_m)**(-a)) 
      
# =============================================================================
#     if f == 'Monthly':
#         n = 12
#         r_m = (1+r_e)**(1/n)-1  
#         c = c
#         
#     elif f == 'Semi-Monthly':
#         n = 24
#         r_m = (1+r_e)**(1/n)-1  
#         c = c/2
#         t = t*2
# 
#     elif f == 'Bi-Weekly':
#         n = 26
#         r_m = (1+r_e)**(1/n)-1  
#         c = c*12/26
#         t = 781
#         
#     elif f == 'Weekly':
#         n = 52
#         r_m = (1+r_e)**(1/n)-1  
#         c = c*12/52
#         t = 156
#         
#     elif f == 'Accelerated Bi-Weekly':
#         n = 26
#         r_m = (1+r_e)**(1/n)-1  
#         c = c/2 
#         t = 78
#         
#     elif f == 'Accelerated Weekly':
#         n = 52
#         r_m = (1+r_e)**(1/n)-1  
#         c = c/4    
# =============================================================================
   
    schedule = pd.DataFrame(columns=['Period', 'Opening Balance', 'Payment', 'Interest Payment', 'Principal Payment', 'Closing Balance'])
    
    balance = P
    
    for x in range(0,t):
        
        period = x
        opening_balance = balance
        payment = c
        interest = opening_balance * r_m
        principal = payment - interest
        balance = balance - principal
        closing_balance = balance
        

        
        row = [period, opening_balance, payment, interest, principal, closing_balance]
        
        schedule.loc[len(schedule)] = row
            

    
    return schedule

#%%
#==============================================================================
# Tab 1 Commission
#==============================================================================

def tab1():
  price = st.number_input("Enter Purchase Price")

  total_commission = round(7000 + (price-100000)*0.02, 2)

  total_commission_percentage = round((total_commission/price)*100, 3)

  buy_commission = round(3220+0.0115*(price-100000), 2)

  buy_commission_percentage = round((buy_commission / price)*100, 3)

  listing_commission = round(3780 + 0.0135*(price-100000),2)
  
  listing_commission_percentage = round((listing_commission / price)*100, 3)

  st.write("Total Commission: {}, or {}% of purchase price".format(total_commission, total_commission_percentage))

  st.write("Commission for Buyer's Agent: {}, or {}% of purchase price".format(buy_commission, buy_commission_percentage))
  
  st.write("Commission for Seller's Agent: {}, or {}% of purchase price".format(listing_commission, listing_commission_percentage))


  
  

#%%
#==============================================================================
# Tab 2 Mortgage 
#==============================================================================

def tab2():

  
  P = st.number_input("Enter Loan Amount")
  r = st.number_input("Enter Annual Nominal Interest Rate in %")
  a = st.number_input("Enter Amortization Period in Month")
  t = st.number_input("Enter Mortgage Term in Month")


  df = round(payment_calculator(r,P,a,t),2)

  st.markdown("Monthly Payment is {}".format(df.iloc[0,2]))

  st.dataframe(df)


#%%
#==============================================================================
# Tab 3 Interest Analysis
#==============================================================================

def tab3():

  r = st.number_input("Enter Annual Nominal Interest Rate in %")
    
  r_e = round(100*((1+r/2)**2-1),2)
    
  r_m = round(100*(1+r_e)**(1/12)-1,2)

  st.markdown("Annual Effective Rate is {r_e}%".format(c))

  st.markdown("Monthly Effective Rate is {r_m}".format(c))


  c = round(payment_calculator(r,P,N,f),2)

  st.title("To Calculate Cumulative Interests")

  T = st.number_input("Enter Interest Period in Month")

  i = round(interest_calculator(c, r, P, T),2)

  st.markdown("Monthly Payment is {}".format(c))

  st.markdown("Cumulative Interests for {} Months Are {}".format(T, i))


#%%
#==============================================================================
# Tab 3 Fixed Vs. Varible
#==============================================================================

def tab4():
    st.markdown('''
    :red[Be very careful for interest rate hikes as this program assumes trigger rate is never hit.]''')
    
    st.write("Use the sample input file as template. Add rows as needed, but do not change columns.")
    
    text_contents = '''Month,Variable Rate (%),Fixed Rate (%)
                        1,5,4
                        2,5,4
                        3,4.75,4
                        4,4.75,4
                        5,4.5,4
                        6,4.5,4
                        7,4.25,4
                        8,4.25,4
                        9,4,4
                        10,4,4
                        11,3.5,4
                        12,3.5,4'''
    
    st.download_button('Download Sample Input File', text_contents, 'Sample_input.csv')
    
    rates = st.file_uploader("Upload Custom Rates")
    custom_rate = pd.read_csv(rates)


    row_min = 1
    row_max = len(custom_rate)
    
    P = st.number_input("Enter Loan Amount")
    N = st.number_input("Enter Amortization Period in Month")
    gic_rate = st.number_input("Enter Discount Rate (%) for Present Value Analysis (Optional)")/100

    # Variable Rate Analysis
    
    
    r = custom_rate.iloc[0,1]/100
    
    c = payment_calculator(r,P,N)
    
    custom_rate['monthly_payment_variable'] = c
    
    custom_rate['interest_variable'] = np.nan
    custom_rate['unpaid_balance_variable'] = np.nan
    
    
    
    custom_rate.iloc[0,4] = P * r / 12
    custom_rate.iloc[0,5] = P - c + custom_rate.iloc[0,4]
    
    
    
    
    for row in range(row_min, row_max):
        last_row = row - 1
        custom_rate.iloc[row,4] = custom_rate.iloc[last_row,5] * custom_rate.iloc[row,1] / 100 / 12
        custom_rate.iloc[row,5] = custom_rate.iloc[last_row,5] - custom_rate.iloc[row,3] + custom_rate.iloc[row,4]
        
    
       
    # Fixed Rate Analysis
    
    
    
    
    r = custom_rate.iloc[0,2]/100
    
    c = payment_calculator(r,P,N)
    
    custom_rate['monthly_payment_fixed'] = c
    
    custom_rate['interest_fixed'] = np.nan
    custom_rate['unpaid_balance_fixed'] = np.nan
    
    custom_rate.iloc[0,7] = P * r / 12
    custom_rate.iloc[0,8] = P - c + custom_rate.iloc[0,7]
    
    
    
    
    
    
    for row in range(row_min, row_max):
        last_row = row - 1
        custom_rate.iloc[row,7] = custom_rate.iloc[last_row,8] * custom_rate.iloc[row,2] / 100 / 12
        custom_rate.iloc[row,8] = custom_rate.iloc[last_row,8] - custom_rate.iloc[row,6] + custom_rate.iloc[row,7]
        
    
    custom_rate['cumulative_interests_variable'] = custom_rate['interest_variable'].cumsum()
    custom_rate['cumulative_interests_fixed'] = custom_rate['interest_fixed'].cumsum()
    

    custom_rate['interest_variable_pv'] = custom_rate['interest_variable']/((1+gic_rate/12)**custom_rate['Month'])
    custom_rate['interest_fixed_pv'] = custom_rate['interest_fixed']/((1+gic_rate/12)**custom_rate['Month'])
    
    
    custom_rate['cumulative_interests_variable_pv'] = custom_rate['interest_variable_pv'].cumsum()
    custom_rate['cumulative_interests_fixed_pv'] = custom_rate['interest_fixed_pv'].cumsum()
    
    fig_interest = px.line(custom_rate,
            x=custom_rate.Month,
            y=custom_rate.columns[[9,10]]
            )
    
    st.title('Cumulative Interests') 
    st.plotly_chart(fig_interest)
    
    fig_interest_pv = px.line(custom_rate,
            x=custom_rate.Month,
            y=custom_rate.columns[[13,14]]
            )
    
    st.title('Cumulative Interests: PV') 
    st.plotly_chart(fig_interest_pv)
    
    
    








#%%
#==============================================================================
# Tab 3 Bond
#==============================================================================

def tab5():
    
    url = "https://www.bankofcanada.ca/valet/observations/group/bond_yields_all/csv"

    text = requests.get(url).text[1170:]

    df = pd.read_csv(io.StringIO(text), sep=",")
    df['date'] = pd.to_datetime(df['date']).dt.date

    # plotly setup 3 Month Year Treasury
    fig_3m = px.line(df, x=df['date'], y=['BD.CDN.2YR.DQ.YLD', 'BD.CDN.5YR.DQ.YLD', 'BD.CDN.10YR.DQ.YLD'])
    fig_3m.update_xaxes(showgrid=False, gridwidth=1, gridcolor='rgba(0,0,255,0.1)')
    fig_3m.update_yaxes(showgrid=False, gridwidth=1, gridcolor='rgba(0,0,255,0.1)')

    st.title('T-bill Yields (Canada)')
    st.plotly_chart(fig_3m)

      

  
 

    



#==============================================================================
# Main body
#==============================================================================

def run():
    
    
    
    # Add a radio box
    select_tab = st.sidebar.radio("Select tab", ['Commission', 'Mortgage Payment Calculator', 'Variable Vs. Fixed Mortage', 'T-bill Yields (Canada)'])

    # Show the selected tab
    if select_tab == 'Commission':
        tab1()
    elif select_tab == 'Mortgage Payment Calculator':
        tab2()
    elif select_tab == 'Variable Vs. Fixed Mortage':
        tab3()        
    elif select_tab == 'T-bill Yields (Canada)':
        tab4()    
   
        
if __name__ == "__main__":
    run()   
