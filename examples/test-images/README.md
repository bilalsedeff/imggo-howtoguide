# Test Images

This directory contains test images for trying out ImgGo workflows and code examples.

## Directory Structure

```text
test-images/
├── invoice1.jpg              # Sample invoice for testing
├── invoice2.jpg
├── receipt1.jpg              # Sample receipt for expense management
├── shelf-audit1.jpg          # Retail shelf photo
├── parking1.jpg              # Parking camera / license plate
├── construction1.jpg         # Construction progress photo
├── construction2.jpg
├── document-classification1.png  # Document for classification
├── document-classification2.png
├── document-classification3.png
├── id-card1.jpg             # Sample ID card (anonymized)
├── medical-prescription1.jpg # Medical prescription sample
└── inventory1.jpg           # Warehouse inventory photo
```

## Usage in Code Examples

All code examples in this repository reference images from this directory:

### Python Examples
```python
test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "invoice1.jpg"
```

### curl Examples
```bash
TEST_IMAGE="../../test-images/invoice1.jpg"
```

### Node.js Examples
```typescript
const testImage = path.join(__dirname, '../../test-images/invoice1.jpg');
```

## Getting Test Images

### Option 1: Use Your Own Images

Simply add your own images to this directory. Recommended formats:
- Invoices: JPG, PNG, PDF
- Receipts: JPG, PNG
- ID cards: JPG, PNG (ensure PII is removed/anonymized)
- Construction photos: JPG
- Parking: JPG (from cameras)

### Option 2: Download Sample Images

For testing purposes, here are the expected test images:

**Required for examples to work**:
- `invoice1.jpg`, `invoice2.jpg` - Business invoices
- `receipt1.jpg` - Purchase receipt
- `document-classification1.png`, `document-classification2.png`, `document-classification3.png` - Various documents
- `parking1.jpg` - Vehicle with license plate
- `construction1.jpg`, `construction2.jpg` - Construction sites
- `shelf-audit1.jpg` - Retail shelf
- `inventory1.jpg` - Warehouse inventory
- `id-card1.jpg` - Sample ID (anonymized)
- `medical-prescription1.jpg` - Medical prescription (anonymized)

**Important**: Never use real documents with actual PII, financial data, or sensitive information for testing.

## Privacy & Security

⚠️ **Important Security Notes**:

1. **This directory is .gitignored** - Test images are never committed to version control
2. **Remove PII** - Strip all personally identifiable information before testing
3. **Anonymize sensitive data** - Replace real names, addresses, account numbers
4. **Use sample data** - Prefer generated/mock data over real documents
5. **HIPAA/GDPR compliance** - Never use real protected health information or personal data

## Image Requirements

For best results with ImgGo:

### Technical Requirements
- **Format**: JPG, PNG, PDF
- **Resolution**: Minimum 1024x768 pixels
- **File size**: Under 10MB (recommended under 5MB)
- **Quality**: Clear, well-lit, minimal blur
- **Orientation**: Correct orientation (not rotated)

### Content Requirements
- **Text legibility**: All text should be clearly readable
- **Full document**: Entire document should be visible
- **No obstruction**: No fingers, shadows, or objects blocking content
- **Good lighting**: Avoid glare, shadows, or underexposure

## Creating Your Own Test Images

### For Document Testing

1. Use online invoice/receipt generators
2. Create mockups in Canva or Figma
3. Use Google Docs with sample data
4. Take photos of non-sensitive documents

### For Retail/Shelf Audits

1. Visit a local store and photograph shelves (check store policy)
2. Use stock photos (ensure licensing)
3. Create product mockups

### For Medical/Healthcare

1. **Never use real patient data**
2. Use sample/demo data from healthcare systems
3. Create anonymized examples

## Adding New Test Images

To add new test images:

1. Save image to `test-images/` directory
2. Use descriptive filename: `{use-case}-{variant}.{ext}`
   - Example: `invoice-multi-page.pdf`
   - Example: `receipt-handwritten.jpg`
3. **Never commit real sensitive data**

## Resources

- [ImgGo Documentation](https://img-go.com/docs)
- [Pattern Creation Guide](https://img-go.com/patterns)
- [Image Guidelines](https://img-go.com/docs/image-guidelines)
