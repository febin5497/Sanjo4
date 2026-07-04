"""GST Compliance Reports for Indian Tax Filing"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from extensions import db


class GSTReportService:
    """Service to generate GST compliance reports"""

    @staticmethod
    def get_monthly_gst_summary(company_id, month, year):
        """
        Generate monthly GST summary for a company
        Returns: GSTR-1 (outward supplies) data
        """
        from purchase_management.models import Purchase
        from sales_management.models import Sale

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - relativedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - relativedelta(days=1)

        # Fetch all sales
        sales = Sale.query.filter(
            Sale.company_id == company_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).all()

        # Calculate totals
        total_intra_state_sales = sum(s.subtotal for s in sales if s.supply_type == 'Intra-state')
        total_inter_state_sales = sum(s.subtotal for s in sales if s.supply_type == 'Inter-state')
        total_cgst = sum(s.cgst_amount for s in sales)
        total_sgst = sum(s.sgst_amount for s in sales)
        total_igst = sum(s.igst_amount for s in sales)

        return {
            'month': month,
            'year': year,
            'type': 'GSTR-1 (Outward Supplies)',
            'period': f"{start_date.strftime('%B %Y')}",
            'intra_state_sales': total_intra_state_sales,
            'inter_state_sales': total_inter_state_sales,
            'total_sales': total_intra_state_sales + total_inter_state_sales,
            'cgst_collected': total_cgst,
            'sgst_collected': total_sgst,
            'igst_collected': total_igst,
            'total_gst_collected': total_cgst + total_sgst + total_igst,
            'number_of_invoices': len(sales)
        }

    @staticmethod
    def get_gst_liability_summary(company_id, month, year):
        """
        Calculate GST liability (Tax collected - Tax paid)
        """
        from purchase_management.models import Purchase
        from sales_management.models import Sale

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - relativedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - relativedelta(days=1)

        # Inward supplies (purchases)
        purchases = Purchase.query.filter(
            Purchase.company_id == company_id,
            Purchase.purchase_date >= start_date,
            Purchase.purchase_date <= end_date
        ).all()

        # Outward supplies (sales)
        sales = Sale.query.filter(
            Sale.company_id == company_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).all()

        # Tax collected (on sales)
        cgst_collected = sum(s.cgst_amount for s in sales)
        sgst_collected = sum(s.sgst_amount for s in sales)
        igst_collected = sum(s.igst_amount for s in sales)
        total_collected = cgst_collected + sgst_collected + igst_collected

        # Tax paid (on purchases)
        cgst_paid = sum(p.cgst_amount for p in purchases)
        sgst_paid = sum(p.sgst_amount for p in purchases)
        igst_paid = sum(p.igst_amount for p in purchases)
        total_paid = cgst_paid + sgst_paid + igst_paid

        # Liability
        cgst_liability = cgst_collected - cgst_paid
        sgst_liability = sgst_collected - sgst_paid
        igst_liability = igst_collected - igst_paid
        total_liability = total_collected - total_paid

        return {
            'period': f"{start_date.strftime('%B %Y')}",
            'tax_collected': {
                'cgst': cgst_collected,
                'sgst': sgst_collected,
                'igst': igst_collected,
                'total': total_collected
            },
            'tax_paid': {
                'cgst': cgst_paid,
                'sgst': sgst_paid,
                'igst': igst_paid,
                'total': total_paid
            },
            'tax_liability': {
                'cgst': cgst_liability,
                'sgst': sgst_liability,
                'igst': igst_liability,
                'total': total_liability
            },
            'payable_amount': max(0, total_liability)  # Only if positive
        }

    @staticmethod
    def get_hsn_wise_summary(company_id, month, year):
        """
        Get HSN-wise summary of sales (for GSTR-1 Annexure)
        """
        from sales_management.models import Sale, SaleItem

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - relativedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - relativedelta(days=1)

        sales = Sale.query.filter(
            Sale.company_id == company_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).all()

        hsn_summary = {}
        for sale in sales:
            for item in sale.items:
                hsn_code = item.hsn_sac_code or 'UNCLASSIFIED'
                if hsn_code not in hsn_summary:
                    hsn_summary[hsn_code] = {
                        'hsn_code': hsn_code,
                        'description': item.material_name,
                        'quantity': 0,
                        'unit_price': 0,
                        'total_value': 0,
                        'gst_rate': item.gst_rate,
                        'gst_amount': 0
                    }
                hsn_summary[hsn_code]['quantity'] += item.quantity
                hsn_summary[hsn_code]['total_value'] += item.total
                hsn_summary[hsn_code]['gst_amount'] += item.gst_amount

        return list(hsn_summary.values())

    @staticmethod
    def get_customer_wise_summary(company_id, month, year):
        """
        Get customer-wise summary of sales (for GSTR-1 B2B invoices)
        """
        from sales_management.models import Sale
        from client_management.models import Client

        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - relativedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - relativedelta(days=1)

        sales = Sale.query.filter(
            Sale.company_id == company_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Sale.customer_gstin != None  # B2B only
        ).all()

        customer_summary = {}
        for sale in sales:
            customer_gstin = sale.customer_gstin or 'NO-GSTIN'
            if customer_gstin not in customer_summary:
                customer_summary[customer_gstin] = {
                    'customer_gstin': customer_gstin,
                    'invoice_count': 0,
                    'total_taxable_value': 0,
                    'total_gst': 0
                }
            customer_summary[customer_gstin]['invoice_count'] += 1
            customer_summary[customer_gstin]['total_taxable_value'] += sale.subtotal
            customer_summary[customer_gstin]['total_gst'] += sale.total_gst

        return list(customer_summary.values())

    @staticmethod
    def generate_gstr3b_summary(company_id, month, year):
        """
        Generate GSTR-3B (Monthly return) summary
        GSTR-3B = GSTR-1 (Outward) + GSTR-2 (Inward) + ITC + Payment
        """
        liability = GSTReportService.get_gst_liability_summary(company_id, month, year)

        return {
            'return_type': 'GSTR-3B',
            'period': liability['period'],
            'financial_year': f"{year}-{year+1}",
            'section_1': {
                'description': 'Outward Supplies',
                'cgst': liability['tax_collected']['cgst'],
                'sgst': liability['tax_collected']['sgst'],
                'igst': liability['tax_collected']['igst']
            },
            'section_2': {
                'description': 'Input Tax Credit',
                'cgst': liability['tax_paid']['cgst'],
                'sgst': liability['tax_paid']['sgst'],
                'igst': liability['tax_paid']['igst']
            },
            'section_3': {
                'description': 'Net GST Liability',
                'cgst': liability['tax_liability']['cgst'],
                'sgst': liability['tax_liability']['sgst'],
                'igst': liability['tax_liability']['igst'],
                'total': liability['tax_liability']['total']
            },
            'payment_status': 'Pending',
            'filing_deadline': None
        }
