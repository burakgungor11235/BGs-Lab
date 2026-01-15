+++
title = "Ancient Sumerian NMT"
description = "A Neural Machine Translation system for the bidirectional translation of ancient Sumerian and modern Turkish using T5 Transformers."
date = 2023-11-06
template = "project-single.html"
[extra]
stack = ["Python", "T5 Transformer", "NLP", "C", "Perl"]
link = "https://ebideb.tubitak.gov.tr/pdf.htm?dosyaNo=5884825&bsvNo=1689B012437192"
+++

This is a research project that addresses the challenge of translating
a low-resource, linguistic isolate like Ancient Sumerian into modern Turkish.

### Technical Deep Dive

- **Transformer Architecture**: Fine-tuned a T5 model using transfer learning to overcome sparse data.
- **Custom Tokenization**: Developed a tokenizer specifically tailored to Sumerian transliteration.
- **Complex Data Pipeline**: Engineered a multi-language pipeline (Python, C, Perl) to harmonize data from diverse academic sources (ORACC, CDLI, ETCSL).
- **Evaluation**: Rigorous performance testing using BLEU, METEOR, and WER metrics.

This work combines digital humanities with (used to be) state-of-the-art AI to preserve and understand ancient knowledge.
