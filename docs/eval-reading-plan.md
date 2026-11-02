# Reference-set reading plan

This plan identifies passages to read before writing the 25 entries in
`eval/questions.jsonl` (five per guide). It deliberately does not contain the
question wording: write the questions by hand before the first retrieval run,
without looking at retrieval results.

## Rules

- Write five natural, paraphrased questions per guide, as a system
  administrator would ask them.
- Vary the intent across the set: definition, procedure, exact value or
  recommendation number, and a question combining two sections.
- Include four unanswerable questions in total (`answerable: false`). For these
  use `expected_doc_id: null` and `expected_pages: []`; do not assign an
  expected source passage.
- For answerable questions, use one or two pages that actually contain the
  answer. Avoid facts repeated throughout a guide.
- Page ranges are shown as **PDF-viewer pages / printed guide pages**. Use the
  first value in the JSONL (`Page.page` is 1-based).

## 1. Windows 10 — virtualization-based security

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| W1 | Section 2.1 — how Virtual Secure Mode relates to VBS | 8–9 / 6–7 | Definition | true |
| W2 | Sections 2.4–2.5 — UEFI Secure Boot and VBS activation | 11–14 / 9–12 | Procedure | true |
| W3 | Sections 3.4.1–3.4.2 — CCI policy and HVCI | 17–18 / 15–16 | Compare two mechanisms | true |
| W4 | Appendix A — hardware and software prerequisites | 27–28 / 25–26 | Specific prerequisite or value | true |
| W5 | Windows 11-specific security features and compatibility requirements | — | Plausible adjacent topic, but this guide documents Windows 10 version 1703 | false |

## 2. Industrial systems — detailed measures

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| I1 | Section 2.2.1 — patch-management constraints in industrial environments | 17–18 / 15–16 | Explain a concept or constraint | true |
| I2 | Section 2.2.7 — risks from inadequately protected industrial network protocols | 22–23 / 20–21 | Risk-reduction procedure | true |
| I3 | Industrial protocol examples (Modbus, S7Comm, EtherNet/IP, BACnet, OPC UA) | 66–67 / 64–65 | Exact port/protocol value | true |
| I4 | Recommendations R103–R105 — inter-zone connections and administration-network segmentation | 66–67 / 64–65 | Combine recommendations | true |
| I5 | Kubernetes `NetworkPolicy` and admission control for an OT cluster | — | Related to segmentation, but Kubernetes is not covered by these guides | false |

## 3. Sensitive or restricted-distribution information systems

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| A1 | Section 2.1 — definition of sensitive information and its confidentiality-protection needs | 9–10 / 7–8 | Definition | true |
| A2 | Section 3.2.1 — architecture of a physically isolated sensitive SI | 22–23 / 20–21 | Architecture choice and constraints | true |
| A3 | Section 5.5 — access-right review and review frequency | 57–58 / 55–56 | Exact frequency or value | true |
| A4 | Section 3.2.1 architecture and section 4.3.2 placement of security gateways | 22 and 38 / 20 and 36 | Cross-section architecture question | true |
| A5 | Automatic AWS KMS key rotation for sensitive data hosted in the cloud | — | Relevant key-management topic, but AWS/KMS is not covered by these guides | false |

## 4. GNU/Linux system configuration

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| L1 | Sections 3.1–3.3 — minimisation, least privilege and defence in depth | 10–11 / 8–9 | Definition | true |
| L2 | Section 5.2.1 — memory configuration and the role of IOMMU | 18–19 / 16–17 | Technical explanation | true |
| L3 | Section 6.2.2 — administrator accounts, role separation and traceability | 38–39 / 36–37 | Procedure or recommendation | true |
| L4 | Section 6.3.3 — SELinux in `enforcing` mode with the `targeted` policy | 49–50 / 47–48 | Configuration procedure and exact values | true |
| L5 | Section 5.2.2 — recommended kernel configuration options in `sysctl.conf` | 21–22 / 19–20 | Exact configuration value | true |

## 5. Information-security hygiene guide

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| H1 | Measure 8 — individual user identities and separate user/administrator roles | 16–17 / 14–15 | Definition or measure | true |
| H2 | Section VI, measure 29 — limiting workstation administrator rights | 41–42 / 39–40 | Procedure and rationale | true |
| H3 | Section IX, measure 37 — backup policy for critical components | 53–54 / 51–52 | Required elements or values | true |
| H4 | Measures 8 and 29 — named accounts, separate administrator accounts and local rights | 16 and 42 / 14 and 40 | Cross-section question | true |
| H5 | NIS2 incident-notification deadlines (24 h / 72 h) | — | Plausible cybersecurity topic, but NIS2 is not covered by these guides | false |

## Checks before the first evaluation run

- [ ] All 25 questions are paraphrased and do not copy guide headings verbatim.
- [ ] There are five entries per PDF and exactly four `answerable: false` entries.
- [ ] Unanswerable entries have `expected_doc_id: null` and
  `expected_pages: []`.
- [ ] Answerable entries point to the correct `expected_doc_id` and one or two
  PDF-viewer pages.
- [ ] The JSONL file is validated and committed before the first retrieval
  result is inspected.
