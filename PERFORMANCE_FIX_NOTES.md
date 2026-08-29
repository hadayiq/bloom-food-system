# Performance fix

This branch reduces repeated reads of `inventory.xlsx` by caching Products, Opening_Balance, Batches, and Transactions in memory and invalidating them when the workbook changes.

It also calculates the inventory summary from one transaction read instead of reopening the workbook once per product, avoids normal startup schema writes, and coalesces duplicate refresh notifications after internal writes.
