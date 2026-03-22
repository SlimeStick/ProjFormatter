# TODO: Understand WTF this code does, make it readable and simplify it. Then delete this file move code to MSBuildTree
import re

from sympy import symbols, simplify_logic
from sympy.logic.boolalg import Boolean, Or, And, Not


def _convert_msbuild_string_to_symbol(expression: str) -> str:
    """
    Convert a msbuild condition like "'$(Platform)'=='x64'" to "Platform_eq_x64" in order to be able to pass it to
    SymPy.
    """
    match = re.match(r"'?\$\(([^)]+)\)'?\s*([!=]=)\s*'?(.*?)'?$", expression.strip())
    if match:
        left, operator, right = match.groups()
        safe = f"{left}_{'eq' if operator == '==' else 'neq'}_{right}"
        return safe.replace("-", "_").replace(" ", "_")
    return re.sub(r"\W+", "_", expression)


def _convert_symbol_to_msbuild_string(symbol_name: str) -> str:
    """
    Convert a symbol like 'Platform_eq_x64' back to "'$(Platform)'=='x64'".
    """
    if symbol_name.endswith("_eq_x64") or "_eq_" in symbol_name:
        parts = symbol_name.rsplit("_eq_", 1)
        return f"'$({parts[0]})'=='{parts[1]}'"
    elif "_neq_" in symbol_name:
        parts = symbol_name.rsplit("_neq_", 1)
        return f"'$({parts[0]})'!='{parts[1]}'"
    return symbol_name



def _msbuild_string_to_sympy_boolean(condition: str) -> tuple[Boolean, dict[Boolean, str]]:
    reverse: dict[Boolean, str] = {}

    def replacer(match: re.Match) -> str:
        expression = match.group(0).strip()
        sym = symbols(_convert_msbuild_string_to_symbol(expression))
        reverse[sym] = expression
        return str(sym)

    replaced = re.sub(r"'[^']*'\s*[!=]=\s*'[^']*'", replacer, condition)

    # Convert MSBuild operators to Python for SymPy
    replaced = replaced.replace("Or", "|").replace("And", "&").replace("!", "~")

    local_scope = {str(sym): sym for sym in reverse}
    boolean: Boolean = eval(replaced, {}, local_scope)
    return boolean, reverse


def _sympy_boolean_to_msbuild_string(simplified: Boolean, reverse) -> str:
    if simplified.is_Symbol:
        return reverse[simplified]
    if isinstance(simplified, Not):
        # Unary NOT
        return "!" + _sympy_boolean_to_msbuild_string(simplified.args[0], reverse)
    if isinstance(simplified, And):
        parts = []
        for arg in simplified.args:
            # If child is Or, wrap it
            if isinstance(arg, Or):
                parts.append(f"({_sympy_boolean_to_msbuild_string(arg, reverse)})")
            else:
                parts.append(_sympy_boolean_to_msbuild_string(arg, reverse))
        return " And ".join(parts)
    if isinstance(simplified, Or):
        parts = [_sympy_boolean_to_msbuild_string(arg, reverse) for arg in simplified.args]
        return " Or ".join(parts)
    return str(simplified)


def optimize_condition(:
    """
    :param condition: The MSBuild Condition attribute to optimize.
    """
