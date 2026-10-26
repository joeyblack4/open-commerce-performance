# Engineering instructions for any coding agent working on OCP

Read `CODEX_HANDOFF.md`, `docs/01_STANDARDS_AND_DECISIONS.md`, and `docs/04_PRIVACY_SECURITY_AND_GAMEABILITY.md` before changes.

Order of precedence:
1. Official upstream protocol conformance and their governance rules; refresh versions at runtime.
2. Accurate evidence semantics, security, privacy and explicit opt-in.
3. Better consumer decisions and independent evaluation.
4. Reuse Black 4's existing Platform Control and Connector Hub after inspecting them.
5. Favor an incrementally shipping open implementation, not premature breadth.

Do not claim official UCP/ACP endorsement, create fictional merchant metrics as fact, infer hardware product reliability from order fulfillment, or submit public upstream proposals automatically. Any schema here marked `experimental` is OCP-authored only. Keep all real merchant interactions read-only until human approvals. When blocked, document blocker and proceed with synthetic data instead.

After each task: run tests; report evidence and new issues; no production deployments without an explicit approval. If another repository's AGENTS.md conflicts, follow the target repo's stricter requirements.
