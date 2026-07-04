"""Tax Management Module for Indian Tax Compliance"""
from tax_management.hsn_sac_codes import HSNCode, SACCode, GSTConfiguration
from tax_management.tds_module import TDSConfiguration, TDSPayment, TDSCertificate
from tax_management.professional_tax import ProfessionalTaxConfiguration, ProfessionalTaxDeduction

__all__ = [
    'HSNCode',
    'SACCode',
    'GSTConfiguration',
    'TDSConfiguration',
    'TDSPayment',
    'TDSCertificate',
    'ProfessionalTaxConfiguration',
    'ProfessionalTaxDeduction'
]
