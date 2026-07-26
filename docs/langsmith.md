# LangSmith Monitoring

LangSmith can trace LangGraph workflow execution:

- node execution
- conditional transitions
- interrupts and resumes
- timings
- tool calls

## Activation

Set these variables in `.env`:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=real-estate-marketing-agent
```

When `LANGCHAIN_TRACING_V2=false` or no API key is configured, the application runs normally without tracing.

## Workflow Trace

Each `POST /drafts/generate` creates a trace tied to the workflow `thread_id`.

```text
thread_id: abc-123
├─ generate_facebook_node
├─ generate_instagram_node
├─ aggregate_drafts_node
├─ wait_for_approval_node -> interrupted
└─ publish nodes after resume
```

The same `thread_id` is used after approval so the initial generation and later publication remain correlated.

LangSmith UI: https://smith.langchain.com
