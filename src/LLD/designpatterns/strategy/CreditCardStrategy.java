package LLD.designpatterns.strategy;

public class CreditCardStrategy implements PaymentStrategy {
    @Override
    public void pay(int amount) {
        System.out.println("Paid Rs." + amount + " via Credit Card");

    }
}
