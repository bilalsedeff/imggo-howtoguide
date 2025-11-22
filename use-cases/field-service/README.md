# Field Service Documentation and Work Order Automation

## Overview

Automate field service documentation by extracting equipment readings, maintenance notes, and service details from technician photos and converting them into **human-readable plain text reports**. Eliminate manual data entry and generate instant work order summaries.

**Output Format**: Plain Text (narrative reports for work orders and service tickets)
**Upload Method**: Direct Upload (from mobile devices at service locations)
**Industry**: HVAC, Electrical, Plumbing, Telecom, Equipment Maintenance, Facilities Management

---

## The Problem

Field service organizations face these documentation challenges:

- **Slow Report Writing**: Technicians spend 30-45 minutes after each job writing service reports
- **Incomplete Documentation**: 40% of work orders lack critical details due to rushed data entry
- **Billing Delays**: Incomplete documentation delays invoicing by 3-5 days
- **Knowledge Loss**: Equipment history scattered across handwritten notes and memory
- **Compliance Gaps**: Missing safety checks or maintenance steps create liability risks
- **Customer Communication**: Customers wait days for service reports and next-step recommendations

Traditional methods require technicians to manually type observations, measurements, and recommendations into work order systems after completing service calls.

---

## The Solution

ImgGo extracts equipment readings, service notes, and observations from photos taken on-site and outputs **structured plain text narratives** that integrate directly into work order systems:

**Workflow**:
```
Technician Photo (Mobile) → ImgGo API (Direct Upload) → Plain Text Report → Work Order System
```

**What Gets Extracted**:
- Equipment model and serial numbers
- Gauge readings and measurements
- Visible issues and anomalies
- Parts replaced or serviced
- Safety observations
- Technician recommendations
- Next maintenance due date

---

## Why Plain Text Output?

Plain text is ideal for field service documentation:

- **Universal Compatibility**: Every work order system accepts text-based notes
- **Human-Readable**: Customers and supervisors read narrative reports naturally
- **Email-Ready**: Send reports directly in email bodies without attachments
- **SMS-Friendly**: Text summaries fit in SMS updates to customers
- **No Formatting Issues**: Plain text works everywhere (mobile, desktop, printouts)
- **Search-Friendly**: Easy to search work order history for keywords

**Example Output** (HVAC Service Report):
```
SERVICE REPORT - HVAC Maintenance Call

Customer: Downtown Office Complex
Location: 123 Main Street, Building A, Roof
Service Date: January 22, 2025, 2:30 PM
Technician: John Smith, ID #TS-1247

EQUIPMENT INSPECTED:
- Carrier Model 50TCQ12A2A6-0A0A0
- Serial Number: 0418E12345
- 10-ton rooftop packaged unit, installed 2018
- Operating hours: 14,237 hours

READINGS AND MEASUREMENTS:
- Supply air temperature: 58°F
- Return air temperature: 72°F
- Temperature differential: 14°F (within normal range)
- Refrigerant pressure (high side): 285 PSI
- Refrigerant pressure (low side): 68 PSI
- Amp draw: 42.3 amps (rated 48 amps)
- Static pressure: 0.8 inches w.c.

OBSERVATIONS:
- Condenser coil moderately dirty, restricting airflow approximately 20%
- Evaporator coil clean, no visible algae growth
- Blower wheel clean, no debris accumulation
- Drain pan clear, drain line flowing freely
- All electrical connections tight, no signs of arcing
- Compressor sound normal, no unusual vibrations
- Belt tension acceptable, no cracking visible

ISSUES IDENTIFIED:
1. Condenser coil cleaning required due to dirt accumulation
2. Low refrigerant charge detected (subcooling 8°F, should be 10-12°F)
3. Economizer damper actuator slow to respond, may need replacement soon

ACTIONS TAKEN:
- Cleaned condenser coil using coil cleaner and pressure washer
- Added 1.5 lbs R-410A refrigerant to achieve proper subcooling
- Lubricated economizer damper linkage
- Replaced cabin air filter (16x25x4)
- Tightened all electrical terminals
- Verified all safety controls operational

PARTS USED:
- R-410A refrigerant: 1.5 lbs
- Air filter 16x25x4 MERV 11: 1 unit
- Coil cleaner: 1 bottle

POST-SERVICE READINGS:
- Subcooling: 11°F (corrected)
- System operating efficiently
- Temperature differential maintained at 14°F
- Amp draw: 43.1 amps (slight increase due to clean coil)

RECOMMENDATIONS:
- Replace economizer actuator within next 30 days to prevent failure (estimated cost $450)
- Schedule condenser coil cleaning quarterly due to high pollen area
- Consider installing coil protection spray to extend cleaning intervals
- Next routine maintenance due: April 22, 2025 (90 days)

SAFETY OBSERVATIONS:
- All electrical panels properly covered and labeled
- No refrigerant leaks detected
- Unit secured properly, no loose panels
- Roof access safe, no trip hazards

CUSTOMER COMMUNICATION:
Explained findings to facility manager Mr. Johnson. He approved economizer actuator replacement for next visit. Customer satisfied with service, system cooling properly.

Work Order Status: COMPLETED
Total Service Time: 2 hours 15 minutes
Follow-up Required: Yes - economizer actuator replacement scheduled
```

---

## Implementation Guide

### Step 1: Create Field Service Pattern

Define pattern to extract equipment details and generate narrative reports:

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Field Service Report Generator",
  "output_format": "text",
  "instructions": "Extract equipment details, readings, observations, and generate a comprehensive plain text service report in narrative format",
  "schema": {
    "report_type": "field_service",
    "extract": [
      "equipment_model_serial",
      "gauge_readings",
      "meter_readings",
      "visual_observations",
      "parts_replaced",
      "safety_issues",
      "recommendations"
    ],
    "format": "narrative_paragraphs"
  }
}
```

### Step 2: Mobile App Direct Upload (React Native)

Create mobile app for technicians to upload photos and generate instant reports:

```javascript
import React, { useState } from 'react';
import { View, Button, Image, Text, ScrollView, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';

const FieldServiceApp = () => {
  const [photos, setPhotos] = useState([]);
  const [serviceReport, setServiceReport] = useState('');
  const [loading, setLoading] = useState(false);

  const takePhoto = async () => {
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
      allowsEditing: false,
    });

    if (!result.cancelled) {
      setPhotos([...photos, result.uri]);
    }
  };

  const generateReport = async () => {
    setLoading(true);

    try {
      // Upload all photos and generate report
      const reports = [];

      for (const photoUri of photos) {
        const report = await uploadAndGenerateReport(photoUri);
        reports.push(report);
      }

      // Consolidate into single report
      const consolidatedReport = consolidateReports(reports);
      setServiceReport(consolidatedReport);

    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const uploadAndGenerateReport = async (photoUri) => {
    // Convert photo to blob
    const response = await fetch(photoUri);
    const blob = await response.blob();

    // Create form data
    const formData = new FormData();
    formData.append('file', {
      uri: photoUri,
      type: 'image/jpeg',
      name: `service_photo_${Date.now()}.jpg`,
    });

    // Upload directly to ImgGo
    const uploadResponse = await axios.post(
      `https://img-go.com/api/patterns/${process.env.IMGGO_PATTERN_ID}/ingest`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${process.env.IMGGO_API_KEY}`,
          'Content-Type': 'multipart/form-data',
          'Idempotency-Key': `service-${Date.now()}-${Math.random()}`,
        },
      }
    );

    const jobId = uploadResponse.data.data.job_id;

    // Poll for results
    const result = await pollForResults(jobId);

    return result;
  };

  const pollForResults = async (jobId) => {
    for (let i = 0; i < 30; i++) {
      const response = await axios.get(
        `https://img-go.com/api/jobs/${jobId}`,
        {
          headers: {
            'Authorization': `Bearer ${process.env.IMGGO_API_KEY}`,
          },
        }
      );

      if (response.data.data.status === 'completed') {
        return response.data.data.result;
      } else if (response.data.data.status === 'failed') {
        throw new Error(response.data.data.error);
      }

      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    throw new Error('Processing timeout');
  };

  const consolidateReports = (reports) => {
    // Combine multiple photo reports into single narrative
    return reports.join('\n\n---\n\n');
  };

  const sendReport = async () => {
    // Send report to work order system
    await axios.post(
      'https://work-orders.company.com/api/complete',
      {
        work_order_id: workOrderId,
        service_notes: serviceReport,
        completion_time: new Date().toISOString(),
        technician_id: technicianId,
      },
      {
        headers: {
          'Authorization': `Bearer ${workOrderToken}`,
        },
      }
    );

    alert('Report sent successfully!');
  };

  return (
    <ScrollView style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>
        Field Service Report
      </Text>

      <Button title="Take Photo" onPress={takePhoto} />

      <View style={{ marginTop: 20 }}>
        {photos.map((uri, idx) => (
          <Image
            key={idx}
            source={{ uri }}
            style={{ width: 100, height: 100, margin: 5 }}
          />
        ))}
      </View>

      {photos.length > 0 && (
        <Button
          title="Generate Report from Photos"
          onPress={generateReport}
          disabled={loading}
        />
      )}

      {loading && <ActivityIndicator size="large" style={{ marginTop: 20 }} />}

      {serviceReport && (
        <View style={{ marginTop: 20 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold' }}>Service Report:</Text>
          <Text style={{ marginTop: 10, fontFamily: 'monospace' }}>
            {serviceReport}
          </Text>

          <Button title="Send Report" onPress={sendReport} />
        </View>
      )}
    </ScrollView>
  );
};

export default FieldServiceApp;
```

### Step 3: Backend Work Order Integration

Integrate reports into work order management system:

```javascript
const express = require('express');
const axios = require('axios');
const nodemailer = require('nodemailer');
const router = express.Router();

router.post('/complete-work-order', async (req, res) => {
  try {
    const { work_order_id, service_report, technician_id, photos } = req.body;

    // Get work order details
    const workOrder = await getWorkOrder(work_order_id);

    // Update work order with service report
    await updateWorkOrder(work_order_id, {
      status: 'COMPLETED',
      completion_notes: service_report,
      completed_by: technician_id,
      completed_at: new Date(),
      attachments: photos,
    });

    // Generate invoice from service report
    const invoice = await generateInvoiceFromReport(service_report, workOrder);

    // Email report to customer
    await emailReportToCustomer(workOrder.customer_email, service_report, invoice);

    // Send SMS summary to customer
    await sendSMSSummary(workOrder.customer_phone, service_report);

    // Log to equipment history
    await logEquipmentHistory(workOrder.equipment_id, service_report);

    res.json({
      success: true,
      work_order_id: work_order_id,
      invoice_id: invoice.id,
    });

  } catch (error) {
    console.error('Error completing work order:', error);
    res.status(500).json({ error: error.message });
  }
});

async function generateInvoiceFromReport(serviceReport, workOrder) {
  // Extract parts and labor from plain text report
  const partsSection = extractSection(serviceReport, 'PARTS USED:');
  const serviceTime = extractServiceTime(serviceReport);

  // Calculate costs
  const partsCost = calculatePartsCost(partsSection);
  const laborCost = serviceTime * workOrder.labor_rate;

  // Create invoice
  const invoice = await createInvoice({
    customer_id: workOrder.customer_id,
    work_order_id: workOrder.id,
    line_items: [
      {
        description: 'Service Labor',
        quantity: serviceTime,
        rate: workOrder.labor_rate,
        amount: laborCost,
      },
      ...parsePartsLineItems(partsSection),
    ],
    subtotal: partsCost + laborCost,
    tax: (partsCost + laborCost) * 0.08,
    total: (partsCost + laborCost) * 1.08,
  });

  return invoice;
}

async function emailReportToCustomer(email, report, invoice) {
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: 587,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASSWORD,
    },
  });

  await transporter.sendMail({
    from: 'service@hvaccompany.com',
    to: email,
    subject: 'Service Report - HVAC Maintenance Completed',
    text: `
Dear Customer,

Your HVAC maintenance service has been completed. Please see the detailed service report below:

${report}

---

INVOICE SUMMARY
Total Due: $${invoice.total.toFixed(2)}
Due Date: ${invoice.due_date}

Pay online: https://billing.hvaccompany.com/pay/${invoice.id}

Thank you for your business!

HVAC Company Service Team
    `,
  });

  console.log(`Service report emailed to ${email}`);
}

async function sendSMSSummary(phone, report) {
  // Extract key points for SMS
  const issues = extractSection(report, 'ISSUES IDENTIFIED:');
  const recommendations = extractSection(report, 'RECOMMENDATIONS:');

  const smsText = `Your HVAC service is complete. ${
    issues ? 'Issues found: ' + summarizeIssues(issues) + '. ' : ''
  }${
    recommendations ? 'Recommendation: ' + summarizeRecommendations(recommendations) : 'System operating normally.'
  } Full report emailed.`;

  await sendSMS(phone, smsText);
}

function extractSection(report, sectionHeader) {
  const lines = report.split('\n');
  const startIdx = lines.findIndex(line => line.includes(sectionHeader));

  if (startIdx === -1) return null;

  const endIdx = lines.findIndex((line, idx) => idx > startIdx && line.match(/^[A-Z ]+:$/));

  return lines.slice(startIdx + 1, endIdx === -1 ? undefined : endIdx).join('\n');
}

module.exports = router;
```

### Step 4: Equipment History Logging

Automatically log service reports to equipment maintenance history:

```javascript
const mongoose = require('mongoose');

const EquipmentSchema = new mongoose.Schema({
  equipment_id: String,
  model: String,
  serial_number: String,
  installation_date: Date,
  service_history: [
    {
      service_date: Date,
      technician_id: String,
      service_type: String,
      service_report: String,
      parts_replaced: [String],
      next_service_due: Date,
    },
  ],
});

const Equipment = mongoose.model('Equipment', EquipmentSchema);

async function logEquipmentHistory(equipmentId, serviceReport) {
  // Parse service report
  const servicedDate = extractDate(serviceReport);
  const partsReplaced = extractParts(serviceReport);
  const nextServiceDue = extractNextServiceDate(serviceReport);

  // Update equipment record
  await Equipment.findOneAndUpdate(
    { equipment_id: equipmentId },
    {
      $push: {
        service_history: {
          service_date: servicedDate,
          service_report: serviceReport,
          parts_replaced: partsReplaced,
          next_service_due: nextServiceDue,
        },
      },
      $set: {
        last_service_date: servicedDate,
        next_service_due: nextServiceDue,
      },
    },
    { upsert: true }
  );

  console.log(`Equipment history updated for ${equipmentId}`);
}

// Generate equipment health score from service history
async function calculateEquipmentHealthScore(equipmentId) {
  const equipment = await Equipment.findOne({ equipment_id: equipmentId });

  if (!equipment || equipment.service_history.length === 0) {
    return { score: 50, status: 'UNKNOWN' };
  }

  const recentServices = equipment.service_history.slice(-5);

  // Analyze service reports for recurring issues
  const issueKeywords = ['leak', 'failure', 'broken', 'replace', 'malfunction'];
  let issueCount = 0;

  for (const service of recentServices) {
    const report = service.service_report.toLowerCase();
    issueCount += issueKeywords.filter(keyword => report.includes(keyword)).length;
  }

  // Calculate score (100 - penalty for issues)
  const score = Math.max(0, 100 - (issueCount * 10));

  let status;
  if (score >= 80) status = 'EXCELLENT';
  else if (score >= 60) status = 'GOOD';
  else if (score >= 40) status = 'FAIR';
  else status = 'POOR';

  return { score, status, recent_issues: issueCount };
}
```

---

## Integration Examples

### ServiceTitan Integration

```javascript
const axios = require('axios');

const SERVICETITAN_API_URL = 'https://api.servicetitan.io/v2';
const SERVICETITAN_TOKEN = process.env.SERVICETITAN_TOKEN;

async function completeJobInServiceTitan(jobId, serviceReport) {
  // Update job with completion notes
  await axios.patch(
    `${SERVICETITAN_API_URL}/jpm/v2/jobs/${jobId}`,
    {
      summary: extractSummary(serviceReport),
      completionNotes: serviceReport,
      status: 'Completed',
    },
    {
      headers: {
        'Authorization': `Bearer ${SERVICETITAN_TOKEN}`,
        'Content-Type': 'application/json',
      },
    }
  );

  // Create invoice from extracted parts
  const parts = extractParts(serviceReport);
  const laborTime = extractServiceTime(serviceReport);

  await axios.post(
    `${SERVICETITAN_API_URL}/accounting/v2/invoices`,
    {
      jobId: jobId,
      items: [
        { description: 'Service Labor', quantity: laborTime, price: 125 },
        ...parts.map(part => ({ description: part.name, quantity: part.quantity, price: part.price })),
      ],
    },
    {
      headers: { 'Authorization': `Bearer ${SERVICETITAN_TOKEN}` },
    }
  );
}
```

### Salesforce Field Service Integration

```javascript
const jsforce = require('jsforce');

async function updateSalesforceWorkOrder(workOrderId, serviceReport) {
  const conn = new jsforce.Connection({ loginUrl: 'https://login.salesforce.com' });
  await conn.login(process.env.SF_USERNAME, process.env.SF_PASSWORD);

  // Update WorkOrder
  await conn.sobject('WorkOrder').update({
    Id: workOrderId,
    Status: 'Completed',
    Description: serviceReport,
    ActualDuration: extractServiceTime(serviceReport),
  });

  // Create WorkOrderLineItems for parts used
  const parts = extractParts(serviceReport);

  for (const part of parts) {
    await conn.sobject('WorkOrderLineItem').create({
      WorkOrderId: workOrderId,
      Description: part.name,
      Quantity: part.quantity,
      UnitPrice: part.price,
    });
  }

  console.log(`Salesforce WorkOrder ${workOrderId} updated`);
}
```

---

## Performance Metrics

### Time Savings

| Task | Manual Process | With ImgGo | Savings |
|------|----------------|------------|---------|
| Write service report | 35 minutes | 2 minutes | 94% |
| Create invoice | 15 minutes | Automated | 100% |
| Email customer | 10 minutes | Automated | 100% |
| Log equipment history | 8 minutes | Automated | 100% |
| **Total per job** | **68 minutes** | **2 minutes** | **97%** |

**For 20 jobs/day**: 22 hours saved daily per technician

### Business Impact

**Service company with 10 technicians** (200 jobs/day):

- **Labor Savings**: $550,000/year (220 admin hours/day × $12.50/hour × 200 days)
- **Faster Invoicing**: $180,000/year (improved cash flow from same-day invoicing)
- **Customer Satisfaction**: +18% (instant reports improve NPS scores)
- **Billable Hours**: +15% (technicians spend more time on service, less on paperwork)
- **Total Annual Benefit**: $730,000
- **ImgGo Cost**: $24,000/year
- **ROI**: 2,942%

---

## Advanced Features

### Voice Dictation Integration

```javascript
import Voice from '@react-native-voice/voice';

const dictateNotes = async () => {
  try {
    await Voice.start('en-US');

    Voice.onSpeechResults = (e) => {
      const spokenText = e.value[0];

      // Append to service notes
      setTechnicianNotes(prev => prev + '\n\n' + spokenText);
    };

  } catch (error) {
    console.error('Voice error:', error);
  }
};

// Combine dictated notes with photo-extracted data
const generateFinalReport = async () => {
  const photoReport = await uploadAndGenerateReport(photoUri);
  const finalReport = `${photoReport}\n\nTECHNICIAN NOTES:\n${technicianNotes}`;

  return finalReport;
};
```

### Predictive Maintenance Alerts

```javascript
const analyzeTrends = async (equipmentId) => {
  const equipment = await Equipment.findOne({ equipment_id: equipmentId });
  const history = equipment.service_history;

  // Detect if issues are escalating
  const recentIssues = history.slice(-3).map(s =>
    countIssues(s.service_report)
  );

  if (recentIssues[2] > recentIssues[1] && recentIssues[1] > recentIssues[0]) {
    // Issues increasing over last 3 visits
    await sendPredictiveAlert(equipmentId, 'Escalating issues detected. Recommend equipment replacement evaluation.');
  }

  // Detect if parts replaced repeatedly
  const partFrequency = {};
  history.forEach(service => {
    service.parts_replaced.forEach(part => {
      partFrequency[part] = (partFrequency[part] || 0) + 1;
    });
  });

  const repeatedParts = Object.entries(partFrequency)
    .filter(([part, count]) => count >= 3);

  if (repeatedParts.length > 0) {
    await sendPredictiveAlert(equipmentId,
      `Parts replaced frequently: ${repeatedParts.map(([part]) => part).join(', ')}. May indicate underlying issue.`
    );
  }
};
```

---

## Best Practices

### Photo Guidelines

- **Multiple Angles**: Take 3-5 photos per equipment (overall, nameplates, gauges, issues)
- **Focus on Text**: Ensure model numbers and gauge readings are legible
- **Lighting**: Use phone flashlight for dark mechanical rooms
- **Close-ups**: Capture gauge readings and serial numbers up close

### Report Quality

- **Review Before Sending**: Quickly scan generated report for accuracy
- **Add Context**: Use voice dictation to add technician observations
- **Be Specific**: Supplement photo reports with exact measurements when critical

### Data Management

- **Backup Photos**: Keep original photos for 90 days in case of disputes
- **Privacy**: Blur customer information in photos before archiving
- **Archive Reports**: Store service reports for 7 years for warranty/liability

---

## Troubleshooting

### Issue: Gauge Readings Not Extracted

**Solution**: Take close-up photo of gauge, ensure good lighting, avoid glare

### Issue: Model Number Incorrect

**Solution**: Clean nameplates before photos, take multiple angles, manually verify

### Issue: Report Too Generic

**Solution**: Use voice dictation to add specific observations, combine multiple photos

---

## Related Use Cases

- [Medical Prescription](../medical-prescription) - Plain text extraction from healthcare images
- [Construction Progress](../construction-progress) - Job site documentation
- [Quality Control](../quality-control) - Equipment inspection reports

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- Plain Text Guide: [https://img-go.com/docs/output-formats#text](https://img-go.com/docs/output-formats#text)
- Integration Help: support@img-go.com
