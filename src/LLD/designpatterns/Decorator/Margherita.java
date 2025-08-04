package LLD.designpatterns.Decorator;

public class Margherita implements BasePizza {

    @Override
    public String getDescription() {
        return "Margherita Pizza";
    }

    @Override
    public int getCost() {
        return 100;
    }
}
