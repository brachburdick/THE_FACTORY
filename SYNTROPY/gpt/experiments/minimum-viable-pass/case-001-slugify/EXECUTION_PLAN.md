# Execution Plan: Case 001

**Purpose:** Run the `case-001-slugify` test case from a clean start and compare `L1`, `L2`, and `L3` on the same trivial task.

---

## Important Note

The current [slugify.py](./slugify.py) file is a solved reference implementation.

Do **not** run the experiment in-place against that file.

For a real run, start from a fresh directory and use [slugify.stub.py](./slugify.stub.py) as the initial `slugify.py`.

---

## Materials

Use these files as the source of truth:

- [TASK.md](./TASK.md)
- [test_slugify.py](./test_slugify.py)
- [slugify.stub.py](./slugify.stub.py)
- [RUN_TEMPLATE.md](./RUN_TEMPLATE.md)

Use these supporting docs for the layer definitions:

- [STARTING_POINT_MODEL.md](../STARTING_POINT_MODEL.md)
- [README.md](../README.md)

---

## Goal

Determine the shallowest useful starting layer that is still reliable enough to solve a trivial software task with real verification.

The comparison to run is:

1. `L1`
2. `L2`
3. `L3`

---

## Shared Rules

Apply these rules to every run:

1. Start from a fresh working directory.
2. Do not manually edit code during the model run.
3. Let the model edit only `slugify.py`.
4. Preserve the prompt or transcript used for the run.
5. Run the verifier exactly as specified:

```bash
python3 -m unittest -v
```

6. Record results in a fresh copy of [RUN_TEMPLATE.md](./RUN_TEMPLATE.md).
7. If you compare layers, keep the task, tests, and initial starter file identical across all runs.

---

## Preparation

Create a clean workspace for each layer under test.

Example for `L2`:

```bash
mkdir -p /tmp/syntropy-case-001-l2
cp /Users/brach/Documents/THE_FACTORY/SYNTROPY/gpt/experiments/minimum-viable-pass/case-001-slugify/TASK.md /tmp/syntropy-case-001-l2/
cp /Users/brach/Documents/THE_FACTORY/SYNTROPY/gpt/experiments/minimum-viable-pass/case-001-slugify/test_slugify.py /tmp/syntropy-case-001-l2/
cp /Users/brach/Documents/THE_FACTORY/SYNTROPY/gpt/experiments/minimum-viable-pass/case-001-slugify/slugify.stub.py /tmp/syntropy-case-001-l2/slugify.py
cp /Users/brach/Documents/THE_FACTORY/SYNTROPY/gpt/experiments/minimum-viable-pass/case-001-slugify/RUN_TEMPLATE.md /tmp/syntropy-case-001-l2/RUN.md
cd /tmp/syntropy-case-001-l2
```

Repeat that for `L1` and `L3` using separate directories.

---

## Layer Instructions

Use the same task for every run and vary only the model layer instructions.

### L1 Prompt

Use this when testing `L1`:

```text
You are solving a small software task.

Read TASK.md and implement the solution in slugify.py.

Requirements:
- keep the acceptance criteria in view
- do not change test_slugify.py
- run python3 -m unittest -v when you think you are done
- report whether the tests passed
```

### L2 Prompt

Use this when testing `L2`:

```text
You are solving a small software task using the SYNTROPY L2 starting model.

Read TASK.md and implement the solution in slugify.py.

Rules:
1. Restate the goal and acceptance criteria before changing code.
2. Create a plan with at most 3 steps.
3. Execute one step at a time.
4. After each meaningful code change, run python3 -m unittest -v.
5. If verification fails, do one local replan and try again.
6. Do not change test_slugify.py.
7. Finish by reporting whether the acceptance criteria were met, what verification was run, and whether a replan was needed.
```

### L3 Prompt

Use this when testing `L3`:

```text
You are solving a small software task using the SYNTROPY L3 light decomposition model.

Read TASK.md and implement the solution in slugify.py.

Rules:
1. Restate the goal and acceptance criteria before changing code.
2. Create a plan with at most 3 steps.
3. For each step, write a lightweight leaf contract with:
   - objective
   - artifact
   - verifier
   - dependency
4. Execute one step at a time.
5. After each meaningful code change, run python3 -m unittest -v.
6. If verification fails, do one local replan and try again.
7. Do not change test_slugify.py.
8. Finish by reporting whether the acceptance criteria were met, what verification was run, and whether a replan was needed.
```

---

## Run Procedure

Execute the following for each layer:

1. Prepare a fresh run directory.
2. Give the model the layer-specific prompt.
3. Let the model read `TASK.md` and edit only `slugify.py`.
4. Let the model run the verifier according to its layer rules.
5. Save the final `slugify.py`.
6. Fill out `RUN.md` using the run template.

---

## Metrics To Capture

At minimum, record:

- `pass` or `fail`
- total tests passed
- whether a replan was used
- number of files edited
- number of extra artifacts generated
- time to green tests
- subjective overhead

If you have the logs available, also capture:

- number of verifier runs
- prompt length or token footprint
- whether the model drifted from the acceptance criteria

---

## Decision Rule

Use this decision rule after running `L1`, `L2`, and `L3`:

1. If `L1` fails and `L2` passes, start at `L2`.
2. If `L1` and `L2` both pass, prefer the one with lower overhead unless `L2` gives noticeably better reliability or discipline.
3. If `L3` does not materially outperform `L2` on this trivial case, do not start at `L3`.
4. Only move deeper into structure when the simpler layer stops being sufficient.

This is the core heuristic:

> start at the shallowest layer that reliably clears the current task family.

---

## What Success Means

For this case, success means:

- the model satisfies the acceptance criteria
- the test suite passes
- the process feels light enough to repeat

This case is not meant to validate the whole SYNTROPY idea.

It is only meant to establish a practical floor for iteration.
