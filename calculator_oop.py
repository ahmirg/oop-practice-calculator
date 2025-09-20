##--/-///-/-----
##    9/16- 9/17 first classes mini project, chatgpt guided. deeply helped understanding
##

import json, re, os
from typing import List, Tuple, Optional # type hints


class Calculator:
    def __init__(self):
        self.last_result: Optional[float] = None
        self.history: List[Tuple[str,float]] = []  # [(expr, result), ...]
        self.memory: Optional[float] = None

    # --- ops ---
    def add(self: "Calculator", a:float, b:float): return a + b
    def sub(self: "Calculator", a:float, b:float): return a - b
    def mul(self: "Calculator", a:float, b:float): return a * b
    def div(self: "Calculator", a:float, b:float):
        if b == 0:
            raise ZeroDivisionError("You Can't divide by zero!!")
        return a / b

    # --- parsing ---
    def _parse_binary(self, expr: str):
        m = re.fullmatch(
            r'\s*([+-]?\d+(?:\.\d+)?)\s*([+\-*/])\s*([+-]?\d+(?:\.\d+)?)\s*', # got ts from chatgpt, it just makes it so entry is clean. dont need to remember this
            expr
        )
        if not m:
            raise ValueError("Use: <num><op><num>. Examples: 2+8, -3.5 * 2, 10 / -4")
        a_str, op, b_str = m.groups()
        return float(a_str), op, float(b_str)

    # --- core ---
    def evaluate(self, expr: str) -> float:
        a, op, b = self._parse_binary(expr)  # <-- uses the parser.
        if op == "+": result = self.add(a, b)
        elif op == "-": result = self.sub(a, b)
        elif op == "*": result = self.mul(a, b)
        elif op == "/": result = self.div(a, b)
        else: raise ValueError("Operation Not Supported")

        # --------memory update

        self.last_result = result
        pretty_expr = f"{a} {op} {b}"
        self.history.append((pretty_expr, result))

        # -------json log

        log = {
            "expr": pretty_expr,
            "operands": [a,b],
            "operator": op,
            "result": result,
            "question_num":len(self.history)

        }
        with open("calc_log.jsonl", "a") as f:
            f.write(json.dumps(log) + "\n")

        return result

    def to_json(self) -> str:
            data = {
                "last_result": self.last_result,
                "memory": self.memory,
                "history": self.history,
            }
            return json.dumps(data, indent=4)
# adds persistence api
    def to_dict(self) -> dict:
        #Tuples become list auto, but make it explict
        return {
            "last_result": self.last_result,
            "memory": self.memory,
            "history": [[expr, res] for (expr, res) in self.history],
         }
    def save(self, path: str = "calc_state.json") -> None:
        tmp = path + ".tmp" #          _->  tmp is a temp file
        with open(tmp, "w") as f: #        ->with open w opens it for writing (w)
            json.dump(self.to_dict(), f, indent=2)
        os.replace(tmp, path)

    @classmethod
    def from_dict(cls, data:dict) -> "Calculator":
        c = cls()
        c.last_result = data.get("last_result")
        c.memory = data.get("memory")
        c.history = [(expr, float(res)) for expr, res in data.get("history", [])]
        return c

    @classmethod
    def load(cls, path:str = "calc_state.json") -> "Calculator":
        try:
            with open(path) as f:
                data = json.load(f)
            return cls.from_dict(data)
        except FileNotFoundError:
            return cls()
        except json.JSONDecodeError:
            print("State file corrupted, restarting from a fresh copy")
            return cls()

    ## repl

def repl(state_path="calc_state.json"):
    calc = Calculator.load(state_path)
    print("Persisted Calculator --- enter expressions (e.g 2+9) or commands: last, history, save, q(quit)")

    while True:
        s = input("> ").strip()
        raw = s.lower()

        if raw in ("q", "quit", "exit"):
            calc.save(state_path)
            print("Saved calculator state. Bye!")
            break

        if raw == "save":
            calc.save(state_path); print("Saved."); continue

        if raw == "last":
            print(calc.last_result if calc.last_result is not None else "No calculations yet mud")
            continue
        if raw == "history":
            if not calc.history:
                print("History empty mud"); continue
            for expr, res in calc.history:
                out = int(res) if float(res).is_integer() else res
                print(f"{expr} = {out}")
            continue
        try:
            res = calc.evaluate(s)
            out = int(res) if float(res).is_integer() else res
            print(out)
            print()
            print("Enter next expression, /quit/history/last/save")
            calc.save(state_path) #autosave ts
        except Exception as e:
            print(e)


if __name__ == "__main__":
    repl()


# --- test ---
