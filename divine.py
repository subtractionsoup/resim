from resim import Resim
from io import StringIO
import closed_form_solver_faster_no_numpy
from multiprocessing import Pool


def flip_blocks(input, offset):
    block_series = [None] * offset + input

    rem = 64 - (len(block_series) % 64)
    block_series.extend([None] * rem)

    for x in range(len(block_series) // 64 + 1):
        block_series[x * 64 : (x + 1) * 64] = block_series[x * 64 : (x + 1) * 64][::-1]

    return block_series


def block_permutations(input):
    for i in range(64):
        yield i, flip_blocks(input, 64 - i)


class StubRng:
    def __init__(self):
        self.state = (0, 0)
        self.offset = 0

    def next(self):
        # shouldn't be too low, otherwise we'll trigger the "roll again on low rolls" cases and throw things off
        return 0.5

    def get_state_str(self):
        return "[STUB]"


def inner(window):
    start_time = min(w.timestamp for w in window)
    end_time = max(w.timestamp for w in window)

    knowns = []
    for roll in window:
        if roll.lower_bound > 0 or roll.upper_bound < 1:
            knowns.append((roll.lower_bound, roll.upper_bound))
        else:
            knowns.append(None)

    print(f"trying window {start_time} - {end_time}")

    found = False
    for i, knowns_block in block_permutations(knowns):
        res = closed_form_solver_faster_no_numpy.solve(knowns_block)
        if res:
            # since we're adding block padding the offset for the roll it finds is always gonna be zero
            # and said roll is probably gonna be one of the padding rolls but that's okay, we just need something in the general area
            print(f"- found! {res[0]}+0")
            found = True


def main():
    start_timestamp = "2021-03-17T20:05:00.000Z"
    end_timestamp = "2021-03-17T20:50:00.000Z"

    out_file = StringIO()

    stub_rng = StubRng()
    resim = Resim(stub_rng, out_file, None, False)
    resim.run(start_timestamp, end_timestamp, None)

    print(f"got {len(resim.roll_log)} rolls")

    # todo: parallelize this in a way that doesn't make ctrl-c explode, and that supports tqdm
    # with Pool(1) as p:
    args = []

    # window size and step size are kinda arbitrary
    # but we don't want it to waste too much time on a range that def. doesn't work
    window_size = 2800
    step_size = 100
    for window_pos in range(0, len(resim.roll_log) - window_size, step_size):
        window = resim.roll_log[window_pos : window_pos + window_size]
        args.append(window)

    for w in args:
        inner(w)
    # p.map(inner, args)


if __name__ == "__main__":
    main()