#!/usr/bin/env python3
import json
from datetime import datetime
import re
from typing import Dict, Any, List
import data
import sys


"""
This is the schema used by Cal (deduced from data, inaccurate)
```
result:
  transArr:
    - trnIntId:
        type: string
        description: "Internal transaction identifier"
      cardUniqueId:
        type: string
        description: "Unique identifier for the card used in the transaction"
      merchantName:
        type: string
        description: "Name of the merchant where the transaction occurred"
      amountForDisplay:
        type: float
        description: "Transaction amount formatted for display, including currency conversion if applicable"
      currencyForDisplay:
        type: string
        description: "Symbol of the currency for display purposes"
      trnPurchaseDate:
        type: string (ISO 8601 datetime)
        description: "Date and time when the transaction was made"
      trnAmt:
        type: float
        description: "Original amount of the transaction in the transaction currency"
      trnCurrencyIsoCode:
        type: string
        description: "ISO 4217 numeric code of the transaction currency"
      trnCurrencySymbol:
        type: string
        description: "Symbol of the transaction currency"
      debCrdCurrencyDesc:
        type: string
        description: "Description of the debit or credit currency (e.g., 'שח' for Israeli Shekel)"
      debCrdCurrencyCode:
        type: integer
        description: "Internal code representing the debit or credit currency"
      debCrdDate:
        type: string (ISO 8601 date)
        description: "Date when the transaction was debited or credited"
      amtBeforeConvAndIndex:
        type: float
        description: "Amount before any conversion or indexing"
      debCrdCurrencySymbol:
        type: string
        description: "Symbol of the debit or credit currency"
      merchantAddress:
        type: string
        description: "Physical address of the merchant"
      merchantPhoneNo:
        type: string
        description: "Contact phone number of the merchant"
      branchCodeDesc:
        type: string or null
        description: "Description of the branch code, if applicable"
      transCardPresentInd:
        type: boolean
        description: "Indicator whether the physical card was present during the transaction"
      curPaymentNum:
        type: integer
        description: "Current payment number in installment transactions"
      numOfPayments:
        type: integer
        description: "Total number of payments in installment transactions"
      trnType:
        type: string
        description: "Type of transaction (e.g., 'רגילה' for regular, 'הוראת קבע' for standing order)"
      transMahut:
        type: string
        description: "Transaction nature code, possibly for internal classification"
      trnNumaretor:
        type: float
        description: "Transaction numerator, potentially used for calculations like interest"
      comments:
        type: list of objects
        items:
          key:
            type: string
            description: "Title or header of the comment"
          value:
            type: string
            description: "Content or details of the comment"
        description: "List of comments associated with the transaction"
      linkedComments:
        type: list of objects
        items:
          text:
            type: string
            description: "Display text for the linked comment"
          linkDisplayName:
            type: string
            description: "Display name for the hyperlink"
          linkType:
            type: integer
            description: "Type code of the link (e.g., 1 for internal links)"
          link:
            type: string
            description: "URL or reference identifier for the link"
        description: "List of comments that include hyperlinks or references"
      tokenInd:
        type: integer
        description: "Tokenization indicator (e.g., 1 if tokenized via digital wallet)"
      walletProviderCode:
        type: integer
        description: "Code representing the wallet provider (e.g., 3 for Apple Pay)"
      walletProviderDesc:
        type: string
        description: "Description of the wallet provider"
      tokenNumberPart4:
        type: string
        description: "Last four digits of the tokenized card number used in the transaction"
      roundingAmount:
        type: float or null
        description: "Amount rounded during the transaction, if applicable"
      roundingReason:
        type: string or null
        description: "Reason for rounding the transaction amount"
      discountAmount:
        type: float or null
        description: "Discount amount applied to the transaction"
      discountReason:
        type: string or null
        description: "Reason for the discount applied"
      internationalBranchID:
        type: string
        description: "Merchant Category Code (MCC) representing the type of merchant"
      transTypeCommentDetails:
        type: list
        description: "Additional details or comments regarding the transaction type"
      internationalBranchDesc:
        type: string
        description: "Description of the international branch or MCC category"
      chargeExternalToCardComment:
        type: string
        description: "Comments regarding charges external to the card"
      superBranchDesc:
        type: string or null
        description: "Higher-level branch description, if applicable"
      transactionTypeCode:
        type: integer
        description: "Code representing the transaction type for internal processing"
      refundInd:
        type: boolean
        description: "Indicator whether the transaction is a refund"
      isImmediate:
        type: boolean
        description: "Indicator whether the transaction is processed immediately"
      isImmediateCommentInd:
        type: boolean
        description: "Indicator for immediate transaction comments"
      isImmediateHHKInd:
        type: boolean
        description: "Indicator for immediate standing order transactions"
      immediateComments:
        type: string or null
        description: "Comments related to immediate transactions"
      isMargaritaInd:
        type: boolean
        description: "Special processing indicator (exact meaning may be specific to issuer)"
      isSpreadPaymenstAbroadInd:
        type: boolean
        description: "Indicator if the transaction is an abroad installment payment"
      trnExacWay:
        type: integer
        description: "Code representing how the transaction was executed (e.g., in-person, online)"
      isInterestTransaction:
        type: boolean
        description: "Indicator whether the transaction involves interest charges"
      onGoingTransactionsComment:
        type: string
        description: "Comments regarding ongoing transactions"
      merchantId:
        type: string
        description: "Unique identifier assigned to the merchant by the card issuer"
      crdExtIdNumTypeCode:
        type: string
        description: "Code representing the type of external card identifier"
      transSource:
        type: string
        description: "Source code of the transaction, indicating origin (e.g., POS terminal, online)"
      transIndication:
        type: string
        description: "Additional indication or flag related to the transaction"
      cashAccountTrnAmt:
        type: float
        description: "Transaction amount in terms of cash account, if applicable"
      transOriginalSumCurrency:
        type: string
        description: "Description of the original transaction currency"
      crmIccCurrencyDesc:
        type: string
        description: "Currency description used in CRM or ICC systems (e.g., 'ILS' for Israeli Shekel)"
      transOriginalCurrencyCode:
        type: integer or null
        description: "ISO 4217 numeric code of the original transaction currency"
      isAbroadTransaction:
        type: boolean
        description: "Indicator whether the transaction was made abroad"
```
"""

def clean_string(s: str) -> str:
    """Clean strings to be ledger-compatible."""
    if not s:
        return ""
    # Remove problematic characters and normalize whitespace
    return re.sub(r'\s+', ' ', s.strip())

def format_amount(amount: float, currency: str) -> str:
    """Format amount with currency symbol."""
    return f"{amount:.2f} {currency}"

def get_category_from_mcc(mcc: str) -> str:
    """Get expense category based on MCC code."""
    return data.MCC_EXPENSE_CATEGORIES.get(mcc, "Expense:Uncategorized")

def format_metadata(data: Dict[str, Any]) -> List[str]:
    """Format transaction metadata as ledger comments."""
    metadata = []
    
    # Essential transaction details
    if data.get("trnIntId"):
        metadata.append(f"; Transaction ID: {data['trnIntId']}")
    
    # Merchant information
    if data.get("merchantAddress"):
        metadata.append(f"; Address: {clean_string(data['merchantAddress'])}")
    if data.get("merchantPhoneNo"):
        metadata.append(f"; Phone: {data['merchantPhoneNo']}")
    if data.get("merchantId"):
        metadata.append(f"; Merchant ID: {data['merchantId']}")
    
    # Transaction details
    if data.get("transCardPresentInd") is not None:
        metadata.append(f"; Card Present: {'Yes' if data['transCardPresentInd'] else 'No'}")
    if data.get("trnType"):
        metadata.append(f"; Transaction Type: {data['trnType']}")
    if data.get("internationalBranchID"):
        metadata.append(f"; MCC: {data['internationalBranchID']}")
    
    # Payment information
    if data.get("numOfPayments") and data["numOfPayments"] > 0:
        metadata.append(f"; Payment {data['curPaymentNum']} of {data['numOfPayments']}")
    
    # Additional flags
    if data.get("isAbroadTransaction"):
        metadata.append("; Foreign Transaction")
    if data.get("refundInd"):
        metadata.append("; Refund")
    
    # Comments
    if data.get("comments"):
        for comment in data["comments"]:
            metadata.append(f"; Comment: {clean_string(str(comment))}")
    
    return metadata

def convert_transaction(trans: Dict[str, Any]) -> str:
    """Convert a single transaction to ledger format."""
    # Parse and format the date
    date = datetime.fromisoformat(trans["trnPurchaseDate"]).strftime("%Y-%m-%d")
    card_id = trans["cardUniqueId"]
    
    # Clean and format the merchant name
    merchant_name = clean_string(trans["merchantName"])
    
    # Get the category based on MCC
    category = get_category_from_mcc(trans.get("internationalBranchID", ""))
    
    # Format the amount and currency
    amount = trans["amountForDisplay"]
    currency = trans["currencyForDisplay"]
    formatted_amount = format_amount(amount, currency)
    
    # Generate metadata
    metadata = format_metadata(trans)
    
    # Build the transaction
    lines = [f"{date} * {merchant_name}"]
    lines.extend(["    " + l for l in metadata])
    lines.append(f"    {category}  {formatted_amount}")
    lines.append(f"    Liabilities:CreditCard:Cal:{card_id}")
    
    return "\n".join(lines)

def convert_json_to_ledger(json_data: str) -> str:
    """Convert JSON data from CAL online to ledger format."""
    try:
        data = json.loads(json_data)
        transactions = data["result"]["transArr"]
        
        # Convert each transaction and join with double newline
        ledger_entries = []
        for trans in transactions:
            ledger_entries.append(convert_transaction(trans))
        
        return "\n\n".join(ledger_entries)
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Missing required field in JSON data: {str(e)}")

if __name__ == "__main__":
    json_str = sys.stdin.read()
    
    try:
        ledger_output = convert_json_to_ledger(json_str)
        print(ledger_output)
    except ValueError as e:
        print(f"Error: {str(e)}")
