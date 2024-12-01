# personal-finance-tools

Tools I use for personal finance.

## Scripts

### `cal_to_ledger.py`

Converts Cal-online statements from the JSON files to ledger format.

To use, open devtools, go to network tab, filter by XHR/Fetch, and look for the request that fetches the statement data (`getFilteredTransactions`). Save it to a json file and run the script: `python cal_to_ledger.py < /path/to/json_file > output.txt`

The card will be formatted as `Liabilities:CreditCard:Cal:<uniqueId>`. To give it a different name simply add an `alias` in your ledger file, e.g.

```
alias Liabilities:CreditCard:Cal:1234567890=Liabilities:CompanyCard
```

### `data.py`

Contains static (automatically generated) data:
- list of MCC (merchant category code) names - pulled from https://github.com/greggles/mcc-codes
- Currency codes - pulled from https://github.com/datasets/currency-codes
- MCC to ledger-compatible expense mapping (thanks ChatGPT)
