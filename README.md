# 🎯 Design Patterns Implementation in Java

[![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=java&logoColor=white)](https://www.oracle.com/java/)
[![Design Patterns](https://img.shields.io/badge/Design_Patterns-Gang_of_Four-blue?style=for-the-badge)](https://en.wikipedia.org/wiki/Design_Patterns)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://choosealicense.com/licenses/mit/)

A comprehensive collection of **Gang of Four Design Patterns** implemented in Java, demonstrating clean code principles and object-oriented design best practices.

## 📋 Table of Contents

- [Overview](#-overview)
- [Design Patterns Implemented](#-design-patterns-implemented)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Design Pattern Details](#-design-pattern-details)
- [Running the Examples](#-running-the-examples)
- [Contributing](#-contributing)

## 🌟 Overview

This repository contains implementations of classical design patterns that solve common software design problems. Each pattern is implemented with:

- ✅ **Clean, readable code** with proper documentation
- ✅ **Real-world examples** that demonstrate practical usage
- ✅ **Comprehensive demos** showing pattern behavior
- ✅ **Best practices** following SOLID principles

## 🎨 Design Patterns Implemented

| Pattern | Type | Status | Description |
|---------|------|--------|-------------|
| **Strategy** | Behavioral | ✅ Live | Payment processing with interchangeable algorithms |
| **Factory** | Creational | ✅ Live | Shape creation with runtime type selection |
| **Abstract Factory** | Creational | ✅ Live | Vehicle manufacturing families (BMW, Tata) |
| **Builder** | Creational | 📝 Available | Burger meal construction with optional components |
| **Decorator** | Structural | 📝 Available | Pizza customization with dynamic toppings |
| **Observer** | Behavioral | 📝 Available | iPhone stock notification system |
| **Chain of Responsibility** | Behavioral | 📝 Available | Logger chain with different levels |
| **Null Object** | Behavioral | 📝 Available | Animal handling without null checks |
| **State + Strategy** | Behavioral | 📝 Available | Vending machine with multiple payment methods |

## 📁 Project Structure

```
Design-Patterns/
├── src/
│   └── LLD/
│       └── designpatterns/
│           ├── strategy/           # ✅ Strategy Pattern (Live)
│           │   ├── PaymentStrategy.java
│           │   ├── CreditCardStrategy.java
│           │   ├── UpIPaymentStrategy.java
│           │   ├── ShoppingCart.java
│           │   └── Main.java
│           ├── factory/            # ✅ Factory Pattern (Live)
│           │   ├── Shape.java
│           │   ├── Circle.java, Rectangle.java, Square.java
│           │   ├── ShapeFactory.java
│           │   └── main.java
│           ├── abstractfactory/    # ✅ Abstract Factory Pattern (Live)
│           │   ├── VehicleFactory.java
│           │   ├── concretefactories/
│           │   ├── concreteproducts/
│           │   └── products/
│           ├── builderpattern/     # 📝 Builder Pattern
│           ├── Decorator/          # 📝 Decorator Pattern
│           ├── observer/           # 📝 Observer Pattern
│           ├── cor/                # 📝 Chain of Responsibility
│           ├── nullobjectpattern/  # 📝 Null Object Pattern
│           └── vendingmachine/     # 📝 State + Strategy Pattern
├── README.md
└── .gitignore
```

## 🚀 Getting Started

### Prerequisites

- **Java 8+** installed on your system
- **Git** for cloning the repository

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/stuck-in-a-local-optimum/Design-Patterns.git
   cd Design-Patterns
   ```

2. **Compile the code**
   ```bash
   javac -cp src src/LLD/designpatterns/strategy/Main.java
   ```

3. **Run the example**
   ```bash
   java -cp src LLD.designpatterns.strategy.Main
   ```

## 🔍 Design Pattern Details

### 💳 **Strategy Pattern**
**Problem**: Need to switch between different payment algorithms at runtime  
**Solution**: Encapsulate payment algorithms in separate strategy classes

**Key Components**:
- `PaymentStrategy` - Strategy interface
- `CreditCardStrategy` - Concrete strategy for card payments
- `UpIPaymentStrategy` - Concrete strategy for UPI payments  
- `ShoppingCart` - Context class that uses strategies

**Benefits**:
- ✅ Runtime algorithm selection
- ✅ Easy to add new payment methods
- ✅ Follows Open/Closed Principle
- ✅ Eliminates conditional statements

**Example Usage**:
```java
ShoppingCart cart = new ShoppingCart();
cart.setStrategy(new CreditCardStrategy());
cart.checkout(1000); // Uses credit card payment

cart.setStrategy(new UpIPaymentStrategy());  
cart.checkout(500);  // Uses UPI payment
```

## ▶️ Running the Examples

Each design pattern includes a `Main.java` file with comprehensive demonstrations:

```bash
# Strategy Pattern
javac -cp src src/LLD/designpatterns/strategy/Main.java
java -cp src LLD.designpatterns.strategy.Main

# Factory Pattern
javac -cp src src/LLD/designpatterns/factory/main.java
java -cp src LLD.designpatterns.factory.main

# Abstract Factory Pattern
javac -cp src src/LLD/designpatterns/abstractfactory/main.java
java -cp src LLD.designpatterns.abstractfactory.main
```

## 🎯 Learning Objectives

By exploring these implementations, you'll learn:

- **When to use** each design pattern
- **How to implement** patterns correctly in Java
- **Real-world applications** of design patterns
- **Best practices** for object-oriented design
- **SOLID principles** in action

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/new-pattern`)
3. **Commit** your changes (`git commit -m 'Add Singleton pattern'`)
4. **Push** to the branch (`git push origin feature/new-pattern`)
5. **Open** a Pull Request

### Contribution Guidelines

- Follow existing code style and structure
- Include comprehensive documentation
- Add meaningful examples and demos
- Write clean, readable code
- Test your implementations thoroughly

## 💡 About This Implementation

These design patterns were **implemented independently** as learning exercises, 
demonstrating practical understanding of object-oriented design principles.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**stuck-in-a-local-optimum**
- GitHub: [@stuck-in-a-local-optimum](https://github.com/stuck-in-a-local-optimum)
- Email: ajeet19010@iiitd.ac.in

---

⭐ **Star this repository** if you find it helpful for learning design patterns!

🚀 **Watch this repository** to stay updated with new pattern implementations! 