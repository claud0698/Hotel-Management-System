# Future Features & Roadmap
## Kos Management Dashboard

---

## Phase 2: Dashboard Report Export (HIGH PRIORITY)

### Overview
Post v1.0 launch feature that adds comprehensive report export functionality. Users can export financial data and reports in multiple formats (PDF, Excel, CSV) for custom time periods.

### Timeline: 1-2 weeks after v1.0 stable

### Business Value
- Enables users to share financial reports with accountants
- Allows automated monthly/quarterly reporting
- Supports compliance and audit requirements
- Increases data utility and portability

---

## Phase 2 Feature Details

### 1. **Dashboard Report Export** (High Priority)

**What Users Can Do**:
- Generate financial reports for any date range
- Choose report period: Monthly, Quarterly, Yearly, or Custom dates
- Select report sections to include:
  - Income Summary (paid rent, collection rate)
  - Expense Breakdown (by category)
  - Occupancy Metrics (occupancy rate, trends)
  - Payment Status (pending, paid, overdue)
  - Financial Summary (net profit/loss)
- Choose export format:
  - **PDF**: Professional formatted report (for printing, sharing)
  - **Excel**: Multi-sheet workbook with formulas (for analysis)
  - **CSV**: Raw data (for accounting software import)
- Preview report before downloading
- Download reports on demand
- Re-download previously generated reports

**UI Components**:
```
Dashboard → "Export Report" button → Modal
├── Date Range Selector
│   ├── This Month (default)
│   ├── Last Month
│   ├── Last 3 Months
│   ├── Last 6 Months
│   ├── Last 12 Months
│   └── Custom (date picker)
├── Report Type Selector
│   ├── Financial Summary (key metrics only)
│   ├── Detailed Report (all sections)
│   └── Data Export (raw CSV)
├── Format Selector
│   ├── PDF ✓
│   ├── Excel ✓
│   └── CSV ✓
├── Sections Selector (checkboxes)
│   ├── Income ☑
│   ├── Expenses ☑
│   ├── Occupancy ☑
│   ├── Payments ☑
│   └── Summary ☑
└── Action Buttons
    ├── Preview
    ├── Export (Download)
    └── Cancel
```

**Example Reports Generated**:

**PDF Report Example**:
```
═══════════════════════════════════════════════════════════
         FINANCIAL REPORT - KOS ABC MANAGEMENT
═══════════════════════════════════════════════════════════

Period: January 1, 2025 - December 31, 2025
Generated: October 24, 2025

───────────────────────────────────────────────────────────
EXECUTIVE SUMMARY
───────────────────────────────────────────────────────────
Total Income (Rent):        IDR 18,000,000
Total Expenses:             IDR  2,400,000
Net Profit:                 IDR 15,600,000
Profit Margin:              86.7%
Average Occupancy Rate:     82.5%

───────────────────────────────────────────────────────────
INCOME REPORT
───────────────────────────────────────────────────────────
Paid Rent:                  IDR 18,000,000
Pending Payments:           IDR    300,000
Overdue Payments:           IDR    600,000
Collection Rate:            95.5%

Monthly Breakdown:
January   : IDR 1,500,000
February  : IDR 1,500,000
...
December  : IDR 1,500,000

───────────────────────────────────────────────────────────
EXPENSE REPORT
───────────────────────────────────────────────────────────
Total Expenses:             IDR 2,400,000

By Category:
  Maintenance:              IDR   800,000 (33%)
  Utilities:                IDR   900,000 (38%)
  Supplies:                 IDR   300,000 (13%)
  Cleaning:                 IDR   400,000 (16%)

Monthly Breakdown:
[Table with monthly expense totals]

───────────────────────────────────────────────────────────
OCCUPANCY REPORT
───────────────────────────────────────────────────────────
Total Rooms:                10
Average Occupied:           8.25
Average Occupancy Rate:     82.5%

Room Status Breakdown:
  Occupied:                 8 rooms (80%)
  Available:                2 rooms (20%)
  Maintenance:              0 rooms (0%)

Occupancy Trend:
[Line chart: Jan-Dec occupancy rates]

═══════════════════════════════════════════════════════════
Page 1 of 2 | Report generated on October 24, 2025
═══════════════════════════════════════════════════════════
```

**Excel Report Example**:
```
Sheet 1: Summary
├── Key Metrics (total income, expenses, net profit, occupancy rate)
├── Monthly Breakdown (with formulas for totals)
└── Comparison to previous period

Sheet 2: Income Details
├── Payment ID | Tenant | Amount | Due Date | Paid Date | Status

Sheet 3: Expenses
├── Date | Category | Amount | Description

Sheet 4: Occupancy
├── Room | Tenant | Move-in | Move-out | Occupancy Days

Sheet 5: Monthly Summary
├── Month | Income | Expenses | Net Profit | Occupancy %
```

**CSV Report Example**:
```
payments_2025.csv:
payment_id,tenant_name,tenant_id,amount,due_date,paid_date,status,payment_method
1,Ahmad Malik,5,1500000,2025-01-01,2025-01-05,paid,transfer
2,Siti Nurhaliza,6,1500000,2025-01-01,2025-01-15,paid,cash
...

expenses_2025.csv:
expense_id,date,category,amount,description
1,2025-01-10,maintenance,500000,Fixed AC in room 101
2,2025-01-15,utilities,200000,Electricity bill
...
```

### 2. **Report Scheduling** (Optional)

**What Users Can Do**:
- Set automatic report generation schedule
- Options: Monthly (specific day), Quarterly, Yearly
- Reports automatically emailed to user
- Customize which sections to include
- Select preferred format

**UI**:
```
Dashboard → Settings → Report Scheduling

Schedule Monthly Report
├── Enabled: ☑
├── Day of Month: [1 ▼] (dropdown: 1-31)
├── Format: [PDF ▼]
├── Sections:
│   ├── Income ☑
│   ├── Expenses ☑
│   ├── Occupancy ☑
│   └── Summary ☑
└── Email to: [claudio@example.com]

Next Report: November 1, 2025
```

### 3. **Report Customization** (Optional)

**What Users Can Do**:
- Add property logo to reports
- Set custom report title
- Choose color theme (Professional, Simple, Colorful)
- Add custom footer text
- Choose which metrics to display

**UI**:
```
Settings → Report Customization

Property Logo:
├── Upload Logo: [Choose File]
└── [Preview of logo]

Report Title:
├── Custom Title: [KOS ABC MANAGEMENT ▼]

Color Theme:
├── ◉ Professional (Blue & White)
├── ○ Simple (Black & White)
└── ○ Colorful (Multi-color)

Footer Text:
└── [Custom footer text...]

Preview: [Show preview of formatted report]
```

### 4. **Export History** (Optional)

**What Users Can Do**:
- View list of previously generated reports
- Re-download reports without regenerating
- Delete old reports to save space
- Search/filter by date range or format

**UI**:
```
Dashboard → Reports → History

Recent Exports:
┌────┬───────────────────────┬──────────┬────────────┬──────────┐
│ #  │ Report                │ Format   │ Generated  │ Action   │
├────┼───────────────────────┼──────────┼────────────┼──────────┤
│ 1  │ Jan-Dec 2025 Summary  │ PDF      │ Oct 24     │ ↓ Delete │
│ 2  │ Q4 2025 Detailed      │ Excel    │ Oct 15     │ ↓ Delete │
│ 3  │ September 2025        │ CSV      │ Oct 10     │ ↓ Delete │
└────┴───────────────────────┴──────────┴────────────┴──────────┘
```

---

## Implementation Priorities

### Minimum Viable (MVP) for Phase 2:
1. PDF export with income, expenses, and summary
2. Excel export with basic sheets
3. CSV export for data
4. Date range selection (month, year, custom)
5. Export button on dashboard

### Nice-to-Have:
6. CSV export
7. Report preview
8. Export history tracking
9. Report scheduling (automated)
10. Report customization (logo, title)
11. Email delivery of reports

---

## Technical Implementation

### Backend Requirements:
- `GET /api/reports/financial` - Generate financial report
- `GET /api/reports/export/pdf` - PDF export
- `GET /api/reports/export/excel` - Excel export
- `GET /api/reports/export/csv` - CSV export
- `POST /api/reports/schedule` - Schedule reports
- `GET /api/reports/history` - Get export history

### Frontend Requirements:
- `ExportReportModal.tsx` - Export UI component
- `ReportPreview.tsx` - Preview component
- `DateRangeSelector.tsx` - Date picker
- `SectionSelector.tsx` - Report sections selector
- `FormatSelector.tsx` - Format chooser
- `ReportHistory.tsx` - History list

### Libraries Needed:
- **PDF**: ReportLab or Python PDF Kit
- **Excel**: openpyxl or xlsxwriter
- **CSV**: Python csv module (built-in)
- **Email**: SendGrid or AWS SES (optional)
- **Scheduling**: APScheduler (optional)

---

## Other Future Features (Phase 3+)

### High Priority Features
1. **Multi-user Support with Roles**
   - Admin (full access)
   - Accountant (view reports only)
   - Manager (can manage tenants/rooms but not expenses)

2. **Payment Reminders**
   - SMS reminders before payment due date
   - Email reminders for overdue payments

3. **Payment Gateway Integration**
   - Midtrans (popular in Indonesia)
   - Xendit
   - Automatic payment processing

4. **Mobile App**
   - Quick occupancy check
   - Record payments on the go
   - Receive notifications

### Medium Priority Features
5. **Utility Bill Tracking**
   - Track electricity, water per room
   - Auto-calculate costs
   - Include in tenant reports

6. **Lease Contract Management**
   - Store lease terms
   - Auto-renewal reminders
   - Contract expiration alerts

7. **Maintenance Request System**
   - Tenants submit maintenance requests
   - Track resolution
   - Schedule maintenance

8. **Tenant Applications**
   - Tenant screening
   - Background checks
   - Application workflow

### Lower Priority Features
9. **Advanced Analytics**
   - Custom reports builder
   - Data visualization improvements
   - Predictive analytics (revenue forecasting)

10. **Integrations**
    - Accounting software (Xero, SAP)
    - Payment gateways
    - CRM systems

11. **Multi-property Management**
    - Manage multiple Kos properties
    - Consolidated reporting
    - Per-property analytics

---

## Estimated Effort & Timeline

| Phase | Feature | Effort | Timeline |
|-------|---------|--------|----------|
| 2 | Dashboard Export (MVP) | 12-15h | 3-4 days |
| 2 | Report Scheduling | 6-8h | 2 days |
| 2 | Report Customization | 4-5h | 1 day |
| 3 | Multi-user Support | 20-30h | 1 week |
| 3 | Payment Reminders | 12-16h | 3-4 days |
| 3 | Mobile App | 40-60h | 2 weeks |

---

## Success Metrics for Phase 2

- [ ] Users can export reports in all 3 formats (PDF, Excel, CSV)
- [ ] Reports are accurate with correct calculations
- [ ] Users can customize date ranges
- [ ] Exports contain all requested sections
- [ ] PDF formatting is professional
- [ ] Excel files contain formulas and proper formatting
- [ ] CSV files are compatible with accounting software
- [ ] Report generation performs well even with large datasets
- [ ] Users can re-download previously exported reports (if history enabled)
- [ ] (Optional) Scheduled reports email to users automatically

---

## Questions for Product Owner

1. **Priority of Export Feature**: Is this genuinely needed immediately after v1.0 or can it wait?
2. **Report Scheduling**: Do you need automatic monthly reports or is manual export sufficient?
3. **Accounting Integration**: Do you use any specific accounting software (SAP, Xero, IQBAL) that needs special format?
4. **Report Customization**: Do you want to customize reports with your logo/brand?
5. **Email Delivery**: Is automatic emailing of reports a must-have or nice-to-have?
6. **Export History**: Should we keep all exported reports on server for re-download?

---

**Document Version**: 1.0
**Last Updated**: October 24, 2025
**Status**: Planned for Phase 2

