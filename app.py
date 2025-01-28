import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Load product data
biolume_df = pd.read_csv('Biolume Products List - Data - Product List (2).csv')

# Company Details
company_name = "Biolume Skin Science Pvt Ltd"
company_address = """
GROUND FLOOR, RAMPAL AWANA COMPLEX,
INDRA MARKET, SECTOR-27, Atta, Noida,
Gautambuddha Nagar, Uttar Pradesh, 201301
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
        self.cell(0, 10, 'INVOICE', ln=True, align='C')
        self.line(10, 50, 200, 50)
        self.ln(5)

    def footer(self):
        self.set_y(-40)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 5, bank_details, align='C')
        self.cell(0, 10, 'Thank you for your business!', ln=True, align='C')
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# Generate Invoice
def generate_invoice(customer_name, gst_number, person_name, contact_number, selected_products, quantities):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    current_date = datetime.now().strftime("%d-%m-%Y")
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 10, f"Customer Name: {customer_name}", ln=True)
    pdf.cell(100, 10, f"GST: {gst_number}", ln=True)
    pdf.cell(100, 10, f"Person Name: {person_name}", ln=True)
    pdf.cell(100, 10, f"Contact: {contact_number}", ln=True)
    pdf.cell(100, 10, f"Date: {current_date}", ln=True)
    pdf.ln(10)

    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(20, 8, "ID", border=1, align='C', fill=True)
    pdf.cell(50, 8, "Product", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Qty", border=1, align='C', fill=True)
    pdf.cell(25, 8, "Unit Price", border=1, align='C', fill=True)
    pdf.cell(25, 8, "Discount", border=1, align='C', fill=True)
    pdf.cell(25, 8, "After Disc.", border=1, align='C', fill=True)
    pdf.cell(25, 8, "Total", border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_font("Arial", '', 9)
    total_price = 0
    for idx, product in enumerate(selected_products):
        product_data = biolume_df[biolume_df['Product Name'] == product].iloc[0]
        quantity = quantities[idx]
        unit_price = float(product_data['Price'])
        discount = float(product_data['Discount'])
        after_disc = float(product_data['After Disc.'])
        item_total_price = after_disc * quantity
        
        pdf.cell(20, 8, str(product_data['Product ID']), border=1)
        pdf.cell(50, 8, product, border=1)
        pdf.cell(20, 8, str(quantity), border=1, align='C')
        pdf.cell(25, 8, f"{unit_price:.2f}", border=1, align='R')
        pdf.cell(25, 8, f"{discount:.1f}%", border=1, align='R')
        pdf.cell(25, 8, f"{after_disc:.2f}", border=1, align='R')
        pdf.cell(25, 8, f"{item_total_price:.2f}", border=1, align='R')
        total_price += item_total_price
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(160, 10, "Subtotal", border=0, align='R')
    pdf.cell(30, 10, f"{total_price:.2f}", border=1, align='R')
    pdf.ln()

    tax_rate = 0.18
    tax_amount = total_price * tax_rate
    grand_total = total_price + tax_amount

    pdf.cell(160, 10, "Tax (18%)", border=0, align='R')
    pdf.cell(30, 10, f"{tax_amount:.2f}", border=1, align='R')
    pdf.ln()

    pdf.cell(160, 10, "Grand Total", border=0, align='R')
    pdf.cell(30, 10, f"{grand_total:.2f} INR", border=1, align='R')
    pdf.ln(20)

    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "We appreciate your business and hope to serve you again!", ln=True, align='C')

    return pdf

st.title("Professional Invoice Billing System")
customer_name = st.text_input("Enter Customer Name")
gst_number = st.text_input("Enter GST Number")
person_name = st.text_input("Enter Person Name")
contact_number = st.text_input("Enter Contact Number")
selected_products = st.multiselect("Select Products", biolume_df['Product Name'].tolist())

quantities = []
if selected_products:
    for product in selected_products:
        qty = st.number_input(f"Quantity for {product}", min_value=1, value=1, step=1)
        quantities.append(qty)

if st.button("Generate Invoice"):
    if customer_name and gst_number and person_name and contact_number and selected_products and quantities:
        pdf = generate_invoice(customer_name, gst_number, person_name, contact_number, selected_products, quantities)
        pdf_file = f"invoice_{customer_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("Download Invoice", f, file_name=pdf_file)
    else:
        st.error("Please fill all fields and select products.")
