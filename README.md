# JSON to CSV Studio 📊

> A lightning-fast, privacy-first, 100% browser-based JSON to CSV converter with recursive flattening, customizable array strategies, formula injection protection, live preview, and RFC 4180 compliance.

![JSON to CSV Studio UI Screenshot](https://raw.githubusercontent.com/placeholder/json-to-csv/main/screenshot.png)

---

## 🌟 Features

- **100% Client-Side & Private**: All parsing and CSV conversion occurs strictly in your browser using vanilla ES Modules and Web Workers. Zero telemetry, zero network calls, zero data leaks.
- **Deep Recursive Flattening**: Automatically flattens nested objects into path-based columns (e.g. `{"user": {"address": {"city": "Paris"}}}` becomes `user.address.city`) using configurable separators (`.`, `_`, `/`).
- **4 Powerful Array Strategies**:
  1. **Join**: Combines primitive elements into a single cell with a chosen delimiter (e.g. `apple; banana; cherry`).
  2. **Indexed Columns**: Flattens elements into distinct columns (e.g. `tags.0`, `tags.1`).
  3. **Explode Rows**: Replicates parent records per array item (Cartesian expansion for multiple arrays).
  4. **Raw JSON String**: Retains array values as intact JSON strings in one cell.
- **Top-Level Collection Detection**: If your JSON contains a root object wrapping arrays (e.g. `{"data": [...], "meta": {...}}`), the UI lets you select which array to extract.
- **RFC 4180 Escaping & Excel Ready**:
  - Automatically wraps cells containing commas, double quotes, and newlines in double quotes and doubles internal quotes (`""`).
  - Standard `\r\n` line endings.
  - Optional **UTF-8 Byte Order Mark (BOM)** toggle for seamless opening in Microsoft Excel.
- **Formula Injection Sanitization (CSV Injection Protection)**: Prefixes cell values starting with `=`, `+`, `-`, `@`, `\t`, or `\r` with an apostrophe (`'`) so spreadsheet software does not execute arbitrary formulas.
- **Number & Leading-Zero Protection**: Preserves leading zeros (`00123`) and scientific notations (`1E5`) from spreadsheet auto-formatting.
- **Interactive Column Manager**: Reorder columns with drag-and-drop, toggle specific columns on or off, and search column names in real-time.
- **Live 50-Row Preview & Stats Bar**: Instant feedback showing row count, exported columns, file size estimation, and skipped records.
- **Bonus Nice-to-Haves**:
  - Reverse converter: Convert CSV back into JSON arrays with a single click.
  - Settings preset manager: Save and load option configurations in `localStorage`.
  - Sleek Dark / Light theme toggle.
  - One-click sample loader for testing various data shapes.

---

## 🚀 Getting Started

### Option 1: Direct File (Zero Dependencies)
Simply open `index.html` directly in any modern browser:
```bash
# On Windows
start index.html

# Or open via browser
```

### Option 2: Local HTTP Server
Run the built-in npm server:
```bash
npm start
```
Then navigate to `http://localhost:3000` (or the port output by the server).

---

## 📖 Usage Walkthrough

1. **Step 1: Input JSON**
   - Click the **Upload File** tab to drag and drop or browse for a `.json` file.
   - Alternatively, use the **Paste JSON** tab to paste raw JSON text.
   - You can also click **Try an Example...** to test with pre-packaged data (Flat, Nested, Arrays, Mixed Keys, or Unicode).
   - If an error occurs, the validation banner highlights the exact **Line and Column** of the syntax error.
2. **Step 2: Configure Conversion**
   - Select your preferred CSV **Delimiter** (comma, semicolon, tab, pipe).
   - Choose a **Nested Separator** (`.`, `_`, `/`).
   - Select an **Array Strategy** (`join`, `index`, `explode`, or `json`).
   - Adjust the **Max Flatten Depth** (default 10) or define a custom **Missing Fill Value** (e.g. `N/A`).
   - Reorder or toggle columns in the **Column Selection & Order** section.
3. **Step 3: Preview & Export**
   - Inspect the live 50-row preview table.
   - Enter your desired filename (default `converted.csv`).
   - Click **Download CSV** to save the file or **Copy CSV** to copy the content to your clipboard.

---

## ⚙️ Options Reference

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **Delimiter** | `string` | `,` (Comma) | Cell separator character: comma `,`, semicolon `;`, tab `\t`, or pipe `\|`. |
| **Nested Separator** | `string` | `.` | String linking parent and child property names (e.g. `user.profile.name`). |
| **Array Strategy** | `string` | `join` | One of `join`, `index`, `explode`, or `json`. |
| **Array Joiner** | `string` | `; ` | Separator used between elements when Array Strategy is set to `join`. |
| **Max Flatten Depth** | `number` | `10` | Maximum nesting depth. Objects or arrays deeper than this threshold are serialized as JSON strings. |
| **Missing Fill Value** | `string` | `""` | Value inserted for absent object properties (e.g. `NULL` or `N/A`). |
| **File Encoding (BOM)**| `boolean`| `false` | Prepends UTF-8 Byte Order Mark (`\uFEFF`) so Excel detects UTF-8 correctly without corrupted accents. |
| **Include Header Row** | `boolean`| `true` | When unchecked, generates data rows only without the top column header row. |
| **Sanitize Formulas**  | `boolean`| `true` | Prevents CSV formula injection by prefixing dangerous cells (`=`, `+`, `-`, `@`) with `'`. |
| **Protect Leading Zeros**| `boolean`| `false` | Protects strings like `00123` or `1E5` from losing leading zeros in spreadsheet tools. |

---

## 🔄 Array Strategy Comparisons

Consider this input record:
```json
{
  "id": 1,
  "product": "Keyboard",
  "tags": ["gaming", "wireless"]
}
```

### 1. Strategy: `join` (Default)
Merges array primitives into a single cell using the `arrayJoiner` (e.g. `; `):
```csv
id,product,tags
1,Keyboard,gaming; wireless
```

### 2. Strategy: `index`
Generates indexed columns for each item:
```csv
id,product,tags.0,tags.1
1,Keyboard,gaming,wireless
```

### 3. Strategy: `explode`
Generates one row per array item, duplicating the scalar parent fields:
```csv
id,product,tags
1,Keyboard,gaming
1,Keyboard,wireless
```

### 4. Strategy: `json`
Retains the entire array as an intact JSON string in one cell:
```csv
id,product,tags
1,Keyboard,"[""gaming"",""wireless""]"
```

---

## 🧪 Running Tests

The test suite runs using Node's native test runner (`node:test`) with zero external test dependencies:

```bash
npm test
```

### Covered Test Areas:
- **`flattener.test.js`**: Deep nesting, custom separators, all 4 array strategies, Cartesian product explode, recursion depth limits, key collision deduplication (`_2`), and skipping non-object elements.
- **`headers.test.js`**: Union of all keys in first-seen appearance order, empty inputs, selection filtering, and reordering.
- **`csvWriter.test.js`**: RFC 4180 escaping (quotes, commas, newlines), delimiters, UTF-8 BOM, header toggling, fill values, formula injection protection, and leading-zero preservation.
- **`parser.test.js`**: Parsing valid arrays of objects and single objects, primitive rejection, and precise line and column location extraction on syntax errors.
- **`samples.test.js`**: End-to-end verification comparing sample JSON files against expected CSV fixtures.

---

## ⚠️ Known Limitations & Sensible Defaults

1. **Cartesian Product with Multiple Large Arrays**: When using the `explode` strategy on an object that has multiple large arrays (e.g. 100 tags and 100 categories), the rows expand exponentially ($100 \times 100 = 10,000$ rows). For datasets with multiple large arrays, the `join` or `json` strategy is recommended.
2. **Circular References**: Standard JSON cannot contain circular structures. If invalid circular JSON is supplied, `JSON.parse` will reject it cleanly.
3. **Web Worker on `file://` protocol**: Some browsers restrict Web Workers when opening HTML files directly from local filesystem paths (`file:///`). The application automatically detects this and falls back to fast synchronous main-thread processing so it works everywhere.

---

## 📄 License

MIT License. Free for personal and commercial use.
