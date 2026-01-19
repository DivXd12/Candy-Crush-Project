import argparse
import csv
import random
import copy

COLORS = [1, 2, 3, 4]

SCORES = {
    "LINE3": 5,
    "LINE4": 10,
    "LINE5": 50,
    "L": 20,
    "T": 30,
}

def random_board(rows, cols, rng):
    return [[rng.choice(COLORS) for _ in range(cols)] for _ in range(rows)]

def detect_lines(board):
    rows, cols = len(board), len(board[0])
    found = []

    for i in range(rows):
        j = 0
        while j < cols:
            k = j
            while k < cols and board[i][k] == board[i][j] and board[i][j] != 0:
                k += 1
            length = k - j
            if length >= 3:
                cells = {(i, x) for x in range(j, k)}
                if length == 3:
                    found.append((cells, SCORES["LINE3"]))
                elif length == 4:
                    found.append((cells, SCORES["LINE4"]))
                else:
                    found.append((cells, SCORES["LINE5"]))
            j = k

    for j in range(cols):
        i = 0
        while i < rows:
            k = i
            while k < rows and board[k][j] == board[i][j] and board[i][j] != 0:
                k += 1
            length = k - i
            if length >= 3:
                cells = {(x, j) for x in range(i, k)}
                if length == 3:
                    found.append((cells, SCORES["LINE3"]))
                elif length == 4:
                    found.append((cells, SCORES["LINE4"]))
                else:
                    found.append((cells, SCORES["LINE5"]))
            i = k

    return found

def detect_L_T(board):
    rows, cols = len(board), len(board[0])
    found = []

    for i in range(rows):
        for j in range(cols):
            c = board[i][j]
            if c == 0:
                continue

            if i+2 < rows and j+2 < cols:
                if board[i+1][j] == c and board[i+2][j] == c and board[i][j+1] == c and board[i][j+2] == c:
                    found.append(({
                        (i,j),(i+1,j),(i+2,j),(i,j+1),(i,j+2)
                    }, SCORES["L"]))

            if i+2 < rows and j-2 >= 0:
                if board[i+1][j] == c and board[i+2][j] == c and board[i][j-1] == c and board[i][j-2] == c:
                    found.append(({
                        (i,j),(i+1,j),(i+2,j),(i,j-1),(i,j-2)
                    }, SCORES["L"]))

            if i-2 >= 0 and j+2 < cols:
                if board[i-1][j] == c and board[i-2][j] == c and board[i][j+1] == c and board[i][j+2] == c:
                    found.append(({
                        (i,j),(i-1,j),(i-2,j),(i,j+1),(i,j+2)
                    }, SCORES["L"]))

            if i-2 >= 0 and j-2 >= 0:
                if board[i-1][j] == c and board[i-2][j] == c and board[i][j-1] == c and board[i][j-2] == c:
                    found.append(({
                        (i,j),(i-1,j),(i-2,j),(i,j-1),(i,j-2)
                    }, SCORES["L"]))

            if i-1 >= 0 and i+1 < rows and j-1 >= 0 and j+1 < cols:
                if board[i-1][j] == c and board[i+1][j] == c and board[i][j-1] == c and board[i][j+1] == c:
                    found.append(({
                        (i,j),(i-1,j),(i+1,j),(i,j-1),(i,j+1)
                    }, SCORES["T"]))

    return found

def detect_all(board):
    return detect_lines(board) + detect_L_T(board)

def select_shapes(shapes):
    shapes = sorted(shapes, key=lambda x: x[1], reverse=True)
    used = set()
    chosen = []

    for cells, score in shapes:
        if not (cells & used):
            chosen.append((cells, score))
            used |= cells

    return chosen

def remove_shapes(board, chosen):
    for cells, _ in chosen:
        for i, j in cells:
            board[i][j] = 0

def apply_gravity(board, rng):
    rows, cols = len(board), len(board[0])
    for j in range(cols):
        stack = []
        for i in range(rows):
            if board[i][j] != 0:
                stack.append(board[i][j])
        for i in range(rows-1, -1, -1):
            if stack:
                board[i][j] = stack.pop()
            else:
                board[i][j] = rng.choice(COLORS)

def resolve_board(board, rng):
    total_score = 0
    cascades = 0

    while True:
        shapes = detect_all(board)
        if not shapes:
            break
        chosen = select_shapes(shapes)
        if not chosen:
            break
        for _, s in chosen:
            total_score += s
        remove_shapes(board, chosen)
        apply_gravity(board, rng)
        cascades += 1

    return total_score, cascades

def valid_swaps(board):
    rows, cols = len(board), len(board[0])
    swaps = []
    for i in range(rows):
        for j in range(cols):
            if j+1 < cols:
                swaps.append(((i,j),(i,j+1)))
            if i+1 < rows:
                swaps.append(((i,j),(i+1,j)))
    return swaps

def evaluate_swap(board, a, b, rng):
    tmp = copy.deepcopy(board)
    (i1,j1),(i2,j2) = a,b
    tmp[i1][j1], tmp[i2][j2] = tmp[i2][j2], tmp[i1][j1]
    shapes = detect_all(tmp)
    if not shapes:
        return 0, 0
    pts, casc = resolve_board(tmp, rng)
    return pts, casc

def find_best_swap(board, rng):
    best = None
    best_pts = 0
    best_casc = 0

    for a,b in valid_swaps(board):
        pts, casc = evaluate_swap(board, a, b, rng)
        if pts > best_pts:
            best_pts = pts
            best_casc = casc
            best = (a,b)

    return best, best_pts, best_casc

def play_game(rows, cols, target, rng):
    board = random_board(rows, cols, rng)
    score = 0
    swaps = 0
    cascades_total = 0
    moves_to_target = None

    pts, casc = resolve_board(board, rng)
    score += pts
    cascades_total += casc

    while True:
        if score >= target:
            return {
                "points": score,
                "swaps": swaps,
                "total_cascades": cascades_total,
                "reached_target": True,
                "stopping_reason": "REACHED_TARGET",
                "moves_to_10000": moves_to_target if moves_to_target is not None else swaps
            }

        best, best_pts, best_casc = find_best_swap(board, rng)
        if best is None:
            return {
                "points": score,
                "swaps": swaps,
                "total_cascades": cascades_total,
                "reached_target": False,
                "stopping_reason": "NO_MOVES",
                "moves_to_10000": ""
            }

        (a,b) = best
        (i1,j1),(i2,j2) = a,b
        board[i1][j1], board[i2][j2] = board[i2][j2], board[i1][j1]
        swaps += 1

        pts, casc = resolve_board(board, rng)
        score += pts
        cascades_total += casc

        if moves_to_target is None and score >= target:
            moves_to_target = swaps

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=100)
    ap.add_argument("--rows", type=int, default=11)
    ap.add_argument("--cols", type=int, default=11)
    ap.add_argument("--target", type=int, default=10000)
    ap.add_argument("--out", type=str, default="results/summary.csv")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    rng = random.Random(args.seed)

    results = []
    for gid in range(args.games):
        res = play_game(args.rows, args.cols, args.target, rng)
        res["game_id"] = gid
        results.append(res)

    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["game_id","points","swaps","total_cascades","reached_target","stopping_reason","moves_to_10000"])
        for r in results:
            writer.writerow([
                r["game_id"], r["points"], r["swaps"], r["total_cascades"],
                r["reached_target"], r["stopping_reason"], r["moves_to_10000"]
            ])

    print(f"Done. Results in {args.out}")

if __name__ == "__main__":
    main()
