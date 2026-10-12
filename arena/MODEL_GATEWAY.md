# Agent-authored prompts and iteration controls — 0.5.0

This release connects a **provider-neutral gateway** to `PackageAttempts`.
The backend is a trusted controller object, not candidate code. Only a simulated
backend has been tested. A paid provider bridge and a CLI/config integration are
still needed; the original `iterate` command is unchanged.

## Package protocol

The package receives the author's task and environment passport as before. With
a gateway enabled, the passport contains its limits, current usage and latest
reply. To request model output the program emits exactly one JSON object:

```json
{"action":"model","request":{"id":"step-1","prompt":"The package writes this text itself.","max_output_tokens":256}}
```

It saves its own continuation state in its workspace and exits successfully.
The controller performs the model request outside Docker and relaunches the
package. The new passport contains `model_gateway.reply` with the request ID,
text and token usage. The package decides how to use that text; the controller
does not execute model-returned code or prescribe internal roles. It can issue
further requests with different IDs, including prompts assembled from its own
files or prior replies. To finish the iteration it emits:

```json
{"action":"complete"}
```

These relaunches belong to **one iteration**, not separate rate-limited iterations.
The external evaluator runs only after completion. Package structure and entry
are reloaded between launches. This is cooperative yield/resume, not an in-process
blocking API call. Arbitrary long-running processes are not preserved across yields.

## Controller setup

Pass `gateway_limits=GatewayLimits(...)`, `backend=...`, `backend_id="..."` and
optionally `rate=IterationRate(iterations=1, period_seconds=3600)` to
`PackageAttempts.run`. All limits are controller inputs. The backend implements:

- `count(prompt) -> int`: token count for the exact request it will send;
- `generate(prompt, max_output_tokens) -> dict` with exactly `text`, `input_tokens`,
  `output_tokens`. It must count all billed tokens, including reasoning output,
  obey the output cap, enforce its own request timeout and avoid hidden retries.

The backend chooses the fixed model and manages credentials. No credentials,
controller journal or other lineage files are mounted into the package.
Gateway integration does not yet implement money limits; before paid use the
bridge must integrate monetary accounting as well. Do not use an ad hoc paid
backend and assume the existing OpenAI iteration cost ledger applies here.

## Token accounting and recovery

`GatewayLimits` supplies call count, cumulative input, output and **combined**
token limits for the iteration, per-request input/output caps and prompt length.
Every request shares this one journal, regardless of internal roles or prompt
styles. The full input cap plus requested output allowance must fit before
generation; successful usage refunds the unused portion. This is conservative
admission control, not a forecast of actual token use.

The journal is checksummed, atomically replaced and flushed before generation.
A failed, malformed or interrupted generation retains its reservation. Repeating
an identical completed ID returns the saved response with no new call; changing
its content is rejected. Uncertain requests are never automatically repeated.
Journal settings/backend identity cannot change on reopening. It is an accidental
corruption check, not protection against a malicious host administrator.

Prompts and responses are retained in the controller journal for audit. Package
code does not receive keys, but experiment authors must still avoid putting secrets
in task text or model prompts.

`max_launches` bounds container relaunches, including repeated cached requests.
The runtime timeout is the dialogue's wall-time allowance; remaining time is
passed to each container launch. Synchronous backend work cannot be forcibly
interrupted by this loop; it must have its own timeout. If it overruns, no next
container launch occurs. Actual container execution of this protocol remains
unverified; the passing integration tests use simulated runtime and model backends.

## Iteration frequency

The optional rolling-window limit persists per lineage, reserves a slot before
creating a working copy and does not refund failed/aborted attempts. Setup failures
after reservation can also consume a slot. When full it returns `IterationRateLimited`
with a Unix UTC retry time; it neither sleeps nor schedules an automatic restart.
Settings cannot change or be omitted after establishing the rate. A backwards
clock change refuses reservations; forward clock changes follow host wall time.
This is a trusted-host clock, not a tamper-resistant timer.

There is no catch-up queue: after idle time only the configured window allowance
is available. Each lineage has its own rate, not a global three-lineage rate.
Manual one-round orchestration, common launch configuration, multi-iteration
total budgets, paid API bridge and production crash recovery remain upcoming.
