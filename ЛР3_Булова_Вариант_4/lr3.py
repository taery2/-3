"""
Лабораторная работа № 3
Предмет: Основы алгоритмизации и программирование
Студент: Булова Екатерина
Группа: БИ 2-1
Вариант: 4

Быстрая сортировка: случайный опорный элемент + схема Хоара.
Сортировка слиянием: восходящая (bottom-up, итеративная).
Дополнительное задание Г4: максимальная глубина рекурсии.
"""

import random
import statistics
import time
import matplotlib.pyplot as plt


SEED = 42
REPEATS = 3


def bubble_sort(arr):
    a = arr.copy()
    for i in range(len(a) - 1):
        swapped = False
        for j in range(len(a) - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def insertion_sort(arr):
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def quick_sort(arr, seed=SEED, return_depth=False):
    """Quick Sort: случайный pivot + Hoare.
    Рекурсивно обрабатывается меньшая часть, большая — циклом.
    Это ограничивает глубину стека до O(log n).
    """
    a = arr.copy()
    rng = random.Random(seed)
    max_depth = 0

    def partition(lo, hi):
        pivot = a[rng.randint(lo, hi)]
        i, j = lo - 1, hi + 1
        while True:
            i += 1
            while a[i] < pivot:
                i += 1
            j -= 1
            while a[j] > pivot:
                j -= 1
            if i >= j:
                return j
            a[i], a[j] = a[j], a[i]

    def quick(lo, hi, depth):
        nonlocal max_depth
        max_depth = max(max_depth, depth)

        while lo < hi:
            p = partition(lo, hi)

            if p - lo < hi - p:
                quick(lo, p, depth + 1)
                lo = p + 1
            else:
                quick(p + 1, hi, depth + 1)
                hi = p

    if a:
        quick(0, len(a) - 1, 1)

    if return_depth:
        return a, max_depth
    return a


def merge_sort_bottom_up(arr):
    """Восходящая итеративная сортировка слиянием."""
    n = len(arr)
    if n <= 1:
        return arr.copy()

    src = arr.copy()
    dst = [None] * n
    width = 1

    while width < n:
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            i, j, k = lo, mid, lo

            while i < mid and j < hi:
                if src[i] <= src[j]:
                    dst[k] = src[i]
                    i += 1
                else:
                    dst[k] = src[j]
                    j += 1
                k += 1

            while i < mid:
                dst[k] = src[i]
                i += 1
                k += 1

            while j < hi:
                dst[k] = src[j]
                j += 1
                k += 1

        src, dst = dst, src
        width *= 2

    return src


def generate_data(n, kind="random", lo=-500, hi=500, seed=SEED):
    rng = random.Random(seed + n)
    data = [rng.randint(lo, hi) for _ in range(n)]

    if kind == "sorted":
        data.sort()
    elif kind == "reversed":
        data.sort(reverse=True)
    elif kind == "nearly_sorted":
        data.sort()
        for _ in range(max(1, n // 20)):
            i, j = rng.randrange(n), rng.randrange(n)
            data[i], data[j] = data[j], data[i]
    elif kind == "random":
        pass
    else:
        raise ValueError("Неизвестный тип данных")

    return data


def measure(sort_func, data, repeats=REPEATS):
    times = []
    expected = sorted(data)

    for _ in range(repeats):
        start = time.perf_counter()
        result = sort_func(data)
        elapsed = time.perf_counter() - start
        if result != expected:
            raise AssertionError("Алгоритм сортировки дал неверный результат")
        times.append(elapsed)

    return statistics.median(times)


def measure_quick_depth(data, repeats=REPEATS):
    times = []
    max_depth = 0
    expected = sorted(data)

    for _ in range(repeats):
        start = time.perf_counter()
        result, depth = quick_sort(data, return_depth=True)
        elapsed = time.perf_counter() - start
        if result != expected:
            raise AssertionError("Quick Sort дал неверный результат")
        times.append(elapsed)
        max_depth = max(max_depth, depth)

    return statistics.median(times), max_depth


def experiment_1():
    """Размеры варианта ЛР №2: 200...3200."""
    sizes = [200, 400, 800, 1600, 3200]
    algorithms = {
        "Пузырьком": bubble_sort,
        "Вставками": insertion_sort,
        "Быстрая": quick_sort,
        "Слиянием": merge_sort_bottom_up,
    }
    results = {name: [] for name in algorithms}

    for n in sizes:
        data = generate_data(n)
        for name, func in algorithms.items():
            results[name].append(measure(func, data, 5))

    return sizes, results


def experiment_2():
    """Размеры варианта 4: 10k, 50k, 100k, 150k."""
    sizes = [10_000, 50_000, 100_000, 150_000]
    algorithms = {
        "Быстрая": quick_sort,
        "Слиянием": merge_sort_bottom_up,
        "sorted()": sorted,
    }
    results = {name: [] for name in algorithms}

    for n in sizes:
        data = generate_data(n)
        for name, func in algorithms.items():
            results[name].append(measure(func, data))

    return sizes, results


def experiment_3():
    """R/S/V/N при n=50 000."""
    results = {}
    for code, kind in [
        ("R", "random"),
        ("S", "sorted"),
        ("V", "reversed"),
        ("N", "nearly_sorted"),
    ]:
        data = generate_data(50_000, kind)
        results[code] = {
            "Быстрая": measure(quick_sort, data),
            "Слиянием": measure(merge_sort_bottom_up, data),
        }
    return results


def additional_g4():
    """Максимальная глубина рекурсии Quick Sort для R/S/V."""
    results = {}
    for code, kind in [
        ("R", "random"),
        ("S", "sorted"),
        ("V", "reversed"),
    ]:
        data = generate_data(50_000, kind)
        _, depth = measure_quick_depth(data)
        results[code] = depth
    return results


def save_plots(res1, res2, res3, g4):
    sizes1, data1 = res1
    plt.figure(figsize=(9, 5.5))
    for name, times in data1.items():
        plt.plot(sizes1, times, marker="o", label=name)
    plt.yscale("log")
    plt.xlabel("Размер массива n")
    plt.ylabel("Время, с (логарифмическая шкала)")
    plt.title("ЛР №3, вариант 4 — эксперимент 1")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("experiment1.png", dpi=160)
    plt.close()

    sizes2, data2 = res2
    plt.figure(figsize=(9, 5.5))
    for name, times in data2.items():
        plt.plot(sizes2, times, marker="o", label=name)
    plt.xlabel("Размер массива n")
    plt.ylabel("Время, с")
    plt.title("ЛР №3, вариант 4 — эксперимент 2")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("experiment2.png", dpi=160)
    plt.close()

    codes = ["R", "S", "V", "N"]
    x = list(range(len(codes)))
    width = 0.36

    plt.figure(figsize=(9, 5.5))
    plt.bar(
        [i - width / 2 for i in x],
        [res3[c]["Быстрая"] for c in codes],
        width,
        label="Быстрая",
    )
    plt.bar(
        [i + width / 2 for i in x],
        [res3[c]["Слиянием"] for c in codes],
        width,
        label="Слиянием",
    )
    plt.xticks(x, codes)
    plt.xlabel("Тип данных")
    plt.ylabel("Время, с")
    plt.title("Эксперимент 3: n = 50 000")
    plt.grid(axis="y")
    plt.legend()
    plt.tight_layout()
    plt.savefig("experiment3.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(list(g4.keys()), list(g4.values()))
    plt.xlabel("Тип данных")
    plt.ylabel("Максимальная глубина рекурсии")
    plt.title("Г4: глубина рекурсии Quick Sort, n = 50 000")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("g4_recursion_depth.png", dpi=160)
    plt.close()


if __name__ == "__main__":
    r1 = experiment_1()
    r2 = experiment_2()
    r3 = experiment_3()
    g4 = additional_g4()

    save_plots(r1, r2, r3, g4)

    print("Эксперимент 1:", r1)
    print("Эксперимент 2:", r2)
    print("Эксперимент 3:", r3)
    print("Г4:", g4)
