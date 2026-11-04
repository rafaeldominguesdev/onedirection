#!/usr/bin/env python3
"""Confere os resumos de tests/evals/results/ (ou de outra pasta): metadados coerentes e números que fecham.

    python3 tests/evals/check_results.py [PASTA]

Sai com 1 e lista os problemas se algum resumo:
  - não for o schema 2, ou não disser se é rodada ao vivo ("live") ou replay;
  - for replay e disser que o modelo rodou, tiver custo de replay diferente de zero, ou não separar
    o commit da rodada original (source_commit) do commit do corretor (grader_commit);
  - declarar um modelo que não bate com o nome do arquivo (X-sonnet.json só com modelo sonnet);
  - tiver passed/total/custo que não fecham com a lista de cenários;
  - tiver versão do plugin diferente do prefixo do nome do arquivo;
  - for replay e não bater com a rodada ao vivo de mesma versão e modelo (commit e custo originais);
  - tiver caminho absoluto da máquina de alguém (/Users/, /home/, /private/, /var/folders/).
Só lê arquivos: não roda modelo, não usa rede.
"""
import json
import re
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent / "results"
NAME = re.compile(r"^(?P<version>\d+\.\d+\.\d+)-(?P<model>[a-z0-9]+)(?P<replay>-replay)?\.json$")
LOCAL_PATH = re.compile(r"(/Users/|/home/|/private/|/var/folders/)")
REQUIRED = ["schema", "kind", "model_executed", "plugin_version", "source_commit", "grader_commit",
            "models", "date", "passed", "total", "original_cost_usd", "scenarios"]


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)


def check_file(path: Path, live_by_key: dict) -> list:
    errs = []
    try:
        d = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [f"não é JSON válido: {exc}"]
    m = NAME.match(path.name)
    if not m:
        errs.append("nome fora do padrão VERSÃO-MODELO[-replay].json")
    missing = [k for k in REQUIRED if k not in d]
    if missing:
        return errs + [f"faltam campos: {missing}"]
    if d["schema"] != 2:
        errs.append(f"schema {d['schema']!r}, esperado 2")
    if d["kind"] not in ("live", "replay"):
        errs.append(f"kind {d['kind']!r}: tem que ser live ou replay")

    sc = d["scenarios"]
    if d["total"] != len(sc):
        errs.append(f"total={d['total']} mas há {len(sc)} cenários")
    if d["passed"] != sum(1 for s in sc if s.get("pass")):
        errs.append(f"passed={d['passed']} mas {sum(1 for s in sc if s.get('pass'))} cenários passaram")
    for s in sc:
        if bool(s.get("pass")) == bool(s.get("fails")):
            errs.append(f"cenário {s.get('name')}: pass={s.get('pass')} não bate com fails={s.get('fails')}")
    cost = round(sum(s.get("cost_usd", 0) for s in sc), 2)
    if abs(cost - d["original_cost_usd"]) > 0.06:
        errs.append(f"original_cost_usd={d['original_cost_usd']} mas os cenários somam {cost}")
    if "total_cost_usd" in d:
        errs.append("total_cost_usd é ambíguo num replay: use original_cost_usd (e replay_cost_usd no replay)")

    if not d["models"]:
        errs.append("models vazio: o modelo tem que vir do init dos transcripts")
    if m:
        if d["plugin_version"] != m["version"]:
            errs.append(f"plugin_version={d['plugin_version']} mas o arquivo diz {m['version']}")
        wrong = [x for x in d["models"] if m["model"] not in x.lower()]
        if wrong:
            errs.append(f"modelo(s) {wrong} num arquivo de {m['model']}")
        if d.get("model_requested") and m["model"] not in str(d["model_requested"]).lower():
            errs.append(f"model_requested={d['model_requested']!r} num arquivo de {m['model']}")
        if bool(m["replay"]) != (d["kind"] == "replay"):
            errs.append(f"kind={d['kind']} não bate com o nome do arquivo")

    if d["kind"] == "live":
        if d["model_executed"] is not True:
            errs.append("rodada ao vivo com model_executed diferente de true")
        if "replay_cost_usd" in d:
            errs.append("rodada ao vivo não tem replay_cost_usd")
    if d["kind"] == "replay":
        if d["model_executed"] is not False:
            errs.append("replay com model_executed diferente de false: replay não executa o modelo")
        if d.get("replay_cost_usd") != 0:
            errs.append(f"replay_cost_usd={d.get('replay_cost_usd')!r}: replay não chama a API, custa 0")
        if not d["source_commit"] or not d["grader_commit"]:
            errs.append("replay precisa de source_commit (rodada original) e grader_commit (corretor)")
        elif d["source_commit"] == d["grader_commit"]:
            errs.append("replay com source_commit == grader_commit: ou o corretor não mudou, ou os commits foram confundidos")
        if m:
            live = live_by_key.get((m["version"], m["model"]))
            if live is None:
                errs.append("replay sem a rodada ao vivo correspondente na mesma pasta")
            else:
                if live.get("source_commit") != d["source_commit"]:
                    errs.append(f"source_commit={d['source_commit']} mas a rodada ao vivo foi em {live.get('source_commit')}")
                if abs(live.get("original_cost_usd", -1) - d["original_cost_usd"]) > 0.01:
                    errs.append("original_cost_usd diferente do da rodada ao vivo")
                if sorted(s["name"] for s in live["scenarios"]) != sorted(s["name"] for s in sc):
                    errs.append("cenários diferentes dos da rodada ao vivo")

    leaks = sorted({s for s in strings(d) if LOCAL_PATH.search(s)})
    if leaks:
        errs.append(f"caminho local no resumo: {leaks[:2]}")
    return errs


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    files = sorted(folder.glob("*.json"))
    if not files:
        sys.exit(f"nenhum resumo em {folder}")
    live_by_key = {}
    for f in files:
        m = NAME.match(f.name)
        if m and not m["replay"]:
            try:
                live_by_key[(m["version"], m["model"])] = json.loads(f.read_text())
            except (OSError, json.JSONDecodeError):
                pass
    bad = 0
    for f in files:
        errs = check_file(f, live_by_key)
        print(f"{'ok  ' if not errs else 'FAIL'} {f.name}")
        for e in errs:
            print(f"       - {e}")
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
