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
company_logo = 'company_logo.png'  # Replace with the path to your company logo image

# Custom PDF class
class PDF(FPDF):
    def header(self):
        # Company Logo
        if company_logo:
            self.image(company_logo, 10, 8, 33)  # Adjust the dimensions as needed
        # Company Name and Address
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, company_name, ln=True, align='C')
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 5, company_address, align='C')
        # Invoice Title
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'INVOICE', ln=True, align='C')
        # Draw line
        self.line(10, 50, 200, 50)
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-20)
        # Footer Text
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Thank you for your business!', ln=True, align='C')
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# Generate Invoice
def generate_invoice(customer_name, selected_products, quantities):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Current Date
    current_date = datetime.now().strftime("%d-%m-%Y")
    
    # Customer Info Section
    pdf.set_font("Arial", '', 12)
    pdf.cell(100, 10, f"Customer Name: {customer_name}", ln=True)
    pdf.cell(100, 10, f"Date: {current_date}", ln=True)
    pdf.ln(10)

    # Table Header (adjusted column widths)
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(25, 10, "ID", border=1, align='C', fill=True)
    pdf.cell(80, 10, "Product", border=1, align='C', fill=True)  # Widened for long product names
    pdf.cell(40, 10, "Category", border=1, align='C', fill=True)
    pdf.cell(15, 10, "Qty", border=1, align='C', fill=True)
    pdf.cell(20, 10, "Unit Price", border=1, align='C', fill=True)
    pdf.cell(25, 10, "Total", border=1, align='C', fill=True)
    pdf.ln()

    # Product details
    pdf.set_font("Arial", '', 12)
    total_price = 0
    for idx, product in enumerate(selected_products):
        product_data = biolume_df[biolume_df['Product Name'] == product].iloc[0]
        quantity = quantities[idx]
        unit_price = product_data['Price']
        item_total_price = unit_price * quantity
        
        # Adding cell wrapping for long product names
        pdf.cell(25, 10, product_data['Product ID'], border=1)
        pdf.cell(80, 10, product_data['Product Name'], border=1)  # More space for product names
        pdf.cell(40, 10, product_data['Product Category'], border=1)
        pdf.cell(15, 10, str(quantity), border=1, align='C')
        pdf.cell(20, 10, f"{unit_price:.2f}", border=1, align='R')
        pdf.cell(25, 10, f"{item_total_price:.2f}", border=1, align='R')
        total_price += item_total_price
        pdf.ln()

    # Summary Section
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(165, 10, "Subtotal", border=0, align='R')
    pdf.cell(25, 10, f"{total_price:.2f}", border=1, align='R')
    pdf.ln()

    # Assuming a tax rate of 18%
    tax_rate = 0.18
    tax_amount = total_price * tax_rate
    grand_total = total_price + tax_amount

    pdf.cell(165, 10, "Tax (18%)", border=0, align='R')
    pdf.cell(25, 10, f"{tax_amount:.2f}", border=1, align='R')
    pdf.ln()

    pdf.cell(165, 10, "Grand Total", border=0, align='R')
    pdf.cell(25, 10, f"{grand_total:.2f} INR", border=1, align='R')
    pdf.ln(20)

    # Thank You Note
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, "We appreciate your business and hope to serve you again!", ln=True, align='C')

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
        pdf_file = f"invoice_{customer_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button("Download Invoice", f, file_name=pdf_file)

    else:
        st.error("Please enter customer name, select products, and enter quantities.")
