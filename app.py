import streamlit as st
import pandas as pd
from fpdf import FPDF

# Load product data
biolume_df = pd.read_csv('Biolume Products List - Data - Product List (2).csv')

# Company Details
company_name = "Biolume Skin Science Pvt Ltd"
company_address = """
GROUND FLOOR, RAMPAL AWANA COMPLEX,
INDRA MARKET, SECTOR-27, Atta, Noida,
Gautambuddha Nagar, Uttar Pradesh, 201301
"""

# Create an FPDF instance to generate the PDF
class PDF(FPDF):
    def header(self):
        # Company Name
        self.set_font("Arial", 'B', 16)
        self.cell(200, 10, company_name, ln=True, align="C")
        self.set_font("Arial", size=12)
        self.multi_cell(200, 10, company_address, align="C")
        self.ln(10)

    def footer(self):
        # Footer with page number
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.cell(0, 10, company_name, 0, 0, 'R')

# Generate Invoice
def generate_invoice(customer_name, selected_products, quantities):
    pdf = PDF()
    pdf.add_page()

    # Customer Info Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"Customer Name: {customer_name}", ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(30, 10, "Product ID", border=1, align='C')
    pdf.cell(70, 10, "Product", border=1, align='C')
    pdf.cell(40, 10, "Category", border=1, align='C')
    pdf.cell(20, 10, "Qty", border=1, align='C')
    pdf.cell(30, 10, "Price (INR)", border=1, align='C')
    pdf.ln()

    # Product details
    pdf.set_font("Arial", size=12)
    total_price = 0
    for idx, product in enumerate(selected_products):
        product_data = biolume_df[biolume_df['Product Name'] == product].iloc[0]
        quantity = quantities[idx]
        item_total_price = product_data['Price'] * quantity
        
        pdf.cell(30, 10, product_data['Product ID'], border=1)
        pdf.cell(70, 10, product_data['Product Name'], border=1)
        pdf.cell(40, 10, product_data['Product Category'], border=1)
        pdf.cell(20, 10, str(quantity), border=1, align='C')
        pdf.cell(30, 10, str(item_total_price), border=1, align='R')
        total_price += item_total_price
        pdf.ln()

    # Total Price
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(160, 10, "Total Price", border=1, align="R")
    pdf.cell(30, 10, f"{total_price} INR", border=1, align="R")

    return pdf

# Streamlit App
st.title("Professional Invoice Billing System")

# Customer Name input
customer_name = st.text_input("Enter Customer Name")

# Product Selection
selected_products = st.multiselect(
    "Select Products",
    biolume_df['Product Name'].tolist()
)

# Display quantity input for each selected product
quantities = []
if selected_products:
    st.write("Enter quantity for each product:")
    for product in selected_products:
        qty = st.number_input(f"Quantity for {product}", min_value=1, value=1, step=1)
        quantities.append(qty)

# Generate Invoice Button
if st.button("Generate Invoice"):
    if customer_name and selected_products and quantities:
        pdf = generate_invoice(customer_name, selected_products, quantities)

        # Generate PDF file
        pdf_file = f"invoice_{customer_name}.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button("Download Invoice", f, file_name=pdf_file)

    else:
        st.error("Please enter customer name, select products, and enter quantities.")
