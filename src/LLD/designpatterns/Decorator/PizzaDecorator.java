package LLD.designpatterns.Decorator;

public abstract class PizzaDecorator implements BasePizza {

    public BasePizza pizza;
    public PizzaDecorator(BasePizza pizza) {
        this.pizza = pizza;
    }


}
