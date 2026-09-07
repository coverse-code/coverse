class phone:

    def __init__(self, model, color, price):
        self.model = model
        self.color = color
        self.price = price

    def phone_info(self):
        print(f"Model: {self.model}, Color: {self.color}, Price: {self.price}")


phone1 = phone("redmagic 11s pro", "silver", 10000)
phone1.phone_info()