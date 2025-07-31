package LLD.designpatterns.strategy;

public class Main {

    public static void main(String[] args) {
        //Demonstrate the Strategy Design Pattern
        System.out.println("=============================STRATEGY DESIGN PATTERN======================================================");
        ShoppingCart cart = new ShoppingCart();
        cart.setStrategy(new UpIPaymentStrategy());
        cart.checkout(1000);
        System.out.println();
    }
}
