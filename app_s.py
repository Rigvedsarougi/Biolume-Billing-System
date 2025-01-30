import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
from config import COMPANY_NAME, COMPANY_ADDRESS, COMPANY_LOGO, PHOTO_LOGO, BANK_DETAILS

# Ensure invoice directory exists
INVOICE_DIR = "generated_invoices"
os.makedirs(INVOICE_DIR, exist_ok=True)

# Load product data
biolume_df = pd.read_csv('data/inventory.csv')

# Custom PDF class
class PDF(FPDF):
    def header(self):
        if COMPANY_LOGO:
            self.image(COMPANY_LOGO, 10, 8, 33)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, COMPANY_NAME, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, COMPANY_ADDRESS, align='C')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Proforma Invoice', ln=True, align='C')
        self.line(10, 50, 200, 50)
        self.ln(5)

    def footer(self):
        if PHOTO_LOGO:
            self.image(PHOTO_LOGO, 10, 265, 33)
        self.set_y(-40)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 5, BANK_DETAILS, align='R')
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# Generate Invoice
def generate_invoice(customer_name, gst_number, contact_number, selected_products, quantities):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    current_date = datetime.now().strftime("%d-%m-%Y")
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 10, f"Party: {customer_name}", ln=True)
    pdf.cell(100, 10, f"GSTIN/UN: {gst_number}", ln=True)
    pdf.cell(100, 10, f"Contact: {contact_number}", ln=True)
    pdf.cell(100, 10, f"Date: {current_date}", ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 9)
    headers = ["S.No", "Description", "HSN/SAC", "GST %", "Qty", "Rate", "Disc. %", "Amount"]
    col_widths = [10, 60, 20, 20, 20, 20, 20, 20]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align='C', fill=True)
    pdf.ln()

    # Table Data
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
        pdf.cell(20, 8, "3304", border=1, align='C')  # HSN/SAC code
        pdf.cell(20, 8, "18%", border=1, align='C')  # GST Rate
        pdf.cell(20, 8, str(quantity), border=1, align='C')
        pdf.cell(20, 8, f"{unit_price:.2f}", border=1, align='R')
        pdf.cell(20, 8, f"{discount:.1f}%", border=1, align='R')
        pdf.cell(20, 8, f"{item_total_price:.2f}", border=1, align='R')
        total_price += item_total_price
        pdf.ln()

    # Subtotal, GST, and Grand Total
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    
    tax_rate = 0.18
    tax_amount = total_price * tax_rate
    grand_total = total_price + tax_amount

    totals = [("Subtotal", total_price), ("CGST (9%)", tax_amount / 2), 
              ("SGST (9%)", tax_amount / 2), ("Grand Total", grand_total)]
    
    for label, amount in totals:
        pdf.cell(160, 10, label, border=0, align='R')
        pdf.cell(30, 10, f"{amount:.2f} INR", border=1, align='R')
        pdf.ln()

    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    
    return pdf

# Streamlit UI
st.title("Biolume: Billing System")

customer_name = st.text_input("Enter Customer Name")
gst_number = st.text_input("Enter GST Number")
contact_number = st.text_input("Enter Contact Number")
selected_products = st.multiselect("Select Products", biolume_df['Product Name'].tolist())

quantities = []
if selected_products:
    for product in selected_products:
        qty = st.number_input(f"Quantity for {product}", min_value=1, value=1, step=1)
        quantities.append(qty)

if st.button("Generate Invoice"):
    if customer_name and gst_number and contact_number and selected_products and quantities:
        pdf = generate_invoice(customer_name, gst_number, contact_number, selected_products, quantities)
        
        pdf_file = os.path.join(INVOICE_DIR, f"invoice_{customer_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button("Download Invoice", f, file_name=os.path.basename(pdf_file))
    else:
        st.error("Please fill all fields and select products.")
