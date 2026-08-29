# UI Kit Phase 2

Applied to the Add Transaction page as the reference implementation.

## Components
- Page title/subtitle hierarchy
- Transaction action card
- Modern primary/secondary buttons
- Product and batch combo fields
- Quantity field using QDoubleSpinBox
- Notes field
- KPI summary cards
- Recent-transactions table

## Styling approach
The page already uses semantic Qt object names (`page_title`, `page_subtitle`, `transaction_card`, `form_label`, `primary_button`, `secondary_button`, `kpi_card`, etc.). These are the UI Kit hooks used by the global stylesheet. Qt Style Sheets support object-name selectors, widget selectors, pseudo-states such as `:focus` and `:hover`, and subcontrols such as QComboBox drop-downs. This keeps the design system centralized rather than adding ad-hoc colors and borders in each page.

No inventory/business logic is changed by this phase.