import argparse
import copy
from dateutil.parser import parse
from datetime import datetime, timedelta

DEFAULT_DICT = {
    "catch": [],
    "fail": [],
    "mission_catch": [],
    "mission_fail": [],
    "skip": []
}


class Args():
    def __init__(self, args):
        self.when = args.when
        self.start = args.start
        self.end = args.end
        self.timeframe = args.timeframe
        self.fill = args.fill
        self.detailed = args.detailed
        self.days = args.days

    def clean_args(self):
        today = datetime.now().date()
        if self.days is None:
            self.days = 30

        if self.when == "all":
            self.when = "before"
            self.start = None
        elif self.when == "last":
            self.when = "after"
            self.start = str(today - timedelta(days=self.days))
        elif self.when == "today":
            self.when = "on"
            self.start = None

        if self.timeframe is None:
            self.timeframe = "daily"
        else:
            self.timeframe = self.timeframe

        if self.start is None:
            self.start = today
        else:
            try:
                self.start = parse(self.start).date()
            except Exception as e:
                print(e)
                self.start = today

        if self.end is None:
            self.end = self.start
        else:
            try:
                self.end = parse(self.end).date()
            except Exception as e:
                print(e)
                self.end = self.start

        if self.end < self.start:
            self.end = self.start


def main():
    funcs = {
        "on": when_on,
        "between": when_between,
        "after": when_after,
        "before": when_before,
        "all": None,
        "last": None,
        "today": None,
    }

    parser = argparse.ArgumentParser(description="Statistics for the Pokemon Comunity Game catch rates")
    parser.add_argument("when", help="look at data relating to when", choices=sorted(funcs.keys()))
    parser.add_argument("-s", "--start", help="start date")
    parser.add_argument("-e", "--end", help="end date")
    parser.add_argument("-x", "--days", help="number of days to use with last", type=int)
    parser.add_argument("-t", "--timeframe", help="timeframe", choices=["hourly", "daily", "monthly"])
    parser.add_argument("-d", "--detailed", help="detailed summary", action="store_true")

    parser.add_argument(
        "-f", "--fill",
        help="fill holes in data",
        action="store_true"
    )

    args = Args(parser.parse_args())
    args.clean_args()

    data = get_logs_data()
    funcs[args.when](data, args.start, args.end, args.fill)
    final = apply_timeframe(data, args.timeframe)

    if args.timeframe == "hourly":
        length = 1
    elif args.timeframe == "daily":
        length = 2
    else:
        length = 3

    show_results(final, args.detailed, length)


def leading(n, length, zeros=False):
    return (("0" if zeros else " ") * (length - len(str(n)))) + str(n)


def show_results(data, detailed, zeros):
    lines = []
    final_catch = 0
    final_total = 0
    for k in sorted(data.keys()):
        caught = len(data[k]["catch"]) + len(data[k]["mission_catch"])
        skipped = len(data[k]["skip"])
        total = len(data[k]["catch"] + data[k]["mission_catch"] + data[k]["fail"] + data[k]["mission_fail"])
        total_skip = total + len(data[k]["skip"])
        caught_per = 0 if total == 0 else round(caught * 100 / total)
        skiped_per = 0 if total_skip == 0 else round(skipped * 100 / total_skip)
        final_catch += caught
        final_total += total

        if detailed:
            s = "{date}:\n\tcaught={caught} ({caught_str})\n\tmissed={missed} ({missed_str})\n\tskipped={skipped} ({skipped_str})\n\tmissions:\n\t\tcaught={mission_c} ({mission_c_str})\n\t\tmissed={mission_f} ({mission_f_str})\n\t(caught={c}%, skipped={s}%)".format(
                date=k,
                caught=leading(len(data[k]["catch"]), zeros),
                missed=leading(len(data[k]["fail"]), zeros),
                skipped=leading(len(data[k]["skip"]), zeros),
                mission_c=leading(len(data[k]["mission_catch"]), zeros),
                mission_f=leading(len(data[k]["mission_fail"]), zeros),
                caught_str=",".join(data[k]["catch"]),
                missed_str=",".join(data[k]["fail"]),
                skipped_str=",".join(data[k]["skip"]),
                mission_c_str=",".join(data[k]["mission_catch"]),
                mission_f_str=",".join(data[k]["mission_fail"]),
                c=leading(caught_per, 3),
                s=leading(skiped_per, 3)
            )
        else:
            s = "{date}: caught={caught}, missed={missed}, skipped={skipped}, missions->(caught={mission_c}, missed={mission_f})  (caught={c}%, skipped={s}%)".format(
                date=k,
                caught=leading(len(data[k]["catch"]), zeros),
                missed=leading(len(data[k]["fail"]), zeros),
                skipped=leading(len(data[k]["skip"]), zeros),
                mission_c=leading(len(data[k]["mission_catch"]), zeros),
                mission_f=leading(len(data[k]["mission_fail"]), zeros),
                c=leading(caught_per, 3),
                s=leading(skiped_per, 3)
            )
        lines.append(s)
        print(s)

    s = "Overall Catch Rate: {per}% ({catch}/{total})".format(per=round(final_catch * 100 / final_total), catch=final_catch, total=final_total)
    lines.append(s)
    print(s)

    final_string = "\n".join(lines)
    with open('statistics.txt', 'w') as f:
        f.write(final_string)


def split_daily(d):
    return d.split(" ")[0]


def split_monthly(d):
    return "-".join(d.split["-"][0:2])


def apply_timeframe(data, timeframe):
    if timeframe == "hourly":
        return data

    timeframes = {
        "daily": split_daily,
        "monthly": split_monthly
    }
    final = {}
    func = timeframes[timeframe]

    for k in data:
        new_k = func(k)
        if new_k not in final:
            final[new_k] = copy.deepcopy(data[k])
        else:
            final[new_k]["catch"] = final[new_k]["catch"] + data[k]["catch"]
            final[new_k]["fail"] = final[new_k]["fail"] + data[k]["fail"]
            final[new_k]["mission_catch"] = final[new_k]["mission_catch"] + data[k]["mission_catch"]
            final[new_k]["mission_fail"] = final[new_k]["mission_fail"] + data[k]["mission_fail"]
            final[new_k]["skip"] = final[new_k]["skip"] + data[k]["skip"]

    return final


def when_on(data, start, end, fill):
    delete_before(data, start)
    delete_after(data, start)
    fill_data(fill, data, start, start)


def when_before(data, start, end, fill):
    delete_before(data, start)
    if len(data.keys()) > 0:
        first = parse(sorted(data.keys())[0].split(" ")[0]).date()
        fill_data(fill, data, first, start)


def when_after(data, start, end, fill):
    delete_after(data, start)
    if len(data.keys()) > 0:
        last = parse(sorted(data.keys())[-1].split(" ")[0]).date()
        fill_data(fill, data, start, last)


def when_between(data, start, end, fill):
    delete_before(data, end)
    delete_after(data, end)
    fill_data(fill, data, start, end)


def delete_before(data, d):
    for k in list(data.keys()):
        tmp = parse(k.split(" ")[0]).date()
        if tmp > d:
            del data[k]


def delete_after(data, d):
    for k in list(data.keys()):
        tmp = parse(k.split(" ")[0]).date()
        if tmp < d:
            del data[k]


def fill_data(fill, data, start, end):
    if not fill:
        return
    current_date = start
    while current_date <= end:
        for h in range(0, 24):
            d_string = "{d} {h}".format(
                d=str(current_date),
                h=leading(h, 2, zeros=True)
            )
            if d_string not in data:
                data[d_string] = copy.deepcopy(DEFAULT_DICT)
        current_date = current_date + timedelta(days=1)


def get_logs_data():
    data = {}
    mission = False

    with open("logs/pokemoncg.txt") as file:
        for uline in file:
            line = uline.rstrip()

            if "Balance" in line or "Bought" in line:
                continue
            elif "Already" in line:
                mission = True
                continue

            dateh = line.split(":")[0]
            if dateh not in data:
                data[dateh] = copy.deepcopy(DEFAULT_DICT)

            pokemon = line.split(" ")[-1]
            if "Won't" in line:
                data[dateh]["skip"].append(pokemon)
            elif "Failed" in line:
                data[dateh]["%sfail" % ("mission_" if mission else "")].append(pokemon)
            else:
                data[dateh]["%scatch" % ("mission_" if mission else "")].append(pokemon)
            mission = False
    return data


if __name__ == "__main__":
    main()
