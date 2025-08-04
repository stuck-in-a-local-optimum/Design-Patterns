package LLD.designpatterns.Decorator;

public class ExtraCheeseDecorator extends PizzaDecorator{
    public ExtraCheeseDecorator(BasePizza pizza) {
        super(pizza);
    }

    @Override
    public String getDescription() {
        return "+ Extra-Cheese";
    }

    @Override
    public int getCost() {
        return pizza.getCost() + 40;
    }
}
