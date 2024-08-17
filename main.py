import streamlit as st
import requests
import io
import numpy as np
import pandas as pd
import plotly.express as px
import math

def amortization(r,P,a,f = 'Monthly'):
    
    # r is the nominal annual interest rate
    # P is the principal
    # a is amortization in month
    # t is the mortgage term in month
    # f is the payment frequency
    

    r = r/100

    r_e = (1+r/2)**2-1 
    
    r_m = (1+r_e)**(1/12)-1 

    c = (r_m * P)/(1-(1+r_m)**(-a)) 
      
    if f == 'Monthly':
        n = 12
        r_m = (1+r_e)**(1/n)-1  
        c = c
        t = a

        
    elif f == 'Semi-Monthly':
        n = 24
        r_m = (1+r_e)**(1/n)-1  
        c = c/2
        t = a*2

        

    elif f == 'Bi-Weekly':
        n = 26
        r_m = (1+r_e)**(14/365.25)-1  
        c = c*12/26
        t = math.ceil(n*a/12)
        
    elif f == 'Weekly':
        n = 52
        r_m = (1+r_e)**(7/365.25)-1  
        c = c*12/52
        t = math.ceil(n*a/12)
        
    elif f == 'Accelerated Bi-Weekly':
        n = 26
        r_m = (1+r_e)**(14/365.25)-1  
        c = c/2 
        t = math.ceil(n*a/12)
        
    elif f == 'Accelerated Weekly':
        n = 52
        r_m = (1+r_e)**(7/365.25)-1  
        c = c/4  
        t = math.ceil(n*a/12)
   
    schedule = pd.DataFrame(columns=['Period', 'Opening Balance', 'Payment', 'Interest Payment', 'Principal Payment', 'Closing Balance'])
    
    balance = P
    
    for x in range(0,t):
        
        period = x
        opening_balance = balance
        payment = c
        interest = opening_balance * r_m
        if payment > opening_balance:
            payment = opening_balance + interest
        principal = payment - interest
        balance = balance - principal
        closing_balance = balance
        

        
        row = [period, opening_balance, payment, interest, principal, closing_balance]
        
        schedule.loc[len(schedule)] = row
            
        if closing_balance == 0:
            break


    actual_amortization = round(len(schedule)/n,2)

    
    return schedule, actual_amortization, n

def interest_rate(r,f = 'Monthly'):
    
    # r is the nominal annual interest rate
    # f is the payment frequency
    

    r = r/100

    r_e = (1+r/2)**2-1 
    
    r_m = (1+r_e)**(1/12)-1 

      
    if f == 'Monthly':
        n = 12
        r_m = (1+r_e)**(1/n)-1  
     

        
    elif f == 'Semi-Monthly':
        n = 24
        r_m = (1+r_e)**(1/n)-1  


        

    elif f == 'Bi-Weekly':
        n = 26
        r_m = (1+r_e)**(14/365.25)-1  

        
    elif f == 'Weekly':
        n = 52
        r_m = (1+r_e)**(7/365.25)-1  

        
    elif f == 'Accelerated Bi-Weekly':
        n = 26
        r_m = (1+r_e)**(14/365.25)-1  

        
    elif f == 'Accelerated Weekly':
        n = 52
        r_m = (1+r_e)**(7/365.25)-1  

    
    return r_e, r_m



def fixed_variable_rate(df,P,a):
    
    df['Variable Rate (%)'] = df['Variable Rate (%)']/100
    df['Fixed Rate (%)'] = df['Fixed Rate (%)']/100
    
    df['Effective Annual Variable Rate (%)'] =  (1+df['Variable Rate (%)']/2)**2-1
        
    df['Effective Annual Fixed Rate (%)'] = (1+df['Fixed Rate (%)']/2)**2-1
    
    df['Effective Monthly Variable Rate (%)'] =  (1+df['Effective Annual Variable Rate (%)'])**(1/12)-1
        
    df['Effective Monthly Fixed Rate (%)'] = (1+df['Effective Annual Fixed Rate (%)'])**(1/12)-1
    
    df['Monthly Payment - Variable']  = (df['Effective Monthly Variable Rate (%)'][0] * P)/(1-(1+df['Effective Monthly Variable Rate (%)'][0])**(-a)) 
    
    df['Monthly Payment - Fixed']  = (df['Effective Monthly Fixed Rate (%)'][0] * P)/(1-(1+df['Effective Monthly Fixed Rate (%)'][0])**(-a)) 
    
    df['Opening Balance - Variable'] = np.nan
    df['Opening Balance - Variable'][0] = P
    df['Closing Balance - Variable'] = np.nan
    
    
    df['Opening Balance - Fixed'] = np.nan
    df['Opening Balance - Fixed'][0] = P
    df['Closing Balance - Fixed'] = np.nan
    
    
    df['Monthly Interest - Variable']  = df['Effective Monthly Variable Rate (%)'] * df['Opening Balance - Variable']
    df['Monthly Interest - Fixed'] = df['Effective Monthly Fixed Rate (%)'] * df['Opening Balance - Fixed']
    
    df['Monthly Principal - Variable']  = df['Monthly Payment - Variable'] - df['Monthly Interest - Variable']
    df['Monthly Principal - Fixed'] = df['Monthly Payment - Fixed'] - df['Monthly Interest - Fixed']
    
    df['Closing Balance - Variable'] = df['Opening Balance - Variable'] - df['Monthly Principal - Variable']
    df['Closing Balance - Fixed'] = df['Opening Balance - Fixed'] - df['Monthly Principal - Fixed']
    
    
    current_balance_variable = df['Closing Balance - Variable'][0]
    current_balance_fixed = df['Closing Balance - Fixed'][0]
    
    for t in range(1,max(df['Month'])):
        
        df.iloc[t,9] = current_balance_variable # opening balance variable
        df.iloc[t,11] = current_balance_fixed # opening balance fixed
        df.iloc[t,13] = df.iloc[t,9] * df.iloc[t,5] # interest variable
        df.iloc[t,14] = df.iloc[t,11] * df.iloc[t,6] # interest fixed
        df.iloc[t,15] = df.iloc[t,7] - df.iloc[t,13] # principal variable
        df.iloc[t,16] = df.iloc[t,8] - df.iloc[t,14] # principal fixed
        current_balance_variable = df.iloc[t,9] - df.iloc[t,15]
        current_balance_fixed = df.iloc[t,11] - df.iloc[t,16]
        df.iloc[t,10] = current_balance_variable # closing balance variable
        df.iloc[t,12] = current_balance_fixed # closing balance fixed
    
    

    df['Cumulative Interest - Variable'] = df['Monthly Interest - Variable'].cumsum()
    df['Cumulative Interest - Fixed'] = df['Monthly Interest - Fixed'].cumsum()
    
    return df


#%%
#==============================================================================
# Tab 1 Commission
#==============================================================================

def tab_commission():
  price = st.number_input("Enter Purchase/Sale Price", value = 1000000)
 
  if price<=100000:
        total_commission = round(price * 0.07, 2)

        total_commission_percentage = round((total_commission/price)*100, 2)

        buy_commission = round(price*0.0322, 2)

        buy_commission_percentage = round((buy_commission / price)*100, 2)

        listing_commission = round(price*0.0378, 2)
  
        listing_commission_percentage = round((listing_commission / price)*100, 2)

  else:
      total_commission = round(7000 + (price-100000)*0.02, 2)

      total_commission_percentage = round((total_commission/price)*100, 2)

      buy_commission = round(3220+0.0115*(price-100000), 2)

      buy_commission_percentage = round((buy_commission / price)*100, 3)

      listing_commission = round(3780 + 0.0135*(price-100000),2)
  
      listing_commission_percentage = round((listing_commission / price)*100, 2)
      
      


  

  st.write("Total Commission: {}, or {}% of purchase price".format(total_commission, total_commission_percentage))

  st.write("Commission for Buyer's Agent: {}, or {}% of purchase price".format(buy_commission, buy_commission_percentage))
  
  st.write("Commission for Seller's Agent: {}, or {}% of purchase price".format(listing_commission, listing_commission_percentage))


  
  

#%%
#==============================================================================
# Tab 2 Mortgage 
#==============================================================================

def tab_mortgage():

  
  P = st.number_input("Enter Loan Amount", value = 200000)
  r = st.number_input("Enter Annual Nominal Interest Rate in %", value = 6.95)
  a = st.number_input("Enter Nominal Amortization Period in Month", value = 360)
  t = st.number_input("Enter Term Period in Month", value = 36)  
  f = st.selectbox("Select Payment Frequency",
                  ('Monthly', 'Semi-Monthly', 'Bi-Weekly', 'Weekly', 'Accelerated Bi-Weekly', 'Accelerated Weekly'),)
             
  

  df,a,n = amortization(r,P,a,f)

  st.title("Term Summary")

  n = math.ceil(n*36/12)
  df_t = df.head(n)

  st.markdown("Periodic Payment: {} ".format(round(df.iloc[0,2],2)))
  st.markdown("Cumulative Interest Over Term: {} ".format(round(df_t['Interest Payment'].sum(),2)))  
  st.markdown("Cumulative Principal Over Term: {} ".format(round(df_t['Principal Payment'].sum(),2)))  
    
  
  st.title("Amortization Summary")
  
  st.markdown("Actual Amortization: {} Years".format(a))

  st.dataframe(df)

  fig = px.bar(df,
        x=df.Period,
        y=['Interest Payment', 'Principal Payment'],
        title = 'Periodic Payment Decomposition'
        )    

  st.plotly_chart(fig)


#%%
#==============================================================================
# Tab 3 Interest Analysis
#==============================================================================

def tab_interest():

  r = st.number_input("Enter Annual Nominal Interest Rate in %", value = 6.95)
  f = st.selectbox("Select Payment Frequency",
                  ('Monthly', 'Semi-Monthly', 'Bi-Weekly', 'Weekly', 'Accelerated Bi-Weekly', 'Accelerated Weekly'),)
             
  

  r_e,r_m = interest_rate(r,f)

  st.markdown("Effective Annual Rate: {} %".format(round(100*r_e,2)))
  st.markdown("Effective Periodic Rate: {} %".format(round(100*r_m,2)))


#%%
#==============================================================================
# Tab 4 Fixed Vs. Varible
#==============================================================================

def tab_fix_var():
    st.markdown('''
    :red[Be very careful for interest rate hikes as this program assumes no monthly payment adjustment (i.e, hitting trigger rate results in negative amortization)]''')
    
    P = st.number_input("Enter Loan Amount", value = 200000)
    a = st.number_input("Enter Amortization Period in Month", value = 360)
    
    st.write("Use the sample input file as template. Add as many rows as needed, but do not change columns.")
    
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
    

    if rates is not None:

        custom_rate = pd.read_csv(rates)
        df = fixed_variable_rate(custom_rate,P,a)
        
        fig_interest = px.line(df,
                x=df['Month'],
                y=['Cumulative Interest - Variable', 'Cumulative Interest - Fixed']
                )
        
        st.title('Cumulative Interests') 
        st.plotly_chart(fig_interest)
        

    
    
    








#%%
#==============================================================================
# Tab 5 Bonds
#==============================================================================

def tab_tbill():
    
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

      
#%%
#==============================================================================
# Tab 5 Transfer Tax
#==============================================================================

def tab_tax():
    
    price = st.number_input("Enter Purchase/Sale Price", value = 1000000)

    if price <= 200000:
        tax = price * 0.01
    elif (price > 200000) & (price <= 2000000):
        tax = 2000 + (price - 200000)*0.02
    elif (price > 2000000):
        tax = 38000 + (price - 2000000)*0.03

    st.markdown("The property transfer tax is {} dolars".format(round(tax,2)))
 

#%%
#==============================================================================
# Tab 6 Prepayment
#==============================================================================

def tab_prepay():
    
    type = st.selectbox("Select Mortgage Type",
                       ('Variable', 'Fixed'),)

    if type == 'Variable':
        amount = st.number_input("Enter Prepayment Amount", value = 60000)
        current_prime = st.number_input("Enter Current Prime Rate in %", value = 5)
        penalty = amount*current_prime/100/4

    elif type == 'Fixed':
        amount = st.number_input("Enter Prepayment Amount", value = 100000)
        fixed_rate = st.number_input("Enter Fixed Mortgage Rate in %", value = 6.5)
        discount = st.number_input("Enter Discount Received in %", value = 0.5)
        monthly_payment = st.number_input("Enter Monthly Payment", value = 693.47)
        remaining_term_in_month = st.number_input("Enter Remaining Term in Month", value = 24)
        comparison_rate = st.number_input("Enter Posted Comparison Mortgage Rate in %", value = 5)
        
        
        no_discount_rate = (fixed_rate+discount)/100
        three_month_interest = amount * (no_discount_rate)/100/4

        
        r_e1 = (1+no_discount_rate/2)**2-1 
        r_m1 = (1+r_e1)**(1/12)-1 
        existing_interest = (amount*r_m1-monthly_payment)*((1+r_m1)**remaining_term_in_month-1)/r_m1 + monthly_payment*remaining_term_in_month

        comparison_rate = comparison_rate/100
        r_e2 = (1+comparison_rate/2)**2-1 
        r_m2 = (1+r_e2)**(1/12)-1 
        comparison_interest = (amount*r_m2-monthly_payment)*((1+r_m2)**remaining_term_in_month-1)/r_m2 + monthly_payment*remaining_term_in_month

        interest_differential = existing_interest - comparison_interest

        penalty = max(three_month_interest, interest_differential)

    st.markdown("Prepayment Penalty is {} dollars".format(round(penalty,2)))


  



#==============================================================================
# Main body
#==============================================================================

def run():
    
    
    
    # Add a radio box
    select_tab = st.sidebar.radio("Select tab", ['Commission', 'Property Transfer Tax', 'Mortgage Payment Calculator', 'Interest Rates', 'Variable Vs. Fixed Mortage', 'Prepayment', 'T-bill Yields (Canada)'])

    # Show the selected tab
    if select_tab == 'Commission':
        tab_commission()
    elif select_tab == 'Property Transfer Tax':
        tab_tax()    
    elif select_tab == 'Mortgage Payment Calculator':
        tab_mortgage()
    elif select_tab == 'Interest Rates':
        tab_interest()  
    elif select_tab == 'Variable Vs. Fixed Mortage':
        tab_fix_var()  
    elif select_tab == 'Prepayment':
        tab_prepay()        
    elif select_tab == 'T-bill Yields (Canada)':
        tab_tbill()    
   
        
if __name__ == "__main__":
    run()   
