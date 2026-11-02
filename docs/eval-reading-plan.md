# Reference-set reading plan

This plan identifies passages to read before writing the 25 entries in
`eval/questions.jsonl` (five per guide). It deliberately does not contain the
question wording: write the questions before the first retrieval run, without
looking at retrieval results. Page ranges below were checked against the PDFs.

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
| W2 | Sections 2.4–2.5 — UEFI Secure Boot (R4) and VBS activation (R5) | 12–13 / 10–11 | Procedure | true |
| W3 | Sections 3.4.1–3.4.2 — CCI policy and HVCI | 17–18 / 15–16 | Compare two mechanisms | true |
| W4 | Appendix A — minimum hardware and software prerequisites | 27 / 25 | Specific prerequisite or value | true |
| W5 | Windows 11-specific security features and compatibility requirements | — | Plausible adjacent topic, but this guide documents Windows 10 version 1703 | false |

## 2. Industrial systems — detailed measures

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| I1 | Section 2.2.1 — patch-management constraints in industrial environments | 17 / 15 | Explain a concept or constraint | true |
| I2 | Section 4.2.8 (R153–R155) — compensating measures for protocols that cannot be secured | 82 / 80 | Risk-reduction procedure | true |
| I3 | Industrial protocol examples (Modbus, S7Comm; the rest of the list is on the next page) | 66 / 64 | Exact port/protocol value | true |
| I4 | Recommendations R103–R105 — inter-zone connections and administration-network segmentation | 67 / 65 | Combine recommendations | true |
| I5 | Kubernetes `NetworkPolicy` and admission control for an OT cluster | — | Related to segmentation, but Kubernetes is not covered by these guides | false |

## 3. Sensitive or restricted-distribution information systems

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| A1 | Section 2.1 — definition of sensitive information | 9 / 7 | Definition | true |
| A2 | Section 3.2.1 — architecture of a physically isolated sensitive SI | 23 / 21 | Architecture choice and constraints | true |
| A3 | Section 5.5 — access-right review and review frequency | 57 / 55 | Exact frequency or value | true |
| A4 | Section 3.2.1 (no Internet from class 2) and section 4.3.1 (class 1 gateway firewalls); 4.3.2 was dropped because it relies on diagrams | 22 and 36 / 20 and 34 | Cross-section architecture question | true |
| A5 | Automatic AWS KMS key rotation for sensitive data hosted in the cloud | — | Relevant key-management topic, but AWS/KMS is not covered by these guides | false |

## 4. GNU/Linux system configuration

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| L1 | Section 3.3 — defence in depth | 11 / 9 | Definition | true |
| L2 | Section 5.2.1 — memory configuration and the role of IOMMU | 18–19 / 16–17 | Technical explanation | true |
| L3 | Section 6.2.2 — administrator accounts, role separation and traceability | 38–39 / 36–37 | Procedure or recommendation | true |
| L4 | Section 6.3.3 — SELinux in `enforcing` mode with the `targeted` policy | 49 / 47 | Configuration procedure and exact values | true |
| L5 | Section 5.2.2 — recommended kernel configuration options in `sysctl.conf` | 21 / 19 | Exact configuration value | true |

## 5. Information-security hygiene guide

| Entry | Passage to read | Viewer pages / printed pages | Suggested question type | Answerable |
|---|---|---:|---|---|
| H1 | Measure 8 — individual user identities and separate user/administrator roles | 16 / 14 | Definition or measure | true |
| H2 | Section VI, measure 29 — limiting workstation administrator rights | 41 / 39 | Procedure and rationale | true |
| H3 | Section IX, measure 37 — backup policy for critical components | 53 / 51 | Required elements or values | true |
| H4 | Measures 8 and 29 — named accounts, separate administrator accounts and local rights | 16 and 41 / 14 and 39 | Cross-section question | true |
| H5 | NIS2 incident-notification deadlines (24 h / 72 h) | — | Plausible cybersecurity topic, but NIS2 is not covered by these guides | false |

## Checks before the first evaluation run

- [x] All 25 questions are paraphrased and do not copy guide headings verbatim.
- [x] There are five entries per PDF and exactly four `answerable: false` entries.
- [x] Unanswerable entries have `expected_doc_id: null` and
  `expected_pages: []`.
- [x] Answerable entries point to the correct `expected_doc_id` and one or two
  PDF-viewer pages.
- [x] The JSONL file is validated and committed before the first retrieval
  result is inspected.
