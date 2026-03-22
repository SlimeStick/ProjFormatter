"""
Parsing and boolean simplification helpers for MSBuild Condition attributes.

Supported comparison form: '$(PropertyName)'=='value' or '$(PropertyName)'!='value'
(with single quotes as in typical MSBuild projects).

Comparisons are located by scanning for ``'$(`` and parsing with :func:`parse_comparison_at`
(no regular expressions). After comparisons are replaced by SymPy symbols, the words ``Or`` and
``And`` are turned into ``|`` and ``&`` for evaluation; this matches how conditions are written
in MSBuild and assumes those keywords do not appear inside quoted values.
"""

from __future__ import annotations

import itertools
from typing import Optional

from sympy import simplify_logic, symbols, true as sym_true, false as sym_false
from sympy.logic.boolalg import Boolean, Or, And, Not

# --- Parsing comparisons (see module docstring for supported syntax) ---


def _symbol_name_for_comparison(property_name: str, operator: str, value: str) -> str:
    kind = "eq" if operator == "==" else "neq"
    safe = f"{property_name}_{kind}_{value}"
    return safe.replace("-", "_").replace(" ", "_")


def parse_comparison_at(condition: str, start: int) -> Optional[tuple[int, str, str, str]]:
    """
    Parse one comparison starting at ``start`` (must point at ``'$(``).

    :return: ``(end_index_exclusive, property_name, operator, value)`` or ``None``.
    """
    if start >= len(condition) or not condition.startswith("'$(", start):
        return None
    fragment = condition[start:]
    try:
        close_paren = fragment.index(")", 2)
    except ValueError:
        return None
    property_name = fragment[3:close_paren]
    rest = fragment[close_paren + 1 :]
    if rest.startswith("'=="):
        operator = "=="
        tail = rest[3:]
    elif rest.startswith("'!="):
        operator = "!="
        tail = rest[3:]
    else:
        return None
    if not tail.startswith("'"):
        return None
    close_value = tail.find("'", 1)
    if close_value < 0:
        return None
    value = tail[1:close_value]
    end = start + (close_paren + 1) + 3 + (close_value + 1)
    return end, property_name, operator, value


def _iter_comparison_spans(condition: str) -> list[tuple[int, int, str, str, str]]:
    """Non-overlapping comparisons in order: (start, end, prop, op, value)."""
    spans: list[tuple[int, int, str, str, str]] = []
    i = 0
    while i < len(condition):
        j = condition.find("'$(", i)
        if j < 0:
            break
        parsed = parse_comparison_at(condition, j)
        if parsed is None:
            i = j + 1
            continue
        end, prop, op, val = parsed
        spans.append((j, end, prop, op, val))
        i = end
    return spans


# --- SymPy bridge (comparisons become symbols; MSBuild Or/And become boolean ops) ---


def replace_comparisons_with_sympy(condition: str) -> tuple[Boolean, dict[Boolean, str]]:
    """
    Replace each comparison with a SymPy symbol; return the boolean expression and a map back to original text.
    """
    reverse: dict[Boolean, str] = {}
    stripped = condition.strip()
    lower = stripped.lower()
    if lower == "true":
        return sym_true, reverse
    if lower == "false":
        return sym_false, reverse

    parts: list[str] = []
    pos = 0
    for start, end, prop, op, val in _iter_comparison_spans(condition):
        parts.append(condition[pos:start])
        original = condition[start:end]
        sym = symbols(_symbol_name_for_comparison(prop, op, val))
        reverse[sym] = original
        parts.append(str(sym))
        pos = end
    parts.append(condition[pos:])
    replaced = "".join(parts)

    replaced = replaced.replace("Or", "|").replace("And", "&").replace("!", "~")
    local_scope = {str(sym): sym for sym in reverse}
    eval_ns = {**local_scope, "False": sym_false, "True": sym_true}
    boolean: Boolean = eval(replaced, {"__builtins__": {}}, eval_ns)
    return boolean, reverse


def _variables_from_reverse(reverse: dict[Boolean, str]) -> set[str]:
    variables: set[str] = set()
    for text in reverse.values():
        parsed = parse_comparison_at(text, 0)
        if parsed is not None:
            variables.add(parsed[1])
    return variables


# --- Finite-domain checks (possible_values) ---


def truth_value_for_comparison_text(
    original_text: str,
    assignment: dict[str, str],
) -> bool:
    """Evaluate one comparison literal against a variable assignment."""
    parsed = parse_comparison_at(original_text, 0)
    if parsed is None:
        return True
    _, prop, op, val = parsed
    if prop not in assignment:
        return True
    if op == "==":
        return assignment[prop] == val
    return assignment[prop] != val


def evaluate_sympy_on_assignment(
    expr: Boolean,
    reverse: dict[Boolean, str],
    assignment: dict[str, str],
) -> bool:
    subs = {}
    for sym in expr.free_symbols:
        subs[sym] = truth_value_for_comparison_text(reverse[sym], assignment)
    out = simplify_logic(expr.subs(subs))
    return out == sym_true


def domain_removes_condition(
    simplified: Boolean,
    reverse: dict[Boolean, str],
    possible_values: dict[str, list[str]],
) -> bool:
    if not possible_values:
        return False
    vars_in_expr = _variables_from_reverse(reverse)
    if not vars_in_expr:
        return False
    if not vars_in_expr.issubset(possible_values.keys()):
        return False
    empty_domain_vars = {k for k, v in possible_values.items() if len(v) == 0}
    if vars_in_expr <= empty_domain_vars:
        return True
    keys = [k for k in possible_values if k in vars_in_expr]
    domains = [possible_values[k] for k in keys]
    if any(len(d) == 0 for d in domains):
        return False
    all_true = True
    all_false = True
    for combo in itertools.product(*domains):
        assignment = dict(zip(keys, combo))
        holds = evaluate_sympy_on_assignment(simplified, reverse, assignment)
        if not holds:
            all_true = False
        if holds:
            all_false = False
    return all_true or all_false


# --- Output formatting and inequality expansion ---


def try_collapse_or_equals_to_neq(
    expr: Boolean,
    reverse: dict[Boolean, str],
    possible_values: dict[str, list[str]],
) -> Optional[str]:
    if not isinstance(expr, Or):
        return None
    var_name: Optional[str] = None
    value_set: set[str] = set()
    for arg in expr.args:
        if not arg.is_Symbol or arg not in reverse:
            return None
        parsed = parse_comparison_at(reverse[arg], 0)
        if parsed is None or parsed[2] != "==":
            return None
        _, prop, _, val = parsed
        if var_name is None:
            var_name = prop
        elif var_name != prop:
            return None
        value_set.add(val)
    if var_name is None or var_name not in possible_values:
        return None
    domain = set(possible_values[var_name])
    missing = domain - value_set
    if len(missing) != 1:
        return None
    excluded = next(iter(missing))
    return f"'$({var_name})'!='{excluded}'"


def sympy_boolean_to_msbuild_string(simplified: Boolean, reverse: dict[Boolean, str]) -> str:
    if simplified == sym_true or simplified == sym_false:
        return ""
    if simplified.is_Symbol:
        return reverse[simplified]
    if isinstance(simplified, Not):
        return "!" + sympy_boolean_to_msbuild_string(simplified.args[0], reverse)
    if isinstance(simplified, And):
        parts = []
        for arg in simplified.args:
            if isinstance(arg, Or):
                parts.append(f"({sympy_boolean_to_msbuild_string(arg, reverse)})")
            else:
                parts.append(sympy_boolean_to_msbuild_string(arg, reverse))
        return " And ".join(parts)
    if isinstance(simplified, Or):
        parts = [sympy_boolean_to_msbuild_string(arg, reverse) for arg in simplified.args]
        return " Or ".join(parts)
    return str(simplified)


def expand_inequality_to_or_equals(
    property_name: str,
    excluded_value: str,
    possible_values: dict[str, list[str]],
) -> Optional[str]:
    """
    If ``property_name`` is listed in ``possible_values``, return an ``(Or of ==)`` string
    for every value except ``excluded_value``. Otherwise return ``None`` (caller keeps original).
    """
    if property_name not in possible_values:
        return None
    allowed = [v for v in possible_values[property_name] if v != excluded_value]
    if not allowed:
        return "False"
    parts = [f"'$({property_name})'=='{val}'" for val in allowed]
    return "(" + " Or ".join(parts) + ")"


def expand_not_equal_subexpressions(
    condition: str,
    possible_values: dict[str, list[str]],
) -> str:
    """
    Replace each ``!=`` comparison whose property appears in ``possible_values`` with an ``Or`` of ``==``.
    """
    current = condition
    previous = None
    while previous != current:
        previous = current
        next_current: list[str] = []
        pos = 0
        while pos < len(current):
            j = current.find("'$(", pos)
            if j < 0:
                next_current.append(current[pos:])
                break
            next_current.append(current[pos:j])
            parsed = parse_comparison_at(current, j)
            if parsed is None:
                next_current.append(current[j])
                pos = j + 1
                continue
            end, prop, op, val = parsed
            if op != "!=":
                next_current.append(current[j:end])
                pos = end
                continue
            expanded = expand_inequality_to_or_equals(prop, val, possible_values)
            if expanded is None:
                next_current.append(current[j:end])
            else:
                next_current.append(expanded)
            pos = end
        current = "".join(next_current)
    return current
