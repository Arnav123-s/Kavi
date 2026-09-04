# Language-first teaching and repeated-answer diagnosis

## What changed

The live text learner previously encountered substantial arithmetic prose and
number questions before any measured English letter/word/sentence prerequisites.
It often emitted the same few incorrect numbers. Teacher-generated explanations
were also supervised after short answers, so most correction tokens rewarded
explanation continuation rather than answering the question. These are plausible
contributors, not an exhaustive explanation of the model's limitations.

The default `kavi.wave_cli run` now uses `LanguageFirstTeacher`. It resumes the
actual learned parameters and optimizer, but starts a separately recorded
language prerequisite ladder. Previous arithmetic attempts are preserved as
history, not credited as language competence. The core remains the same
66,880-parameter sparse recurrent network; no lookup-based answer engine or
pretrained answering model has been inserted.

## Exact implemented order

| Gate | What is taught | What passing would actually establish |
| --- | --- | --- |
| Letters | Four letters initially, then four more after a 90% familiar score, up to 52 upper/lowercase Latin letters | Familiar letter reproduction, then separately tested new two-/three-letter combinations |
| Written words | Joining letter sequences into a small fixed vocabulary | Spelling and new combinations of those words, not their complete meanings |
| Small quantities | `zero` through `nine`, corresponding to explicitly shown marks | Matching these ten names and quantities in either direction |
| Sentence roles | Simple `name has an object` statements | Binding a name/object in this controlled sentence family |
| Short passages | Two or three distinct name/object statements | Keeping these explicit facts separate within one prompt |
| Arithmetic | Numeration, addition/subtraction, multiplication, division, fractions, decimals, square roots, proportion, combinations | Narrow English questions from the admitted De Morgan sections |

Names in exercises are arbitrary labels, not biographical claims. Four object
words and ten quantity words do not constitute a general English vocabulary.
Original-language teaching and exams for the other languages in the global
catalog, unrestricted reading, and advanced fields still require implementation
and their own evaluations. No degree or master's-level claim is available.

## Learning objective

`WaveLearner.learn_answers` handles at most four independent examples per
update. Each row has its own recurrent state. The prompt and supplied answer
fit within 256 UTF-8 bytes. Unlike the paragraph method, this bounded answer
update propagates gradients through the entire prompt without a 64-byte
truncation boundary. For prefix `p`, answer bytes `a` (including newline), and
batch size `B`:

\[
L_{answer}=-\frac1B\sum_{b=1}^B\frac1{|a_b|}
\sum_{t=1}^{|a_b|}\log P_\theta(a_{b,t}\mid p_b,a_{b,<t}).
\]

Prefix and padding positions receive no direct target loss. Each example has
equal weight regardless of answer length. Gradients still pass through prefix
processing and update the model's encodings, transmission strengths, phases,
gates and readout. Adam, finite-gradient checking and clipping remain in the
core. Parameter count does not grow when examples are added.

Explanations are visible teacher feedback, but are no longer appended to the
short-answer target. This does **not** establish that Kavi understands those
explanations. Original educational passages have a separate next-byte training
objective after the letter prerequisite. Unicode records at the letter stage
are teacher references, not a claim that Kavi reads metadata or understands a
grammar book. Answer practice receives repeated balanced updates rather than
being overwhelmed by pages of prose in each round.

## Evaluation and remediation

1. Present the appropriate verified source packet and within-stage practice.
2. Generate answers using only question bytes. The grader holds the expected
   answers separately. Record the full answer, correctness and output diversity.
3. Check familiar practice. A 90% familiar score is **not** generalization.
4. Only then draw unused questions, followed by harder unused questions. Both
   require at least 90%. This delays consumption of finite test pools until the
   learner is ready to attempt them.
5. Recheck every protected, previously correct example before promotion. Any
   regression rolls parameters/optimizer back to the pre-round witness.
6. On failure, revisit the immediate prerequisite, display corrections, practise
   again, and rotate through the current stage's reviewed source packets. A
   corrected test question is thereafter familiar, never relabeled unseen.

Practice may repeat: repetition is teaching. Exact question fingerprints prevent
repeated questions from receiving fresh-test credit. If an unused test pool
is exhausted, the teacher logs that limitation and continues familiar practice;
it does not crash or manufacture a new-test pass. A broader reviewed question
family is then needed to obtain more independent evidence. Protected tests are
finite and cannot guarantee universal retention or absence of forgetting.

## Sources and fetching

The exact URLs, private paths, complete-document hashes, original-language
status and selected line ranges are in
[`language-source-packets.json`](../curriculum/language-source-packets.json).
Admission is separately checked against the source manifest.

- [The Unicode Consortium, Unicode 17.0 character data](https://www.unicode.org/Public/17.0.0/ucd/UnicodeData.txt): original character identifiers, Latin letter names and case mappings. This is a technical standard, not a language textbook.
- [William Malone Baskervill and James Witt Sewell, An English Grammar](https://www.gutenberg.org/ebooks/14006): original English definitions from sections 2, 336 and 340. The full book targets older students; only selected definitions guide these basic lessons. Historic English grammar claims are not universal rules for all languages.
- [Augustus De Morgan, Elements of Arithmetic](https://www.gutenberg.org/ebooks/68662): original English number-name tables, numeration definitions, and the nine Book I sections already admitted separately.

The selected records and excerpts were inspected; the books are not represented
as exhaustively reviewed. Classroom questions are generated from these topics,
not quotations or questions purportedly copied from the authors. No stories or
poems are added as filler. This release does not claim that ingesting complete
books is equivalent to learning their contents.

Missing admitted files may be fetched anonymously from the exact reviewed HTTPS
URLs, at most 3 MB each. Redirects to another host are rejected before following
them. Changed fingerprints require review; cached material is not silently
overwritten. No account, credentials, payment, paywall bypass, arbitrary web
crawl, or execution of document contents is used. Verified cached sources are
reused; that is not falsely reported as acquiring a new source. Unavailable
sources trigger a 30-second, interruptible retry delay.

## Live operation and limits

```powershell
.\scripts\start-live-learning.ps1 -Resume 'runs\previous-run'
```

The `Kavi SCHOOL` terminal tabs show lessons, actual answers, learned link
parameters, optimizer updates, grades and chat/controls. A controller tab owns
the process. In Chat, `Copy a` uses the same prompt wrapper as a lesson.
`/teach Copy a => a || Keep the same letter.` supplies an owner correction.
`/pause`, `/resume` and `/stop` remain available; `/quit` closes only Chat.

The start script uses `--keep-available`: unsuccessful rounds continue teaching
instead of changing to an idle chat service after 48 attempts. Without that
flag, `--max-rounds` bounds a test run. The explicit wall-clock budget still
applies (at most 24 hours per launched session). This is not an immortal process
or automatic OS startup service. At the end of implemented gates, unimplemented
languages/fields cannot be marked complete by repetition.

Two numerical CPU threads, batches no larger than four and the existing graph
budget are retained. No GPU, temperature threshold or hardware protection is
changed. A free-disk check stops the run below 2 GB free. Logs and archived
checkpoints grow outside the active model. Durable snapshots occur every three
minutes, at promotion, conversations and clean exit; the old run is preserved.
An interrupted partial round may repeat after resume, as recorded in session
metadata. No unrelated application is closed.

## What the evidence does not establish

The diagnosis, measured training-fit comparison and first live results are in
the [experiment record](../experiments/2026-09-04-language-first-repair.md).
Software tests verify engineering properties, not intelligence. A four-letter
or 52-letter fit does not prove language understanding, arithmetic reasoning,
long-range context, quantum advantage, automatic graph restructuring, or the
ability to finish the proposed global curriculum. Architecture limitations
remain possible and must be investigated with separate held-out measurements.
