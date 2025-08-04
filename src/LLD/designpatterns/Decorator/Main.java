package LLD.designpatterns.Decorator;

public class Main {
    public static void main(String[] args) {
        BasePizza pizza1 = new MushRoomsDecorator(new ExtraCheeseDecorator(new Margherita()));
        BasePizza pizza2 = new ExtraCheeseDecorator(new MushRoomsDecorator(new VegDelight()));


        System.out.println("Pizza1 cost: " + pizza1.getCost());
        System.out.println("Pizza2 cost: " + pizza2.getCost());


    }
}
