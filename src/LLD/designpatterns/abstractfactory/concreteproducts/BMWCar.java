package LLD.designpatterns.abstractfactory.concreteproducts;

import LLD.designpatterns.abstractfactory.products.Car;

public class BMWCar implements Car {
    @Override
    public void drive() {
        System.out.println("Driving BMW Car");

    }
}
