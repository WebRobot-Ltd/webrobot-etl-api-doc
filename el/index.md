---
title: Τεκμηρίωση WebRobot ETL API (Ελληνικά)
version: 1.0.0
description: Οδηγοί και αναφορά API για την κατασκευή και διαχείριση pipeline ETL σε YAML
---

# WebRobot ETL API – Τεκμηρίωση (EL)

[English version](../index.md) | [Versione italiana](../it/index.md)

Αυτή είναι η έκδοση **στα ελληνικά** της τεκμηρίωσης.

## Σχετικά με το WebRobot

Το **WebRobot** είναι μια **υποδομή δεδομένων native Spark, API-first** για την κατασκευή **agentic pipeline ETL** και **προϊόντων δεδομένων**.

Αυτή η τεκμηρίωση καλύπτει το **συστατικό ETL** του WebRobot, το οποίο παρέχει:

- **Επεξεργασία native Spark**: Χτισμένο πάνω στο Apache Spark για επεκτάσιμη επεξεργασία δεδομένων
- **Αρχιτεκτονική API-first**: Διαχείριση pipeline, έργων και jobs μέσω REST API
- **Δυνατότητες agentic**: Έξυπνα stages με LLM για προσαρμοστική εξαγωγή δεδομένων από το web
- **Πλαίσιο επεκτάσιμο**: Προσαρμοσμένα plugins, stages, resolvers και επεκτάσεις Python

## Ενσωμάτωση AI Agent & Πρωτόκολλο MCP

Αυτή η τεκμηρίωση χρησιμεύει ως **βάση γνώσης αναφοράς** για AI agents και εργαλεία ανάπτυξης:

### 🤖 Υποστήριξη AI Agent

Αυτή η τεκμηρίωση σχεδιάστηκε να καταναλώνεται από AI βοηθούς προγραμματισμού και agents, συμπεριλαμβανομένων:

- **Cursor AI**: Ενσωματωμένος AI βοηθός για παραγωγή κώδικα και δημιουργία pipeline
- **ChatGPT**: Τεκμηρίωση αναφοράς για τις δυνατότητες ETL του WebRobot
- **Claude Desktop**: Βάση γνώσης για κατανόηση της αρχιτεκτονικής και των API του WebRobot
- **Ενσωματωμένος Agent Ανάπτυξης**: Ενσωματωμένος AI agent στο WebRobot για αυτόματη παραγωγή και βελτιστοποίηση pipeline

### 🔌 Model Context Protocol (MCP)

Όλες οι λειτουργίες ETL του WebRobot εκτίθενται μέσω **endpoint MCP (Model Context Protocol)**, επιτρέποντας:

- **Τυποποιημένη ενσωμάτωση AI**: Συνεπής διεπαφή για AI agents να αλληλεπιδρούν με το WebRobot
- **Function calling**: Τα AI agents μπορούν να καλέσουν λειτουργίες WebRobot μέσω εργαλείων MCP
- **Βοήθεια context-aware**: Τα agents μπορούν να ερωτήσουν σχήματα pipeline, δυνατότητες stages και προδιαγραφές API
- **Αυτόματη παραγωγή pipeline**: Τα AI agents μπορούν να δημιουργήσουν, να επικυρώσουν και να εκτελέσουν pipeline προγραμματιστικά

Κάθε λειτουργία που τεκμηριώνεται εδώ είναι προσβάσιμη τόσο μέσω REST API όσο και endpoint MCP, εξασφαλίζοντας απρόσκοπτη ενσωμάτωση με ροές εργασίας ανάπτυξης που βασίζονται σε AI.

## Ξεκινήστε αμέσως

- **[Κατασκευή pipeline](guides/build-a-pipeline.md)** (EL)
- **[Αναφορά stages pipeline](guides/pipeline-stages.md)** (EL)
- **[Παραδείγματα pipeline](guides/pipeline-examples.md)** (EL)
- **[Plugin EAN Image Sourcing](guides/ean-image-sourcing.md)** (EL)
- **[Τεχνικοί συνεργάτες](guides/technical-partners.md)** (EL)

## Σημείωση για τη γλώσσα

Για να ξεκινήσετε αμέσως, η πιο λεπτομερής τεχνική τεκμηρίωση παραμένει συχνά στα αγγλικά. Η ελληνική έκδοση διατηρείται ευθυγραμμισμένη με τα πιο λειτουργικά μέρη και τις κύριες ροές API.

