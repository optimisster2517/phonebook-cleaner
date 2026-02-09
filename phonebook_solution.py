from pprint import pprint
import csv
import re
from collections import defaultdict

# Читаем адресную книгу в формате CSV в список contacts_list
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

print("Исходные данные:")
pprint(contacts_list)


# TODO 1: выполните пункты 1-3 ДЗ

# Пункт 1: Разделение ФИО на отдельные поля
def fix_name_fields(contact):
    """Разделяет ФИО на отдельные поля lastname, firstname, surname"""
    # Объединяем первые три поля (которые могут содержать части ФИО)
    full_name = " ".join(contact[:3]).strip()

    # Разделяем по пробелам и очищаем от пустых строк
    name_parts = [part.strip() for part in full_name.split() if part.strip()]

    # Заполняем поля: фамилия, имя, отчество
    lastname = name_parts[0] if len(name_parts) > 0 else ""
    firstname = name_parts[1] if len(name_parts) > 1 else ""
    surname = name_parts[2] if len(name_parts) > 2 else ""

    # Возвращаем обновленный контакт
    result = [lastname, firstname, surname] + contact[3:]
    return result


# Пункт 2: Приведение телефонов к единому формату
def normalize_phone(phone):
    """Приводит телефон к формату +7(999)999-99-99 или +7(999)999-99-99 доб.9999"""
    if not phone or phone.strip() == "":
        return ""

    # Паттерн для поиска добавочного номера
    extension_pattern = r'(?:доб\.?|ext\.?|добавочный)\s*(\d+)'
    extension_match = re.search(extension_pattern, phone, re.IGNORECASE)
    extension = extension_match.group(1) if extension_match else ""

    # Извлекаем только цифры из основного номера
    digits_only = re.sub(r'\D', '', phone)

    # Если нет цифр, возвращаем пустую строку
    if len(digits_only) == 0:
        return ""

    # Приводим к 11-значному номеру с кодом страны 7
    if len(digits_only) == 11:
        # Если начинается с 8, заменяем на 7
        if digits_only.startswith('8'):
            digits_only = '7' + digits_only[1:]
        # Если не начинается с 7, добавляем 7 в начало
        elif not digits_only.startswith('7'):
            digits_only = '7' + digits_only
    elif len(digits_only) == 10:
        # Если 10 цифр, добавляем 7 в начало
        digits_only = '7' + digits_only
    elif len(digits_only) == 7:
        # Если 7 цифр, добавляем код страны и региона (Москва)
        digits_only = '7495' + digits_only
    elif len(digits_only) < 7:
        # Слишком короткий номер
        return ""
    else:
        # Более 11 цифр - берем последние 10 и добавляем 7
        digits_only = '7' + digits_only[-10:]

    # Форматируем номер
    if len(digits_only) == 11 and digits_only.startswith('7'):
        formatted = f"+7({digits_only[1:4]}){digits_only[4:7]}-{digits_only[7:9]}-{digits_only[9:11]}"
        if extension:
            formatted += f" доб.{extension}"
        return formatted

    # Если что-то пошло не так, возвращаем исходный номер
    return phone


# Применяем обработку к каждому контакту
processed_contacts = []
for contact in contacts_list:
    # Пропускаем заголовок
    if contact == contacts_list[0]:
        processed_contacts.append(contact)
        continue

    # Исправляем поля имени
    fixed_contact = fix_name_fields(contact)

    # Нормализуем телефон (поле с индексом 5)
    if len(fixed_contact) > 5:
        original_phone = fixed_contact[5]
        normalized_phone = normalize_phone(original_phone)
        fixed_contact[5] = normalized_phone

        # Отладочная информация для телефонов
        if original_phone.strip():
            print(f"Телефон: '{original_phone}' → '{normalized_phone}'")

    processed_contacts.append(fixed_contact)

print("\nПосле обработки имен и телефонов:")
for i, contact in enumerate(processed_contacts):
    if i == 0:
        print("Заголовок:", contact)
    else:
        print(f"Запись {i}: {contact}")


# Пункт 3: Объединение дублирующихся записей
def merge_contacts(contacts):
    """Объединяет дублирующиеся записи по ФИО"""
    contacts_dict = defaultdict(list)
    header = contacts[0]

    # Группируем контакты по ФИО (lastname + firstname)
    for contact in contacts[1:]:
        if len(contact) >= 2:
            lastname = contact[0].lower().strip() if contact[0] else ""
            firstname = contact[1].lower().strip() if contact[1] else ""
            key = (lastname, firstname)

            # Пропускаем записи с пустыми фамилией и именем
            if lastname and firstname:
                contacts_dict[key].append(contact)

    # Объединяем дублирующиеся записи
    merged_contacts = [header]

    for key, contact_group in contacts_dict.items():
        if len(contact_group) == 1:
            merged_contacts.append(contact_group[0])
        else:
            print(f"\nОбъединяем {len(contact_group)} записей для: {key[0].title()} {key[1].title()}")

            # Инициализируем результирующую запись
            merged_contact = ["", "", "", "", "", "", ""]

            # Собираем все непустые значения из каждого поля
            for contact in contact_group:
                print(f"  Обрабатываем: {contact}")
                for field_idx in range(min(len(merged_contact), len(contact))):
                    current_value = contact[field_idx].strip() if contact[field_idx] else ""
                    existing_value = merged_contact[field_idx].strip() if merged_contact[field_idx] else ""

                    # Если поле пустое, заполняем
                    if not existing_value and current_value:
                        merged_contact[field_idx] = current_value
                    # Для организации и должности - берем наиболее полную информацию
                    elif field_idx in [3, 4] and current_value and len(current_value) > len(existing_value):
                        merged_contact[field_idx] = current_value
                    # Для телефона и email - берем непустые значения
                    elif field_idx in [5, 6] and current_value and not existing_value:
                        merged_contact[field_idx] = current_value

            print(f"  Результат: {merged_contact}")
            merged_contacts.append(merged_contact)

    return merged_contacts


# Объединяем дублирующиеся записи
final_contacts = merge_contacts(processed_contacts)

print("\nФинальный результат после объединения дублей:")
for i, contact in enumerate(final_contacts):
    if i == 0:
        print("Заголовок:", contact)
    else:
        print(f"Запись {i}: {contact}")

print(f"\nСтатистика обработки:")
print(f"Исходное количество записей: {len(contacts_list)} (включая заголовок)")
print(f"Итоговое количество записей: {len(final_contacts)} (включая заголовок)")
print(f"Удалено дублей: {len(contacts_list) - len(final_contacts)}")

# TODO 2: сохраните получившиеся данные в другой файл
with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_contacts)

print(f"\nОбработка завершена! Результат сохранен в файл phonebook.csv")