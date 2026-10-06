# Modelling integrity and feature boundary

## Core Gupio model

The primary model predicts `Dropout`, `Enrolled` or `Graduate` from information available at enrollment.

The following 12 fields are excluded by code before any split/model training:

- Curricular units 1st sem (credited)
- Curricular units 1st sem (enrolled)
- Curricular units 1st sem (evaluations)
- Curricular units 1st sem (approved)
- Curricular units 1st sem (grade)
- Curricular units 1st sem (without evaluations)
- Curricular units 2nd sem (credited)
- Curricular units 2nd sem (enrolled)
- Curricular units 2nd sem (evaluations)
- Curricular units 2nd sem (approved)
- Curricular units 2nd sem (grade)
- Curricular units 2nd sem (without evaluations)

## Semester coaching extension

The teacher/student coaching feature is intentionally separate. It can use:

- previous-semester average,
- current Internal 1 and Internal 2,
- assignment score,
- lab score,
- attendance,
- backlog count.

The extension is a transparent weighted scenario engine. It is not trained on the Gupio final target and does not contaminate the primary model. Its "pass with support" number is a what-if scenario, not a causal claim.
