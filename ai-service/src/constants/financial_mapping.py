# ─────────────────────────────────────────────────────────────────
# src/constants/financial_mapping.py
# ─────────────────────────────────────────────────────────────────
#
# Centralized Financial Field Mapping Configuration.
#
# Map canonical model fields to Yahoo Finance timeseries identifiers
# using prioritized fallback lists (e.g. Total Revenue -> Operating Revenue).
# ─────────────────────────────────────────────────────────────────

FINANCIAL_FIELD_MAP = {
    # ── Income Statement mapping ──
    "revenue": {
        "annual": ["annualTotalRevenue", "annualOperatingRevenue"],
        "quarterly": ["quarterlyTotalRevenue", "quarterlyOperatingRevenue"],
    },
    "costOfRevenue": {
        "annual": ["annualCostOfRevenue"],
        "quarterly": ["quarterlyCostOfRevenue"],
    },
    "grossProfit": {
        "annual": ["annualGrossProfit"],
        "quarterly": ["quarterlyGrossProfit"],
    },
    "researchDevelopment": {
        "annual": ["annualResearchAndDevelopment"],
        "quarterly": ["quarterlyResearchAndDevelopment"],
    },
    "sellingGeneralAdministrative": {
        "annual": ["annualSellingGeneralAndAdministration"],
        "quarterly": ["quarterlySellingGeneralAndAdministration"],
    },
    "operatingExpenses": {
        "annual": ["annualOperatingExpense"],
        "quarterly": ["quarterlyOperatingExpense"],
    },
    "operatingIncome": {
        "annual": ["annualOperatingIncome"],
        "quarterly": ["quarterlyOperatingIncome"],
    },
    "netIncome": {
        "annual": ["annualNetIncome", "annualNetIncomeCommonStockholders", "annualNetIncomeContinuousOperations"],
        "quarterly": ["quarterlyNetIncome", "quarterlyNetIncomeCommonStockholders", "quarterlyNetIncomeContinuousOperations"],
    },
    
    # ── Balance Sheet mapping ──
    "totalAssets": {
        "annual": ["annualTotalAssets"],
        "quarterly": ["quarterlyTotalAssets"],
    },
    "totalLiabilities": {
        "annual": ["annualTotalLiabilitiesNetMinorityInterest"],
        "quarterly": ["quarterlyTotalLiabilitiesNetMinorityInterest"],
    },
    "stockholdersEquity": {
        "annual": ["annualStockholdersEquity"],
        "quarterly": ["quarterlyStockholdersEquity"],
    },
    "cashAndCashEquivalents": {
        "annual": ["annualCashAndCashEquivalents"],
        "quarterly": ["quarterlyCashAndCashEquivalents"],
    },
    "longTermDebt": {
        "annual": ["annualLongTermDebt"],
        "quarterly": ["quarterlyLongTermDebt"],
    },
    "retainedEarnings": {
        "annual": ["annualRetainedEarnings"],
        "quarterly": ["quarterlyRetainedEarnings"],
    },
    "currentAssets": {
        "annual": ["annualCurrentAssets"],
        "quarterly": ["quarterlyCurrentAssets"],
    },
    "currentLiabilities": {
        "annual": ["annualCurrentLiabilities"],
        "quarterly": ["quarterlyCurrentLiabilities"],
    },
    
    # ── Cash Flow Statement mapping ──
    "operatingCashFlow": {
        "annual": ["annualOperatingCashFlow"],
        "quarterly": ["quarterlyOperatingCashFlow"],
    },
    "capitalExpenditures": {
        "annual": ["annualCapitalExpenditure"],
        "quarterly": ["quarterlyCapitalExpenditure"],
    },
    "freeCashFlow": {
        "annual": ["annualFreeCashFlow"],
        "quarterly": ["quarterlyFreeCashFlow"],
    }
}
