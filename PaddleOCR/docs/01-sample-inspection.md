# Sample document inspection

Source folder: `C:\Users\drpvg\Desktop\medical-scans` (45 JPG scans, 14 Oct 2026, no PDFs).
Inspected visually on 2026-10-22. No OCR has been run yet.

## Totals

| Kind | Images | Notes |
|---|---|---|
| Purchase invoices | 29 | 28 distinct business invoices (one captured twice), 16 suppliers |
| Ledger / account statements | 10 | 8 suppliers; 3 statements are multi-page |
| Handwritten cash receipts | 5 | Pre-printed receipt books, handwritten amounts |
| Handwritten delivery challan | 1 | Sri Ganapathi, matches an invoice of the same day |

Buyer on almost every document: **Parinitha Medicals, Bhimavaram**, GSTIN `37ARFPP9754N1ZT`, DL 1015.
Spelled six ways: PARINITHA, PARINEETHA, PARNEETHA, PARNEETA, PARINITHA MEDICALS-BHIMAVARAM-2, Parinitha Medicals.
Several addresses: Main Road, Undi Road, c/o Medicare Hospital, c/o Medinova, c/o Venu Ortho Care.

The shop has **no item codes of its own** printed anywhere. What exists are the codes **suppliers assign to the shop**:
PCODE 1012 (Health Care), A/C CODE 1093 (Sri Lakshmi Balaji), 000263 (Douglas), C691 (Sri Aditya),
B375 (Sri Murtyram), Code 000548 (Sri Nidhi).

## Layout families

The layouts fall into a few families that come from the supplier's billing software.

| Family | What it looks like | Suppliers in samples |
|---|---|---|
| A. Dot-matrix text invoice | "TAX INVOICE", dashed lines, monospace, fixed column order MFG / BATCH / HSN / PRODUCT / PACK / EXPDT / QTY / FREE / MRP / RATE / DISC / AMOUNT / TAX / CGST / SGST / TOTAL. Two sub-variants: with `|` separators and without. | Bhimeswara (2), Sri Lakshmi Balaji (2), Health Care Medical Agency (4), Gangadhar Sai (3) |
| B. Marg ERP grid invoice | Boxed grid, "GST INVOICE / CREDIT", GST class summary table, "Grand Total". Column order differs per supplier. | Balaji Medical Lines, Sri Balaji Medical Distributors, Sri Durga Pharma, Sri Aditya (3), Maharshi Infusions, Divya Sai Balaji, Lakshmi Gayatri Surgicals |
| C. Monospace "NET PAYABLE" invoice | Text layout, product line then totals block "SubTotal / Less Disc / Rounding". | Sri Murtyram, Sri Nidhi |
| D. Tally-style / custom | Proportional fonts; batch and expiry often on a **second line** under the product. | RSV Surgicals (3), Jyoti Enterprises, Sri Ganapathi (2) |

A template still belongs to one supplier and one document type, but a supplier template can start as a copy of its family's base layout.

## Per-file inventory

### Invoices

| File | Supplier | Invoice no / date | Rows | Observations |
|---|---|---|---|---|
| 1927-01 | Bhimeswara Medicals | 1023 / 20-03-2026 | 2 | Family A with pipes. Handwritten ticks over QTY/FREE. |
| 1927-03 | Sri Lakshmi Balaji | 1626 / 26-03-2026 | 1 | Family A, no pipes. Yellow paper. Handwritten "saved", "Received cash 1524". |
| 1927-04 | Divya Sai Balaji Med. Agencies | DSB03262 / 25-06-2025 | 1 | Marg "CREDIT INVOICE". **Right edge cropped**: amounts partly cut off. |
| 1927-06 | Balaji Medical Lines | MRV051734 / 17-02-2026 | 1 | Family B. Product name contains "SOLD MRP: 63.50". Line Amount is **before** discount; discount applied in footer. Handwritten "Paid". |
| 1927-07 | Sri Balaji Medical Distributors | RG03599 / 06-05-2025 | 1 | Family B. Product text spills into the batch column. **Summary table's TOTAL row is shifted one column** (source inconsistency). |
| 1927-08 | Health Care Medical Agency | 441 / 05-03-2026 | 1 | Family A with pipes. **Handwritten blue "30" inside the FREE column**; printed FREE blank. |
| 1927-10 | Sri Durga Pharma | RS16178 / 06-03-2026 | 1 | Family B variant (OLD MRP column, NET AMOUNT incl. GST). 10 + 10 free, "Total Qty 20". |
| 1927-13 | Sri Aditya Medicals | RG008197 / 23-06-2026 | 2 | Family B variant (Qty first, Discount column). |
| 1927-14 | Gangadhar Sai Medicals | 632 / 03-08-2026 | 2 | Family A, no pipes. **Fractional qty 14.5**. |
| 1927-15 | Health Care Medical Agency | 8 / 06-04-2026 | 1 | Same product, batch and amounts as #441 but a different invoice. Must **not** be called a duplicate. Invoice numbers restart in April. |
| 1927-16 | Sri Lakshmi Balaji | 511 / 09-07-2026 | 2 | MFG and FREE blank. Matches ledger line "SALES 511 599.00". |
| 1927-18 | Gangadhar Sai Medicals | 703 / 15-08-2026 | 2 | Pack printed "VAIL". |
| 1927-19 | Sri Aditya Medicals | RG013744 / 15-08-2026 | 1 | Slight skew. Marg advertising QR code (not a GST e-invoice QR). |
| 1927-20 | Health Care Medical Agency | 162 / 13-08-2026 | 1 | Handwritten "Same Inv no 162 30/8/26" across the table. |
| 1927-21 | Bhimeswara Medicals | 94 / 05-05-2026 | 1 | Long batch `DT2602064A` touches the HSN column with no gap. |
| 1927-22 | Lakshmi Gayatri Surgicals | A000272 / 21-07-2026 | 1 | **Very faint**: supplier name/GSTIN barely readable; right-side amounts faint. 40% discount + "BILL DISC AMT". Batch "0", no expiry. |
| 1927-23 | Health Care Medical Agency | 239 / 08-10-2026 | 1 | Date slightly faint. Pack "SINGL". |
| 1927-24 | Sri Ganapathi Med. Agencies | Gst-6521/26-27 / 29-09-2026 | 2 | Family D, portrait. Qty "2 Nos", **full expiry date** "31-5-2028", batch "1" (placeholder). Grouping commas "1,160.00". |
| 1927-27 | Sri Murtyram Medicals | KV10864 / 06-12-2025 | 1 | Family C. MRP printed **after** Amount. Handwritten partial-payment arithmetic "2468 − 1468 = 1000". |
| 1927-29 | RSV Surgicals & Medicals | Rsv/2627/MAY/46 / 7-May-26 | 1 | Tally. **Buyer is Venu Ortho Care Hospital, not the shop.** Batch on second line. 50% disc. |
| 1927-30 | RSV Surgicals & Medicals | Rsv/2627/MAY/52 / 8-May-26 | 1 | Buyer = Parinitha. **No batch, no expiry.** |
| 1927-31 | Sri Nidhi Medical & General | ME02167 / 27-06-2025 | 1 | Family C. **Skewed ~2°, paper curled**, bottom cropped. Header columns not aligned with values. |
| 1933-01 | Gangadhar Sai Medicals | 1680 / 17-02-2026 | 2 | **Left third faded** (MFG/batch hard to read). |
| 1933-04 | RSV Surgicals & Medicals | Rsv/2627/MAY/45 / 7-May-26 | 11 | **Buyer Venu Ortho Care Hospital.** 11 products, each with batch on following line; quantities repeated on second line; irregular blank lines. Batch "268437.25" looks like a number. |
| 1933-05 | Sri Aditya Medicals | RF028390 / 31-01-2026 | 1 | Expiry 5/26 (short expiry). |
| 1933-08 | Maharshi Infusions | A000790 / 21-05-2025 | 1 | Family B variant (COMP column). |
| 1933-09 | Sri Ganapathi Med. Agencies | Gst-6837/25-26 / 10-11-2025 | 4 | Landscape capture, **bottom cropped: Total and Grand Total missing.** |
| 1933-10 | Sri Ganapathi Med. Agencies | Gst-6837/25-26 / 10-11-2025 | 4 | **Same business invoice as 1933-09**, full capture. Total 806.00. Handwritten "VOCH 1234". |
| 1933-13 | Jyoti Enterprises | JE/25-26/7730 / 6-Sep-25 | 4 | Tally-like. Batch + expiry ("Jan-2030") on second line; qty repeated. GST 12%. |

### Ledger statements

| File | Supplier | Period | Observations |
|---|---|---|---|
| 1927-05 | Sri Lakshmi Balaji | 01-04-2025 – 30-06-2025 | Dot-matrix. Date / ACHNO (SALES/CASH) / RC-NO / Debit / Credit. No running balance. Handwritten ticks. |
| 1927-17 | Sri Lakshmi Balaji | **FROM blank** – 23-07-2026 | Same layout. Contains "SALES 511 599.00" = invoice 1927-16. Totals 312339.00 both sides. |
| 1927-09 | Douglas Pharmaceuticals | 01-04-2024 – 31-03-2025 | Running balance "Dr". Comment "NEFT:08/11/2025" on a 2025-01-09 row (source inconsistency). Stray printer characters. |
| 1933-02 | Venkata Srirama Med. Agencies | 01-04-2025 – 31-03-2026 | **Dates without year** ("Jul 19"). Amount rows staggered half a line from text rows. Receipts "Ag. A000536" allocate payments to bills. |
| 1933-03 | Sri Ganapathi | 1-Apr-25 – 31-Mar-26, **page 1 only** | Tally. "Carried Over" + "continued…": page 2 missing. Rows with no date (inherit previous). |
| 1933-06 | Sri Ganapathi | 1-Apr-2024 – 13-Feb-2025, **page 1 only** | Same supplier, older header (different DL/FSSAI). Date format "1-4-2024". |
| 1933-07 | Sri Aditya Medicals | 01-04-25 – 31-05-25 | Marg grid with Balance column. Receipt lines list allocated bills over 2–3 lines. |
| 1933-11 | Aswini Agencies | 01-04-2024 – 31-03-2025, page 1 | Dates without year; heavily staggered amounts; "Carried Over 44022.00 / 35000.00". |
| 1933-12 | Aswini Agencies | page 2 | **Rotated ~3°**, folded corner, page 1 visible underneath on the right edge. "Brought" forward row. |
| 1933-14 | Jyoti Enterprises | 1-Apr-24 – 31-Mar-25 | Tally; staggered; closing balance on credit side. |

### Receipts and challan (handwritten)

| File | Issuer | Content |
|---|---|---|
| 1927-02 | Bhimeswara Medical's | Cash receipt 2194, 24/3/2026, Rs 2479. Invoice 1023 (20-03-2026, net 3246) has a first line of 2479.05, so this may be a part payment. Telugu footer. |
| 1927-11 | Gangadhar Sai Medicals | Cash receipt 1892, 29/8/26, Rs 2000 |
| 1927-12 | Maharshi Infusions | Book 2, receipt 64, 20/8/26, Rs 1000 |
| 1927-26 | Sri Murtyram Medicals | Receipt 33, 28/?/26, Rs 1000 |
| 1927-28 | Sri Ganapathi | Receipt 58, 24/3/?, Rs 500 |
| 1927-25 | Sri Ganapathi | Delivery challan 100, 29/09/26: gauze + cotton. MRP 325 vs 347 on the matching invoice. |

## Findings that affect the design

1. **Line-amount meaning differs by supplier.** Family A: AMOUNT = qty × rate less discount, TOTAL includes GST.
   Balaji Medical Lines / Sri Murtyram: AMOUNT is before discount, discount appears only in the footer.
   Sri Durga: NET AMOUNT includes GST. Arithmetic rules must be per template.
2. **Invoice numbers restart each financial year** (Health Care #8 on 06-04-2026, Sri Lakshmi Balaji #15 in April).
   The duplicate key must be supplier GSTIN + invoice number + financial year, not invoice number alone.
3. **Free quantity is never included in the amount**, but some invoices add it into "Total Qty".
4. **Expiry formats:** `07/27`, `1/29`, `5/26`, `Jan-2030`, and full dates `31-5-2028`.
5. **Multi-line products** occur in Family D (RSV, Jyoti). Batch/expiry and a repeated quantity sit on the next line.
6. **Handwriting inside tables** ("Saved", "Paid", ticks, a blue "30" in a FREE column, signatures over rows).
   Almost all of it is blue ink while print is black/grey, so separating ink colour on the working copy is worth testing.
7. **Buyer is not always the shop** (two RSV invoices billed to Venu Ortho Care Hospital).
8. **Ledger dates sometimes lack a year**; it must come from the statement period.
9. **Ledger amounts are often printed half a line away from their text**. The running balance (when printed) is the best way to confirm which amount belongs to which row and whether it is a debit or credit.
10. **Missing continuation pages are real**: Sri Ganapathi ledgers (page 1 only, twice).
11. **Real duplicate capture exists**: 1933-09 and 1933-10. A near-duplicate that is *not* a duplicate also exists: Health Care #441 vs #8.
12. **Ledger ↔ invoice matches are visible in the samples**: SLB ledger "SALES 511 599.00" ↔ invoice 511 net 599.00; SLB ledger "CASH SL34 1524.00" ↔ invoice 1626 net 1524.00 (handwritten "Received cash 1524").
13. Only 6 suppliers have 2+ invoice samples. Most templates cannot be tested on unseen documents until more samples are collected.
