package LLD.designpatterns.abstractfactory.concreteproducts;

import LLD.designpatterns.abstractfactory.products.Car;

public class TataCar implements Car {

    @Override
    public void drive() {
        System.out.println("Driving TataCar");

    }
}
