# Intelligent Document Classification and Routing

## Overview

Automate document classification and intelligent routing by extracting document type, metadata, and routing rules from uploaded images. Convert scanned documents into **structured JSON** that triggers automated workflows for invoices, contracts, tax forms, and other business documents.

**Output Format**: JSON (flexible structure for workflow automation)
**Upload Method**: Direct Upload (from scanners, mobile apps, web portals)
**Industry**: Finance, Legal, Healthcare, Government, Shared Services

---

## The Problem

Organizations processing high volumes of documents face these challenges:

- **Manual Sorting**: Staff spend hours manually classifying and routing incoming documents
- **Misrouted Documents**: 15-20% of documents end up in wrong departments, causing delays
- **Data Entry Errors**: Manual data extraction from forms has 2-5% error rate
- **Slow Processing**: Documents sit in queues for days waiting for manual review
- **Compliance Risks**: Missing deadlines due to lost or misrouted documents
- **Audit Gaps**: No automated audit trail of document handling

Traditional document management requires manual review, OCR post-processing, and rule-based routing that breaks when document formats change.

---

## The Solution

ImgGo automatically classifies documents, extracts metadata, and outputs **structured JSON** that triggers intelligent routing workflows:

**Workflow**:
```
Scanner/Mobile Upload → ImgGo API (Direct Upload) → JSON Classification → Workflow Automation → Correct Department
```

**What Gets Extracted**:
- Document type and subtype
- Confidence score for classification
- Key metadata (dates, amounts, parties, IDs)
- Routing destination
- Priority level
- Compliance flags
- Retention period

---

## Why JSON Output?

JSON is ideal for document workflow automation:

- **Workflow Integration**: Direct mapping to automation platforms (Zapier, n8n, Power Automate)
- **API-Friendly**: Easy integration with modern web services and SaaS platforms
- **Conditional Logic**: Simple to implement routing rules based on extracted fields
- **Database Storage**: Direct insertion into NoSQL databases (MongoDB, DynamoDB)
- **Extensible**: Add custom fields without breaking existing integrations

**Example Output**:
```json
{
  "classification": {
    "document_type": "invoice",
    "document_subtype": "vendor_invoice",
    "confidence": 0.97,
    "alternative_types": [
      {"type": "purchase_order", "confidence": 0.65},
      {"type": "receipt", "confidence": 0.42}
    ]
  },

  "metadata": {
    "vendor": {
      "name": "Acme Office Supplies",
      "tax_id": "12-3456789",
      "vendor_id": "VND-00542"
    },
    "invoice_number": "INV-2025-001234",
    "invoice_date": "2025-01-15",
    "due_date": "2025-02-14",
    "total_amount": 1247.50,
    "currency": "USD",
    "payment_terms": "Net 30",
    "po_number": "PO-987654"
  },

  "routing": {
    "destination_department": "accounts_payable",
    "assigned_queue": "ap_invoices_high_priority",
    "priority": "high",
    "reason": "Amount > $1000 requires approval",
    "approvers": [
      {
        "role": "department_manager",
        "email": "ap.manager@company.com",
        "approval_limit": 5000
      },
      {
        "role": "director",
        "email": "finance.director@company.com",
        "required_if": "amount > 10000"
      }
    ]
  },

  "compliance": {
    "requires_three_way_match": true,
    "tax_deductible": true,
    "retention_period_years": 7,
    "sensitive_data": false,
    "flags": ["high_value", "foreign_vendor"]
  },

  "extracted_line_items": [
    {
      "description": "Premium Copy Paper - Case of 10",
      "quantity": 5,
      "unit_price": 45.00,
      "amount": 225.00,
      "gl_code": "5100-100"
    },
    {
      "description": "Toner Cartridges - HP LaserJet",
      "quantity": 12,
      "unit_price": 78.50,
      "amount": 942.00,
      "gl_code": "5100-105"
    }
  ],

  "processing_metadata": {
    "processed_at": "2025-01-22T14:30:45Z",
    "job_id": "job_abc123xyz",
    "image_url": "https://s3.amazonaws.com/docs/invoices/inv_2025_001234.pdf",
    "page_count": 2,
    "language": "en",
    "quality_score": 0.94
  }
}
```

---

## Implementation Guide

### Step 1: Create Classification Pattern

Define document types and routing rules:

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Financial Document Classifier",
  "output_format": "json",
  "schema": {
    "classification": {
      "document_type": "enum[invoice,receipt,purchase_order,contract,tax_form,bank_statement,check,credit_memo,other]",
      "document_subtype": "string",
      "confidence": "number",
      "alternative_types": [
        {
          "type": "string",
          "confidence": "number"
        }
      ]
    },
    "metadata": {
      "vendor": {
        "name": "string",
        "tax_id": "string",
        "vendor_id": "string"
      },
      "invoice_number": "string",
      "invoice_date": "date",
      "due_date": "date",
      "total_amount": "number",
      "currency": "string",
      "payment_terms": "string",
      "po_number": "string"
    },
    "routing": {
      "destination_department": "enum[accounts_payable,accounts_receivable,tax,legal,hr,procurement]",
      "assigned_queue": "string",
      "priority": "enum[low,medium,high,urgent]",
      "reason": "string"
    },
    "compliance": {
      "retention_period_years": "number",
      "sensitive_data": "boolean",
      "flags": ["string"]
    }
  }
}
```

### Step 2: Direct Upload Implementation (React)

Create a document upload portal with drag-and-drop:

```jsx
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const DocumentUploadPortal = () => {
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [processing, setProcessing] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    setProcessing(true);

    for (const file of acceptedFiles) {
      try {
        // Upload directly to ImgGo
        const classification = await classifyDocument(file);

        // Route based on classification
        await routeDocument(classification);

        setUploadedDocs(prev => [...prev, {
          filename: file.name,
          classification: classification.classification.document_type,
          destination: classification.routing.destination_department,
          status: 'routed'
        }]);

      } catch (error) {
        console.error(`Failed to process ${file.name}:`, error);
        setUploadedDocs(prev => [...prev, {
          filename: file.name,
          status: 'error',
          error: error.message
        }]);
      }
    }

    setProcessing(false);
  }, []);

  const classifyDocument = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(
      `https://img-go.com/api/patterns/${process.env.REACT_APP_IMGGO_PATTERN_ID}/ingest`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${process.env.REACT_APP_IMGGO_API_KEY}`,
          'Content-Type': 'multipart/form-data',
          'Idempotency-Key': `${file.name}-${Date.now()}`
        }
      }
    );

    const jobId = response.data.data.job_id;

    // Poll for results
    return await pollForResults(jobId);
  };

  const pollForResults = async (jobId, maxAttempts = 30) => {
    for (let i = 0; i < maxAttempts; i++) {
      const result = await axios.get(
        `https://img-go.com/api/jobs/${jobId}`,
        {
          headers: {
            'Authorization': `Bearer ${process.env.REACT_APP_IMGGO_API_KEY}`
          }
        }
      );

      if (result.data.data.status === 'completed') {
        return result.data.data.result;
      } else if (result.data.data.status === 'failed') {
        throw new Error(result.data.data.error);
      }

      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    throw new Error('Processing timeout');
  };

  const routeDocument = async (classification) => {
    // Send to routing service
    await axios.post('/api/route-document', {
      classification: classification,
      timestamp: new Date().toISOString()
    });
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf']
    },
    multiple: true
  });

  return (
    <div className="document-upload-portal">
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        {processing ? (
          <p>Processing documents...</p>
        ) : isDragActive ? (
          <p>Drop documents here to classify and route</p>
        ) : (
          <p>Drag & drop documents, or click to select</p>
        )}
      </div>

      <div className="upload-history">
        <h3>Recent Uploads</h3>
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Classification</th>
              <th>Routed To</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {uploadedDocs.map((doc, idx) => (
              <tr key={idx}>
                <td>{doc.filename}</td>
                <td>{doc.classification || '-'}</td>
                <td>{doc.destination || '-'}</td>
                <td className={`status-${doc.status}`}>{doc.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DocumentUploadPortal;
```

### Step 3: Backend Routing Service (Node.js)

Implement intelligent routing based on classification:

```javascript
const express = require('express');
const axios = require('axios');
const router = express.Router();

// Routing rules configuration
const ROUTING_RULES = {
  invoice: {
    default_queue: 'ap_invoices',
    priority_rules: [
      { condition: (doc) => doc.metadata.total_amount > 10000, priority: 'urgent', queue: 'ap_high_value' },
      { condition: (doc) => doc.metadata.total_amount > 1000, priority: 'high', queue: 'ap_invoices_high' },
      { condition: (doc) => doc.compliance.flags.includes('foreign_vendor'), priority: 'high', queue: 'ap_foreign' }
    ],
    approval_workflow: (doc) => {
      if (doc.metadata.total_amount < 1000) {
        return { approval_required: false };
      } else if (doc.metadata.total_amount < 5000) {
        return { approval_required: true, approver: 'ap_manager' };
      } else if (doc.metadata.total_amount < 25000) {
        return { approval_required: true, approver: 'finance_director' };
      } else {
        return { approval_required: true, approver: 'cfo', secondary_approver: 'ceo' };
      }
    }
  },

  contract: {
    default_queue: 'legal_review',
    priority_rules: [
      { condition: (doc) => doc.compliance.flags.includes('high_risk'), priority: 'urgent' },
      { condition: (doc) => doc.metadata.contract_value > 100000, priority: 'high' }
    ]
  },

  tax_form: {
    default_queue: 'tax_department',
    priority_rules: [
      { condition: (doc) => isDeadlineApproaching(doc.metadata.due_date), priority: 'urgent' }
    ]
  },

  receipt: {
    default_queue: 'expense_processing',
    priority_rules: [
      { condition: (doc) => doc.metadata.total_amount > 500, priority: 'high' }
    ]
  }
};

router.post('/route-document', async (req, res) => {
  try {
    const { classification } = req.body;

    const docType = classification.classification.document_type;
    const rules = ROUTING_RULES[docType] || { default_queue: 'manual_review' };

    // Determine priority and queue
    let priority = 'medium';
    let queue = rules.default_queue;

    if (rules.priority_rules) {
      for (const rule of rules.priority_rules) {
        if (rule.condition(classification)) {
          priority = rule.priority;
          if (rule.queue) queue = rule.queue;
          break;
        }
      }
    }

    // Check if approval required
    let approval = { approval_required: false };
    if (rules.approval_workflow) {
      approval = rules.approval_workflow(classification);
    }

    // Create workflow ticket
    const ticket = await createWorkflowTicket({
      document_type: docType,
      metadata: classification.metadata,
      queue: queue,
      priority: priority,
      approval: approval,
      image_url: classification.processing_metadata.image_url
    });

    // Send notifications
    await sendNotifications(ticket, approval);

    // Store in database
    await storeDocument({
      ticket_id: ticket.id,
      classification: classification,
      routing: {
        queue: queue,
        priority: priority,
        routed_at: new Date()
      }
    });

    res.json({
      success: true,
      ticket_id: ticket.id,
      queue: queue,
      priority: priority,
      approval_required: approval.approval_required
    });

  } catch (error) {
    console.error('Routing error:', error);
    res.status(500).json({ error: error.message });
  }
});

async function createWorkflowTicket(data) {
  // Create ticket in workflow system (e.g., ServiceNow, Jira)
  const response = await axios.post(
    'https://workflow.company.com/api/tickets',
    {
      type: data.document_type,
      queue: data.queue,
      priority: data.priority,
      metadata: data.metadata,
      approval_required: data.approval.approval_required,
      approver: data.approval.approver,
      attachments: [data.image_url]
    },
    {
      headers: { 'Authorization': `Bearer ${process.env.WORKFLOW_API_KEY}` }
    }
  );

  return response.data;
}

async function sendNotifications(ticket, approval) {
  // Email assigned queue
  await sendEmail({
    to: `${ticket.queue}@company.com`,
    subject: `New ${ticket.type} - ${ticket.priority} priority`,
    body: `Ticket ${ticket.id} has been assigned to your queue. Please review.`
  });

  // If approval required, notify approver
  if (approval.approval_required) {
    await sendEmail({
      to: getApproverEmail(approval.approver),
      subject: `Approval Required: ${ticket.type}`,
      body: `Please approve ticket ${ticket.id}. Approve here: https://workflow.company.com/approve/${ticket.id}`
    });
  }
}

function isDeadlineApproaching(dueDate, daysThreshold = 7) {
  const due = new Date(dueDate);
  const today = new Date();
  const diffDays = (due - today) / (1000 * 60 * 60 * 24);
  return diffDays <= daysThreshold && diffDays >= 0;
}

module.exports = router;
```

### Step 4: Three-Way Match Automation (for invoices)

Automatically match invoices with POs and receipts:

```javascript
const matchInvoiceToPO = async (invoiceClassification) => {
  const { po_number, vendor, total_amount, line_items } = invoiceClassification.metadata;

  // Retrieve PO from ERP
  const purchaseOrder = await fetchPurchaseOrder(po_number);

  if (!purchaseOrder) {
    return {
      match_status: 'no_po_found',
      action: 'route_to_manual_review',
      reason: `Purchase order ${po_number} not found in system`
    };
  }

  // Verify vendor matches
  if (purchaseOrder.vendor_id !== vendor.vendor_id) {
    return {
      match_status: 'vendor_mismatch',
      action: 'flag_for_review',
      reason: `Vendor mismatch: Expected ${purchaseOrder.vendor_id}, got ${vendor.vendor_id}`
    };
  }

  // Verify amounts within tolerance (±2%)
  const tolerance = purchaseOrder.total * 0.02;
  const amountDiff = Math.abs(total_amount - purchaseOrder.total);

  if (amountDiff > tolerance) {
    return {
      match_status: 'amount_mismatch',
      action: 'flag_for_review',
      reason: `Amount variance: $${amountDiff.toFixed(2)} (tolerance: $${tolerance.toFixed(2)})`
    };
  }

  // Line-level matching
  const lineMatches = await matchLineItems(line_items, purchaseOrder.line_items);

  if (lineMatches.unmatched.length > 0) {
    return {
      match_status: 'partial_match',
      action: 'flag_for_review',
      matched_lines: lineMatches.matched,
      unmatched_lines: lineMatches.unmatched
    };
  }

  // Perfect three-way match
  return {
    match_status: 'matched',
    action: 'auto_approve',
    po_number: po_number,
    match_confidence: 0.99
  };
};

// Example usage
router.post('/process-invoice', async (req, res) => {
  const { classification } = req.body;

  if (classification.classification.document_type === 'invoice') {
    const matchResult = await matchInvoiceToPO(classification);

    if (matchResult.match_status === 'matched') {
      // Auto-approve and send to payment
      await approveInvoice(classification.metadata.invoice_number);
      await schedulePayment(classification.metadata);

      res.json({ status: 'approved', payment_scheduled: true });
    } else {
      // Route to manual review
      await routeToManualReview(classification, matchResult);

      res.json({ status: 'requires_review', reason: matchResult.reason });
    }
  }
});
```

---

## Integration Examples

### SharePoint Integration

Route classified documents to SharePoint folders:

```javascript
const { SharePointAPI } = require('@pnp/sp');

async function uploadToSharePoint(classification) {
  const sp = SharePointAPI(process.env.SHAREPOINT_SITE_URL);

  // Determine folder based on document type
  const folderMap = {
    invoice: 'Shared Documents/Finance/Invoices',
    contract: 'Shared Documents/Legal/Contracts',
    tax_form: 'Shared Documents/Tax/Forms',
    receipt: 'Shared Documents/Finance/Receipts'
  };

  const folder = folderMap[classification.classification.document_type] || 'Shared Documents/Uncategorized';

  // Download document
  const docBuffer = await downloadDocument(classification.processing_metadata.image_url);

  // Upload to SharePoint
  await sp.web.getFolderByServerRelativeUrl(folder)
    .files.add(
      `${classification.metadata.invoice_number}.pdf`,
      docBuffer,
      true
    );

  // Set metadata
  const file = await sp.web.getFileByServerRelativeUrl(`${folder}/${classification.metadata.invoice_number}.pdf`);

  await file.listItemAllFields.update({
    DocumentType: classification.classification.document_type,
    VendorName: classification.metadata.vendor.name,
    Amount: classification.metadata.total_amount,
    InvoiceDate: classification.metadata.invoice_date,
    ProcessedDate: new Date().toISOString()
  });

  console.log(`Uploaded to SharePoint: ${folder}`);
}
```

### Salesforce Integration

Create Salesforce records from classified documents:

```javascript
const jsforce = require('jsforce');

async function createSalesforceRecord(classification) {
  const conn = new jsforce.Connection({
    loginUrl: 'https://login.salesforce.com'
  });

  await conn.login(process.env.SF_USERNAME, process.env.SF_PASSWORD + process.env.SF_TOKEN);

  if (classification.classification.document_type === 'invoice') {
    // Create Invoice record
    const invoice = await conn.sobject('Invoice__c').create({
      Name: classification.metadata.invoice_number,
      Vendor__c: classification.metadata.vendor.vendor_id,
      Amount__c: classification.metadata.total_amount,
      Invoice_Date__c: classification.metadata.invoice_date,
      Due_Date__c: classification.metadata.due_date,
      Status__c: 'Pending Approval',
      Document_URL__c: classification.processing_metadata.image_url
    });

    console.log(`Created Salesforce invoice: ${invoice.id}`);
  } else if (classification.classification.document_type === 'contract') {
    // Create Contract record
    const contract = await conn.sobject('Contract').create({
      AccountId: classification.metadata.customer_id,
      Status: 'In Review',
      ContractNumber: classification.metadata.contract_number,
      StartDate: classification.metadata.effective_date,
      ContractTerm: classification.metadata.term_months
    });

    console.log(`Created Salesforce contract: ${contract.id}`);
  }
}
```

---

## Performance Metrics

### Classification Accuracy

- **Overall Accuracy**: 96.5% for 9 document types
- **Invoice Detection**: 98.2% accuracy
- **Contract Detection**: 94.7% accuracy
- **Tax Form Detection**: 97.1% accuracy
- **False Positive Rate**: <3%

### Processing Speed

- **Average Classification Time**: 1.2 seconds
- **Throughput**: 3,000 documents/hour per API instance
- **Upload Time** (100KB scan): 200ms
- **End-to-End (upload → routed)**: 4.5 seconds average

### Business Impact

| Metric | Before Automation | With ImgGo | Improvement |
|--------|-------------------|------------|-------------|
| Routing time per doc | 5 minutes | 4.5 seconds | 98.5% |
| Misrouted documents | 18% | 2% | 89% reduction |
| Processing cost per doc | $2.50 | $0.12 | 95% |
| Staff time (1000 docs/day) | 83 hours | 2 hours | 98% |

**ROI Example** (Processing 1,000 docs/day):
- **Annual Cost**: $14,400 (API fees)
- **Annual Savings**: $621,000 (staff time at $30/hour)
- **ROI**: 4,213%

---

## Advanced Features

### Machine Learning Feedback Loop

Improve classification accuracy over time:

```javascript
const provideFeedback = async (jobId, correctClassification) => {
  // Send correction back to ImgGo to improve model
  await axios.post(
    `https://img-go.com/api/jobs/${jobId}/feedback`,
    {
      correct_classification: correctClassification,
      feedback_type: 'correction'
    },
    {
      headers: { 'Authorization': `Bearer ${IMGGO_API_KEY}` }
    }
  );

  console.log('Feedback submitted to improve accuracy');
};

// When user corrects classification in UI
router.post('/correct-classification', async (req, res) => {
  const { job_id, correct_type } = req.body;

  await provideFeedback(job_id, { document_type: correct_type });

  res.json({ success: true });
});
```

### Multi-Language Support

```javascript
const classificationPatterns = {
  'en': 'pat_english_docs',
  'es': 'pat_spanish_docs',
  'fr': 'pat_french_docs',
  'de': 'pat_german_docs'
};

const detectLanguageAndClassify = async (file) => {
  // Quick language detection pass
  const langDetectionResult = await detectDocumentLanguage(file);
  const language = langDetectionResult.language;

  // Use language-specific pattern
  const patternId = classificationPatterns[language] || classificationPatterns['en'];

  // Classify with appropriate pattern
  const result = await classifyWithPattern(file, patternId);

  return result;
};
```

### Compliance Audit Trail

```javascript
const createAuditLog = async (classification, routing) => {
  await db.collection('document_audit_log').insertOne({
    document_id: classification.metadata.invoice_number,
    timestamp: new Date(),
    classification: classification.classification.document_type,
    confidence: classification.classification.confidence,
    routed_to: routing.queue,
    priority: routing.priority,
    processed_by: 'imggo_automation',
    ip_address: req.ip,
    retention_period: classification.compliance.retention_period_years,
    compliance_flags: classification.compliance.flags
  });
};
```

---

## Best Practices

### Upload Optimization

- **File Size**: Compress images to <2MB for faster upload
- **Resolution**: 300 DPI minimum for good OCR accuracy
- **Format**: PDF preferred for multi-page documents, JPEG/PNG for single pages
- **Batch Uploads**: Group related documents (invoice + PO + receipt) in single transaction

### Classification Tuning

- **Training Data**: Provide 50+ examples per document type for initial training
- **Confidence Thresholds**: Set 85% minimum confidence for auto-routing, below that → manual review
- **Feedback Loop**: Correct misclassifications to improve model over time
- **Edge Cases**: Manually review documents with multiple possible classifications

### Routing Rules

- **Keep Simple**: Start with basic rules, add complexity as needed
- **Test Thoroughly**: Validate routing logic with test documents before production
- **Monitor Queues**: Alert if queues exceed capacity thresholds
- **Escalation**: Auto-escalate documents stuck in review >72 hours

### Security

- **Encryption**: Encrypt documents at rest and in transit (TLS 1.2+)
- **Access Control**: Implement role-based access to classified documents
- **Audit Logging**: Log all document access and routing decisions
- **Retention**: Auto-delete documents after retention period expires

---

## Troubleshooting

### Issue: Low Classification Confidence

**Solution**: Improve document quality (higher resolution scans), provide more training examples

### Issue: Incorrect Routing

**Solution**: Review routing rules logic, add test cases, use feedback loop to correct

### Issue: Upload Failures

**Solution**: Check file size (<10MB), validate format (PDF, JPEG, PNG only), verify API key

### Issue: Slow Processing

**Solution**: Implement async processing with webhooks instead of polling, batch uploads off-peak

---

## Related Use Cases

- [Invoice Processing](../invoice-processing) - Dedicated invoice AP automation
- [Expense Management](../expense-management) - Receipt classification and routing
- [Medical Prescription](../medical-prescription) - Healthcare document processing

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- Direct Upload Guide: [https://img-go.com/docs/direct-upload](https://img-go.com/docs/direct-upload)
- Classification Best Practices: [https://img-go.com/docs/classification](https://img-go.com/docs/classification)
- Integration Help: support@img-go.com
