[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/Eugen417/Ippon-UPS-SNMP)
# Ippon UPS SNMP Integration for Home Assistant

Интеграция для мониторинга ИБП **Ippon** через протокол **SNMP v3**.

### ✅ Протестировано на оборудовании:

* **ИБП:** [Innova G2 Euro 3000](https://ippon.ru/catalog/item/innova-g2-euro-3000/)
* **SNMP-карта:** [Ippon NMC SNMP II](https://ippon.ru/catalog/item/ippon-NMC-SNMP-II-card-1022865/)

---
[![Open your Home Assistant instance and open a repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg?style=for-the-badge)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Eugen417&repository=Ippon-UPS-SNMP&category=integration)

---

## ✨ Особенности

* **SNMP v3**: Безопасный мониторинг с использованием авторизации (MD5/SHA).
* **13 ключевых показателей**: Напряжение, частота, температура, состояние батарей и системы.
* **Полная совместимость с Python 3.13**: Работает на последних версиях Home Assistant (2024.12+).
* **Простая установка**: Настройка через UI (Config Flow) без правки конфигурационных файлов.

## 📊 Доступные сенсоры

Интеграция автоматически создает следующие объекты:

* **Battery**: Статус, Уровень заряда (%), Напряжение, Температура, Оставшееся время работы.
* **Input/Output**: Напряжение (V), Частота (Hz).
* **System**: Общий статус системы, Источник питания (Line/Battery), Результат последнего теста.

## 🚀 Установка

### Вариант 1: Через HACS (Рекомендуется)

1. Нажмите на кнопку **Open Repo in HACS** выше.
2. В открывшемся окне вашего Home Assistant нажмите **Download**.
3. Перезагрузите Home Assistant.

### Вариант 2: Вручную

1. Скопируйте папку `ippon_ups_snmp` из данного репозитория в директорию `/config/custom_components/`.
2. Перезагрузите Home Assistant.

## ⚙️ Настройка

1. Перейдите в **Настройки** -> **Устройства и службы** -> **Добавить интеграцию**.
2. Найдите в списке **Ippon UPS SNMP**.
3. Введите данные вашей SNMP-карты:
* **Host**: IP-адрес карты.
* **Username**: Имя пользователя (по умолчанию `HomeAs`).
* **Auth Key**: Пароль (Auth Password).
* **Protocol**: Протокол (например, `hmac-md5`).



## 📝 Пример автоматизации

Оповещение при переходе ИБП на работу от батарей:

```yaml
alias: "ИБП: Переход на батарею"
trigger:
  - platform: state
    entity_id: sensor.ups_ippon_output_source
    to: "battery"
action:
  - service: notify.mobile_app
    data:
      title: "Питание потеряно"
      message: "ИБП Innova G2 перешел на работу от батарей!"

```

---
<img width="349" height="780" alt="Снимок экрана — 2026-06-21 в 17 27 55" src="https://github.com/user-attachments/assets/8062dda1-4d21-4f77-9ce6-3beed5c500a9" />

**Разработчик:** [@Eugen417](https://www.google.com/search?q=https://github.com/Eugen417)
