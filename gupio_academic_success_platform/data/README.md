# Dataset placement

Place the **panel-supplied Gupio `data.csv`** here with this exact filename:

```text
data/data.csv
```

The supplied brief states that the panel copy is semicolon-delimited. Do not replace it with a different dataset or modify data-row values. The training script only normalizes header whitespace/BOM and explicitly removes the 12 prohibited semester-performance columns from the primary enrollment-time model.

No assessment dataset is bundled in this zip because the project must use the panel-supplied file.
