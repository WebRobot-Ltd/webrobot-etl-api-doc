---
title: LLM Fine-Tuning Dataset Construction
version: 1.0.0
description: "Complete guide for building high-quality datasets for LLM fine-tuning using WebRobot ETL pipelines"
---

# LLM Fine-Tuning Dataset Construction

This guide demonstrates how to use WebRobot ETL to build **production-ready datasets for LLM fine-tuning** by aggregating, cleaning, and structuring data from multiple sources into formats suitable for supervised fine-tuning (SFT), instruction-following, and domain-specific adaptation.

## Business Use Case

**Goal**: Build high-quality training datasets for fine-tuning Large Language Models (LLMs) by:

- **Collecting data** from multiple web sources (forums, documentation, Q&A sites, code repositories)
- **Cleaning and normalizing** text data (remove noise, deduplicate, format)
- **Structuring data** into fine-tuning formats (instruction-following, chat, code completion)
- **Enriching data** with metadata and annotations
- **Balancing datasets** across domains and difficulty levels

**Key Challenges**:
- **Data quality**: Ensure high-quality, properly formatted examples
- **Format standardization**: Convert diverse sources into consistent fine-tuning formats
- **Domain coverage**: Balance datasets across different domains and use cases
- **Licensing compliance**: Ensure data can be used for training (public domain, open licenses)

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Source A    │     │ Source B    │     │ Source C    │     │ Source D    │
│ (Forums)    │     │ (Docs)      │     │ (Q&A)       │     │ (Code)      │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┘
                    │   Union &   │
                    │  Normalize  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┘
                    │  Clean &    │
                    │  Deduplicate│
                    └──────┬──────┘
                           │
                    ┌──────▼──────┘
                    │  Structure  │
                    │  for SFT    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┘
                    │  Enrich &   │
                    │  Annotate   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┘
                    │  Balance &  │
                    │  Split      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┘
                    │  Export     │
                    │  (JSONL)    │
                    └─────────────┘
```

## Fine-Tuning Dataset Formats

### Format 1: Instruction-Following (Alpaca/ShareGPT style)

```json
{
  "instruction": "What is the capital of France?",
  "input": "",
  "output": "The capital of France is Paris."
}
```

### Format 2: Chat/Conversational (ChatML/OpenAI style)

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing."},
    {"role": "assistant", "content": "Quantum computing uses quantum mechanical phenomena..."}
  ]
}
```

### Format 3: Code Completion

```json
{
  "prompt": "def calculate_fibonacci(n):\n    \"\"\"Calculate the nth Fibonacci number.\"\"\"\n    ",
  "completion": "if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)"
}
```

### Format 4: Question-Answering (Q&A)

```json
{
  "question": "How does WebRobot ETL handle dynamic content?",
  "context": "WebRobot ETL uses browser automation...",
  "answer": "WebRobot ETL handles dynamic content through browser automation with headless Chrome..."
}
```

## Concrete Example: Building Instruction-Following Dataset

This example demonstrates how to build an instruction-following dataset by aggregating Q&A data from multiple sources (Stack Overflow, Reddit, documentation sites) and converting them into the Alpaca format.

### Data Sources

1. **Stack Overflow** - Q&A pairs (question = instruction, answer = output)
2. **Reddit** - Discussion threads (title = instruction, top comment = output)
3. **Documentation Sites** - Tutorials (section title = instruction, content = output)
4. **GitHub Issues** - Problem-solution pairs (issue = instruction, solution = output)
5. **Wikipedia** - Article summaries (title = instruction, summary = output)

### Complete Pipeline: Multi-Source Dataset Construction

```yaml
# Complete example: Build instruction-following dataset for LLM fine-tuning
fetch:
  url: "https://stackoverflow.com/questions/tagged/python"  # Starting URL for Stack Overflow

pipeline:
  # ============================================
  # Source 1: Stack Overflow (Q&A pairs)
  # ============================================
  - stage: explore
    args: [ "a.pagination-next", 20 ]  # Navigate through question pages
  - stage: join
    args: [ "h3.question-summary a", "LeftOuter" ]  # Click on questions
  - stage: extract
    args:
      - { selector: "h1.question-title", method: "text", as: "question" }
      - { selector: "div.question-body", method: "text", as: "question_body" }
      - { selector: "div.accepted-answer", method: "text", as: "answer" }
      - { selector: "span.post-tag", method: "text", as: "tags" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_stackoverflow
    args: []
  - stage: python_row_transform:convert_to_instruction_format
    args:
      - format: "instruction_following"
      - instruction_field: "question"
      - output_field: "answer"
  - stage: python_row_transform:add_metadata
    args:
      - source: "stackoverflow.com"
        domain: "programming"
        format: "instruction_following"
  - stage: cache
    args: []
  - stage: store
    args: [ "stackoverflow_dataset" ]

  # ============================================
  # Source 2: Reddit (Discussion threads)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.reddit.com/r/learnprogramming/" ]
  - stage: explore
    args: [ "a.next-button", 20 ]
  - stage: join
    args: [ "a.title", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1.title", method: "text", as: "title" }
      - { selector: "div.post-content", method: "text", as: "post_content" }
      - { selector: "div.top-comment", method: "text", as: "top_comment" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_reddit
    args: []
  - stage: python_row_transform:convert_to_instruction_format
    args:
      - format: "instruction_following"
      - instruction_field: "title"
      - output_field: "top_comment"
  - stage: python_row_transform:add_metadata
    args:
      - source: "reddit.com"
        domain: "programming"
        format: "instruction_following"
  - stage: cache
    args: []
  - stage: store
    args: [ "reddit_dataset" ]

  # ============================================
  # Source 3: Documentation Sites (Tutorials)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://docs.python.org/3/tutorial/" ]
  - stage: explore
    args: [ "a.next", 10 ]
  - stage: join
    args: [ "a.section-link", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1.section-title", method: "text", as: "section_title" }
      - { selector: "div.section-content", method: "text", as: "section_content" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_documentation
    args: []
  - stage: python_row_transform:convert_to_instruction_format
    args:
      - format: "instruction_following"
      - instruction_field: "section_title"
      - output_field: "section_content"
  - stage: python_row_transform:add_metadata
    args:
      - source: "python.org"
        domain: "programming"
        format: "instruction_following"
  - stage: cache
    args: []
  - stage: store
    args: [ "documentation_dataset" ]

  # ============================================
  # Source 4: GitHub Issues (Problem-Solution)
  # ============================================
  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${GITHUB_ISSUES_CSV_PATH}", header: "true", inferSchema: "true" }
  - stage: python_row_transform:normalize_github_issues
    args: []
  - stage: python_row_transform:convert_to_instruction_format
    args:
      - format: "instruction_following"
      - instruction_field: "issue_title"
      - output_field: "solution"
  - stage: python_row_transform:add_metadata
    args:
      - source: "github.com"
        domain: "programming"
        format: "instruction_following"
  - stage: cache
    args: []
  - stage: store
    args: [ "github_dataset" ]

  # ============================================
  # Source 5: Wikipedia (Article Summaries)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://en.wikipedia.org/wiki/Special:Random" ]
  - stage: explore
    args: [ "a.random-article", 100 ]
  - stage: extract
    args:
      - { selector: "h1.firstHeading", method: "text", as: "article_title" }
      - { selector: "div.mw-parser-output p", method: "text", as: "article_summary" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_wikipedia
    args: []
  - stage: python_row_transform:convert_to_instruction_format
    args:
      - format: "instruction_following"
      - instruction_field: "article_title"
      - output_field: "article_summary"
  - stage: python_row_transform:add_metadata
    args:
      - source: "wikipedia.org"
        domain: "general_knowledge"
        format: "instruction_following"
  - stage: cache
    args: []
  - stage: store
    args: [ "wikipedia_dataset" ]

  # ============================================
  # Merge: Union all sources
  # ============================================
  - stage: reset
    args: []
  - stage: union_with
    args: [ "stackoverflow_dataset", "reddit_dataset", "documentation_dataset", "github_dataset", "wikipedia_dataset" ]

  # ============================================
  # Clean and Normalize Text
  # ============================================
  - stage: python_row_transform:clean_text
    args: []
  - stage: python_row_transform:normalize_text
    args: []

  # ============================================
  # Deduplicate Similar Examples
  # ============================================
  - stage: python_row_transform:generate_text_hash
    args: []  # Generate hash for deduplication
  - stage: dedup
    args: [ "text_hash" ]  # Remove duplicates

  # ============================================
  # Filter by Quality Metrics
  # ============================================
  - stage: python_row_transform:filter_by_quality
    args:
      - min_instruction_length: 10
      - min_output_length: 20
      - max_instruction_length: 500
      - max_output_length: 2000

  # ============================================
  # Balance Dataset by Domain
  # ============================================
  - stage: python_row_transform:balance_dataset
    args:
      - max_per_domain: 10000
      - domains: ["programming", "general_knowledge"]

  # ============================================
  # Split into Train/Val/Test
  # ============================================
  - stage: python_row_transform:split_dataset
    args:
      - train_ratio: 0.8
      - val_ratio: 0.1
      - test_ratio: 0.1

  # ============================================
  # Export to JSONL Format
  # ============================================
  - stage: python_row_transform:export_to_jsonl
    args:
      - output_format: "instruction_following"
      - fields: ["instruction", "input", "output"]

  # ============================================
  # Save Final Dataset
  # ============================================
  - stage: save_csv
    args: [ "${OUTPUT_PATH_DATASET_JSONL}", "overwrite" ]
```

### Python Extensions for Dataset Construction

```python
# python_extensions:
#   stages:
#     normalize_stackoverflow:
#       type: row_transform
#       function: |
def normalize_stackoverflow(row):
    """Normalize Stack Overflow Q&A data."""
    question = row.get("question", "").strip()
    question_body = row.get("question_body", "").strip()
    answer = row.get("answer", "").strip()
    
    # Combine question title and body
    if question_body:
        full_question = f"{question}\n\n{question_body}"
    else:
        full_question = question
    
    row["question"] = full_question
    row["answer"] = answer
    
    # Extract tags
    tags = row.get("tags", [])
    if isinstance(tags, list):
        row["tags"] = ",".join(tags)
    
    return row

#     convert_to_instruction_format:
#       type: row_transform
#       function: |
def convert_to_instruction_format(row, format="instruction_following", instruction_field="question", output_field="answer"):
    """Convert data to instruction-following format."""
    if format == "instruction_following":
        instruction = row.get(instruction_field, "").strip()
        output = row.get(output_field, "").strip()
        
        # Create Alpaca-style format
        row["instruction"] = instruction
        row["input"] = ""  # Empty input for simple Q&A
        row["output"] = output
        
        # Store original fields for reference
        row["_original_instruction"] = instruction
        row["_original_output"] = output
    
    return row

#     clean_text:
#       type: row_transform
#       function: |
def clean_text(row):
    """Clean text data (remove HTML, normalize whitespace, etc.)."""
    import re
    import html
    
    # Clean instruction
    instruction = row.get("instruction", "")
    if instruction:
        # Decode HTML entities
        instruction = html.unescape(instruction)
        # Remove HTML tags
        instruction = re.sub(r'<[^>]+>', '', instruction)
        # Normalize whitespace
        instruction = re.sub(r'\s+', ' ', instruction).strip()
        row["instruction"] = instruction
    
    # Clean output
    output = row.get("output", "")
    if output:
        output = html.unescape(output)
        output = re.sub(r'<[^>]+>', '', output)
        output = re.sub(r'\s+', ' ', output).strip()
        row["output"] = output
    
    return row

#     normalize_text:
#       type: row_transform
#       function: |
def normalize_text(row):
    """Normalize text (lowercase, remove special chars, etc.)."""
    import re
    
    # Normalize instruction
    instruction = row.get("instruction", "")
    if instruction:
        # Remove URLs
        instruction = re.sub(r'http[s]?://\S+', '', instruction)
        # Remove email addresses
        instruction = re.sub(r'\S+@\S+', '', instruction)
        # Remove excessive punctuation
        instruction = re.sub(r'[!]{2,}', '!', instruction)
        instruction = re.sub(r'[?]{2,}', '?', instruction)
        row["instruction"] = instruction
    
    # Normalize output
    output = row.get("output", "")
    if output:
        output = re.sub(r'http[s]?://\S+', '', output)
        output = re.sub(r'\S+@\S+', '', output)
        row["output"] = output
    
    return row

#     generate_text_hash:
#       type: row_transform
#       function: |
def generate_text_hash(row):
    """Generate hash for deduplication."""
    import hashlib
    
    instruction = row.get("instruction", "")
    output = row.get("output", "")
    
    # Create hash from instruction + output
    text_combined = f"{instruction}|{output}".lower().strip()
    text_hash = hashlib.md5(text_combined.encode()).hexdigest()
    
    row["text_hash"] = text_hash
    
    return row

#     filter_by_quality:
#       type: row_transform
#       function: |
def filter_by_quality(row, min_instruction_length=10, min_output_length=20, max_instruction_length=500, max_output_length=2000):
    """Filter examples by quality metrics."""
    instruction = row.get("instruction", "")
    output = row.get("output", "")
    
    instruction_len = len(instruction)
    output_len = len(output)
    
    # Check length constraints
    if instruction_len < min_instruction_length or instruction_len > max_instruction_length:
        row["_quality_filter"] = False
        return row
    
    if output_len < min_output_length or output_len > max_output_length:
        row["_quality_filter"] = False
        return row
    
    # Check for empty or very short content
    if not instruction.strip() or not output.strip():
        row["_quality_filter"] = False
        return row
    
    row["_quality_filter"] = True
    
    return row

#     balance_dataset:
#       type: row_transform
#       function: |
def balance_dataset(row, max_per_domain=10000, domains=None):
    """Balance dataset by domain (simplified - would need aggregation in production)."""
    domain = row.get("domain", "unknown")
    
    # Mark for inclusion/exclusion based on domain limits
    # In production, this would use aggregation to count per domain
    row["_include_in_dataset"] = True
    
    return row

#     split_dataset:
#       type: row_transform
#       function: |
def split_dataset(row, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    """Split dataset into train/val/test."""
    import random
    
    # Use hash-based splitting for consistency
    text_hash = row.get("text_hash", "")
    if text_hash:
        # Use last byte of hash for deterministic splitting
        hash_byte = int(text_hash[-2:], 16)  # Last 2 hex chars = 0-255
        ratio = hash_byte / 255.0
        
        if ratio < train_ratio:
            row["split"] = "train"
        elif ratio < train_ratio + val_ratio:
            row["split"] = "val"
        else:
            row["split"] = "test"
    else:
        # Fallback to random
        rand = random.random()
        if rand < train_ratio:
            row["split"] = "train"
        elif rand < train_ratio + val_ratio:
            row["split"] = "val"
        else:
            row["split"] = "test"
    
    return row

#     export_to_jsonl:
#       type: row_transform
#       function: |
def export_to_jsonl(row, output_format="instruction_following", fields=None):
    """Prepare row for JSONL export."""
    if output_format == "instruction_following":
        # Ensure required fields exist
        if "instruction" not in row:
            row["instruction"] = ""
        if "input" not in row:
            row["input"] = ""
        if "output" not in row:
            row["output"] = ""
    
    return row
```

## Dataset Formats for Different Use Cases

### Use Case 1: Domain-Specific Instruction Following

For fine-tuning a model on a specific domain (e.g., finance, healthcare, legal):

```yaml
# Pipeline: Domain-specific dataset
pipeline:
  - stage: load_csv
    args:
      - { path: "${DOMAIN_SPECIFIC_DATA}", header: "true", inferSchema: "true" }
  
  # Convert to instruction format
  - stage: python_row_transform:convert_to_instruction_format
    args:
      - format: "instruction_following"
      - instruction_field: "question"
      - output_field: "answer"
  
  # Add domain-specific system prompts
  - stage: python_row_transform:add_domain_context
    args:
      - domain: "finance"
        system_prompt: "You are a financial analyst assistant."
  
  - stage: save_csv
    args: [ "${OUTPUT_PATH_DOMAIN_DATASET}", "overwrite" ]
```

### Use Case 2: Chat/Conversational Dataset

For fine-tuning chat models (ChatGPT-style):

```yaml
# Pipeline: Conversational dataset
pipeline:
  - stage: load_csv
    args:
      - { path: "${CONVERSATION_DATA}", header: "true", inferSchema: "true" }
  
  # Convert to chat format
  - stage: python_row_transform:convert_to_chat_format
    args:
      - format: "chat"
      - system_prompt: "You are a helpful assistant."
      - user_field: "user_message"
      - assistant_field: "assistant_message"
  
  - stage: save_csv
    args: [ "${OUTPUT_PATH_CHAT_DATASET}", "overwrite" ]
```

```python
# python_extensions:
#   stages:
#     convert_to_chat_format:
#       type: row_transform
#       function: |
def convert_to_chat_format(row, format="chat", system_prompt="You are a helpful assistant.", user_field="user_message", assistant_field="assistant_message"):
    """Convert data to chat/conversational format."""
    import json
    
    if format == "chat":
        user_message = row.get(user_field, "").strip()
        assistant_message = row.get(assistant_field, "").strip()
        
        # Create ChatML format
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
        
        row["messages"] = json.dumps(messages)
        row["messages_json"] = messages  # Keep as list for easier processing
    
    return row
```

### Use Case 3: Code Completion Dataset

For fine-tuning code completion models:

```yaml
# Pipeline: Code completion dataset
pipeline:
  - stage: load_csv
    args:
      - { path: "${CODE_REPOSITORY_DATA}", header: "true", inferSchema: "true" }
  
  # Extract code context and completion
  - stage: python_row_transform:extract_code_completion
    args:
      - context_length: 500  # Characters of context
      - completion_length: 200  # Characters of completion
  
  # Convert to code completion format
  - stage: python_row_transform:convert_to_code_format
    args:
      - format: "code_completion"
      - prompt_field: "code_context"
      - completion_field: "code_completion"
  
  - stage: save_csv
    args: [ "${OUTPUT_PATH_CODE_DATASET}", "overwrite" ]
```

## Quality Metrics and Filtering

### Quality Metrics

Filter examples based on:

1. **Length constraints**: Min/max instruction and output lengths
2. **Content quality**: Remove low-quality, spam, or irrelevant content
3. **Language detection**: Filter by language (e.g., English only)
4. **Toxicity detection**: Remove toxic or harmful content
5. **Repetition**: Remove highly repetitive content

### Example Quality Filtering

```python
# python_extensions:
#   stages:
#     filter_by_quality_advanced:
#       type: row_transform
#       function: |
def filter_by_quality_advanced(row):
    """Advanced quality filtering."""
    import re
    
    instruction = row.get("instruction", "")
    output = row.get("output", "")
    
    # Check for excessive repetition
    words_instruction = instruction.split()
    if len(words_instruction) > 0:
        unique_ratio = len(set(words_instruction)) / len(words_instruction)
        if unique_ratio < 0.3:  # Less than 30% unique words
            row["_quality_filter"] = False
            return row
    
    # Check for URL spam
    url_count = len(re.findall(r'http[s]?://\S+', instruction + output))
    if url_count > 3:
        row["_quality_filter"] = False
        return row
    
    # Check for excessive capitalization (spam indicator)
    caps_ratio = sum(1 for c in instruction if c.isupper()) / len(instruction) if instruction else 0
    if caps_ratio > 0.5:
        row["_quality_filter"] = False
        return row
    
    row["_quality_filter"] = True
    return row
```

## Dataset Balancing and Splitting

### Balancing Strategies

1. **By domain**: Ensure equal representation across domains
2. **By difficulty**: Balance easy, medium, and hard examples
3. **By source**: Ensure diversity across data sources
4. **By length**: Balance short, medium, and long examples

### Train/Val/Test Split

Use hash-based splitting for deterministic, reproducible splits:

```python
# Hash-based splitting ensures same examples always go to same split
# Useful for version control and reproducibility
```

## Export Formats

### JSONL Format (Recommended)

Each line is a JSON object:

```jsonl
{"instruction": "What is Python?", "input": "", "output": "Python is a programming language."}
{"instruction": "How do I install Python?", "input": "", "output": "You can install Python from python.org..."}
```

### Parquet Format (For Large Datasets)

More efficient for large datasets, preserves data types:

```yaml
- stage: save_parquet
  args: [ "${OUTPUT_PATH_DATASET_PARQUET}", "overwrite" ]
```

## Example Output: Dataset Statistics

After processing, the dataset should include:

- **Total examples**: 100,000+
- **Train/Val/Test split**: 80/10/10
- **Domain distribution**: Balanced across domains
- **Average instruction length**: 50-200 characters
- **Average output length**: 100-500 characters
- **Quality score**: > 0.8 (high quality)

## API Endpoints for Dataset Management

After processing, manage datasets via API:

#### Get Dataset Statistics

```http
GET /api/webrobot/api/datasets/{datasetId}/stats
```

#### Query Dataset Examples

```http
GET /api/webrobot/api/datasets/{datasetId}/query?sqlQuery=SELECT * FROM dataset WHERE split = 'train' AND domain = 'programming' LIMIT 10
```

