package LLD.designpatterns.strategy;

// Context class
public class ShoppingCart {
    private PaymentStrategy strategy;

    public void setStrategy(PaymentStrategy strategy){
        this.strategy = strategy;
    }

    public void checkout(int amount){
        this.strategy.pay(amount);
    }


}
