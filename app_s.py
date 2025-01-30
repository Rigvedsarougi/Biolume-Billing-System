import os
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Load product data
biolume_df = pd.read_csv('MKT+Biolume - Inventory System - Invoice.csv')

# Create a directory for invoices if it doesn't exist
if not os.path.exists("invoices"):
    os.makedirs("invoices")

# CSV file to store invoice records
invoice_csv = "invoices/invoices.csv"

# Company Details
company_name = "KS Agencies"
company_address = """61A/42, Karunanidhi Street, Nehru Nagar,
West Velachery, Chennai - 600042.
GSTIN/UIN: 33AAGFK1394P1ZX
State Name : Tamil Nadu, Code : 33
"""
company_logo = 'Untitled design (3).png'

bank_details = """
For Rtgs / KS Agencies
Kotak Mahindra Bank
Velachery branch
Ac No 0012490288
IFSC code KKBK0000473
Mobile - 9444454461 / GPay / PhonePe / Niyas
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
        self.set_y(-40)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 5, bank_details, align='C')
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# Streamlit UI
st.title("Invoice Billing System")

customer_name = st.text_input("Customer Name")
gst_number = st.text_input("GST Number")
person_name = st.text_input("Person Name")
contact_number = st.text_input("Contact Number")

selected_products = st.multiselect("Select Products", biolume_df['Product Name'].tolist())
quantities = [st.number_input(f"Quantity for {product}", min_value=1, value=1) for product in selected_products]

def generate_invoice():
    pdf = PDF()
    pdf.add_page()
    current_date = datetime.now().strftime("%d-%m-%Y")
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 10, f"Party: {customer_name}", ln=True)
    pdf.cell(100, 10, f"GSTIN/UN: {gst_number}", ln=True)
    pdf.cell(100, 10, f"Contact: {contact_number}", ln=True)
    pdf.cell(100, 10, f"Date: {current_date}", ln=True)
    pdf.ln(10)
    
    total_price = 0
    for idx, product in enumerate(selected_products):
        product_data = biolume_df[biolume_df['Product Name'] == product].iloc[0]
        quantity = quantities[idx]
        unit_price = float(product_data['Price'])
        after_disc = float(product_data['Disc Price'])
        item_total_price = after_disc * quantity
        total_price += item_total_price
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(160, 10, "Grand Total", border=0, align='R')
    pdf.cell(30, 10, f"{total_price:.2f} INR", border=1, align='R')
    pdf.ln(20)
    
    pdf_filename = f"invoices/invoice_{customer_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

if st.button("Generate Invoice"):
    if customer_name and gst_number and contact_number and selected_products:
        pdf_file = generate_invoice()
        with open(pdf_file, "rb") as f:
            st.download_button("Download Invoice", f, file_name=pdf_file)
        st.success("Invoice generated and saved!")
    else:
        st.error("Please fill all fields and select products.")
