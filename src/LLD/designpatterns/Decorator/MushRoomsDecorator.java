package LLD.designpatterns.Decorator;

public class MushRoomsDecorator extends PizzaDecorator{

    public MushRoomsDecorator(BasePizza pizza) {
        super(pizza);
    }

    @Override
    public String getDescription() {
        return "+ mushrooms";
    }

    @Override
    public int getCost() {
        return pizza.getCost() + 20;
    }
}
