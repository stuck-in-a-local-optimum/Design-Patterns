package LLD.designpatterns.factory;

public class ShapeFactory {

    Shape getShape(String shape){
        switch (shape.toUpperCase()){
            case "SQUARE":
                return new Square();
            case "RECTANGLE":
                return new Rectangle();
            case "CIRCLE":
                return new Circle();
            default:
                return null;
        }
    }
}
