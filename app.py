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
def generate_invoice(customer_name, selected_products):
    pdf = FPDF()
    pdf.add_page()

    # Invoice Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, company_name, ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(200, 10, company_address, align="C")
    
    # Customer Details
    pdf.cell(200, 10, f"Customer Name: {customer_name}", ln=True)

    # Table Header
    pdf.cell(40, 10, "Product", border=1)
    pdf.cell(40, 10, "Category", border=1)
    pdf.cell(40, 10, "Price", border=1)
    pdf.ln()

    # Product details
    total_price = 0
    for product in selected_products:
        product_data = biolume_df[biolume_df['Product Name'] == product].iloc[0]
        pdf.cell(40, 10, product_data['Product Name'], border=1)
        pdf.cell(40, 10, product_data['Product Category'], border=1)
        pdf.cell(40, 10, str(product_data['Price']), border=1)
        total_price += product_data['Price']
        pdf.ln()

    # Total price
    pdf.cell(200, 10, f"Total Price: {total_price}", ln=True, align="R")

    return pdf

# Streamlit App
st.title("Invoice Billing System")

# Customer Name input
customer_name = st.text_input("Enter Customer Name")

# Product Selection
selected_products = st.multiselect(
    "Select Products",
    biolume_df['Product Name'].tolist()
)

# Generate Invoice Button
if st.button("Generate Invoice"):
    if customer_name and selected_products:
        pdf = generate_invoice(customer_name, selected_products)

        # Generate PDF file
        pdf_file = f"invoice_{customer_name}.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button("Download Invoice", f, file_name=pdf_file)

    else:
        st.error("Please enter customer name and select products.")
