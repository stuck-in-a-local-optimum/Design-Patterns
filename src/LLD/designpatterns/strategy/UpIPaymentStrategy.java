package LLD.designpatterns.strategy;

public class UpIPaymentStrategy implements PaymentStrategy {
    @Override
    public void pay(int amount) {
        System.out.println("Paid Rs." + amount + " via UPI");

    }
}
