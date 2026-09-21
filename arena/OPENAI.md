# OpenAI provider — Arena 0.3.0

The iterative runner now accepts `model = "openai/<API-model-id>"` alongside
`scripted-v1`. It uses the Responses API with canonical Arena function tools.
The adapter and complete iteration are tested with simulated HTTP responses;
**a live paid API run has not yet been validated**. The integer-sum task remains
a public plumbing demonstration, not an IAH experiment.

## Configure

Copy `openai.example.toml` to your own configuration. It deliberately fails
validation until you fill all three model IDs and both token price fields.
Use an API model accessible to your account that supports Responses function
calling and the input-token-count endpoint. No model is selected automatically.

- Set every lineage's `model` to `openai/<your-model-id>`.
- Set verified input/output prices in **integer micro-USD per million tokens**:
  a price of USD 2.50 per million becomes `2500000`. This is a unit example,
  not a quote for a model. Shared rates must conservatively cover every configured
  model and applicable input-length tier. Cache discounts are ignored.
- Review `[total]` (per lineage), `[attempt]`, and `[openai]` request limits.
  All supplied budgets are editable demonstration values. Example monetary
  budgets are USD 1 per lineage, not a commitment to an experiment budget.
- Use a locally available digest-pinned Python image and a running Linux Docker
  engine. Real providers are refused in trusted-local mode.
- Supply `OPENAI_API_KEY` to the controller's environment via your local secret
  mechanism. Do not put the key in TOML, Git, candidate files, or CLI arguments.
  `key_env` can name another variable. Arena never forwards it to candidate Docker
  containers. A ChatGPT subscription is not an API credential.

From `arena/`, with `PYTHONPATH=src` and the credential already set:

```powershell
python -m iah_arena iterate --config my-openai.toml --output-dir exports/api-pilot --steps 1
python -m iah_arena iteration-status --run-dir exports/api-pilot
python -m iah_arena resume-iterations --run-dir exports/api-pilot --steps 1
```

Review the first attempt's history, events, usage and candidate before running
continuously. The same frozen-configuration and checkpoint rules in
[ITERATIONS.md](ITERATIONS.md) apply. Source changes require a new run.

## Accounting and failures

Before generation, the controller requests the server's count of the complete
input, including accumulated tool results and tool schemas. If that count exceeds
`max_input_tokens`, no generation is sent. Before each generation the ledger must
fit the **full configured input cap plus output cap and calculated cost**, not
just the preliminary count. `max_output_tokens` is also sent to the API.
Successful turns record the API's input/output usage, including reasoning output
tokens, and cost calculated from configured rates. These costs are estimates,
not invoices or provider-enforced account spend limits.

An HTTP failure, timeout, incomplete response, missing usage or malformed function
call after sending generation retains the full request reservation and fails the
attempt. There are no automatic HTTP retries. Consequently ledger usage can exceed
actual billed usage. A process crash retains the full attempt reservation as in
0.2.0. Token-count requests are not counted as model-generation calls. A failure
before generation does not consume generation allowance.

Input counting and generation are separate API operations; if reported generation
usage unexpectedly exceeds a configured cap, the attempt fails and retains its
reservation. That discrepancy is not an exact invoice reconciliation. Use provider
account controls too when establishing a financial limit.

Each attempt has a new adapter and in-memory conversation. Continuations replay
only that attempt's messages, reasoning items and tool outputs with `store=false`;
there is no shared `previous_response_id`. Encrypted reasoning content is requested
for stateless reasoning-model continuation. This does not imply zero provider-side
retention; account data policies still apply. The full conversation is bounded by
the request input cap; it is not silently truncated or compacted.

Only custom Arena function tools are sent; no web, shell, remote MCP or other
provider-hosted tools are enabled. API transport errors are sanitized before they
reach persisted events. The transport targets `https://api.openai.com/v1/` and
refuses redirects. The model still sees its candidate code and test feedback,
which are transmitted to OpenAI for both token counting and generation.

## Official references

- [Function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Counting input tokens](https://developers.openai.com/api/docs/guides/token-counting)
- [Reasoning models](https://developers.openai.com/api/docs/guides/reasoning)

The scientific task, held-out evaluation, and handling of runtime startup noise
remain separate unfinished work. Connecting a model does not validate IAH.
