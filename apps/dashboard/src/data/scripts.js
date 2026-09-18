// Default Medicare Bot Scripts Data according to PRD v1.1
export const INITIAL_SCRIPTS = [
  {
    id: "script-101",
    name: "Medicare Part C/D First-Level Qualification",
    version: "v1.1",
    campaignId: "623d1948-ea8c-460f-815d-2cf26a1a8e28",
    campaignName: "Med Fronter",
    status: "active", // active, draft, pending_review, archived
    approvedBy: "Usama Awan (Director IT)",
    author: "Bilal Satti",
    updatedAt: "Jun 16, 2026 14:30",
    qualificationRate: "18.4%",
    transferRate: "6.84%",
    dropOffRate: "2.1%",
    fallbackCount: 14,
    greeting:
      "Hello, this is Alex calling from SmartBrains BPO on behalf of Medicare Assistance Services. I'm following up on your request regarding Medicare Plan options.",
    consent:
      "Before we begin, please note this call is recorded for quality, training, and compliance purposes under TCPA guidelines. Do I have your permission to proceed?",
    qualificationQuestions: [
      "Are you currently 65 years of age or older, or qualified due to disability?",
      "Do you currently have Medicare Part A and Part B active?",
      "Are you interested in exploring additional dental, vision, or prescription savings?",
    ],
    transferMessage:
      "Great news! Based on your answers, you are eligible to speak with a licensed Medicare verifier. Please hold while I connect you now.",
    disqualificationMessage:
      "Thank you for your time today. Based on your current coverage, you do not meet the qualifications for this specific program. Have a wonderful day.",
    versionHistory: [
      {
        version: "v1.1",
        status: "active",
        releaseDate: "Jun 16, 2026 14:30",
        author: "Bilal Satti",
        approvedBy: "Usama Awan (Director IT)",
        changes: "Updated TCPA compliance consent prompt and added prescription question.",
      },
      {
        version: "v1.0",
        status: "archived",
        releaseDate: "May 10, 2026 09:00",
        author: "Bilal Satti",
        approvedBy: "Usama Awan (Director IT)",
        changes: "Initial production release for Medicare Part C/D campaign.",
      },
      {
        version: "v0.9-beta",
        status: "archived",
        releaseDate: "Apr 20, 2026 11:15",
        author: "DevOp Admin",
        approvedBy: "QA Team",
        changes: "Pilot testing draft for initial caller pool.",
      },
    ],
    snapshots: {
      "v1.1": {
        greeting:
          "Hello, this is Alex calling from SmartBrains BPO on behalf of Medicare Assistance Services. I'm following up on your request regarding Medicare Plan options.",
        consent:
          "Before we begin, please note this call is recorded for quality, training, and compliance purposes under TCPA guidelines. Do I have your permission to proceed?",
        questions: [
          "Are you currently 65 years of age or older, or qualified due to disability?",
          "Do you currently have Medicare Part A and Part B active?",
          "Are you interested in exploring additional dental, vision, or prescription savings?",
        ],
        transferMessage:
          "Great news! Based on your answers, you are eligible to speak with a licensed Medicare verifier. Please hold while I connect you now.",
        disqualificationMessage:
          "Thank you for your time today. Based on your current coverage, you do not meet the qualifications for this specific program. Have a wonderful day.",
      },
      "v1.0": {
        greeting:
          "Hello, this is Alex calling from SmartBrains BPO. I am following up on your inquiry about Medicare coverage.",
        consent:
          "Calls are recorded for quality purposes. Can we continue?",
        questions: [
          "Are you 65 years of age or older?",
          "Do you have active Medicare Parts A and B?",
        ],
        transferMessage:
          "Connecting you to a licensed agent now.",
        disqualificationMessage:
          "Thank you, have a good day.",
      },
    },
  },
  {
    id: "script-102",
    name: "Medicare Advantage Inbound Lead Verification",
    version: "v1.0",
    campaignId: "2f90fe05-8e22-4536-b402-fc7c95d1083f",
    campaignName: "Data Campaign",
    status: "active",
    approvedBy: "Usama Awan (Director IT)",
    author: "Bilal Satti",
    updatedAt: "Jun 15, 2026 09:15",
    qualificationRate: "15.2%",
    transferRate: "5.10%",
    dropOffRate: "3.4%",
    fallbackCount: 22,
    greeting:
      "Thank you for calling Medicare Helpline. My name is Alex, your automated assistant. I'll ask a few quick questions to guide your call.",
    consent:
      "This call is recorded for compliance. By continuing, you agree to speak with our qualification system. Is that alright?",
    qualificationQuestions: [
      "Could you confirm your current state of residence?",
      "Are you enrolled in Medicare Parts A and B?",
    ],
    transferMessage:
      "Thank you! Connecting you to a live licensed Medicare agent now...",
    disqualificationMessage:
      "Thank you for calling. We are unable to assist with your specific request at this time.",
    versionHistory: [
      {
        version: "v1.0",
        status: "active",
        releaseDate: "Jun 15, 2026 09:15",
        author: "Bilal Satti",
        approvedBy: "Usama Awan (Director IT)",
        changes: "First release for inbound Medicare Advantage line.",
      },
    ],
    snapshots: {
      "v1.0": {
        greeting:
          "Thank you for calling Medicare Helpline. My name is Alex, your automated assistant. I'll ask a few quick questions to guide your call.",
        consent:
          "This call is recorded for compliance. By continuing, you agree to speak with our qualification system. Is that alright?",
        questions: [
          "Could you confirm your current state of residence?",
          "Are you enrolled in Medicare Parts A and B?",
        ],
        transferMessage:
          "Thank you! Connecting you to a live licensed Medicare agent now...",
        disqualificationMessage:
          "Thank you for calling. We are unable to assist with your specific request at this time.",
      },
    },
  },
  {
    id: "script-103",
    name: "Medicare Supplemental Plan Savings Pilot V2",
    version: "v2.0-draft",
    campaignId: "f6abb933-6daf-467c-b0bc-71ca33f08b6e",
    campaignName: "mpn-overflow-camp",
    status: "draft",
    approvedBy: "Pending Approval",
    author: "Bilal Satti",
    updatedAt: "Jun 16, 2026 16:45",
    qualificationRate: "—",
    transferRate: "—",
    dropOffRate: "—",
    fallbackCount: 0,
    greeting:
      "Hi, I'm calling regarding Medicare Supplement rate reductions available in your state for 2026.",
    consent:
      "Calls are recorded for compliance under FCC/TCPA rules. May I ask a few quick questions?",
    qualificationQuestions: [
      "Do you currently pay a monthly premium for Medicare Supplement Plan G or N?",
      "Have you lived in your current state for at least 6 months?",
    ],
    transferMessage:
      "Transferring you to a licensed Medicare Specialist now...",
    disqualificationMessage:
      "Thank you. Have a great day.",
    versionHistory: [
      {
        version: "v2.0-draft",
        status: "draft",
        releaseDate: "Jun 16, 2026 16:45",
        author: "Bilal Satti",
        approvedBy: "Pending Review",
        changes: "Drafting new 2026 Supplement Plan savings prompts.",
      },
    ],
    snapshots: {
      "v2.0-draft": {
        greeting:
          "Hi, I'm calling regarding Medicare Supplement rate reductions available in your state for 2026.",
        consent:
          "Calls are recorded for compliance under FCC/TCPA rules. May I ask a few quick questions?",
        questions: [
          "Do you currently pay a monthly premium for Medicare Supplement Plan G or N?",
          "Have you lived in your current state for at least 6 months?",
        ],
        transferMessage:
          "Transferring you to a licensed Medicare Specialist now...",
        disqualificationMessage:
          "Thank you. Have a great day.",
      },
    },
  },
];

export const APPROVAL_QUEUE_SCRIPTS = [
  {
    id: "appr-201",
    scriptId: "script-103",
    scriptName: "Medicare Supplemental Plan Savings Pilot V2",
    version: "v2.0-rc1",
    campaignName: "mpn-overflow-camp",
    author: "Bilal Satti",
    submittedAt: "2026-09-11 15:20",
    complianceScore: "96%",
    diffSummary: "+2 Qualification questions added, TCPA disclaimer expanded",
    status: "pending_review",
  },
  {
    id: "appr-202",
    scriptId: "script-101",
    scriptName: "Medicare Part C/D First-Level Qualification",
    version: "v1.2-draft",
    campaignName: "Med Fronter",
    author: "QA Manager",
    submittedAt: "2026-09-10 18:40",
    complianceScore: "100%",
    diffSummary: "Updated verifier transfer handoff wording for licensed agents",
    status: "pending_review",
  },
];