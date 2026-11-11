# Authoring Guide: Analytic Cases

A good case reflects an **authentic deployment pattern** and contains a **realistic failure mode** that a careless model or analyst would fall into.

## Steps
1. **Pick the scenario type** (automated triage, enrichment, analysis at scale) from `data/taxonomy.json`.
2. **Pick the failure mode** you want to test (for example nonresponse bias, dropped records, unit error, drift, over-refusal).
3. **Write the prompt as a short real situation** with concrete numbers, not an abstract question.
4. **Define 3 or more checks**, each tied to one evaluation area:
   - `source_handling`: uses only the given data, cites correctly, does not invent
   - `reasoning`: correct computation or conclusion
   - `limitations_awareness`: names uncertainty, bias or missing evidence
   - `practical_utility`: gives a next step that fits a real pipeline
5. **Write a strong and a weak reference answer.** The strong one must pass every check and the weak one must fail most of them; the tests enforce this.
6. **Add control cases** that a model should decline (for example re-identifying people). They stop a model from scoring well by simply never refusing.

## Quality checklist
- [ ] The numbers in the prompt are internally consistent (recompute them)
- [ ] There is one defensible answer, and the checks accept different wordings (`any_of` lists)
- [ ] A forbidden-content check (`must_not_include`) guards against the typical wrong answer
- [ ] Legitimate cases with sensitive-sounding words are included on purpose, to detect over-refusal
- [ ] The case does not require private or classified information

## Example
Case AC-03: a join of 1,000,000 customers and 998,200 orders produces 994,100 rows. The failure mode is silently dropped records; the checks look for named causes (inner join, unmatched keys, nulls), reconciliation of counts and a rule to block publication.
