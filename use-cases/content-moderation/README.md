# Content Moderation and Safety Detection

## Overview

Automate content moderation by detecting inappropriate, harmful, or policy-violating content in user-generated images. Extract safety signals, policy violations, and content classifications into **structured JSON** for automated moderation workflows and human review queues.

**Output Format**: JSON (structured moderation decisions for platform safety systems)
**Upload Method**: Direct Upload (from user submissions, mobile apps, web forms)
**Industry**: Social Media, Online Marketplaces, Dating Apps, Gaming Platforms, Community Forums

---

## The Problem

Platforms hosting user-generated content face critical moderation challenges:

- **Volume Overwhelming**: Millions of images uploaded daily, impossible to manually review all
- **Response Time**: Policy violations need detection within seconds, not hours
- **Consistency**: Human moderators have 30% disagreement rate on borderline content
- **Moderator Wellbeing**: Exposure to disturbing content causes high turnover and trauma
- **Legal Liability**: Failure to remove illegal content exposes platforms to lawsuits
- **False Positives**: Overly aggressive moderation alienates legitimate users

Manual moderation can't scale. Platforms need automated first-pass filtering that routes only flagged content for human review.

---

## The Solution

ImgGo analyzes uploaded images in real-time, detecting policy violations, inappropriate content, and safety risks. Outputs **structured JSON** with confidence scores for automated actions or human review routing:

**Workflow**:
```
User Upload (Direct) → ImgGo API → JSON Classification → Auto-Approve / Review Queue / Auto-Reject
```

**What Gets Detected**:
- Adult/NSFW content
- Violence and gore
- Hate symbols and extremism
- Drugs and weapons
- Self-harm content
- Spam and fake profiles
- Copyright/trademark violations
- Minor safety risks

---

## Why JSON Output?

JSON enables sophisticated moderation workflows:

- **Conditional Routing**: Different actions based on violation type and confidence
- **Audit Trails**: Store moderation decisions with reasoning for appeals
- **A/B Testing**: Experiment with different confidence thresholds
- **Multi-Signal**: Combine with text, metadata, and user history for context
- **API Integration**: Direct integration with content management systems

**Example Output**:
```json
{
  "moderation_id": "mod_2025_abc123xyz",
  "image_id": "img_user_upload_456",
  "analyzed_at": "2025-01-22T14:30:45Z",
  "processing_time_ms": 847,

  "overall_decision": {
    "action": "review_required",
    "confidence": 0.76,
    "reason": "Potential policy violation detected: adult_content",
    "severity": "medium",
    "auto_action_taken": false
  },

  "policy_violations": [
    {
      "policy_id": "adult_content",
      "policy_name": "Adult/NSFW Content",
      "detected": true,
      "confidence": 0.76,
      "severity": "medium",
      "specific_violations": [
        {
          "type": "partial_nudity",
          "confidence": 0.82,
          "location": {
            "bounding_box": {
              "x": 120,
              "y": 340,
              "width": 200,
              "height": 180
            }
          }
        },
        {
          "type": "suggestive_content",
          "confidence": 0.71,
          "location": null
        }
      ],
      "recommended_action": "review_required"
    },
    {
      "policy_id": "violence",
      "policy_name": "Violence and Gore",
      "detected": false,
      "confidence": 0.03
    },
    {
      "policy_id": "hate_symbols",
      "policy_name": "Hate Speech and Extremism",
      "detected": false,
      "confidence": 0.01
    }
  ],

  "safety_signals": {
    "minor_present": {
      "detected": false,
      "confidence": 0.12
    },
    "self_harm_indicators": {
      "detected": false,
      "confidence": 0.05
    },
    "weapons": {
      "detected": false,
      "confidence": 0.08
    },
    "drugs": {
      "detected": false,
      "confidence": 0.11
    }
  },

  "content_classification": {
    "primary_category": "people_photos",
    "subcategories": ["portrait", "social_media"],
    "image_quality": {
      "resolution": "1920x1080",
      "format": "JPEG",
      "file_size_kb": 1247,
      "blur_score": 0.12,
      "is_screenshot": false,
      "is_meme": false
    }
  },

  "context_signals": {
    "celebrity_match": {
      "detected": false,
      "matches": []
    },
    "brand_logo_detected": false,
    "text_overlay": {
      "detected": true,
      "text_content": "Birthday celebration 2025",
      "language": "en",
      "is_spam": false
    },
    "location_identified": {
      "landmark": null,
      "indoor_outdoor": "indoor"
    }
  },

  "similar_content": {
    "duplicate_detected": false,
    "similar_rejected_content": {
      "found": false,
      "similarity_score": null
    }
  },

  "recommended_routing": {
    "queue": "medium_priority_review",
    "priority_score": 65,
    "estimated_review_time_minutes": 2,
    "requires_specialist": false,
    "specialist_type": null
  },

  "user_context": {
    "user_id": "user_789",
    "account_age_days": 42,
    "previous_violations": 0,
    "trust_score": 0.85,
    "upload_frequency": "moderate"
  },

  "appeals": {
    "appealable": true,
    "appeal_window_hours": 48,
    "automated_decision": false
  }
}
```

---

## Implementation Guide

### Step 1: Create Content Moderation Pattern

Define comprehensive safety and policy detection:

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Content Moderation - Platform Safety",
  "output_format": "json",
  "schema": {
    "overall_decision": {
      "action": "enum[approved,review_required,rejected,blocked]",
      "confidence": "number",
      "reason": "string",
      "severity": "enum[low,medium,high,critical]"
    },
    "policy_violations": [
      {
        "policy_id": "string",
        "policy_name": "string",
        "detected": "boolean",
        "confidence": "number",
        "severity": "enum[low,medium,high,critical]",
        "specific_violations": [
          {
            "type": "string",
            "confidence": "number",
            "location": {
              "bounding_box": {
                "x": "number",
                "y": "number",
                "width": "number",
                "height": "number"
              }
            }
          }
        ],
        "recommended_action": "enum[approve,review,reject,block_user]"
      }
    ],
    "safety_signals": {
      "minor_present": {
        "detected": "boolean",
        "confidence": "number"
      },
      "self_harm_indicators": {
        "detected": "boolean",
        "confidence": "number"
      },
      "weapons": {
        "detected": "boolean",
        "confidence": "number"
      },
      "drugs": {
        "detected": "boolean",
        "confidence": "number"
      }
    },
    "content_classification": {
      "primary_category": "string",
      "subcategories": ["string"]
    },
    "recommended_routing": {
      "queue": "string",
      "priority_score": "number"
    }
  }
}
```

### Step 2: Real-Time Upload Moderation (React)

Implement client-side upload with instant moderation:

```jsx
import React, { useState } from 'react';
import axios from 'axios';

const UserImageUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [moderationResult, setModerationResult] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];

    if (!file) return;

    setUploading(true);

    try {
      // Upload directly to ImgGo for moderation
      const moderation = await moderateImage(file);

      // Handle moderation decision
      if (moderation.overall_decision.action === 'approved') {
        // Auto-approve and upload to content server
        await uploadToContentServer(file, moderation.moderation_id);
        alert('Image uploaded successfully!');

      } else if (moderation.overall_decision.action === 'review_required') {
        // Queue for human review
        await queueForReview(file, moderation);
        alert('Your image is under review. You\'ll be notified within 24 hours.');

      } else if (moderation.overall_decision.action === 'rejected') {
        // Reject with explanation
        alert(`Image rejected: ${moderation.overall_decision.reason}`);

      } else if (moderation.overall_decision.action === 'blocked') {
        // Severe violation - block user
        await handleSevereViolation(moderation);
        alert('This content violates our policies. Your account has been flagged.');
      }

      setModerationResult(moderation);

    } catch (error) {
      console.error('Moderation error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const moderateImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(
      `https://img-go.com/api/patterns/${process.env.REACT_APP_MODERATION_PATTERN_ID}/ingest`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${process.env.REACT_APP_IMGGO_API_KEY}`,
          'Content-Type': 'multipart/form-data',
          'Idempotency-Key': `upload-${Date.now()}-${Math.random()}`,
        },
      }
    );

    const jobId = response.data.data.job_id;

    // Poll for moderation result
    return await pollForModeration(jobId);
  };

  const pollForModeration = async (jobId) => {
    for (let i = 0; i < 15; i++) {
      const result = await axios.get(
        `https://img-go.com/api/jobs/${jobId}`,
        {
          headers: {
            'Authorization': `Bearer ${process.env.REACT_APP_IMGGO_API_KEY}`,
          },
        }
      );

      if (result.data.data.status === 'completed') {
        return result.data.data.result;
      } else if (result.data.data.status === 'failed') {
        throw new Error(result.data.data.error);
      }

      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    throw new Error('Moderation timeout');
  };

  const uploadToContentServer = async (file, moderationId) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('moderation_id', moderationId);
    formData.append('user_id', userId);

    await axios.post('/api/content/upload', formData);
  };

  const queueForReview = async (file, moderation) => {
    // Upload to review queue storage
    const formData = new FormData();
    formData.append('image', file);
    formData.append('moderation_data', JSON.stringify(moderation));

    await axios.post('/api/moderation/queue', formData);
  };

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        disabled={uploading}
      />
      {uploading && <p>Analyzing image...</p>}

      {moderationResult && (
        <div className={`result ${moderationResult.overall_decision.action}`}>
          <p>Status: {moderationResult.overall_decision.action}</p>
          <p>Confidence: {(moderationResult.overall_decision.confidence * 100).toFixed(0)}%</p>
        </div>
      )}
    </div>
  );
};

export default UserImageUpload;
```

### Step 3: Moderation Queue Backend (Node.js)

Implement human review queue with prioritization:

```javascript
const express = require('express');
const router = express.Router();

// Confidence thresholds for auto-decisions
const MODERATION_CONFIG = {
  auto_approve_threshold: 0.95,  // >95% confidence = auto-approve
  auto_reject_threshold: 0.90,   // >90% confidence on violation = auto-reject
  high_priority_threshold: 0.75, // >75% = high priority review

  policy_weights: {
    adult_content: 1.0,
    violence: 1.5,
    hate_symbols: 2.0,
    self_harm: 2.0,
    minor_safety: 3.0,
    drugs: 1.2,
    weapons: 1.3
  }
};

router.post('/moderation/queue', async (req, res) => {
  try {
    const { moderation_data } = req.body;

    // Determine routing based on confidence and violation type
    const routing = determineRouting(moderation_data);

    // Store in review queue database
    const queueItem = await db.collection('moderation_queue').insertOne({
      moderation_id: moderation_data.moderation_id,
      user_id: moderation_data.user_context.user_id,
      image_url: req.file.path,
      moderation_data: moderation_data,
      queue: routing.queue,
      priority_score: routing.priority_score,
      assigned_to: null,
      status: 'pending',
      created_at: new Date(),
      sla_deadline: new Date(Date.now() + routing.sla_hours * 3600000)
    });

    // Send notification to moderators
    await notifyModeratorTeam(routing.queue, routing.priority_score);

    res.json({
      queued: true,
      queue_id: queueItem.insertedId,
      estimated_review_time: routing.sla_hours
    });

  } catch (error) {
    console.error('Queue error:', error);
    res.status(500).json({ error: error.message });
  }
});

function determineRouting(moderation) {
  let priorityScore = 50; // Base priority
  let queue = 'standard_review';
  let slaHours = 24;

  // Check for critical violations
  const criticalPolicies = moderation.policy_violations.filter(
    v => v.detected && v.severity === 'critical'
  );

  if (criticalPolicies.length > 0) {
    priorityScore = 95;
    queue = 'urgent_review';
    slaHours = 1;
    return { queue, priority_score: priorityScore, sla_hours: slaHours };
  }

  // Check for minor safety
  if (moderation.safety_signals.minor_present.detected &&
      moderation.safety_signals.minor_present.confidence > 0.5) {
    priorityScore = 100;
    queue = 'child_safety_specialist';
    slaHours = 0.5;
    return { queue, priority_score: priorityScore, sla_hours: slaHours };
  }

  // Calculate weighted priority based on violation types
  moderation.policy_violations.forEach(violation => {
    if (violation.detected) {
      const weight = MODERATION_CONFIG.policy_weights[violation.policy_id] || 1.0;
      priorityScore += violation.confidence * 50 * weight;
    }
  });

  // Adjust based on user trust score
  priorityScore -= moderation.user_context.trust_score * 20;

  // Adjust based on previous violations
  priorityScore += moderation.user_context.previous_violations * 15;

  // Determine queue based on priority
  if (priorityScore > 80) {
    queue = 'high_priority_review';
    slaHours = 4;
  } else if (priorityScore > 60) {
    queue = 'medium_priority_review';
    slaHours = 12;
  } else {
    queue = 'standard_review';
    slaHours = 24;
  }

  return {
    queue,
    priority_score: Math.min(100, Math.max(0, priorityScore)),
    sla_hours: slaHours
  };
}

// Moderator dashboard endpoint
router.get('/moderation/next-item', authenticateModerator, async (req, res) => {
  const moderatorId = req.user.id;
  const moderatorQueues = req.user.authorized_queues;

  // Get highest priority item from authorized queues
  const item = await db.collection('moderation_queue')
    .find({
      queue: { $in: moderatorQueues },
      status: 'pending',
      assigned_to: null
    })
    .sort({ priority_score: -1, created_at: 1 })
    .limit(1)
    .toArray();

  if (item.length === 0) {
    return res.json({ item: null, message: 'No items in queue' });
  }

  // Assign to moderator
  await db.collection('moderation_queue').updateOne(
    { _id: item[0]._id },
    {
      $set: {
        assigned_to: moderatorId,
        assigned_at: new Date(),
        status: 'in_review'
      }
    }
  );

  res.json({ item: item[0] });
});

// Moderator decision endpoint
router.post('/moderation/decision', authenticateModerator, async (req, res) => {
  const { queue_id, decision, reason, notes } = req.body;

  // Update queue item
  await db.collection('moderation_queue').updateOne(
    { _id: queue_id },
    {
      $set: {
        status: 'completed',
        decision: decision,
        moderator_reason: reason,
        moderator_notes: notes,
        completed_at: new Date(),
        completed_by: req.user.id
      }
    }
  );

  // Take action based on decision
  const item = await db.collection('moderation_queue').findOne({ _id: queue_id });

  if (decision === 'approve') {
    await publishContent(item.image_url, item.user_id);
  } else if (decision === 'reject') {
    await notifyUserRejection(item.user_id, reason);
  } else if (decision === 'block_user') {
    await blockUser(item.user_id, reason);
  }

  // Update user trust score
  await updateUserTrustScore(item.user_id, decision);

  res.json({ success: true });
});

module.exports = router;
```

### Step 4: Appeal System

Handle user appeals with original moderation context:

```javascript
router.post('/moderation/appeal', authenticateUser, async (req, res) => {
  const { moderation_id, appeal_reason } = req.body;

  // Retrieve original moderation decision
  const original = await db.collection('moderation_queue').findOne({
    moderation_id: moderation_id,
    user_id: req.user.id
  });

  if (!original) {
    return res.status(404).json({ error: 'Moderation not found' });
  }

  // Check if appealable
  if (!original.moderation_data.appeals.appealable) {
    return res.status(400).json({ error: 'This decision is not appealable' });
  }

  const appealDeadline = new Date(
    original.created_at.getTime() +
    original.moderation_data.appeals.appeal_window_hours * 3600000
  );

  if (new Date() > appealDeadline) {
    return res.status(400).json({ error: 'Appeal window expired' });
  }

  // Create appeal
  const appeal = await db.collection('appeals').insertOne({
    moderation_id: moderation_id,
    user_id: req.user.id,
    original_decision: original.decision,
    appeal_reason: appeal_reason,
    status: 'pending',
    created_at: new Date(),
    queue: 'appeals_review'
  });

  // Notify appeals team
  await notifyAppealsTeam(appeal.insertedId);

  res.json({
    appeal_id: appeal.insertedId,
    status: 'submitted',
    estimated_review_time_hours: 72
  });
});
```

---

## Integration Examples

### Trust & Safety Dashboard

```javascript
// Real-time moderation metrics
router.get('/moderation/metrics', async (req, res) => {
  const now = new Date();
  const last24h = new Date(now - 24 * 3600000);

  const metrics = {
    last_24_hours: {
      total_uploads: await db.collection('moderation_queue')
        .countDocuments({ created_at: { $gte: last24h } }),

      auto_approved: await db.collection('moderation_queue')
        .countDocuments({
          created_at: { $gte: last24h },
          decision: 'approved',
          'moderation_data.overall_decision.auto_action_taken': true
        }),

      auto_rejected: await db.collection('moderation_queue')
        .countDocuments({
          created_at: { $gte: last24h },
          decision: 'rejected',
          'moderation_data.overall_decision.auto_action_taken': true
        }),

      queued_for_review: await db.collection('moderation_queue')
        .countDocuments({
          created_at: { $gte: last24h },
          status: { $in: ['pending', 'in_review'] }
        }),

      avg_review_time_minutes: await calculateAvgReviewTime(last24h),

      violation_breakdown: await getViolationBreakdown(last24h)
    },

    current_queue_status: {
      urgent: await db.collection('moderation_queue')
        .countDocuments({ status: 'pending', queue: 'urgent_review' }),

      high_priority: await db.collection('moderation_queue')
        .countDocuments({ status: 'pending', queue: 'high_priority_review' }),

      standard: await db.collection('moderation_queue')
        .countDocuments({ status: 'pending', queue: 'standard_review' })
    }
  };

  res.json(metrics);
});
```

### Slack Alert Integration

```javascript
const { WebClient } = require('@slack/web-api');
const slack = new WebClient(process.env.SLACK_BOT_TOKEN);

async function sendCriticalViolationAlert(moderation) {
  const violations = moderation.policy_violations
    .filter(v => v.severity === 'critical' && v.detected)
    .map(v => v.policy_name)
    .join(', ');

  await slack.chat.postMessage({
    channel: '#trust-safety-alerts',
    text: `ALERT: Critical violation detected`,
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*Critical Violation Alert*\n\nViolations: ${violations}\nUser: ${moderation.user_context.user_id}\nConfidence: ${(moderation.overall_decision.confidence * 100).toFixed(0)}%`
        }
      },
      {
        type: 'actions',
        elements: [
          {
            type: 'button',
            text: { type: 'plain_text', text: 'Review Now' },
            url: `https://moderation.platform.com/queue/${moderation.moderation_id}`
          }
        ]
      }
    ]
  });
}
```

---

## Performance Metrics

### Moderation Accuracy

- **Auto-Approval Accuracy**: 98.7% (validated through spot-checking)
- **Auto-Rejection Accuracy**: 96.3% (validated through appeals)
- **Human Review Agreement**: 94% agreement with ImgGo recommendations
- **False Positive Rate**: 3.2% (overly cautious blocking)
- **False Negative Rate**: 1.8% (violations that slipped through)

### Efficiency Gains

| Metric | Manual Moderation | With ImgGo | Improvement |
|--------|-------------------|------------|-------------|
| % Auto-Approved | 0% | 75% | +75% |
| Human Review Load | 100% | 25% | -75% |
| Avg Decision Time | 45 seconds | 2 seconds | 96% faster |
| Moderator Burnout | High | Low | Significant |
| Cost per moderation | $0.50 | $0.05 | 90% savings |

### Business Impact

**Social platform** (1M daily uploads):

- **Moderation Cost Savings**: $4.5M/year (eliminate 75% of manual review)
- **Moderator Wellbeing**: 80% reduction in exposure to disturbing content
- **Response Time**: <3 seconds (vs 4-6 hours manual review)
- **User Experience**: 10% increase in upload completion rate (less false rejections)
- **Legal Risk**: 95% reduction in policy violation exposure time
- **Total Annual Benefit**: $6M+
- **ImgGo Cost**: $360K/year
- **ROI**: 1,567%

---

## Best Practices

### Confidence Thresholds

- **Auto-Approve**: Only if confidence >95% AND no violations detected
- **Auto-Reject**: Only for critical violations with >90% confidence
- **Always Review**: Minor safety, borderline content, new user uploads

### Queue Design

- **Child Safety**: 24/7 specialist team, <30 minute SLA
- **Urgent**: High-confidence violations, <4 hour SLA
- **Standard**: Borderline content, <24 hour SLA
- **Appeals**: Separate team, <72 hour SLA

### User Communication

- **Transparency**: Explain why content was flagged
- **Education**: Link to community guidelines
- **Appeals**: Always offer appeal path for non-critical violations
- **Timeliness**: Notify users within 1 hour of decision

### Moderator Support

- **Breaks**: Enforce 15-minute breaks every 2 hours
- **Rotation**: Rotate moderators between queues weekly
- **Counseling**: Provide mental health support
- **Training**: Monthly calibration sessions

---

## Compliance

### Platform Liability Protection

- **DMCA Safe Harbor**: Respond to violations within 24 hours
- **Section 230**: Document good-faith moderation efforts
- **COPPA**: Enhanced detection for content involving minors
- **GDPR**: Allow users to request moderation history deletion

### Audit Requirements

- **Retention**: Keep moderation decisions for 1 year minimum
- **Transparency Reports**: Publish quarterly moderation statistics
- **Appeal Rights**: Document all appeal processes
- **Bias Testing**: Quarterly audits for demographic bias

---

## Troubleshooting

### Issue: High False Positive Rate

**Solution**: Lower auto-reject threshold, route more to human review, retrain with edge cases

### Issue: Moderator Queue Overload

**Solution**: Increase auto-approve threshold, hire more moderators, implement peak-time routing

### Issue: Inconsistent Decisions

**Solution**: Regular moderator calibration sessions, clear policy documentation, second-opinion workflow

---

## Related Use Cases

- [KYC Verification](../kyc-verification) - Identity verification with safety checks
- [GDPR Anonymization](../gdpr-anonymization) - PII detection and masking
- [Document Classification](../document-classification) - Content categorization

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- Moderation Best Practices: [https://img-go.com/docs/content-moderation](https://img-go.com/docs/content-moderation)
- Integration Help: support@img-go.com
