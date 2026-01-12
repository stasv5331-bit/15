"""
Модуль для поиска анаграмм в тексте с логированием действий.

Добавлено логирование:
1. Действия пользователя (ввод текста)
2. Действия программы (вызов функций, результаты)
3. Возможность настройки уровня логирования

Уровни логирования:
- DEBUG: Детальная информация для отладки
- INFO: Подтверждение, что все работает нормально
- WARNING: Индикация потенциальных проблем
- ERROR: Ошибки, которые не остановили программу
- CRITICAL: Критические ошибки, программа не может продолжать
"""

import re
import logging
from collections import defaultdict
from datetime import datetime
import sys

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================

def setup_logging(level=logging.INFO):
    """
    Настраивает логирование для программы.
    
    Args:
        level: Уровень логирования (по умолчанию INFO)
    
    Создает:
        - Файловый хендлер для записи в logs/anagram.log
        - Консольный хендлер для вывода в терминал
        - Форматирование логов с временем и уровнем
    """
    # Создаем логгер
    logger = logging.getLogger('anagram_finder')
    logger.setLevel(level)
    
    # Очищаем существующие хендлеры (если есть)
    logger.handlers.clear()
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый хендлер (запись в файл)
    file_handler = logging.FileHandler(
        'logs/anagram.log',
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Консольный хендлер (вывод в терминал)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Добавляем хендлеры к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Логирование настроено. Уровень: {logging.getLevelName(level)}")
    return logger

# Создаем глобальный логгер
logger = setup_logging()

# ==================== ДЕКОРАТОР ДЛЯ ЛОГИРОВАНИЯ ====================

def log_function_call(func):
    """
    Декоратор для логирования вызовов функций.
    
    Логирует:
        - Начало выполнения функции
        - Аргументы функции
        - Результат выполнения
        - Время выполнения
    """
    def wrapper(*args, **kwargs):
        # Логируем начало вызова функции
        logger.debug(f"Вызов функции: {func.__name__}")
        
        # Логируем аргументы (скрываем длинные тексты)
        if args:
            # Для текстовых аргументов показываем только начало
            args_str = []
            for arg in args:
                if isinstance(arg, str) and len(arg) > 50:
                    args_str.append(f"'{arg[:50]}...'")
                else:
                    args_str.append(repr(arg))
            logger.debug(f"Аргументы: {', '.join(args_str)}")
        
        if kwargs:
            logger.debug(f"Ключевые аргументы: {kwargs}")
        
        # Выполняем функцию и замеряем время
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Логируем результат (для длинных результатов показываем только тип)
            if isinstance(result, list) and len(result) > 3:
                logger.debug(f"Функция {func.__name__} вернула список из {len(result)} элементов")
            elif isinstance(result, str) and len(result) > 100:
                logger.debug(f"Функция {func.__name__} вернула строку длиной {len(result)} символов")
            else:
                logger.debug(f"Результат: {result}")
            
            logger.info(f"Функция {func.__name__} выполнена успешно за {execution_time:.4f} сек")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Ошибка в функции {func.__name__}: {str(e)}", exc_info=True)
            logger.warning(f"Функция {func.__name__} завершилась с ошибкой за {execution_time:.4f} сек")
            raise
    
    return wrapper

# ==================== ОСНОВНЫЕ ФУНКЦИИ С ЛОГИРОВАНИЕМ ====================

@log_function_call
def find_anagrams_in_text(text):
    """
    Находит все группы анаграмм во входном тексте.
    
    Args:
        text (str): Входной текст для анализа
        
    Returns:
        list: Массив групп анаграмм
    """
    # Логируем ввод пользователя
    logger.info(f"Пользователь ввел текст: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    
    # Проверка входных данных
    if not text:
        logger.warning("Получен пустой текст")
        return []
    
    if not isinstance(text, str):
        logger.error(f"Неверный тип данных: {type(text)}. Ожидалась строка.")
        return []
    
    logger.info("Начинаем поиск анаграмм...")
    
    # Очищаем текст
    cleaned_text = clean_text(text)
    logger.debug(f"Очищенный текст: {cleaned_text[:50]}{'...' if len(cleaned_text) > 50 else ''}")
    
    # Получаем уникальные слова
    words = get_unique_words(cleaned_text)
    logger.info(f"Извлечено уникальных слов: {len(words)}")
    
    # Группируем анаграммы
    anagram_groups = group_anagrams(words)
    
    # Логируем результат
    if anagram_groups:
        total_anagrams = sum(len(group) for group in anagram_groups)
        logger.info(f"Найдено {len(anagram_groups)} групп анаграмм, всего {total_anagrams} слов")
        for i, group in enumerate(anagram_groups, 1):
            logger.debug(f"Группа {i}: {group}")
    else:
        logger.info("Анаграммы не найдены")
    
    return anagram_groups

@log_function_call
def clean_text(text):
    """
    Очищает текст: приводит к нижнему регистру и удаляет знаки препинания.
    """
    if not text:
        logger.debug("Текст пустой, очистка не требуется")
        return ""
    
    original_length = len(text)
    # Удаляем всё, кроме букв и пробелов
    text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ\s]', ' ', text)
    text = text.lower().strip()
    
    removed_chars = original_length - len(text)
    logger.debug(f"Удалено {removed_chars} не-буквенных символов")
    
    return text

@log_function_call
def normalize_word(word):
    """
    Нормализует слово для сравнения анаграмм.
    """
    if len(word) <= 1:
        logger.debug(f"Слово '{word}' слишком короткое для нормализации")
        return word
    
    normalized = ''.join(sorted(word))
    logger.debug(f"Слово '{word}' нормализовано в '{normalized}'")
    return normalized

@log_function_call
def get_unique_words(text):
    """
    Извлекает уникальные слова из текста.
    """
    words = text.split()
    logger.debug(f"Извлечено {len(words)} слов из текста")
    
    unique_words = []
    seen = set()
    
    short_words_count = 0
    for word in words:
        if len(word) > 1:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)
        else:
            short_words_count += 1
    
    if short_words_count > 0:
        logger.debug(f"Пропущено {short_words_count} однобуквенных слов")
    
    logger.debug(f"Уникальных слов длиной >1: {len(unique_words)}")
    return unique_words

@log_function_call
def group_anagrams(words):
    """
    Группирует слова по анаграммам.
    """
    if not words:
        logger.debug("Список слов пустой, группировка не требуется")
        return []
    
    anagram_dict = defaultdict(list)
    
    for word in words:
        key = normalize_word(word)
        anagram_dict[key].append(word)
    
    # Фильтруем и сортируем результат
    result = []
    for key, group in anagram_dict.items():
        if len(group) > 1:
            result.append(sorted(group))
    
    result.sort(key=lambda x: x[0])
    
    logger.debug(f"Создано {len(anagram_dict)} групп, из них {len(result)} с анаграммами")
    return result

# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЕМ ====================

@log_function_call
def get_user_input():
    """
    Получает текст от пользователя.
    
    Returns:
        str: Текст, введенный пользователем
    """
    print("\n" + "="*50)
    print("ПОИСК АНАГРАММ С ЛОГИРОВАНИЕМ")
    print("="*50)
    print("\nВведите текст для поиска анаграмм:")
    print("(или введите 'exit' для выхода, 'test' для тестового текста)")
    
    user_input = input("> ").strip()
    
    if user_input.lower() == 'exit':
        logger.info("Пользователь выбрал выход из программы")
        return None
    elif user_input.lower() == 'test':
        # Тестовый текст
        test_text = "кот ток кто отк тко. listen silent enlist. Азора роза."
        logger.info("Пользователь выбрал тестовый текст")
        print(f"Используется тестовый текст: {test_text}")
        return test_text
    elif user_input.lower() == 'level':
        # Смена уровня логирования
        change_log_level()
        return get_user_input()
    else:
        logger.info(f"Пользователь ввел текст длиной {len(user_input)} символов")
        return user_input

@log_function_call  
def change_log_level():
    """
    Позволяет пользователю изменить уровень логирования.
    """
    print("\n" + "="*50)
    print("ИЗМЕНЕНИЕ УРОВНЯ ЛОГИРОВАНИЯ")
    print("="*50)
    print("\nДоступные уровни:")
    print("1. DEBUG - детальная отладочная информация")
    print("2. INFO - обычные информационные сообщения (по умолчанию)")
    print("3. WARNING - только предупреждения и ошибки")
    print("4. ERROR - только ошибки")
    print("5. CRITICAL - только критические ошибки")
    
    choice = input("\nВыберите уровень (1-5): ").strip()
    
    level_map = {
        '1': logging.DEBUG,
        '2': logging.INFO,
        '3': logging.WARNING,
        '4': logging.ERROR,
        '5': logging.CRITICAL
    }
    
    if choice in level_map:
        new_level = level_map[choice]
        global logger
        logger = setup_logging(new_level)
        print(f"\nУровень логирования изменен на: {logging.getLevelName(new_level)}")
        logger.info(f"Уровень логирования изменен пользователем на {logging.getLevelName(new_level)}")
    else:
        print("\nНеверный выбор. Уровень не изменен.")
        logger.warning(f"Пользователь ввел неверный выбор уровня логирования: {choice}")

@log_function_call
def display_results(anagrams):
    """
    Отображает результаты поиска анаграмм.
    
    Args:
        anagrams (list): Список групп анаграмм
    """
    if not anagrams:
        print("\n✗ Анаграммы не найдены")
        logger.info("Результат: анаграммы не найдены")
        return
    
    print(f"\n✓ Найдено {len(anagrams)} групп анаграмм:")
    for i, group in enumerate(anagrams, 1):
        print(f"  Группа {i}: {group}")
    
    total_words = sum(len(group) for group in anagrams)
    logger.info(f"Отображено {len(anagrams)} групп, всего {total_words} слов")

@log_function_call
def show_log_file_info():
    """
    Показывает информацию о лог-файле.
    """
    import os
    log_file = 'logs/anagram.log'
    
    if os.path.exists(log_file):
        file_size = os.path.getsize(log_file)
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("\n" + "="*50)
        print("ИНФОРМАЦИЯ О ЛОГ-ФАЙЛЕ")
        print("="*50)
        print(f"Файл: {log_file}")
        print(f"Размер: {file_size} байт")
        print(f"Количество записей: {len(lines)}")
        print(f"Последние 5 записей:")
        print("-" * 50)
        
        for line in lines[-5:]:
            print(line.strip())
    else:
        print("\nЛог-файл еще не создан")
        logger.warning("Попытка просмотра несуществующего лог-файла")

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================

def main():
    """
    Основная функция программы.
    Управляет взаимодействием с пользователем.
    """
    logger.info("=" * 60)
    logger.info("ПРОГРАММА ПОИСКА АНАГРАММ ЗАПУЩЕНА")
    logger.info("=" * 60)
    
    print("Добро пожаловать в программу поиска анаграмм с логированием!")
    print("Команды:")
    print("  'exit' - выход")
    print("  'test' - использовать тестовый текст")
    print("  'level' - изменить уровень логирования")
    print("  'log' - показать информацию о лог-файле")
    
    while True:
        text = get_user_input()
        
        if text is None:  # Пользователь выбрал exit
            break
        
        if text.lower() == 'log':
            show_log_file_info()
            continue
        
        # Выполняем поиск анаграмм
        anagrams = find_anagrams_in_text(text)
        
        # Показываем результаты
        display_results(anagrams)
        
        # Предлагаем продолжить
        print("\n" + "-"*50)
        print("Хотите продолжить? (y/n)")
        choice = input("> ").lower().strip()
        
        if choice != 'y':
            logger.info("Пользователь решил завершить работу")
            break
    
    logger.info("=" * 60)
    logger.info("ПРОГРАММА ПОИСКА АНАГРАММ ЗАВЕРШИЛА РАБОТУ")
    logger.info("=" * 60)
    print("\nСпасибо за использование программы!")
    print(f"Логи сохранены в файле: logs/anagram.log")

# ==================== ДЕМОНСТРАЦИЯ РАЗНЫХ УРОВНЕЙ ЛОГИРОВАНИЯ ====================

def demonstrate_log_levels():
    """
    Демонстрирует работу разных уровней логирования.
    """
    print("\n" + "="*70)
    print("ДЕМОНСТРАЦИЯ РАЗНЫХ УРОВНЕЙ ЛОГИРОВАНИЯ")
    print("="*70)
    
    test_text = "кот ток кто"
    
    # Уровень INFO (по умолчанию)
    print("\n1. Уровень LOGGING.INFO (по умолчанию):")
    print("-" * 50)
    setup_logging(logging.INFO)
    find_anagrams_in_text(test_text)
    
    # Уровень DEBUG
    print("\n2. Уровень LOGGING.DEBUG (максимальная детализация):")
    print("-" * 50)
    setup_logging(logging.DEBUG)
    find_anagrams_in_text(test_text)
    
    # Уровень WARNING
    print("\n3. Уровень LOGGING.WARNING (только предупреждения):")
    print("-" * 50)
    setup_logging(logging.WARNING)
    find_anagrams_in_text(test_text)
    
    # Уровень ERROR
    print("\n4. Уровень LOGGING.ERROR (только ошибки):")
    print("-" * 50)
    setup_logging(logging.ERROR)
    find_anagrams_in_text(test_text)
    
    # Уровень CRITICAL
    print("\n5. Уровень LOGGING.CRITICAL (практически ничего не логируется):")
    print("-" * 50)
    setup_logging(logging.CRITICAL)
    find_anagrams_in_text(test_text)
    
    # Возвращаем уровень по умолчанию
    setup_logging(logging.INFO)

# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    """
    Точка входа в программу.
    
    Режимы работы:
    1. Без аргументов: интерактивный режим
    2. Аргумент 'demo': демонстрация уровней логирования
    3. Аргумент 'test': тестовый прогон
    """
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'demo':
            # Демонстрация уровней логирования
            demonstrate_log_levels()
        elif sys.argv[1] == 'test':
            # Тестовый прогон
            test_texts = [
                "кот ток кто",
                "listen silent",
                "Азора роза",
                "",  # пустой текст
                123,  # не строка (будет ошибка)
            ]
            
            for text in test_texts:
                print(f"\nТестируем текст: {text}")
                try:
                    result = find_anagrams_in_text(text)
                    print(f"Результат: {result}")
                except Exception as e:
                    print(f"Ошибка: {e}")
        else:
            # Обработка переданного текста
            text = ' '.join(sys.argv[1:])
            print(f"Поиск анаграмм в тексте: {text}")
            result = find_anagrams_in_text(text)
            print(f"Результат: {result}")
    else:
        # Интерактивный режим
        main()