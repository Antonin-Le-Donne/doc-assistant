# Corpus

The PDFs are downloaded to `data/raw/` by `scripts/download_corpus.py`.
They are not committed to Git; the repository records their URLs and licence
information instead. Page counts include the cover and front matter.

| doc_id | Local filename | Title | Source URL | Version / date | Licence | Redistribution | PDF pages | Why it was selected | Known extraction issues |
|---|---|---|---|---|---|---|---:|---|---|
| `windows10_vbs` | `windows10_vbs.pdf` | *Mise en œuvre des fonctionnalités de sécurité de Windows 10 reposant sur la virtualisation* (ANSSI-BP-039) | https://messervices.cyber.gouv.fr/documents-guides/np_securisation_windows10_securite_reposant_sur_la_virtualisation_v1.pdf | v1.0 — 2017-11-08 | Etalab Open Licence v1 | Yes, with attribution | 54 | Focused coverage of VBS/VSM, Device Guard, HVCI, Credential Guard and their prerequisites. | The guide targets Windows 10 version 1703 and Enterprise/Education editions. Do not present its procedures as current Windows 11 guidance. Check hardware/software prerequisite tables, recommendation callouts and GPO/WMI appendices after extraction. The PDF's font encoding loses some characters for good, whatever the cleaning: "Microsoft" often extracts as "Microso" and "Figure" as "F". |
| `systemes_industriels` | `systemes_industriels.pdf` | *La cybersécurité des systèmes industriels — Mesures détaillées* (ANSSI-PA-108) | https://messervices.cyber.gouv.fr/documents-guides/Guide_Systemes_industriels__Mesures_detaillees_v2.pdf | v2.0 — 2025-11-27 | Etalab Open Licence v2.0 | Yes, with attribution and update date | 124 | Adds OT/ICS topics: maintenance constraints, vulnerabilities, industrial protocols, segmentation, administration and detailed technical measures. | Contains numbered recommendations, mapping tables, acronyms and port/protocol lists. Verify recommendation numbers, port values and list boundaries after extraction. |
| `architectures_si_sensibles` | `architectures_si_sensibles.pdf` | *Recommandations pour les architectures des systèmes d'information sensibles ou diffusion restreinte* (ANSSI-PG-075) | https://messervices.cyber.gouv.fr/documents-guides/anssi-guide-recommandations_architectures_systemes_information_sensibles_ou_diffusion_restreinte-v1.2.pdf | v1.2 — 2021-09-24 | Etalab Open Licence v2.0 | Yes, with attribution and update date | 112 | Covers SI sensitivity, architecture patterns, interconnections, security gateways and access-right management. | Architecture diagrams are important but are outside the text-only v1 scope. Extracted captions and tables may lose the visual relationships between components. |
| `linux_configuration` | `linux_configuration.pdf` | *Recommandations de configuration d'un système GNU/Linux* (ANSSI-BP-028) | https://messervices.cyber.gouv.fr/documents-guides/fr_np_linux_configuration-v2.0.pdf | v2.0 — 2022-10-03 | Etalab Open Licence v2.0 | Yes, with attribution and update date | 86 | Practical Linux hardening coverage: kernel, system parameters, accounts, access control, files and AppArmor/SELinux. | Keep commands, paths, `sysctl` parameters, configuration snippets and values intact. Watch for line breaks inside commands and recommendation tables. |
| `hygiene_informatique` | `hygiene_informatique.pdf` | *Guide d'hygiène informatique — Renforcer la sécurité de son système d'information en 42 mesures* | https://messervices.cyber.gouv.fr/documents-guides/guide_hygiene_informatique_anssi.pdf | v2.0 — 2017-09 | Etalab Open Licence v1 | Yes, with attribution | 72 | Concise baseline coverage of accounts, endpoints, networks, administration, updates, monitoring and backups. | The layout is highly visual: measure number, title, Standard/Enhanced level and explanation may be in separate blocks. Check their order and association after extraction. |

## Selection and limitations

- All five sources are text-based PDFs; none was selected for OCR-only extraction.
- Licence details appear in the information or closing pages of the PDFs. The
  PDFs are kept local under `data/`, which is ignored by Git.
- `eval/questions.jsonl` must use the **1-based page number shown by a PDF
  viewer**, not only the printed footer page. Covers and front matter can create
  a page-number offset. Use the same convention in `Page.page`, `Chunk.page`,
  API sources and `expected_pages`.
- The v1 pipeline handles text, not figures. Do not mark a question answerable
  if its answer depends only on a diagram or image until image extraction is
  explicitly added to the scope.

## Licence notes

- The Windows 10 guide identifies the Etalab Open Licence and states that it
  may be redistributed without restriction.
- The industrial, sensitive-architecture and GNU/Linux guides identify the
  Etalab Open Licence v2.0 and its attribution requirements.
- The hygiene guide identifies the Etalab Open Licence v1 on its closing page.
