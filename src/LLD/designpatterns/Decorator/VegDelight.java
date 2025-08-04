package LLD.designpatterns.Decorator;

public class VegDelight implements BasePizza{
    @Override
    public String getDescription() {
        return "VegDelight";
    }

    @Override
    public int getCost() {
        return 120;
    }
}
