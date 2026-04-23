# PDF Chunking Reference

**Purpose:** Operational recipe for splitting long PDFs into manageable chunks when the `pdf-learnings` skill needs to process a paper in passes, or when the global `pdf` skill fails on a file that exceeds limits.

This is a **reference**, not a rule — the `pdf-learnings` and `pdf` skills are the preferred interfaces. Use this recipe only when those fail or when you need a predictable, script-friendly chunking pattern.

## When to use

- A PDF is too long for the `pdf-learnings` skill's native batching.
- You want deterministic page ranges named in a reproducible pattern.
- `pdf` skill errors on a specific file and you need a manual fallback.

## Core principle

**Read chunks one at a time.** Extract key information from each chunk into a notes file. Build understanding progressively. Don't hold all chunks in working memory simultaneously.

After scanning all chunks, identify the most relevant sections for deep reading. Skip appendices and references unless specifically needed.

## Recipe

### Step 1: Inspect the PDF

```bash
pdfinfo paper_name.pdf | grep "Pages:"
ls -lh paper_name.pdf
```

### Step 2: Split into 5-page chunks with Ghostscript

```bash
mkdir -p paper_name_chunks/
pages=$(pdfinfo paper_name.pdf | awk '/^Pages:/ {print $2}')
chunks=$(( (pages + 4) / 5 ))
for i in $(seq 0 $((chunks - 1))); do
  start=$((i*5 + 1))
  end=$(((i+1)*5))
  [ $end -gt $pages ] && end=$pages
  gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER \
     -dFirstPage=$start -dLastPage=$end \
     -sOutputFile="paper_name_chunks/paper_name_p$(printf '%03d' $start)-$(printf '%03d' $end).pdf" \
     paper_name.pdf 2>/dev/null
done
```

### Step 3: Process chunks progressively

- Read one chunk at a time via the `Read` tool with the chunk's path.
- Extract structured notes into a running notes file (per `master_supporting_docs/literature/reading_notes/README.md`).
- Don't attempt to read all chunks before taking notes — the point of chunking is to avoid context pressure.

## Error handling

**If a chunk fails to process:**

1. Note the problematic chunk (e.g., "chunk p021–025 failed").
2. Try re-splitting into 1–2 page pieces.
3. If still failing, skip and document the gap in the notes file.

**If Ghostscript splitting fails entirely:**

1. Verify Ghostscript is installed: `gs --version`.
2. Fallback: `pdftk paper.pdf burst output paper_%03d.pdf`.
3. If all else fails, ask the user to upload specific page ranges manually.

**If memory/token issues persist:**

1. Process only 2–3 chunks per session.
2. Ask the user which sections are most important and focus there.

## Interaction with primary-source-first

When reading a paper this way for the first time, the output is a reading-notes file in `master_supporting_docs/literature/reading_notes/` that then unlocks citations of that paper in load-bearing files (see `.claude/rules/primary-source-first.md`). The chunking workflow is upstream of notes production; the notes file is what the primary-source-first hook actually checks.
