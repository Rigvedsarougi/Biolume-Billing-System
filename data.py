import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Load product data and Party data
biolume_df = pd.read_csv('MKT+Biolume - Inventory System - Invoice (2).csv')
party_df = pd.read_csv('MKT+Biolume - Inventory System - Party (2).csv')

# Company Details
company_name = "KS Agencies"
company_address = """61A/42, Karunanidhi Street, Nehru Nagar,
West Velachery, Chennai - 600042.
GSTIN/UIN: 33AAGFK1394P1ZX
State Name : Tamil Nadu, Code : 33
"""
company_logo = 'Untitled design (3).png'
photo_logo = '10.png'

bank_details = """
For Rtgs / KS Agencies
Kotak Mahindra Bank Velachery branch
Ac No 0012490288, IFSC code KKBK0000473 
Mobile - 9444454461 / GPay / PhonePe / Niyas
Delivery/Payment Support: +919094041611
Customer Support: +919311662808
"""

# Custom PDF class
class PDF(FPDF):
    def header(self):
        if company_logo:
            self.image(company_logo, 10, 8, 33)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, company_name, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, company_address, align='C')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Proforma Invoice', ln=True, align='C')
        self.line(10, 50, 200, 50)
        self.ln(5)

    def footer(self):
        if photo_logo:
            self.image(photo_logo, 10, 265, 33)
        self.set_y(-40)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 5, bank_details, align='R')
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# Generate Invoice
def generate_invoice(customer_name, gst_number, contact_number, address, selected_products, quantities):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    current_date = datetime.now().strftime("%d-%m-%Y")
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 10, f"Party: {customer_name}")
    pdf.cell(90, 10, f"Date: {current_date}", ln=True, align='R')
    pdf.cell(100, 10, f"GSTIN/UN: {gst_number}")
    pdf.cell(90, 10, f"Contact: {contact_number}", ln=True, align='R')
    
    # Use multi_cell for address to handle text wrapping
    pdf.cell(100, 10, "Address: ", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 10, address)  # Ensures the address fits within the page
    
    pdf.ln(10)
    
    # Table header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(10, 8, "S.No", border=1, align='C', fill=True)
    pdf.cell(60, 8, "Description of Goods", border=1, align='C', fill=True)
    pdf.cell(20, 8, "HSN/SAC", border=1, align='C', fill=True)
    pdf.cell(20, 8, "GST Rate", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Qty", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Rate", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Disc. %", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Amount", border=1, align='C', fill=True)
    pdf.ln()

    # Table data
    pdf.set_font("Arial", '', 9)
    total_price = 0
    for idx, product in enumerate(selected_products):
        product_data = biolume_df[biolume_df['Product Name'] == product].iloc[0]
        quantity = quantities[idx]
        unit_price = float(product_data['Price'])
        discount = float(product_data['Discount'])
        after_disc = float(product_data['Disc Price'])
        item_total_price = after_disc * quantity

        pdf.cell(10, 8, str(idx + 1), border=1)
        pdf.cell(60, 8, product, border=1)
        pdf.cell(20, 8, "3304", border=1, align='C')
        pdf.cell(20, 8, "18%", border=1, align='C')
        pdf.cell(20, 8, str(quantity), border=1, align='C')
        pdf.cell(20, 8, f"{unit_price:.2f}", border=1, align='R')
        pdf.cell(20, 8, f"{discount:.1f}%", border=1, align='R')
        pdf.cell(20, 8, f"{item_total_price:.2f}", border=1, align='R')
        total_price += item_total_price
        pdf.ln()

    pdf.ln(5)
    tax_rate = 0.18
    tax_amount = total_price * tax_rate

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(160, 10, "CGST (9%)", border=0, align='R')
    pdf.cell(30, 10, f"{tax_amount / 2:.2f}", border=1, align='R')
    pdf.ln()
    pdf.cell(160, 10, "SGST (9%)", border=0, align='R')
    pdf.cell(30, 10, f"{tax_amount / 2:.2f}", border=1, align='R')
    pdf.ln()
    pdf.cell(160, 10, "Grand Total", border=0, align='R')
    pdf.cell(30, 10, f"{total_price + tax_amount:.2f} INR", border=1, align='R')
    pdf.ln(20)

    # Store the invoice details in a CSV file
    invoice_data = {
        "Party": customer_name,
        "GSTIN/UN": gst_number,
        "Contact Number": contact_number,
        "Address": address,
        "Date": current_date,
        "Selected Products": ", ".join(selected_products),
        "Quantities": ", ".join(map(str, quantities)),
        "Total Price": total_price,
        "Tax Amount": tax_amount,
        "Grand Total": total_price + tax_amount
    }

    # Append the data to the CSV file
    invoice_df = pd.DataFrame([invoice_data])
    invoice_df.to_csv('data/invoices.csv', mode='a', header=not pd.io.common.file_exists('data/invoices.csv'), index=False)

    return pdf

# Streamlit UI
st.title("Biolume: Billing System")

# Dropdown for selecting Party from CSV
party_names = party_df['Party'].tolist()
selected_party = st.selectbox("Select Party", party_names)

# Fetch Party details based on selection
party_details = party_df[party_df['Party'] == selected_party].iloc[0]
address = party_details['Address']
gst_number = party_details['GSTIN/UN']

# Customer Name is the same as Party
customer_name = selected_party

# Display the GSTIN in the form
col1, col2 = st.columns(2)
with col1:
    st.text_input("Enter Customer Name", value=customer_name, disabled=True)
with col2:
    st.text_input("Enter GST Number", value=gst_number, disabled=True)

col3, col4 = st.columns(2)
with col3:
    contact_number = st.text_input("Enter Contact Number")  # Define this field
with col4:
    date = datetime.now().strftime("%d-%m-%Y")
    st.text(f"Date: {date}")

# Display the address in the text area
st.text_area("Address", value=address, height=100)

selected_products = st.multiselect("Select Products", biolume_df['Product Name'].tolist())

quantities = []
if selected_products:
    for product in selected_products:
        qty = st.number_input(f"Quantity for {product}", min_value=1, value=1, step=1)
        quantities.append(qty)

if st.button("Generate Invoice"):
    if selected_party and selected_products and quantities and contact_number:
        pdf = generate_invoice(customer_name, gst_number, contact_number, address, selected_products, quantities)
        pdf_file = f"invoice_{selected_party}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("Download Invoice", f, file_name=pdf_file)
    else:
        st.error("Please fill all fields and select products.")
