"""RALPH Loop orchestrator: H -> P -> A -> E -> R -> L cycle."""

import asyncio
import json
import logging
import time
from pathlib import Path

import yaml

from config.settings import settings
from src.personas.loader import load_personas, get_cluster_map
from src.evaluation.aggregator import aggregate_results
from src.ralph.hypothesize import hypothesize
from src.ralph.plan import plan_conversations
from src.ralph.act import act_all
from src.ralph.evaluate_stage import evaluate_all
from src.ralph.reason import reason
from src.ralph.learn import learn

logger = logging.getLogger(__name__)

# Try to use rich for progress output
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    _console = Console()
    _has_rich = True
except ImportError:
    _console = None
    _has_rich = False


def _print(msg: str):
    """Print with rich if available, else plain print."""
    if _has_rich and _console:
        _console.print(msg)
    else:
        print(msg)


def _load_product(product_path: str = "config/product.yaml") -> dict:
    """Load product info from a YAML config path."""
    path = Path(product_path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_strategy_ledger() -> dict | None:
    """Load strategy ledger if it exists."""
    path = Path("strategy_ledger.json")
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load strategy_ledger.json: %s", exc)
    return None


def _load_strategy_prompt() -> str:
    """Load current strategy_prompt.md."""
    # Try local copy first
    local_path = Path("strategy_prompt.md")
    if local_path.exists():
        return local_path.read_text(encoding="utf-8")
    # Fallback to prompts dir
    path = Path(settings.PROMPTS_DIR) / "strategy_prompt.md"
    return path.read_text(encoding="utf-8")


def _save_json(path: Path, data):
    """Save data as JSON to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def run_ralph_loop(run_id: str = None, product_path: str = "config/product.yaml") -> dict:
    """Orchestrate full H->P->A->E->R->L cycle for RALPH_ITERATIONS rounds.

    Each iteration feeds the previous learnings into the next Hypothesize step,
    creating an inner self-improvement loop within a single simulation run.

    Args:
        run_id: Optional run ID. Auto-generated if not provided.

    Returns:
        Summary dict from the final iteration with run_id and all results.
    """
    if run_id is None:
        run_id = f"run_{int(time.time())}"

    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    max_iters = settings.RALPH_ITERATIONS
    _print(f"[bold cyan]RALPH Loop starting: {run_id} ({max_iters} iterations)[/bold cyan]"
           if _has_rich else f"=== RALPH Loop starting: {run_id} ({max_iters} iterations) ===")

    # Load inputs
    product = _load_product(product_path)
    strategy_ledger = _load_strategy_ledger()
    strategy_prompt_text = _load_strategy_prompt()

    # Load personas
    _print("[bold]Loading personas...[/bold]" if _has_rich else "Loading personas...")
    personas = load_personas(settings.PERSONAS_DIR, settings.RALPHTHON_MODE)
    _print(f"  Loaded {len(personas)} personas (mode={settings.RALPHTHON_MODE})")

    cluster_map = get_cluster_map(personas)
    _print(f"  Found {len(cluster_map)} clusters")

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(settings.concurrent)

    # State carried across iterations
    prev_learnings = None
    summary = None

    for iteration in range(1, max_iters + 1):
        iter_tag = f"[{iteration}/{max_iters}]"
        _print("")
        _print(f"[bold cyan]{'='*60}[/bold cyan]" if _has_rich else "=" * 60)
        _print(f"[bold cyan]RALPH Iteration {iter_tag}[/bold cyan]"
               if _has_rich else f"RALPH Iteration {iter_tag}")
        _print(f"[bold cyan]{'='*60}[/bold cyan]" if _has_rich else "=" * 60)

        iter_dir = run_dir / f"iter_{iteration}"
        iter_dir.mkdir(parents=True, exist_ok=True)

        # === H: Hypothesize ===
        _print(f"{iter_tag} [bold green]H: Generating strategies...[/bold green]"
               if _has_rich else f"{iter_tag} H: Generating strategies...")
        strategies = await hypothesize(
            product=product,
            strategy_ledger=strategy_ledger,
            learnings=prev_learnings,
            num_strategies=settings.STRATEGIES_PER_RUN,
        )
        _print(f"  Generated {len(strategies)} strategies: {[s['strategy_id'] for s in strategies]}")
        _save_json(iter_dir / "strategies.json", strategies)

        # === P: Plan ===
        _print(f"{iter_tag} [bold green]P: Planning conversations...[/bold green]"
               if _has_rich else f"{iter_tag} P: Planning conversations...")
        pairs = plan_conversations(strategies, personas)
        _print(f"  Planned {len(pairs)} conversations")

        # === A: Act ===
        _print(f"{iter_tag} [bold green]A: Running conversations...[/bold green]"
               if _has_rich else f"{iter_tag} A: Running conversations...")
        t_start = time.time()
        sessions = await act_all(pairs, product, settings.MAX_TURNS, semaphore)
        t_elapsed = time.time() - t_start
        _print(f"  Completed {len(sessions)} conversations in {t_elapsed:.1f}s")

        # Save transcripts per strategy per persona
        transcripts_dir = iter_dir / "transcripts"
        for session in sessions:
            sid = session.get("strategy_id", "unknown")
            pid = session.get("persona_id", "unknown")
            transcript_path = transcripts_dir / sid / f"{pid}.json"
            _save_json(transcript_path, session)

        # === E: Evaluate ===
        _print(f"{iter_tag} [bold green]E: Evaluating conversations...[/bold green]"
               if _has_rich else f"{iter_tag} E: Evaluating conversations...")
        t_start = time.time()
        evaluations = await evaluate_all(sessions, strategies, semaphore)
        t_elapsed = time.time() - t_start
        _print(f"  Evaluated {len(evaluations)} conversations in {t_elapsed:.1f}s")
        _save_json(iter_dir / "evaluations.json", evaluations)

        # === R: Reason ===
        _print(f"{iter_tag} [bold green]R: Reasoning about results...[/bold green]"
               if _has_rich else f"{iter_tag} R: Reasoning about results...")
        reason_output = await reason(evaluations, sessions)
        _save_json(iter_dir / "reason.json", reason_output)
        _print(f"  Found {len(reason_output.get('winning_patterns', []))} winning patterns, "
               f"{len(reason_output.get('losing_patterns', []))} losing patterns")

        # === L: Learn ===
        _print(f"{iter_tag} [bold green]L: Extracting learnings...[/bold green]"
               if _has_rich else f"{iter_tag} L: Extracting learnings...")
        learnings_output = await learn(reason_output, strategy_prompt_text)
        _save_json(iter_dir / "learnings.json", learnings_output)
        _print(f"  Extracted {len(learnings_output.get('learnings', []))} learning points")

        # === Aggregate ===
        _print(f"{iter_tag} [bold green]Aggregating results...[/bold green]"
               if _has_rich else f"{iter_tag} Aggregating results...")
        summary = aggregate_results(evaluations, personas, strategies)
        summary["run_id"] = run_id
        summary["iteration"] = iteration

        iteration_result = {
            "iteration_id": iteration,
            "run_id": run_id,
            "strategies": strategies,
            "evaluations": evaluations,
            "reason": reason_output,
            "learnings": learnings_output,
            "summary": summary,
        }
        _save_json(iter_dir / "summary.json", iteration_result)

        # Print iteration result
        _print(f"  {iter_tag} avg_score={summary['avg_score']}, "
               f"cluster_coverage={summary['cluster_coverage']}%, "
               f"best={summary['best_strategy']}")

        # Carry learnings to next iteration
        prev_learnings = learnings_output

    # === Final output (from last iteration) ===
    # Also save top-level summary for the whole run
    _save_json(run_dir / "summary.json", iteration_result)

    # Symlink/copy final transcripts & evaluations to run root for dashboard compat
    import shutil
    for name in ["strategies.json", "evaluations.json", "reason.json", "learnings.json"]:
        src = iter_dir / name
        dst = run_dir / name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    final_transcripts = run_dir / "transcripts"
    if not final_transcripts.exists() and (iter_dir / "transcripts").exists():
        shutil.copytree(iter_dir / "transcripts", final_transcripts)

    # Print grep-friendly output
    print(f"avg_score:{summary['avg_score']}")
    print(f"cluster_coverage:{summary['cluster_coverage']}")
    print(f"best_strategy:{summary['best_strategy']}")

    _print("")
    if _has_rich:
        _print(f"[bold green]✓ RALPH Loop complete: {run_id} ({max_iters} iterations)[/bold green]")
        _print(f"  avg_score: [bold]{summary['avg_score']}[/bold]")
        _print(f"  cluster_coverage: [bold]{summary['cluster_coverage']}%[/bold]")
        _print(f"  best_strategy: [bold]{summary['best_strategy']}[/bold]")
        if summary.get("cluster_scores"):
            _print("  cluster_scores:")
            for cluster, score in sorted(summary["cluster_scores"].items()):
                _print(f"    {cluster}: {score}")
        if summary.get("outcome_distribution"):
            _print("  outcomes:")
            for outcome, count in sorted(summary["outcome_distribution"].items()):
                _print(f"    {outcome}: {count}")
    else:
        print(f"=== RALPH Loop complete: {run_id} ({max_iters} iterations) ===")
        print(f"  avg_score: {summary['avg_score']}")
        print(f"  cluster_coverage: {summary['cluster_coverage']}%")
        print(f"  best_strategy: {summary['best_strategy']}")

    _print(f"\nResults saved to: {run_dir}/")

    return summary
