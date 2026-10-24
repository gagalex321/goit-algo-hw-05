# Порівняйте ефективність алгоритмів пошуку підрядка: Боєра-Мура, Кнута-Морріса-Пратта та Рабіна-Карпа на основі двох текстових файлів (стаття 1, стаття 2). 
# Використовуючи timeit, треба виміряти час виконання кожного алгоритму для двох видів підрядків: 
# одного, що дійсно існує в тексті, 
# та іншого — вигаданого (вибір підрядків за вашим бажанням). 
# На основі отриманих даних визначте найшвидший алгоритм для кожного тексту окремо та в цілому.

from pathlib import Path
import timeit


def read_text(path):
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")

# алгоритм Боєра-Мура
def boyer_moore(text, pattern):
    if not pattern:
        return 0
    m, n = len(pattern), len(text)
    if m > n:
        return -1
    last = {char: i for i, char in enumerate(pattern)}
    shift = 0
    while shift <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[shift + j]:
            j -= 1
        if j < 0:
            return shift
        shift += max(1, j - last.get(text[shift + j], -1))
    return -1

# алгоритм Кнута-Морріса-Пратта
def kmp_search(text, pattern):
    if not pattern:
        return 0
    prefix = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = prefix[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            prefix[i] = j
    j = 0
    for i, char in enumerate(text):
        while j > 0 and char != pattern[j]:
            j = prefix[j - 1]
        if char == pattern[j]:
            j += 1
            if j == len(pattern):
                return i - len(pattern) + 1
    return -1

# алгоритм Рабіна-Карпа
def rabin_karp(text, pattern):
    if not pattern:
        return 0
    n, m = len(text), len(pattern)
    if m > n:
        return -1
    base_value, modulus = 256, 1_000_000_007
    pattern_hash = window_hash = 0
    highest = pow(base_value, m - 1, modulus)
    for i in range(m):
        pattern_hash = (pattern_hash * base_value + ord(pattern[i])) % modulus
        window_hash = (window_hash * base_value + ord(text[i])) % modulus
    for start in range(n - m + 1):
        if pattern_hash == window_hash and text[start:start + m] == pattern:
            return start
        if start < n - m:
            window_hash = (
                (window_hash - ord(text[start]) * highest) * base_value
                + ord(text[start + m])
            ) % modulus
    return -1

ALGORITHMS = {
    "Боєра-Мура": boyer_moore,
    "Кнута-Морріса-Пратта": kmp_search,
    "Рабіна-Карпа": rabin_karp,
}

#--------------------------------------------------------------------------------

def main():
    files = [Path("стаття 1.txt"), Path("стаття 2.txt")]
    fake_pattern = "НЕІСНУЮЧИЙ_ПІДРЯДОК"
    for number, path in enumerate(files, start=1):
        text = read_text(path)
        real_pattern = text[int(len(text) * 0.75):int(len(text) * 0.75) + 35]
        for kind, pattern in (("Існує", real_pattern), ("Не існує", fake_pattern)):
            print(f"\nСтаття {number} | підрядок: {kind}")
            print(f"Шуканий текст: {pattern!r}")
            timings = {}
            for name, algorithm in ALGORITHMS.items():
                index = algorithm(text, pattern)
                assert index == text.find(pattern), f"Помилка алгоритму: {name}"
                samples = timeit.repeat(
                    lambda a=algorithm, t=text, p=pattern: a(t, p),
                    repeat=5, number=100
                )
                timings[name] = min(samples) / 100
                print(f"{name:24} {timings[name]:.8f} с | індекс: {index}")
            winner = min(timings, key=timings.get)
            print(f"Найшвидший: {winner}")


if __name__ == "__main__":
    main()