# ==================== АБСТРАКЦИЯ ====================

class MenuItem:

    def __init__(self, name, base_price):
        if type(self) is MenuItem:
            raise TypeError("MenuItem — абстрактный класс, создавать объекты напрямую нельзя")
        if base_price < 0:
            raise ValueError("Цена не может быть отрицательной")
        self._name = name
        self._base_price = base_price

    @property
    def name(self):
        return self._name

    @property
    def base_price(self):
        return self._base_price

    @property
    def display_name(self):
        return self._name

    def calculate_price(self):
        raise NotImplementedError("Метод calculate_price() должен быть переопределён")


# ==================== ПОЛИМОРФИЗМ: ТИПЫ БЛЮД ====================

class Pizza(MenuItem):
    SMALL = "маленькая"
    MEDIUM = "средняя"
    LARGE = "большая"

    def __init__(self, name, base_price, size):
        super().__init__(name, base_price)
        self._size = size

    @property
    def size(self):
        return self._size

    def calculate_price(self):
        if self._size == Pizza.LARGE:
            return self.base_price * 1.30
        return self.base_price


class Drink(MenuItem):
    def __init__(self, name, base_price, is_ice):
        super().__init__(name, base_price)
        self._is_ice = is_ice

    @property
    def is_ice(self):
        return self._is_ice

    def calculate_price(self):
        return self.base_price

    @property
    def display_name(self):
        return f"{self.name} со льдом" if self._is_ice else self.name


class ComboSet(MenuItem):
    DISCOUNT = 0.15

    def __init__(self, name, dishes):
        super().__init__(name, 0) 
        self._dishes = list(dishes)

    @property
    def dishes(self):
        return tuple(self._dishes)

    def calculate_price(self):
        total = sum(dish.calculate_price() for dish in self._dishes)
        return total * (1 - self.DISCOUNT)


# ==================== ИНКАПСУЛЯЦИЯ: ЗАКАЗ ====================

class Order:
    CREATED = "Создан"
    COOKING = "Готовится"
    DELIVERING = "Доставляется"
    DELIVERED = "Доставлен"
    _STEPS = (CREATED, COOKING, DELIVERING, DELIVERED)

    def __init__(self):
        self.__items = []
        self.__status = Order.CREATED

    @property
    def status(self):
        return self.__status

    @property
    def items(self):
        return tuple(self.__items)

    def add_item(self, item):
        if item is None:
            raise ValueError("Блюдо не может быть None")
        if self.__status != Order.CREATED:
            raise RuntimeError(f"Нельзя добавить блюдо: заказ уже в статусе «{self.__status}»")
        self.__items.append(item)

    def next_step(self):
        index = Order._STEPS.index(self.__status)
        if index == len(Order._STEPS) - 1:
            raise RuntimeError("Заказ уже доставлен, дальше переводить нельзя")
        self.__status = Order._STEPS[index + 1]

    def get_total_cost(self):
        return sum(item.calculate_price() for item in self.__items)

    def pay(self, payment_method):
        if payment_method is None:
            raise ValueError("Способ оплаты не указан")
        if not self.__items:
            raise RuntimeError("Нельзя оплатить пустой заказ")
        payment_method.collect_payment(self.get_total_cost())


# ==================== ПОЛИМОРФИЗМ: СПОСОБЫ ОПЛАТЫ ====================

class PaymentStrategy:

    def collect_payment(self, amount):
        raise NotImplementedError("Метод collect_payment() должен быть переопределён")


class CardPayment(PaymentStrategy):
    def __init__(self, card_number, expiry_year, expiry_month):
        self._card_number = card_number
        self._expiry = (expiry_year, expiry_month)

    def collect_payment(self, amount):
        today = (2026, 11)
        if today > self._expiry:
            year, month = self._expiry
            raise RuntimeError(f"Срок действия карты истёк: {month:02d}/{year}")
        last4 = self._card_number[-4:]
        print(f"Списано {amount:.2f} руб. с карты **** {last4}")


class CashPayment(PaymentStrategy):
    def collect_payment(self, amount):
        print(f"Оплата наличными: {amount:.2f} руб.")


# ==================== ДЕМОНСТРАЦИЯ ====================

if __name__ == "__main__":
    order = Order()

    order.add_item(Pizza("Маргарита", 500, Pizza.LARGE))
    order.add_item(Drink("Кола", 100, is_ice=True))
    order.add_item(ComboSet("Комбо Пепперони + Сок", [
        Pizza("Пепперони", 600, Pizza.MEDIUM),
        Drink("Сок", 150, is_ice=False),
    ]))

    print("=== Состав заказа ===")
    for item in order.items:
        print(f"{item.display_name}: {item.calculate_price():.2f} руб.")
    print(f"Итого: {order.get_total_cost():.2f} руб.")

    print("\n=== Оплата ===")
    order.pay(CashPayment())
    try:
        order.pay(CardPayment("1234567812345678", 2020, 1))
    except RuntimeError as e:
        print(f"Ошибка оплаты картой: {e}")
    order.pay(CardPayment("1234567812345678", 2030, 12))

    print("\n=== Статусы ===")
    print(f"Текущий статус: {order.status}")
    order.next_step()
    print(f"Текущий статус: {order.status}")

    try:
        order.add_item(Drink("Чай", 80, is_ice=False))
    except RuntimeError as e:
        print(f"Ошибка: {e}")

    order.next_step()
    order.next_step()
    print(f"Текущий статус: {order.status}")

    try:
        order.next_step()
    except RuntimeError as e:
        print(f"Ошибка: {e}")