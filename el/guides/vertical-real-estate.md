---
title: Real estate arbitrage & clustering (EL)
version: 1.0.0
description: "Οδηγός (EL) για aggregation αγγελιών ακινήτων, entity resolution μέσω clustering και arbitrage signals downstream"
---

# Real estate arbitrage & clustering (EL)

Αυτό το κάθετο use case δείχνει πώς να:

- συγκεντρώνετε αγγελίες από πολλαπλά portals
- normalize διευθύνσεις και να υπολογίζετε features (π.χ. `price_per_sqm`)
- κάνετε clustering με `propertyCluster` για να εντοπίζετε “παρόμοια/ίδια” ακίνητα
- υπολογίζετε arbitrage με cluster στατιστικά και εξωτερικές πηγές (downstream)

## Pipeline example

- File: `examples/pipelines/22-real-estate-arbitrage-clustering.yaml`

## Post-clustering (downstream)

Η ανάλυση clusters (μέσος, διασπορά, outliers) προτείνεται downstream σε Trino/Spark SQL.


