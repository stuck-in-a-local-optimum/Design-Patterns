package LLD.designpatterns.factory;

public class main {
    public static void main(String[] args) {
        ShapeFactory factory = new ShapeFactory();
        Shape rectangle = factory.getShape("RECTANGLE");
        rectangle.draw();

        Shape circle = factory.getShape("circle");
        circle.draw();

        Shape square = factory.getShape("Square");
        square.draw();

    }
}
