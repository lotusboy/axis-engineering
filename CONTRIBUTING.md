# Contributing to Axis Engineering

Axis Engineering is designed to be cross-platform and domain-agnostic. Currently, the experimental evidence in `experiment-results.md` is weighted heavily toward Salesforce and Azure environments.

We actively welcome contributions that test the methodology in other domains, particularly:
- Frontend frameworks (React, Vue, etc.)
- Data engineering and pipelines (Spark, Airflow, dbt)
- Mobile development (iOS, Android, React Native)
- Systems programming (Rust, Go, C++)
- DevOps and Infrastructure as Code

## How to Contribute an Experiment

If you have run an Axis Engineering Two-Pass Review or a Triangle Protocol experiment, you can submit your results via a Pull Request.

### 1. Run the Experiment
Run your selected protocol against a piece of code or a design document. 

**Important:** Please ensure that any code or designs you use are either public/open-source or that you have heavily redacted any proprietary or confidential information before submission.

### 2. Format the Output
Follow the structure of existing applications in `experiment-results.md`. 
Include the **Scoring Rubric** at the bottom of your submission to ensure standardisation:

```markdown
### Review Rubric & Metrics
- **P0 / P1 count:** [Number of critical and high findings]
- **Rediscovery %:** [Overlap with previous/baseline runs]
- **Model used:** [e.g., Claude 3.7 Sonnet, GPT-5.1-Codex Max High, Gemini 3.1 Pro High Thinking]
- **Estimated Elapsed Time:** [e.g., 45 seconds, 3 minutes]
- **Estimated Cost/Tokens:** [e.g., ~$0.10, ~120k tokens]
```

### 3. Submit a Pull Request
Add your writeup to `experiment-results.md` (incrementing the Application number) and place your raw, redacted AI outputs in the `testing/` directory if you wish to share them. 

Submit your PR against the `main` branch. 

By contributing, you agree that your contributions will be licensed under the project's [CC BY 4.0](LICENSE) license.
